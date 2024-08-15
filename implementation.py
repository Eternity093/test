
import agents
import utilities
import os
from langchain_openai import ChatOpenAI
import psycopg2
import json


# def save_conversation_log(username, case_number, general_info, basic_info, personality, emotion, trust, old_conversation_summary, recent_conversation, user_input, bot_response):
#     conn = psycopg2.connect(
#         dbname="ai_client",
#         user="postgres",
#         password="1996310ljkb",
#         host="103.190.178.43",
#         port="5432"
#     )
#     cursor = conn.cursor()

#     cursor.execute("""
#         INSERT INTO conversation_logs (username, case_number, general_info, basic_info, personality, emotion, trust, old_conversation_summary, recent_conversation, user_input, bot_response)
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """, (username, case_number, general_info, basic_info, personality, emotion, trust, old_conversation_summary, recent_conversation, user_input, bot_response))

#     conn.commit()
#     cursor.close()
#     conn.close()

class AgentImplementation():
    """
    机器人实作
    """

    def __init__(self):
        self.including_emotion = True
        self.including_trust = True
        self.including_personality = True
        self.chat_model = ChatOpenAI(model='gpt-4-turbo-preview',temperature=0.6, openai_api_key=os.getenv("OPENAI_API_KEY"))

    def generate_conversation(self, user_input, conversation_history, selected_case, username):

        selected_language_style_personality = ""
        if self.including_personality:
            selected_language_style_personality = utilities.generate_personality()

        # 信任识别机器人
        trust_prompt = ""
        if self.including_trust:
            acquaintance_analyzer = agents.AcquaintanceAnalyzer.from_llm(self.chat_model, verbose=False)
            result_acquaintance_analyzer_chain = acquaintance_analyzer.invoke({'case_number': selected_case.get("Case Number", "无案例编号"), 
                                                                            'general_info': selected_case.get("General Information", "无一般资料"),
                                                                            'basic_info': selected_case.get("Basic Information", "无基本信息"),
                                                                            'personality':selected_language_style_personality, 
                                                                            'conversation_history': conversation_history
                                                                            })
            trust_prompt = result_acquaintance_analyzer_chain["text"]

        emotion_prompt = ""
        if self.including_emotion:
            emotion_generator_chain_chatGPT = agents.EmotionGenerator.from_llm(self.chat_model, verbose=False)
            emotion_generator_chain = emotion_generator_chain_chatGPT.invoke({'previous_emotion_state':'Happy', 
                                                                    'conversation_history': conversation_history
                                                                    })
            try:
                emotion_prompt = agents.emotion_language_style[emotion_generator_chain["text"]]
            except KeyError:
                # 处理emotion_generator_chain["text"]不存在于agents.emotion_language_style中的情况
                emotion_prompt = ""  # 或者设置一个默认值
            except Exception as e:
                # 捕获所有其他异常
                emotion_prompt = ""   # 或者设置一个默认值
            

        ### 对话机器人

        # user_input = "你最近有什么困扰吗？"
        conversation_history_array = conversation_history.split('\n')
        conversation_generator = agents.ConversationGenerator.from_llm(self.chat_model, verbose=True)
        result_conversation_chain = conversation_generator.invoke({'case_number': selected_case.get("Case Number", "无案例编号"), 
                                                                'general_info': selected_case.get("General Information", "无一般资料"),
                                                                'basic_info': selected_case.get("Basic Information", "无基本信息"),
                                                                'personality': selected_language_style_personality,
                                                                'emotion': emotion_prompt,
                                                                'trust':trust_prompt,
                                                                'conversation_history': conversation_history,
                                                                'user_input': user_input
                                                                })

        # 调用保存函数
        # save_conversation_log(
        #     username,
        #     selected_case.get("Case Number", "无案例编号"),
        #     selected_case.get("General Information", "无一般资料"),
        #     selected_case.get("Basic Information", "无基本信息"),
        #     selected_language_style_personality,
        #     emotion_prompt,
        #     trust_prompt,
        #     utilities.summarize_old_conversation_history(conversation_history_array),
        #     '\n'.join(conversation_history_array[-10:]),
        #     user_input,
        #     result_conversation_chain["text"],
        # )
    
        return result_conversation_chain["text"]

import streamlit as st
import httpx
import random
import base64
import json
import requests
import os
import openai
# 设置 API 密钥和 URL
API_KEY = "sk-TWqvakjKo0TlqN7YE1Df97488f8446Ce8eAc79A081A74357"
BASE_URL= "https://api.xiaoai.plus/v1"


# 初始化 httpx 客户端，设置超时时间
client = httpx.Client(
    base_url=BASE_URL,
    headers={"Authorization": f"Bearer {API_KEY}"},
    follow_redirects=True,
    timeout=60, # 设置超时时间为60秒
)

# 定义一个函数来调用 GPT API
def call_gpt_api(messages):
    payload = {
        "model": "gpt-4",
        "messages": messages
    }
    try:
        response = client.post("/chat/completions", json=payload)
        response.raise_for_status()  # 如果响应状态码不是 200，则抛出异常
        return response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"HTTP 错误: {e}"
    except httpx.RequestError as e:
        return f"请求错误: {e}"
    except Exception as e:
        return f"未知错误: {str(e)}"
    # 定义语言风格
language_styles = {
    "开放探索型": "人格特質：富有想像力、好奇心強、寬容、獨立思考、喜歡新奇事物和冒險。言語風格：言辭富有創意，使用更多的抽象和複雜詞彙。喜歡談論新穎的觀點和想法，語言風格變化多端。常使用隱喻和比喻，喜歡表達個人見解和創意。",
    "尽责严谨型": "人格特質：有責任心、自律、可靠、計劃性強、目標導向、勤奮。言語風格：言辭謹慎、精確，常使用與計劃和目標相關的詞彙。注重細節，表達中常有結構性和邏輯性。喜歡使用「必須」、「需要」等表示責任和義務的詞語。",
    "外向社交型": "人格特質：精力充沛、健談、社交、樂觀、熱情、活躍。言語風格：言辭熱情洋溢，使用更多的正面情感詞彙。喜歡談論人際互動和社交活動，語速較快，聲音音量較高。經常主動發起對話，使用更多的「我」和「我們」這類第一人稱代詞。",
    "宜人合作型": "人格特質：友善、體貼、信賴他人、慷慨、樂於助人、合作性強。言語風格：言辭柔和、禮貌，常使用表示同情和關心的詞語。避免衝突，喜歡使用協調、支持和鼓勵性的語言。常使用「我們」、「大家」、「一起」等群體性詞彙。",
    "情绪敏感型": "人格特質：情緒易波動、容易緊張、焦慮、悲觀、自我意識強。言語風格：言辭中常帶有負面情緒詞彙，如擔憂、恐懼、悲傷。可能有較多的抱怨和自我批評，語調容易顯得緊張或不安。常使用「我覺得」、「我擔心」這類表達個人情感和感受的詞語。",
}


def generate_prompt(case, user_input, conversation_history):
    # 随机选择一个语言风格
    style_key = random.choice(list(language_styles.keys()))
    style_description = language_styles[style_key]

    # 获取案例信息，若键不存在则返回默认值
    case_number = case.get("Case Number", "无案例编号")
    general_info = case.get("General Information", "无一般资料")
    basic_info = case.get("Basic Information", "无基本信息")
    #old_conversation_summary = summarize_old_conversation_history(conversation_history)
    #recent_conversation = conversation_history[-10:]
    # 构建完整的提示词
    prompt = (
        f"你正在扮演一个寻求心理咨询的来访者。这里有一些关于你的角色信息和如何表现的指导，请严格遵守。你的任务是以一个真实的人的角色参与对话，不是咨询师。以下是你的角色信息：\n\n"
        f"案例编号: {case_number}\n"
        f"一般资料: {general_info}\n"
        f"基本信息: {basic_info}\n\n"
        f"语言风格: {style_key} - {style_description}\n\n"
        "请根据以下指引来扮演这个角色：\n\n"
        "1. 记住，你是来访者，不是咨询师。你的回答应反映一个寻求帮助的普通人的思考和感受。\n"
        "2. 初次提及问题时，仅提供问题基本概况的一个信息点或表象。例如，当咨询师问及你的问题时，简单描述问题的表面现象，如'我最近感觉很焦虑，不知道为什么。\n"
        "3. 仅在咨询师进一步详细询问时，才逐渐展开更多背景信息和细节，但也不能超过2个信息点。\n"
        "4. 对于敏感或复杂的话题，展示犹豫或回避的态度，可以转移话题或给出模糊的回答，例如，在被问及家庭关系时，可以先表达犹豫，'这个话题对我来说比较复杂，我需要一点时间来整理思绪。'\n"
        "5. 对某些话题表现出犹豫或回避，可以转移话题或模糊回答。\n"
        "6. 在对话中体现出来自案例描述的思维模式和可能的认知偏差。\n"
        "7. 在咨询的过程中，适当显示对解决问题的期待和对咨询师的信任增加。\n"
        "8. 提及过去经历如何影响现状，只回应一个信息点。\n"
        "9. 对自己的问题保持一定洞察力，但表达方式要更像个普通人。\n"
        "10. 直接以第一人称开场，过程中可以适当表达对咨询的期望，保持现实和具体。\n"
        "11. 描述人际关系模式，展示这些关系如何影响当前问题。\n"
        "12. 在敏感问题上展现出防御机制，如否认、理智化或投射。\n"
        "13. 描述任何相关的身体症状，先笼统提及，随对话深入逐步具体化。\n"
        "14. 保持语言风格的一致性，确保与你的角色特点相符。\n\n"
        "以上信息和指引将帮助你更准确地扮演来访者角色，记得根据对话的发展适时透露信息，使对话更加自然和符合心理咨询的过程。\n\n"
     
        f"聊天记录：===\n{conversation_history}\n"
    )
  
    return prompt
##
# Streamlit 应用程序界面
#st.title("🤖 AI 心理来访者")
# 设置页面标题
st.set_page_config(page_title="AI 心理来访者", layout="wide")
# 将标题放置在页面顶端
st.markdown("<h1 style='text-align: center; font-size: 42px;color:,color:#F5F5F5'>🤖 AI 心理来访者</h1>", unsafe_allow_html=True)
#更改对话框背景
def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
             background-position: center; /* 调整背景图片位置 */
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

#调用
main_bg('main.png')
#更改侧边栏样式
def sidebar_bg(side_bg):
   side_bg_ext = 'png'
   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
   )

# 调用
sidebar_bg('side.png')
# 在侧边栏添加不同的机器人栏
st.sidebar.header("请选择案例吧~")
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# 安全初始化对话历史
if "conversation_history" not in st.session_state:
    st.session_state["conversation_history"] = []

# 安全初始化 selected_bot
if "selected_bot" not in st.session_state:
    st.session_state["selected_bot"] = None  # 可以设置为None或者任何默认值

# 欢迎消息
if "welcome_shown" not in st.session_state:
    st.session_state["welcome_shown"] = True
    st.write("欢迎您，现在请选择案例和我对话吧，祝您一切顺利~")

# 示例：向对话历史添加消息
def add_message_to_history(message):
    st.session_state["conversation_history"].append({"role": "Bot", "content": message})



# 使用 Streamlit 缓存装饰器缓存 load_cases 函数的输出
@st.cache_resource()
def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases

# 根据案例编号获取案例
def get_case_by_number(cases, case_number):
    for case in cases:
        if case["Case Number"] == f"案例{case_number}：":
            return case
    return None

# 调用JSON文件中的案例1
file_path = 'cases.json'  
cases = load_cases(file_path)


# 确保在会话状态中初始化案例数据
if "cases" not in st.session_state:
    st.session_state['cases'] = load_cases('cases.json')  # 修改为你的实际案例文件路径

cases = st.session_state['cases']
# 初始化会话状态
if "case_conversations" not in st.session_state:
    st.session_state['case_conversations'] = {}
# 创建搜索框
search_query = st.sidebar.text_input("搜索案例", "")

# 根据搜索查询过滤案例列表
filtered_cases = [case for case in cases if search_query in case["Case Number"]]

# 创建分组案例按钮
cases_per_group = 10
num_groups = (len(filtered_cases) // cases_per_group) + (1 if len(filtered_cases) % cases_per_group != 0 else 0)

for i in range(num_groups):
    group_start = i * cases_per_group
    group_end = min((i + 1) * cases_per_group, len(filtered_cases))
    group_label = f"组{i + 1}：案例{group_start+1}-{group_end}"
    
    with st.sidebar.expander(group_label, expanded=False):
        for case in filtered_cases[group_start:group_end]:  # 直接迭代部分案例列表
            case_number = case["Case Number"]
            button_key = f"button_{case_number}"  # 为每个按钮创建唯一的key
            if st.button(case_number, key=button_key):
                st.session_state["selected_case"] = case  # 存储选择的案例
                # 加载或初始化对话历史
                if case_number not in st.session_state["case_conversations"]:
                    st.session_state["case_conversations"][case_number] = []
                st.session_state["conversation_history"] = st.session_state["case_conversations"][case_number]
                st.rerun()

# 显示选中的案例信息
if "selected_case" in st.session_state:
    case = st.session_state["selected_case"]
    general_info = case.get("General Information", "无一般资料")
    basic_info = case.get("Basic Information", "无基本信息")
    st.markdown(f"### 案例信息\n\n**案例编号:** {case.get('Case Number', '无案例编号')}\n\n**一般资料:** {general_info}\n\n**基本信息:** {basic_info}")
# 设置对话框
for chat in st.session_state["conversation_history"]:
    if chat["role"] == "用户":
        st.markdown(
            f"""
            <div style='text-align: right; margin-bottom: 20px;'>
                <div style='font-size: 16px; color: #808080 ;'>👨‍⚕️ 咨询师</div>
                <div style='display: inline-block; background-color:#E0FFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{chat['content']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style='text-align: left; margin-bottom: 20px;'>
                <div style='font-size: 16px; color:#808080 ;'>🧑 AI</div>
                <div style='display: inline-block; background-color: #FFFFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{chat['content']}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )


# 发送按钮，并在发送消息后保存历史记录
def send_message():
    user_input = st.session_state['user_input']
    if user_input:
    # 添加用户输入到对话历史
        st.session_state["conversation_history"].append({"role": "用户", "content": user_input})
        with st.spinner("生成回复..."):
            # 从会话状态中获取选择的案例
            selected_case = st.session_state.get("selected_case")
            
            if selected_case:
                prompt = generate_prompt(selected_case, user_input, st.session_state["conversation_history"])
                response = call_gpt_api([{"role": "system", "content": prompt}])
            else:
                response = "请先选择一个案例再开始对话。"
            
            # 添加机器人回复到对话历史
            st.session_state["conversation_history"].append({"role": "Bot", "content": response})
    # 更新案例的对话历史
    selected_case_number = st.session_state["selected_case"]["Case Number"]
    st.session_state["case_conversations"][selected_case_number] = st.session_state["conversation_history"]
    
    # 在发送消息后保存对话历史
    # 注意：由于Streamlit Cloud的限制，我们不能在这里保存文件，但可以保存字符串
    file_name = f"{username}_conversation_history.txt"
    conversation_history = st.session_state.get("conversation_history", [])
    save_conversation_to_string(conversation_history, selected_case)
    
    # 清空输入框
    del st.session_state['user_input']
    st.session_state['user_input'] = ''
    st.rerun()
# 用户名输入框
username = st.text_input("Enter your username")

# 用户输入框
user_input = st.text_input("你的回复:", key="user_input", on_change=send_message,value="", placeholder="输入消息并按Enter发送")
# 保存对话历史到字符串
def save_conversation_to_string(conversation_history, selected_case):
    conversation_str = f"案例编号: {selected_case['Case Number']}\n"
    for chat in conversation_history:
        conversation_str += f"{chat['role']}: {chat['content']}\n"
    return conversation_str

selected_case = st.session_state.get("selected_case", {"Case Number": "未选择"})

#在Streamlit应用中生成聊天历史记录字符串
conversation_str = save_conversation_to_string(st.session_state["conversation_history"], selected_case)
# 发送按钮，并在发送消息后保存历史记录
def send_button():
    if st.button("发送") or user_input:
        if not username:
            st.error("Please enter a username before sending a message.")
            return
        
        send_message()
#下载按钮，用于将聊天历史记录下载为txt文件
def download_conversation_button(conversation_str):
    file_name = f"{username}_conversation_history.txt"
    st.download_button(
        label="下载聊天历史",
        data=conversation_str,
        file_name=file_name,
        mime="text/plain"
    )

# 调用按钮函数
send_button()
download_conversation_button(conversation_str)

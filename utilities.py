import random
import json
import streamlit as st

def summarize_old_conversation_history(conversation_history):
    # 提取旧的对话历史
    old_messages = conversation_history[:-200]
    # 在这里添加总结算法
    # 提取每一轮对话的主题
    topics = [message['content'][:50] + '...' for message in old_messages]
    # 将主题转换为字符串
    summary = "\n".join(topics)
    return summary

##人格选择
def generate_personality():
    big_five_personality_language_style = {
        "openness": "以高度开放性人格表现，描述因理想化与现实落差、探索失败、自我怀疑、或过度追求新奇体验而引发的沮丧、无力感或焦虑。",
        "conscientiousness": "以高度尽责性人格表现，表达因无法平衡生活与工作、长期承压、过度关注细节或无法容忍错误而引发的内疚、倦怠、疲惫或自我批评。",
        "extraversio": "以高度外向性人格表现，描述因社交需求未满足、不被认可、或过度依赖社交而产生的孤独感、失落、无价值感或抑郁。",
        "agreeableness": "以高度宜人性人格表现，表达因过度关心他人、无法拒绝请求、长期迎合他人期望而导致的心理耗竭、情感压抑、或自我认同感丧失。",
        "neuroticism": "以高神经质人格表现，描述因对未来担忧、灾难化思维、反复自责或对小事的过度反应而导致的极度焦虑、绝望、无助或精神疲惫。",
    }
    # 隨機為機器人選擇一個人格。
    selected_language_style_personality = random.choice(list(big_five_personality_language_style.items()))
    print(selected_language_style_personality[1])
    return selected_language_style_personality[1]

 ##依从性选择  
def generate_compliance():
    # 定义依从性选项和对应概率
    compliance_levels = ["依从性高", "依从性低"]
    probabilities = [3/4, 1/4]  # 依从性高的概率为3/4，依从性低的概率为1/4

    # 根据概率随机选择依从性
    selected_compliance = random.choices(compliance_levels, weights=probabilities, k=1)[0]

    # 定义依从性对应的提示词
    high_compliance_prompts = ["依从性高的个体在沟通中倾向于合作和顺从，愿意配合咨询师聊天，表达较为保守和谨慎。"
    ]
    
    low_compliance_prompts = [
        "依从性低的个体在沟通中表现出较强的自主性和独立性，可能会表达个人观点，使用批判性语言，可能会对咨询师的意见表示不支持，表现出更多的直接和个性化。"
    ]

    # 根据选择的依从性返回相应的提示词
    if selected_compliance == "依从性高":
        return random.choice(high_compliance_prompts)
    else:
        return random.choice(low_compliance_prompts)
    

def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases


# def generate_personality():
#     # MBTI的四个维度分为两组
#     mbti_dimensions = {
#         'EI': ['E', 'I'],
#         'SN': ['S', 'N'],
#         'TF': ['T', 'F'],
#         'JP': ['J', 'P']
#     }
    
#     # 随机选择每个维度中的一个
#     selected_dimensions = {dimension: random.choice(options) for dimension, options in mbti_dimensions.items()}
    
#     # 根据MBTI维度构建人格描述
#     personality_description = {
#         "E": "你拥有积极主动、充满活力、热情洋溢的个性，擅长即兴思考，并能够建立广泛的人际关系网。你的兴趣广泛，喜欢分享大量信息和反馈，并热衷于参与互动和交流。在充满活力的讨论中，你能够自由地分享想法，并随着对话的进行灵活地改变话题和观点。你喜欢边想边说，并能够立即分享想法或信息，同时也能够迅速地做出反应。在沟通中，你更倾向于表达自己的想法，并经常提出许多即兴问题，展现你的好奇心和求知欲。",
#         "I": "你拥有深思熟虑、内省沉稳的个性，擅长深入分析和独立思考。你倾向于在内心深处建立深厚的联系，而不是广泛地建立人际关系网。你的兴趣集中而深入，喜欢深入探讨特定主题，并享受深入的交流。在对话中，你更倾向于倾听和观察，在深思熟虑后才分享自己的想法。你喜欢在安静的环境中反思，并且倾向于在交流中保持谨慎和专注。你能够耐心地等待对话的节奏，并在适当时机提出深思熟虑的问题。在沟通中，你更注重深度而非广度，经常展现出你的深度思考和洞察力。你的好奇心和求知欲通过深入探究和长时间的专注得以体现。",
#         "N": "你的关键优势在于你对可能性持开放态度，能够预见并创造变革，关注未来趋势，并擅长将信息进行链接和整合，从而产生新的想法。你更关注事物的意义和关联，而不是单纯的事实，容易对细节感到厌倦。你喜欢头脑风暴和探索新想法，并能够理解事物的整体格局和长期影响。你善于发现模式，并受可能性激发，渴望创造、抓住和分享新想法。在沟通中，你经常使用隐喻、类比等象征性语言，并可能在对话中跳跃性地探索不同话题之间的联系。你信任并乐于应用理论、模型和框架，不喜欢受到限制或束缚。",
#         "S": "你具备注重现实和常识的特质，脚踏实地且务实。你观察力敏锐，注重细节，并能从经验中学习和应用。你能够立即将所接收到的信息付诸实践。在沟通中，你倾向于寻求事实、细节和具体的例子，并将信息与实际应用联系起来。你喜欢具体的计划和程序，并喜欢逐步解释。你喜欢将信息与过去发生的事情或正在发生的事情联系起来。你更喜欢实用、简单的语言，而不是符号、隐喻、理论或抽象概念。你关注当下，不喜欢讨论长期或战略性的计划。你相信已经被实践并证明为真理的事情，并对熟悉和实用性感到舒适。",
#         "F": "你具备出色的同理心，能够与人为善，并建立良好的人际关系。你能够理解并欣赏他人的观点，乐于支持、滋养他人，并对他人充满兴趣。你喜欢合作与协作，并致力于与他人建立和谐的环境。在沟通中，你更关注情境和主观信念、价值观，能够看到他人的优点和积极特质。你喜欢鼓励和积极的反馈，并乐于分享个人经历、案例、故事和例子。你渴望深入了解他人，并喜欢与他人建立联系和合作。你温暖、支持、富有表现力和肯定他人，关注氛围和谐，并对他人和他们的需求充满兴趣。",
#         "T": "你冷静、理性且自制力强，能够提供诚实而坦率的反馈。你善于分析、评估和批判，并具备客观和原则性的思维。你拥有清晰的思考过程，并使用明确的评估标准。在沟通中，你使用逻辑和分析来识别缺点或弱点，并需要了解原因。你更喜欢以客观事实的方式呈现信息，并喜欢辩论或质疑信息。你喜欢列出并考虑利弊，并创造或使用明确的评估标准。你信任能力和专业知识，并喜欢竞争，渴望获胜。你使用精确且简洁的语言，并以任务和目标为导向。",
#         "P": "你拥有灵活性和适应性强的特质，能够根据需要应对各种情况，并愿意接受新信息。你能够产生和考虑广泛的选项，并以轻松的方式应对变化。在沟通中，你积极寻求新信息和探索选项，并在决策过程中考虑大量数据和想法。你的沟通风格灵活、自发且无结构，能够灵活应对意外请求和机会。你能够推迟决策或做出暂时的决策，并在需要时寻求他人的意见。如果被要求立即做出决策，你会感到受限。你喜欢提出问题和提供选项，并更喜欢开放式讨论和语言，而不是结论性的陈述。你能够在意外事件和干扰中看到机会。",
#         "J": "你具备果断的特质，能够快速做出决策并付诸行动。你组织能力强，沟通效率高，并以任务和目标为导向，能够提供清晰的期望和时间线。在沟通中，你能够快速得出结论、做出决策并提供明确的结论。你喜欢建立清晰的期望、时间线和目标，并注重准时，期望他人也能按时完成。你喜欢清晰定义的沟通任务和后果，并喜欢组织有序且高效的沟通方式。你喜欢结构化和计划性的互动，对开放式和自由流动的讨论感到不适。你喜欢拥有一些控制权和设定限制，并希望提前获得信息，特别是如果需要完成任务的話。你期望并在预定的时间线内从他人那里获得反馈。"
#     }
    
#     # 组合人格描述
#     selected_language_style_personality = ""
#     for dimension in selected_dimensions.values():
#         selected_language_style_personality += personality_description[dimension] + " "
    
#     return selected_language_style_personality

def load_cases(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        cases = json.load(f)
    return cases

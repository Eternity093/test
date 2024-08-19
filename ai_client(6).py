# ========== Python 环境准备 ========== #

import streamlit as st
import base64
import requests
import utilities
import implementation
import os
import json
import urllib.parse

os.environ["OPENAI_API_BASE"] = 'https://api.xiaoai.plus/v1'
os.environ["OPENAI_API_KEY"] = 'sk-TWqvakjKo0TlqN7YE1Df97488f8446Ce8eAC79A081A74357'


# 初始化代理实现
agent_implementation = implementation.AgentImplementation()

# 案例文件路径
file_path = r'cases.json'  
# 加载案例
cases = utilities.load_cases(file_path)

# ========== 页面设置 ========== #


# 设置页面标题
st.set_page_config(page_title="AI 心理来访者", layout="wide")

# 将标题放置在页面顶端，并设置为白天模式颜色
st.markdown("<h1 style='text-align: center; font-size: 42px; color: #333;'>🤖 AI 心理来访者</h1>", unsafe_allow_html=True)

# 更改对话框背景为浅色
def main_bg(main_bg):
    main_bg_ext = "png"
    st.markdown(
        f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover;
             background-position: center; /* 调整背景图片位置 */
             background-color: #FFF; /* 设置背景颜色为白色 */
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

# 调用背景图片函数，确保背景图片适合白天模式
bg = r'main.png'
main_bg(bg)

# 更改侧边栏样式为浅色
def sidebar_bg(side_bg):
   side_bg_ext = 'png'
   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
          background-color: #EEE; /* 设置侧边栏背景颜色为浅灰色 */
      }}
      </style>
      """,
      unsafe_allow_html=True,
   )

# 调用侧边栏背景图片函数，确保背景图片适合白天模式
side = r'side.png'
sidebar_bg(side)

# 在页面中添加CSS样式以固定为白天模式
st.markdown("""
<style>
    body {
        background-color: #FFF; /* 设置背景颜色为白色 */
        color: #333; /* 设置文本颜色为深灰色 */
    }
    .stApp {
        background-color: #FFF; /* 确保应用区域背景为白色 */
    }
    [data-testid="stSidebar"] {
        background-color: #EEE; /* 设置侧边栏背景为浅灰色 */
    }
    .stMarkdown, .stTextInput, .stSelectbox, .stCheckbox, .stRadio, .stButton, .stText, .stTextArea {
        color: #333; /* 设置所有输入和文本元素的文本颜色为深灰色 */
    }
    .stTextInput input, .stSelectbox select, .stCheckbox input, .stRadio input, .stButton button {
        color: #333; /* 设置输入框、选择框、复选框、单选框和按钮的文本颜色为深灰色 */
        background-color: #FFF; /* 设置输入框、选择框、复选框、单选框和按钮的背景颜色为白色 */
    }
</style>
""", unsafe_allow_html=True)

# 在侧边栏添加不同的机器人栏
st.sidebar.header("请选择案例")

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


# 添加HTML/CSS样式
st.markdown(
    """
    <style>
    .right-align-button {
        position: fixed;
        top: 50px; /* 将按钮向下移动到50px处 */
        right: 10px;
        z-index: 9999;
    }
    .right-align-button button {
        background-color: #77AABF; /* 按钮背景颜色 */
        color: white; /* 按钮文字颜色 */
        padding: 10px 20px; /* 按钮内边距 */
        font-size: 16px; /* 按钮字体大小 */
        border: none; /* 去掉按钮边框 */
        border-radius: 8px; /* 按钮圆角 */
        cursor: pointer; /* 鼠标移上去时显示小手标志 */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* 按钮阴影 */
    }
    .right-align-button button:hover {
        background-color: #45a049; /* 鼠标悬停时的背景颜色 */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ========== 函数 ========== #

# 示例：向对话历史添加消息
def add_message_to_history(message):
    st.session_state["conversation_history"].append({"role": "therapist", "content": message})
# 保存对话历史到本地文件
def save_conversation_to_file(filename, conversation_history):
    selected_case = st.session_state.get("selected_case", {"Case Number": "未选择"})
    with open(filename, 'w', encoding='utf-8') as f:  # 使用 'w' 模式以覆盖内容
        f.write(f"案例编号: {selected_case['Case Number']}\n")
        for chat in conversation_history:
            f.write(f"{chat['role']}: {chat['content']}\n")


# 将对话历史转换为字符串的函数
def conversation_history_to_string(conversation_history):
    conversation_str = ""
    for entry in conversation_history:
        role = entry["role"]
        content = entry["content"]
        conversation_str += f"{role}: {content}\n"
    return conversation_str

# 保存对话历史到字符串
def save_conversation_to_string(conversation_history, selected_case):
    conversation_str = f"案例编号: {selected_case['Case Number']}\n"
    for chat in conversation_history:
        conversation_str += f"{chat['role']}: {chat['content']}\n"
    return conversation_str


def send_message():
    if st.session_state.user_input:
        with st.spinner("生成回复..."):
            # 从会话状态中获取选择的案例
            selected_case = st.session_state.get("selected_case")
            # 将对话历史转换为字符串
            conversation_history_string = conversation_history_to_string(st.session_state["conversation_history"])

            if selected_case:
                response = agent_implementation.generate_conversation(st.session_state.user_input, conversation_history_string, selected_case, username)
            else:
                response = "请先选择一个案例再开始对话。"

            # 添加用户输入到对话历史
            st.session_state["conversation_history"].append({"role": "therapist", "content": st.session_state.user_input})
            # 添加机器人回复到对话历史
            st.session_state["conversation_history"].append({"role": "client", "content": response})

            # 更新案例的对话历史
            selected_case_number = st.session_state["selected_case"]["Case Number"]
            st.session_state["case_conversations"][selected_case_number] = st.session_state["conversation_history"]

            # 清空输入框
            st.session_state['user_input'] = ''
            st.rerun()



# ========== 主要流程 ========== #        

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

# 确保在会话状态中初始化案例数据
if "cases" not in st.session_state:
    st.session_state['cases'] = cases  # 修改为你的实际案例文件路径

cases = st.session_state['cases']

# 初始化会话状态
if "case_conversations" not in st.session_state:
    st.session_state['case_conversations'] = {}

# 假设 cases 是一个包含所有案例的列表

# 创建分组案例按钮
cases_per_group = 10
num_groups = (len(cases) + cases_per_group - 1) // cases_per_group

for i in range(num_groups):
    group_start_number = i * cases_per_group + 1
    group_end_number = (i + 1) * cases_per_group

    group_cases = [case for case in cases
                   if group_start_number <= int(case["Case Number"][2:].replace(":", "")) <= group_end_number]

    group_label = f"组{i + 1}：案例{group_start_number}-{group_end_number}"

    with st.sidebar.expander(group_label, expanded=False):
        for case in group_cases:
            case_number = case["Case Number"].replace(":", "")
            button_key = f"button_{case_number}"  # 为每个按钮创建唯一的key
            if st.button(case_number, key=button_key):
                st.session_state["selected_case"] = case  # 存储选择的案例
                # 加载或初始化对话历史
                if case_number not in st.session_state["case_conversations"]:
                    st.session_state["case_conversations"][case_number] = []
                st.session_state["conversation_history"] = st.session_state["case_conversations"][case_number]
                st.rerun()

selected_case = st.session_state.get("selected_case", {"Case Number": "未选择"})

# 在Streamlit应用中生成聊天历史记录字符串
conversation_str = save_conversation_to_string(st.session_state["conversation_history"], selected_case)

# URL encode the conversation string to make it safe for URLs
conversation_str_encoded = urllib.parse.quote(conversation_str)

# 显示选中的案例信息
if "selected_case" in st.session_state:
    case = st.session_state["selected_case"]
    general_info = case.get("General Information", "无一般资料")
    basic_info = case.get("Basic Information", "无基本信息")
    st.markdown(f"### 案例信息\n\n**案例编号:** {case.get('Case Number', '无案例编号')}\n\n**一般资料:** {general_info}\n\n**基本信息:** {basic_info}")
    # 检查是否已经输入用户名
    if 'username' not in st.session_state:
        with st.form(key='user_form'):
            col1, col2 = st.columns([0.8, 0.2])  # 设置列布局，分配输入框和按钮的宽度

            with col1:
                username_input = st.text_input("输入您的用户名", key="username_input", placeholder="用户名",)

            with col2:
                st.markdown(
                """
                <style>
                div.stButton > button {
                    height: 2.5em; /* 调整高度 */
                    width: 50%; /* 设置宽度为100% */
                    margin-top: 0.7em; /* 调整垂直对齐 */
                    padding: 0; /* 移除内边距 */
                }
                </style>
                """,
                    unsafe_allow_html=True
                )
                # 表单的提交按钮
                submit_button = st.form_submit_button(label='提交')

        # 表单提交后，检查用户名是否已输入
        if submit_button:
            if username_input:
                st.session_state.username = username_input
                username = st.session_state.username
                st.experimental_rerun()  # 重新运行脚本，更新界面
            else:
                st.error("用户名不能为空")
    else:
        # 使用输入的用户名
        username = st.session_state.username
        st.write(f"{st.session_state.username}已进入聊天室")
        # 设置对话框样式并显示对话内容
        for chat in st.session_state["conversation_history"]:
            content = chat.get('content', '')

            if chat.get("role") == "client":
                st.markdown(
                    f"""
                    <div style='text-align: left; margin-bottom: 20px;'>
                        <div style='font-size: 16px; color: #808080;'>🧑来访者</div>
                        <div style='display: inline-block; text-align: left; background-color: #FFFFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='text-align: right; margin-bottom: 20px;'>
                        <div style='font-size: 16px; color: #808080;'>👨‍⚕️{st.session_state.username}(咨询师)</div>
                        <div style='display: inline-block; text-align: left; background-color: #E0FFFF; padding: 10px; border-radius: 10px; font-size: 20px; margin-top: 5px; color: black;'>{content}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        with st.form(key="user_input_form", clear_on_submit=True):
            col3, col4 = st.columns([0.8, 0.2])
            
            # 用户输入框
            with col3:
                user_input = st.text_input(
                    "开始你的对话吧:", 
                    key="user_input", 
                    placeholder="输入消息并按Enter发送"
                )
            
            # 发送按钮，并在发送消息后保存历史记录
            with col4:
                st.markdown(
                    """
                    <style>
                    div.stButton > button {
                        height: 2.5em; /* 调整高度 */
                        width: 50%; /* 设置宽度为100% */
                        margin-top: 0.7em; /* 调整垂直对齐 */
                        padding: 0; /* 移除内边距 */
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                submit_button = st.form_submit_button(label="发送", on_click=send_message)

        # 在页面右上角放置下载按钮
        st.markdown(
            f"""
            <div class="right-align-button">
                <a href="data:text/plain;charset=utf-8,{conversation_str_encoded}" download="{username}_conversation_history.txt">
                    <button>📥下载聊天历史</button>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )






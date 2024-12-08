import streamlit as st
from langserve import RemoteRunnable
from langchain_core.messages import HumanMessage
from PIL import Image


config = {"configurable": {"thread_id": "1"}}

# 使用 Markdown 和样式增强标题，包括图标和渐变色
# st.markdown("""
# <h2 style='text-align: center; color: blue; background: linear-gradient(to right, red, purple); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
#       📊 BiliBili 实时数据分析
# </h2>
# """, unsafe_allow_html=True)

ICON = Image.open("F:\\Learning\\人工智能-网络课程资料\\九天Hector-课程资料\\体验课\\Agent_Demo\\project\\Multi-Agent\\app\\icon.ico")
st.set_page_config(
    page_title="Intelligent Multi-Agent ChatBot",
    layout="wide",
    page_icon=ICON,
    initial_sidebar_state="auto"
)

st.title("📊 Multi-Agent ChatBot")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


with st.spinner("🤔正在处理..."):
    if prompt := st.chat_input("What is up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            app = RemoteRunnable("http://localhost:8000/biliagent_chat")
            message = [HumanMessage(content=prompt, name="user_chat")]
            input_all = {"messages": message,
                         "input": prompt,
                         "generation": "NULL",
                         "next": "NULL",
                         "documents": "NULL"}

            responses = []
            for output in app.stream(input_all, config, stream_mode="values"):
                responses.append(output)

            for response in responses[::-1]:
                if response.get("chat", []):
                    last_response = response.get("chat", [])["generation"]
                    print(last_response)
                    print(type(last_response))
                    break
                elif response.get("generate", []):
                    last_response = response.get("generate", [])["generation"]
                    break
                else:
                    last_response = "Please ask again."

            with st.chat_message("assistant"):
                st.markdown(last_response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": last_response})

            # 收缩显示 documents 的内容
            with st.expander("查看详细思考链信息"):
                st.write(responses)

        except Exception as e:
            st.error(f"处理时出现错误: {str(e)}")

# test demo: 你好，我叫XXX。   请问我叫什么名字？    你能帮我在bilibili上推荐几个有关 LangGraph 的视频吗？

import streamlit as st
from langserve import RemoteRunnable
from langchain_core.messages import HumanMessage


# 使用 Markdown 和样式增强标题，包括图标和渐变色
st.markdown("""
<h1 style='text-align: center; color: blue; background: linear-gradient(to right, red, purple); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
      📊 BiliBili 实时数据分析
</h1>
""", unsafe_allow_html=True)


# 输入框单独占一行显示
# st.write("#### 请输入问题:")
config = {"configurable": {"thread_id": "1"}}

input_text = st.text_input("请输入问题:", key="2")

if input_text:
    with st.spinner("正在处理..."):
        try:
            app = RemoteRunnable("http://localhost:8000/biliagent_chat")
            responses = []
            message = [HumanMessage(content=input_text, name="user_chat")]
            input_all = {"messages": message, "input": input_text, "generation": "NULL", "next": "NULL", "documents": "NULL"}
            for output in app.stream(input_all, config, stream_mode="values"):
                responses.append(output)
            if responses:
                print("responses:", responses)
                st.subheader('分析结果')
                last_response = responses
                st.write(last_response)

                # # 收缩显示 documents 的内容
                # documents = last_response.get("documents", [])
                # with st.expander("查看详细推荐视频信息"):
                    # for idx, doc in enumerate(documents):
                    #     st.write(f"### 视频 {idx + 1}")
                    # st.json(last_response)  # 展示每个文档的详细内容
            else:
                st.info("没有返回结果。")
        except Exception as e:
            st.error(f"处理时出现错误: {str(e)}")



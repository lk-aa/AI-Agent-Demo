import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def create_generate_chain(llm):
    """
    Creates a generate chain for answering bilibili-related questions.

    Args:
        llm (LLM): The language model to use for generating responses.

    Returns:
        A callable function that takes a context and a question as input and returns a string response.
    """
    generate_template = """
    You are an artificial intelligence personal assistant. Users will raise questions related to BiliBili website data, which are displayed in the section attached to the<question></question>tag. The BiliBili website data is displayed in the section attached to the<context></context>tag.\n
    
    Use this information to formulate your answer.\n
    
    When a user's question requires the use of the BiliBili API to obtain data, you can proceed accordingly.\n
    If you can't find the answer, please honestly answer that you don't know. Don't try to fabricate answers.\n
    If the question is unrelated to the context and politely answered, you can only answer questions that are relevant to the provided context.\n
    
    For questions involving data analysis, please write code in Python and conduct a detailed analysis of the results to provide the most comprehensive answers possible.\n
    
    Please note that all your answers should be in Chinese, except for proprietary and academic terms.\n
    For your answer, please answer in the format of a string composed of Markdown.\n
    When a line break is required, please use the double line break to write it.\n
    
    
    <context>
    {context}
    </context>
    
    <question>
    {input}
    </question>
    """

    generate_prompt = PromptTemplate(template=generate_template, input_variables=["context", "input"])

    # 没有StrOutputParser() 输出可能如下所示：
    # {
    #     "content": "This is the response from the LLM.",
    #     "metadata": {
    #         "confidence": 0.8,
    #         "response_time": 0.5
    #     }
    # }

    # 使用StrOutputParser() ，它看起来像这样：
    # This is the response from the LLM.

    # Create the generate chain
    generate_chain = generate_prompt | llm | StrOutputParser()

    return generate_chain


if __name__ == '__main__':
    # https://python.langchain.com/docs/integrations/chat/openai/
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        model=os.getenv('model'),
    )

    # 创建一个生成链
    generate_chain = create_generate_chain(llm)
    final_answer = generate_chain.invoke({
        "context": "这是我查询到的热门视频的描述：ChatGLM3-6B的安装部署、微调、训练智能客服。文档、数据集、微调脚本获取方式：麻烦一键三连，评论后，我会找到评论私发源码，谢谢大家。",
        "input": "请帮我梳理一下热门视频的描述信息"
    })
    print(final_answer)

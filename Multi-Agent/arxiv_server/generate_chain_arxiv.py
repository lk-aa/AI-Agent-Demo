import os
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def create_generate_Arixv_chain(llm):
    """
    Creates a generate chain for answering arxiv-related questions.

    Args:
        llm (LLM): The language model to use for generating responses.

    Returns:
        A callable function that takes a context and a question as input and returns a string response.
    """
    generate_template = """
        You are an artificial intelligence personal assistant. Users will ask questions related to the Arxiv paper website data, which are displayed in the section attached to the<question></question>tag. The data on the Arxiv paper website is displayed in the section attached to the<context></context>tag.\n
    
        Use this information to formulate your answer.\n
    
        When a user's question requires the use of Arixv API to obtain data, you can proceed accordingly.\n
        If you can't find the answer, please honestly answer that you don't know. Don't try to fabricate answers.\n
        If the question is unrelated to the context and politely answered, you can only answer questions that are relevant to the provided context.\n
            
        For questions involving data analysis, please write code in Python and conduct a detailed analysis of the results to provide the most comprehensive answers possible.\n
        
        For your answer, please answer in the format of a string composed of Markdown. When a line break is required, please use the double line break "\\n\\n" to write it.\n
        Please note that all your answers should be in Chinese, except for proprietary and academic terms.\n
        
    
        <context>
        {context}
        </context>

        <question>
        {input}
        </question>
    """

    generate_prompt = PromptTemplate(template=generate_template, input_variables=["context", "input"])

    # Create the generate chain
    generate_chain = generate_prompt | llm | StrOutputParser()

    return generate_chain

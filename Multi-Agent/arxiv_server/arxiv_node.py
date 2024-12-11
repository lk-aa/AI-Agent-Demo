from langchain_core.messages import AIMessage

from .arxiv_loader import get_arxiv_retriever
from .generate_chain_arxiv import create_generate_Arixv_chain
from config.graph import GraphState


class ArxivNodes:
    def __init__(self, llm):
        self.llm = llm
        self.generate_chain = create_generate_Arixv_chain(llm)

    def Arxiv_retrieve(self, state: GraphState):
        """
        根据输入问题检索文档，并将它们添加到图状态中。
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---节点：开始检索---")
        question = state["input"]
        print("查询API的问题question:", question)

        # 执行检索
        documents = get_arxiv_retriever(query=question, top_k_results=10)
        print(f"这是检索到的Docs:{documents}")
        return {"input": question, "documents": documents}

    def Arxiv_generate(self, state: GraphState):
        """
        使用输入问题和检索到的文档生成答案，并将生成添加到图形状态中。
        Generate answer

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains LLM generation
        """
        print("---节点：生成响应---")

        question = state["input"]
        documents = state["documents"]

        generation = self.generate_chain.invoke({"context": documents, "input": question})
        print(f"生成的响应为:{generation}")
        final_response = [AIMessage(content=generation, name="arxiv")]  # 这里要添加名称

        return {"documents": documents, "input": question, "generation": generation, "messages": final_response, "next": "NULL"}

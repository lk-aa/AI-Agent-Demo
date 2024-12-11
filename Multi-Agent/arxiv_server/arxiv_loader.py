from langchain_core.documents import Document
from typing import List
from arxiv_tools import get_arxiv_tools


def get_arxiv_retriever(query: str, top_k_results: int) -> List[Document]:
    """
    Retrieves documents and returns a retriever based on the documents.

    Args:
        query (str): Keywords to search documents.
        top_k_results (int): Paper number of results.

    Returns:
        Retriever instance.
    """
    arxiv_search = get_arxiv_tools.ArxivAPIWrapper()
    arxiv_search.top_k_results = top_k_results

    print(f"开始实时查询Arxiv-API获取数据")
    docs = arxiv_search.get_summaries_as_docs(query)
    print(f"接收到的Arxiv数据为：{docs}")
    print("-------------------------")

    return docs


if __name__ == '__main__':
    get_arxiv_retriever(query="KAN", top_k_results=3)

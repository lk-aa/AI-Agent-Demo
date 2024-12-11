import arxiv_tools
import os
import PyPDF2
from aiohttp.client_exceptions import ClientError, ClientOSError
import asyncio
import json
from typing import List
import fitz


client = arxiv_tools.Client()


# res = [
#     {
#         "title": r.title,  # 文章标题, The title of the article.
#         "id": r.entry_id.split('/')[-1],     # ID号, A url http://arxiv.org/abs/id
#         "published": r.published,      # 提交该论文第1版的日期, The date that version 1 of the article was submitted.
#         "updated": r.updated,    # 提交检索到的文章版本的日期。如果检索到的版本是版本1，则与<published>相同, The date that the retrieved version of the article was submitted. Same as <published> if the retrieved version is version 1.
#         "summary": r.summary,    # 文章摘要, The article abstract.
#         "author": r.authors,     # 每个作者一个。有包含作者姓名的子元素<name>, One for each author. Has child element <name> containing the author name.
#         "entry_id": r.entry_id,  # 文章的ID
#         "link": r.links,         # 最多可以有3个与本文关联的给定网址, Can be up to 3 given url's associated with this article.
#         "category": r.categories,    # 文章的arXiv或ACM或MSC类别（如果有的话）, The arXiv or ACM or MSC category for an article if present.
#         "arxiv_primary_category": r.primary_category,    # arXiv的主要类别, The primary arXiv category.
#         "arxiv_comment": r.comment,     # 作者评论如果存在, The authors comment if present.
#         "arxiv_journal_ref": r.journal_ref,    # 期刊参考文献（如有）, A journal reference if present.
#         "arxiv_": r.doi,         # 已解析DOI到外部资源的url（如果存在）, A url for the resolved DOI to an external resource if present.
#         "pdf_url": r.pdf_url,                # 文章PDF的URL地址
#     }
#     for r in client.results(search)
# ]


async def search_articles(paper):
    paper_content = await fetch_content(paper)
    processed_data = {
        "文章标题(title)": paper.title,  # 文章标题, The title of the article.
        "文章的arxiv地址URL(id)": paper.entry_id.split('/')[-1],  # ID号, A url http://arxiv.org/abs/id
        "论文第一版日期(published)": paper.published,  # 提交该论文第1版的日期, The date that version 1 of the article was submitted.
        "论文出版最新日期(Published)": paper.updated.date(),
        "文章摘要(summary)": paper.summary,  # 文章摘要, The article abstract.
        "文章作者(author)": ", ".join(a.name for a in paper.authors),
        # 每个作者一个。有包含作者姓名的子元素<name>, One for each author. Has child element <name> containing the author name.
        "文章ID(entry_id)": paper.entry_id,  # 文章的ID
        "与文章关联的网址(link)": paper.links,  # 最多可以有3个与本文关联的给定网址, Can be up to 3 given url's associated with this article.
        "文章类别(category)": paper.categories,
        # 文章的arXiv或ACM或MSC类别（如果有的话）, The arXiv or ACM or MSC category for an article if present.
        "arxiv主要类别(arxiv_primary_category)": paper.primary_category,  # arXiv的主要类别, The primary arXiv category.
        "作者评论(arxiv_comment)": paper.comment,  # 作者评论如果存在, The authors comment if present.
        "期刊参考文献(arxiv_journal_ref)": paper.journal_ref,  # 期刊参考文献（如有）, A journal reference if present.
        "已解析DOI到外部资源的url(arxiv_doi)": paper.doi,  # 已解析DOI到外部资源的url（如果存在）, A url for the resolved DOI to an external resource if present.
        "文章PDF的URL地址(pdf_url)": paper.pdf_url,  # 文章PDF的URL地址
        "文章内容(content)": paper_content
    }

    # return json.dumps(processed_data, ensure_ascii=False)
    return processed_data


async def fetch_content(paper):
    """
    Fetches specific article details from arXiv based on the article_id.

    Args:
        article_id (str): The ID of the article to fetch.

    Returns:
        dict: A dictionary containing article details (entry_id, title, pdf_url, summary).
    """
    # filename = f"{paper.get_short_id()}.pdf"
    # dirpath = "pdf"
    # pdf_path = paper.download_pdf(filename=filename)
    # # Convert PDF to TXT
    # if pdf_path:
    #     with open(pdf_path, 'rb') as pdf_file:
    #         pdf_reader = PyPDF2.PdfReader(pdf_file)
    #         text = ''.join(page.extract_text() for page in pdf_reader.pages)

    # from langchain_community.utilities import ArxivAPIWrapper
    #
    # # 初始化API Wrapper
    # arxiv_tools = ArxivAPIWrapper()
    #
    # # 查询特定的ArXiv ID
    # docs = arxiv_tools.run("1605.08386")
    # print(docs)

    doc_file_name: str = paper.download_pdf()
    with fitz.open(doc_file_name) as doc_file:
        text: str = "".join(page.get_text() for page in doc_file)

    return text


async def arxiv_paper_details(query: str, max_results: int) -> List:
    """
    Searches for articles on arXiv based on a query.
    根据参数 “query" 在arXiv上搜索文章。

    Args:
        query (str): The search query string. 搜索查询字符串
        max_results (int): The maximum number of results to return (default is 100). 要返回的最大结果数（默认值为100）

    Returns:
        str: A string of a list of dictionaries containing article details (entry_id, title, pdf_url, summary).
              包含文章详细信息（entry_id、title、pdf_url、summary等）的字典列表。
    """
    all_results = []  # 初始化一个列表来存储所有关键词和页面的结果
    search = arxiv_tools.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv_tools.SortCriterion.SubmittedDate
    )

    for paper in client.results(search):
        res = await search_articles(paper)
        all_results.append(res)
        print(res)
    return all_results


if __name__ == '__main__':
    import asyncio
    asyncio.run(arxiv_paper_details(query="KAN", max_results=1))

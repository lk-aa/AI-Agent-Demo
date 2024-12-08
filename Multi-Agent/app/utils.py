from langchain_openai import ChatOpenAI
from bili_server.document_loader import DocumentLoader
from bili_server.edges import EdgeGraph
from bili_server.generate_chain import create_generate_chain
from bili_server.graph import GraphState, Router
from bili_server.grader import GraderUtils
from bili_server.nodes import GraphNodes

from langgraph.graph import START, END, StateGraph
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
# 导入检查点
from langgraph.checkpoint.memory import MemorySaver

llm = ChatOpenAI(model="gpt-3.5-turbo")
members = ["chat", "bili_analysis"]
options = members + ["FINISH"]


# 主Agent, 进行决策和选择字Agent
def supervisor(state: GraphState):
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}.\n\n"
        "Each worker has a specific role:\n"
        "- chat: Responds directly to user inputs using natural language.\n"
        "- bili_analysis: A video search agent for Bilibili website. If the user's question contains words such as 'Bilibili', then call this agent.\n"
        "Given the following user request, respond with the worker to act next."
        " Each worker will perform a task and respond with their results and status."
        " When finished, respond with FINISH."
        " When the last message is 'AIMessage', respond with FINISH."
    )
    messages = state["messages"]
    input = state["input"]
    print("messages:", messages)

    message = [SystemMessage(content=system_prompt), ] + messages

    if state["messages"] != [] and isinstance(state["messages"][-1], AIMessage):
        return {"next": END}

    response = llm.with_structured_output(Router).invoke(input=message)

    # 判断llm输出的结果, 结构化输出, 由自己定义情况
    next_ = response["next"]

    if next_ == "FINISH":
        next_ = END

    return {"input": input, "generation": state["generation"], "documents": state["documents"], "next": next_}
    # return {"input": input, "next": next_}


def chat(state: GraphState):
    input = state["input"]  # 传入全部信息
    messages = state["messages"]
    print("chat:", messages)

    model_response = llm.invoke(messages)
    final_response = [AIMessage(content=model_response.content, name="chat")]   # 这里要添加名称
    return {"input": input, "generation": model_response.content, "messages": final_response, "next": "NULL", "documents": state["documents"]}


def create_parser_components(llm):
    # 创建 retriever 实例，用于文档检索
    retriever = DocumentLoader()

    # 创建生成链，用于基于语言模型的生成任务
    generate_chain = create_generate_chain(llm)

    # 初始化评分器实例，用于创建和管理多种评分工具
    grader = GraderUtils(llm)

    # 创建评估检索文档与用户问题相关性的评分器
    retrieval_grader = grader.create_retrieval_grader()

    # 创建评估模型的回答是否出现幻觉的评分器
    hallucination_grader = grader.create_hallucination_grader()

    # 创建代码评估器，用于评估代码执行结果的正确性
    code_evaluator = grader.create_code_evaluator()

    # 创建问题重写器，用于优化用户问题，使其更适合模型理解和回答
    question_rewriter = grader.create_question_rewriter()

    # 返回包含所有组件的字典，以便在其他部分的代码中使用
    return {
        "retriever": retriever,
        "generate_chain": generate_chain,
        "retrieval_grader": retrieval_grader,
        "hallucination_grader": hallucination_grader,
        "code_evaluator": code_evaluator,
        "question_rewriter": question_rewriter
    }


def create_workflow(api_key: str, model: str):
    """
    创建并初始化工作流以及其组成的节点和边。

    Returns:
    StateGraph: 完全初始化和编译好的工作流对象。
    """

    # 创建 LLM model 实例，配置为使用 GPT-4o 模型和指定的温度参数
    llm = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.chatanywhere.org/v1",
        model=model,
        temperature=0
    )

    # 调用函数并直接解构字典以获取所有实例
    (retriever, generate_chain,
     retrieval_grader, hallucination_grader,
     code_evaluator, question_rewriter) = create_parser_components(llm).values()

    # 初始化图结构
    workflow = StateGraph(GraphState)

    # 创建图节点的实例
    graph_nodes = GraphNodes(llm, retriever, retrieval_grader, hallucination_grader, code_evaluator, question_rewriter)

    # 创建边节点的实例
    edge_graph = EdgeGraph(hallucination_grader, code_evaluator)

    # 定义节点
    workflow.add_node("supervisor", supervisor)

    workflow.add_node("bili_analysis", graph_nodes.retrieve)  # retrieve documents
    workflow.add_node("grade_documents", graph_nodes.grade_documents)  # grade documents
    workflow.add_node("generate", graph_nodes.generate)  # generate answers
    workflow.add_node("transform_query", graph_nodes.transform_query)  # transform query
    workflow.add_node("chat", chat)

    # 创建图
    workflow.add_edge(START, "supervisor")
    # workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges("supervisor",
                                   lambda state: state["next"]
                                   )
    workflow.add_edge("chat", "supervisor")
    workflow.add_edge("bili_analysis", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        edge_graph.decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        }
    )
    workflow.add_edge("transform_query", "bili_analysis")
    workflow.add_conditional_edges(
        "generate",
        edge_graph.grade_generation_v_documents_and_question,
        {
            "not supported": "generate",
            "useful": "supervisor",
            "not useful": "transform_query",
        }
    )

    # 编译图
    memory = MemorySaver()
    chain = workflow.compile(checkpointer=memory)
    # chain = workflow.compile()

    # chain.get_graph().print_ascii()
    # chain.get_graph().draw_png("supervisor.png")
    # chain.get_graph(xray=True).draw_mermaid_png(output_file_path="supervisor2.png")

    return chain


if __name__ == '__main__':
    import os
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv())

    chain = create_workflow(os.getenv('OPENAI_API_KEY'),
                            os.getenv('model')
                            )

    # 这个 thread_id 可以取任意数值
    config = {"configurable": {"thread_id": "1"}}

    input_text = "你好，我叫木羽"
    a = 1
    message = [HumanMessage(content=input_text, name="user_chat")]
    input_all = {"input": input_text, "generation": "NULL", "messages": message, "next": "NULL", "documents": "NULL"}
    for chunk in chain.stream(input_all, config, stream_mode="values"):
        # print(chunk)
        a += 1

    # for chunk in chain.stream({"messages": ["请问我叫什么？"], "next": "NULL"}, config, stream_mode="values"):
    #     print(chunk)

    # config = {"configurable": {"thread_id": "1"}}
    #
    # a = 1
    # for chunk in chain.stream({"messages": ["请在bilibili上搜索有关 ChatGLM4 的视频, 要求点赞数尽可能的多。"], "next": "NULL"}, config, stream_mode="values"):
    #     print(chunk)
    #     # a += 1

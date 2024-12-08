from langgraph.graph import MessagesState
from typing import TypedDict, Literal, Annotated
import operator
from langchain_core.messages import AnyMessage


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        input: question
        generation: LLM generation
        documents: list of documents
    """

    input: str
    generation: str
    documents: str
    next: str
    messages: Annotated[list[AnyMessage], operator.add]


members = ["chat", "bili_analysis"]
options = members + ["FINISH"]


class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH"""
    next: Literal[*options]

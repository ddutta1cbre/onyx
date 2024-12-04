import operator
from collections.abc import Sequence
from typing import Annotated
from typing import List
from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from danswer.chat.models import DanswerContext
from danswer.llm.interfaces import LLM


class QAState(TypedDict):
    # The 'main' state of the answer graph
    original_question: str
    log_messages: Annotated[Sequence[BaseMessage], add_messages]
    rewritten_queries: List[str]
    sub_questions: List[str]
    sub_qas: Annotated[Sequence[dict], operator.add]
    checked_sub_qas: Annotated[Sequence[dict], operator.add]
    base_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    deduped_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    reranked_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    retrieved_entities_relationships: dict
    questions_context: List[dict]
    qa_level: int
    top_chunks: List[DanswerContext]
    sub_question_top_chunks: Annotated[Sequence[dict], operator.add]
    dynamic_context: str
    initial_base_answer: str
    base_answer: str
    deep_answer: str
    llm: LLM
    tools: list[dict]


class QAOuputState(TypedDict):
    # The 'main' output state of the answer graph. Removes all the intermediate states
    original_question: str
    log_messages: Annotated[Sequence[BaseMessage], add_messages]
    sub_questions: List[str]
    sub_qas: Annotated[Sequence[dict], operator.add]
    checked_sub_qas: Annotated[Sequence[dict], operator.add]
    reranked_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    retrieved_entities_relationships: dict
    top_chunks: List[DanswerContext]
    sub_question_top_chunks: Annotated[Sequence[dict], operator.add]
    base_answer: str
    deep_answer: str


class RetrieverState(TypedDict):
    # The state for the parallel Retrievers. They each need to see only one query
    rewritten_query: str


class VerifierState(TypedDict):
    # The state for the parallel verification step.  Each node execution need to see only one question/doc pair
    document: DanswerContext
    original_question: str
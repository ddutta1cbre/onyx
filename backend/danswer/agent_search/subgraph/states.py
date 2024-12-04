import operator
from collections.abc import Sequence
from typing import Annotated
from typing import List
from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from danswer.chat.models import DanswerContext
from danswer.llm.interfaces import LLM


class SubQuestionRetrieverState(TypedDict):
    # The state for the parallel Retrievers. They each need to see only one query
    sub_question_rewritten_query: str


class SubQuestionVerifierState(TypedDict):
    # The state for the parallel verification step.  Each node execution need to see only one question/doc pair
    sub_question_document: DanswerContext
    sub_question: str


class SubQAState(TypedDict):
    # The 'core SubQuestion'  state.
    original_question: str
    sub_question_rewritten_queries: List[str]
    sub_question: str
    sub_question_base_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    sub_question_deduped_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_verified_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_reranked_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_top_chunks: Annotated[Sequence[DanswerContext], operator.add]
    sub_question_answer: str
    sub_question_answer_check: str
    log_messages: Annotated[Sequence[BaseMessage], add_messages]
    sub_qas: Annotated[
        Sequence[DanswerContext], operator.add
    ]  # Answers sent back to core
    llm: LLM
    tools: list[dict]


class SubQAOutputState(TypedDict):
    # The 'SubQuestion'  output state. Removes all the intermediate states
    sub_question_rewritten_queries: List[str]
    sub_question: str
    sub_qas: Annotated[
        Sequence[DanswerContext], operator.add
    ]  # Answers sent back to core
    sub_question_base_retrieval_docs: Annotated[Sequence[DanswerContext], operator.add]
    sub_question_deduped_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_verified_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_reranked_retrieval_docs: Annotated[
        Sequence[DanswerContext], operator.add
    ]
    sub_question_top_chunks: Annotated[Sequence[DanswerContext], operator.add]
    sub_question_answer: str
    sub_question_answer_check: str
    log_messages: Annotated[Sequence[BaseMessage], add_messages]
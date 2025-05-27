import asyncio
import os

from langchain_openai import ChatOpenAI

from app.utility.env import get_env_key, get_open_ai_model
from app.utility.rag_qa import retrieve

from langgraph.graph import END
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph

from ragas.integrations.langgraph import convert_to_ragas_messages
from ragas.metrics import ToolCallAccuracy, TopicAdherenceScore
from ragas.dataset_schema import MultiTurnSample
import ragas.messages as r

from ragas.metrics import AgentGoalAccuracyWithReference
from ragas.llms import LangchainLLMWrapper

from typing import Annotated
from typing_extensions import TypedDict



llm = ChatOpenAI(
    model=get_open_ai_model(),
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

tools = [retrieve]

llm_with_tools = llm.bind_tools(tools)

os.environ[
    "OPENAI_API_KEY"] = get_env_key("OPEN_AI_KEY")

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

# Define the function that determines whether to continue or not
def should_continue(state: GraphState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Define the function that calls the model
def call_model(state: GraphState):
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# Node
def assistant(state: GraphState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# Implementation of Graph State
class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


async def agent_tool_use_cases():
    ragas_trace = await building_tool()

    sample = MultiTurnSample(
        user_input=ragas_trace,
        reference_tool_calls=[
            r.ToolCall(name="retrieve", args={"query": "inflammatory medicines"})
        ],
    )
    tool_accuracy_scorer = ToolCallAccuracy()

    score_tool_accuracy = await tool_accuracy_scorer.multi_turn_ascore(sample)

    print("Tool call Accuracy : [ " + str(score_tool_accuracy) + " ]")

    sample = MultiTurnSample(
        user_input=ragas_trace,
        reference="A list of inflammatory medicines, including their forms and uses, is provided.",
    )

    scorer_scorer_score_agent_goal = AgentGoalAccuracyWithReference()

    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=get_open_ai_model()))

    scorer_scorer_score_agent_goal.llm = evaluator_llm

    score_agent_goal = await scorer_scorer_score_agent_goal.multi_turn_ascore(sample)

    print("Agent Goal Accuracy : [ " + str(score_agent_goal) + " ]")

    sample = MultiTurnSample(user_input=ragas_trace, reference_topics=["medicine"])
    scorer_score_topic_adherence = TopicAdherenceScore(llm=evaluator_llm, mode="recall")
    score_topic_adherence = await scorer_score_topic_adherence.multi_turn_ascore(sample)

    print("Topic Adherence : [ " + str(score_topic_adherence) + " ]")


async def building_tool():
    tool_node = ToolNode(tools)
    # Define a new graph for the agent
    builder = StateGraph(GraphState)
    # Define the two nodes we will cycle between
    builder.add_node("assistant", assistant)
    builder.add_node("tools", tool_node)
    # Set the entrypoint as `agent`
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", should_continue, ["tools", END])
    builder.add_edge("tools", "assistant")


    react_graph = builder.compile()
    messages = [HumanMessage(content="What are the inflammatory medicines?")]
    result = react_graph.invoke({"messages": messages})

    ragas_trace = convert_to_ragas_messages(
        messages=result["messages"]
    )

    return ragas_trace


if __name__ == '__main__':
    asyncio.run(agent_tool_use_cases())


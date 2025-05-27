import asyncio
import os

from langchain_openai import ChatOpenAI
from app.utility.env import get_env_key, get_open_ai_model
from app.utility.rag_qa import retrieve, init_embeddings

from langchain_core.messages import AnyMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph, END

from ragas.integrations.langgraph import convert_to_ragas_messages
from ragas.metrics import ToolCallAccuracy, TopicAdherenceScore, LLMContextPrecisionWithoutReference, LLMContextRecall, \
    AgentGoalAccuracyWithReference, ContextEntityRecall, NoiseSensitivity, ResponseRelevancy, Faithfulness
from ragas.dataset_schema import SingleTurnSample, MultiTurnSample
import ragas.messages as r

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

os.environ[
    "LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGSMITH_TRACING"] = "true"
os.environ[
    "LANGSMITH_API_KEY"] = get_env_key("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "chatbot"

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

    """
    Retrieval Augmented Generation Metrics

    1. Context Precision - measures how many of the retrieved contexts are actually relevant to the user's question. 
       It looks at each retrieved chunk and checks if it's useful.
       
       LLM-Based Context Precision uses a language model to decide which chunks are relevant.

    2. Context Recall - measures how well the retrieved contexts cover all the important information from the reference answer.
       It checks if anything essential was missed.
       
       High recall = most relevant info was retrieved
       Needs a reference answer to compare against
       
    3. Context Entities Recall - measures how many important entities from the reference are also found in the retrieved contexts.
       It compares entities in the reference vs. retrieved_contexts
       Higher score = more key entities were successfully retrieved
    
    4. Noise Sensitivity - measures how easily a system gets confused by irrelevant or misleading information in the retrieved contexts.
       Lower scores are better – they mean the system stays accurate even with noisy data.
       It checks if each part of the answer is correct and supported by the relevant retrieved info.
    
    5. Response Relevancy - measures how well the response matches the user’s question.
       Higher scores = more relevant and complete answers. 
       Lower scores = response is off-topic, incomplete, or redundant.
       
    6. Faithfulness measures how factually correct the response is based on the retrieved context. 
       Higher scores = all claims are supported by the retrieved info.
       Lower scores = the response includes unsupported or made-up claims
    """


async def metrics_use_cases():
    ragas_trace = await building_tool()

    retrieve_tool_messages = await retrieve_context(ragas_trace)

    sample_without_user_input = SingleTurnSample(
        reference="Inflammatory medicines include acetylsalicylic acid, ibuprofen, paracetamol, sulfasalazine, hydrocortisone, and prednisolone.",
        retrieved_contexts=[retrieve_tool_messages],
    )

    sample_without_reference = SingleTurnSample(
        user_input=ragas_trace[0].content,
        response=ragas_trace[-1].content,
        retrieved_contexts=[retrieve_tool_messages],
    )

    sample_with_reference = SingleTurnSample(
        user_input=ragas_trace[0].content,
        response=ragas_trace[-1].content,
        reference="Inflammatory medicines include acetylsalicylic acid, ibuprofen, paracetamol, sulfasalazine, hydrocortisone, and prednisolone.",
        retrieved_contexts=[retrieve_tool_messages],
    )

    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model=get_open_ai_model()))

    context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)

    score = await context_precision.single_turn_ascore(sample_without_reference)

    print(f"Context Precision : {score}")

    context_recall = LLMContextRecall(llm=evaluator_llm)

    score = await context_recall.single_turn_ascore(sample_with_reference)

    print(f"Context Recall : {score}")

    scorer = ContextEntityRecall(llm=evaluator_llm)

    score = await scorer.single_turn_ascore(sample_without_user_input)

    print(f"Context Entities Recall : {score}")

    scorer = NoiseSensitivity(llm=evaluator_llm)

    score = await scorer.single_turn_ascore(sample_with_reference)

    print(f"Noise Sensitivity : {score}")

    scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=init_embeddings())

    score = await scorer.single_turn_ascore(sample_without_reference)

    print(f"Response Relevancy : {score}")

    scorer = Faithfulness(llm=evaluator_llm)

    score = await scorer.single_turn_ascore(sample_without_reference)

    print(f"Faithfulness : {score}")

    """
    
    Agents or Tool Use Cases Metrics
    
    1. Topic Adherence measures how well an AI sticks to a set of predefined topics or domains.
       It’s important for systems that should only answer questions in specific areas (e.g., medical, legal).

       Higher scores = AI stays on-topic
       Lower scores = AI goes off-topic
       
    2. Tool Call Accuracy measures how well the AI chooses the right tools for a task.
       
       Higher scores = the AI correctly identifies and uses the needed tools
       Lower scores = the AI makes incorrect or missing tool calls
    
    3. Agent Goal Accuracy checks if the AI successfully achieved the user’s goal.

       Score is 1 if the goal was achieved
       Score is 0 if not
    """

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

    scorer_scorer_score_agent_goal.llm = evaluator_llm

    score_agent_goal = await scorer_scorer_score_agent_goal.multi_turn_ascore(sample)

    print("Agent Goal Accuracy : [ " + str(score_agent_goal) + " ]")

    sample = MultiTurnSample(user_input=ragas_trace, reference_topics=["medicine"])
    scorer_score_topic_adherence = TopicAdherenceScore(llm=evaluator_llm, mode="recall")
    score_topic_adherence = await scorer_score_topic_adherence.multi_turn_ascore(sample)

    print("Topic Adherence : [ " + str(score_topic_adherence) + " ]")


async def retrieve_context(ragas_trace):
    tool_messages = [msg for msg in ragas_trace if getattr(msg, "type", None) == "tool"]
    concatenated_tool_messages = ""
    for tool_msg in tool_messages:
        concatenated_tool_messages += "".join(tool_msg.content)
    return concatenated_tool_messages


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
    asyncio.run(metrics_use_cases())

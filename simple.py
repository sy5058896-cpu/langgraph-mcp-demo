from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from typing import TypedDict
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from mcpclient import get_tools
import asyncio

load_dotenv()
handler = CallbackHandler()

client = Langfuse()


class Agent(TypedDict):
    question: str
    response: str
    answer1: str
    answer2: str
    route: str


workflow = StateGraph(Agent)


# define superviser node
def superviser(state: Agent):
    user_input = state["question"]
    """according to user query'intent u need to calssify route the query according to requirement if there is general query or matmatical function like add ,substract ,multiply then route to agent1
    if it's related to latest news u will route to web_search agent """
    prompt_template = ChatPromptTemplate(
        [
            (
                "system",
                """
You are a router.

Return ONLY ONE WORD.

Valid outputs:

agent1
web_search
both

Rules:
- General question -> agent1
- Mathematical calculation -> agent1
- Latest news/current events -> web_search
- Contains both news and math -> both

Return only the route name.
No explanation.
No reasoning.
No extra words.
""",
            ),
            ("human", "{user_input}"),
        ]
    )
    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=200)
    chain = prompt_template | llm
    response = chain.invoke({"user_input": user_input})
    route = response.content.strip()

    return {"response": response.content, "route": response.content.strip()}


# define node1
def agent1(state: Agent):
    """this agent will over given general or or matmatical function like add ,substract ,multiply user query"""
    tools = asyncio.run(get_tools())

    llm = ChatGroq(model="qwen/qwen3.8-27b", temperature=0, max_tokens=200)
    llm_with_tools = llm.bind_tools(tools)

    query = state["question"]
    prompt = f"please help for this {query}."
    answer1 = llm_with_tools.invoke(prompt)
    if answer1.tool_calls:
        tool_call = answer1.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        print("tool_name:", tool_name)
        print("tool_args:", tool_args)
        for tool in tools:
            if tool.name == tool_name:
                tool_result = asyncio.run(tool.ainvoke(tool_args))
                print("tool_result:", tool_result)
                return {"answer1": tool_result}


# node2
def web_search(state: Agent):
    """Search the internet for:
    - latest news
    - current news
    - today's date
    - weather
    - current events
    - gold prices
    - stock prices
    - real-time information

    Use this whenever current or live information is needed."""
    tavily_search = TavilySearch(max_results=5, topic="general", search_depth="basic")
    answer2 = tavily_search.invoke(state["question"])

    return {"answer2": answer2}


def both(state: Agent):
    news = web_search(state)
    math = agent1(state)
    return {"answer1": math.get("answer1"), "answer2": news.get("answer2")}


def decide_route(state: Agent):
    return state["route"]


# define connectivity
workflow.add_node("superviser", superviser)
workflow.add_node("agent1", agent1)
workflow.add_node("web_search", web_search)
workflow.add_node("both_node", both)
workflow.add_edge(START, "superviser")
workflow.add_conditional_edges(
    "superviser",
    decide_route,
    {"agent1": "agent1", "web_search": "web_search", "both": "both_node"},
)
workflow.add_edge("agent1", END)
workflow.add_edge("web_search", END)
checkpointer = InMemorySaver()
graph = workflow.compile(checkpointer=checkpointer)
inital_state = {"question": ""}
config = {
    "configurable": {
        "thread_id": "thread1",
    },
    "callbacks": [handler],
}
print("\nChatbot started! Type 'exit' to stop.\n")
try:
    while True:
        question = input("you: ").strip()
        if question.lower() in ["bye", "stop", "exit"]:
            print("Chatbot:Goodbye!")
            break
        if not question:
            continue
        else:
            result = graph.invoke({"question": question}, config=config)
        # display result according to selected route
        if result["route"] == "agent1":
            print("\n chatbot:", result["answer1"])
        if result["route"] == "web_search":
            print("\nchatbot:", result["answer2"])
finally:
    client.flush()

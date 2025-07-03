from langchain_openai import ChatOpenAI
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage, SystemMessage
from tools import multiply, fetch_page_sync, extract_tables_tool, wiki_search
from langgraph.graph import MessagesState
import asyncio


# combine tools
tools = [multiply, fetch_page_sync, extract_tables_tool, wiki_search]

# Set up LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_tools = llm.bind_tools(tools)

sys_msg = SystemMessage(content="""
You are a general AI assistant. I will ask you a question. Report your thoughts, and
finish your answer with the following template: FINAL ANSWER: [YOUR FINAL ANSWER].
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated
list of numbers and/or strings.
If you are asked for a number, do not use comma to write your number neither use units such as $ or
percent sign unless specified otherwise.
If you are asked for a string, do not use articles, neither abbreviations (e.g. for cities), and write the
digits in plain text unless specified otherwise.
If you are asked for a comma separated list, apply the above rules depending of whether the element
to be put in the list is a number or a string.
""")


# setting up the graph
# Node 1: LLM with tools
def agent_with_tools(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# old node when we were simply routing
""" 
def agent_with_tools(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
"""

# Build Graptgh
builder = StateGraph(MessagesState)
builder.add_node("agent_with_tools", agent_with_tools)
builder.add_node("tools", ToolNode([multiply, fetch_page_sync, extract_tables_tool, wiki_search]))
builder.add_edge(START, "agent_with_tools")
builder.add_conditional_edges(
    "agent_with_tools", tools_condition
)
builder.add_edge("tools", "agent_with_tools")
graph = builder.compile()

# dipsplay the graph

display(Image(graph.get_graph().draw_mermaid_png()))

# to check the steps
messages = [HumanMessage(
    content="How many studio albums were published (released) by Mercedes Sosa between 2000 and 2009 inclusive? Use only data from the 2022 English Wikipedia. Ignore live albums, compilations, and posthumous releases..")]
messages = graph.invoke({"messages": messages})
for m in messages['messages']:
    m.pretty_print()



import asyncio
import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()


async def run_mcp_query(user_input: str):
    # Get Groq API key
    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    # Initialize Groq model
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=groq_key
    )

    # MCP Client (HTTP transport)
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp"  # MCP server URL
            }
        }
    )

    # Fetch tools from MCP server
    tools = await client.get_tools()

    # Bind tools to model
    model_with_tools = model.bind_tools(tools)
    tool_node = ToolNode(tools)

    # Decide whether to call tools again
    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]

        if last_message.tool_calls:
            return "tools"
        return END

    # Call LLM
    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Build LangGraph
    builder = StateGraph(MessagesState)

    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue)
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    # Run graph
    result = await graph.ainvoke(
        {
            "messages": [
                {"role": "user", "content": user_input}
            ]
        }
    )

    # Extract final answer
    last_msg = result["messages"][-1].content
    return last_msg if isinstance(last_msg, str) else str(last_msg)


def main():
    st.set_page_config(
        page_title="MCP Math Chat",
        page_icon="🧮",
        layout="centered"
    )

    st.title("🧮 MCP Math Chat (Groq + MCP + LangGraph)")
    st.caption("Powered by Groq LLaMA 3.1 + MCP Tool Server")

    user_input = st.text_input("Ask me something math-related:")

    if st.button("Send") and user_input.strip():
        with st.spinner("Thinking..."):
            try:
                answer = asyncio.run(run_mcp_query(user_input))
                st.success(answer)
            except Exception as e:
                st.error(str(e))


if __name__ == "__main__":
    main()

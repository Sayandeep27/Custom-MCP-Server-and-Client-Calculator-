import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

# LangChain + MCP imports
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

# LangGraph imports
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode


# ----------------------------
# LOAD ENVIRONMENT VARIABLES
# ----------------------------
load_dotenv()


# ----------------------------
# ASYNC FUNCTION TO RUN MCP QUERY
# ----------------------------
async def run_mcp_query(user_input: str) -> str:
    """
    Takes user input, sends it to the LLM,
    lets the LLM decide whether to call MCP tools,
    and returns the final answer.
    """

    # Load OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")

    # Initialize chat model
    # (You can swap this with any supported LLM)
    model = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=openai_key
    )

    # ----------------------------
    # MCP CLIENT CONFIGURATION
    # ----------------------------
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )


    # use this if we have used stdio transport in server
    # client = MultiServerMCPClient(  
        # {
            # "math": {
                # "command": "python",
                # # Full absolute path to math_server.py
                # "args": ["E:/langraph_custom_mcp_demo/custom_mcp_server.py"],
                # "transport": "stdio",
            # }
        # }
    # )
    

    # Fetch all tools exposed by the MCP server
    tools = await client.get_tools()

    # Bind tools to the LLM
    model_with_tools = model.bind_tools(tools)

    # ToolNode executes MCP tools when the model requests them
    tool_node = ToolNode(tools)


    # ----------------------------
    # CONTROL FLOW DECISION
    # ----------------------------
    def should_continue(state: MessagesState):
        """
        Decide whether to call tools or finish execution.
        """
        messages = state["messages"]
        last_message = messages[-1]

        # If model asked for tool calls → go to tools node
        if last_message.tool_calls:
            return "tools"

        # Otherwise → end graph
        return END


    # ----------------------------
    # MODEL CALL NODE
    # ----------------------------
    async def call_model(state: MessagesState):
        """
        Sends conversation to the LLM.
        """
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}


    # ----------------------------
    # LANGGRAPH PIPELINE
    # ----------------------------
    builder = StateGraph(MessagesState)

    # Register nodes
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)

    # Define execution flow
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue)
    builder.add_edge("tools", "call_model")

    # Compile the graph
    graph = builder.compile()

    # Run the graph
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": user_input}]}
    )

    # Extract final response
    last_msg = result["messages"][-1].content
    return last_msg if isinstance(last_msg, str) else str(last_msg)


# ----------------------------
# STREAMLIT UI
# ----------------------------
def main():
    st.set_page_config(page_title="MCP Math Chat", page_icon="🧮")
    st.title("🧮 MCP Math Chat")

    user_input = st.text_input("Ask me something math-related:")

    if st.button("Send") and user_input.strip():
        with st.spinner("Thinking..."):
            answer = asyncio.run(run_mcp_query(user_input))
            st.success(answer)


# ----------------------------
# APP ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    main()

# 🧠 MCP Math Assistant

### **LangGraph + LangChain + MCP + Streamlit**

> A complete, end‑to‑end example showing **how a UI client (Streamlit) talks to an MCP Tool Server using LangChain and LangGraph**, letting an LLM *decide intelligently* when to call tools.

---

## ✨ What This Project Does

This project demonstrates a **tool‑aware AI assistant** with a clean separation of concerns:

* 🖥️ **Streamlit UI** → acts as the **MCP Client**
* 🧰 **FastMCP Server** → exposes math functions as tools
* 🧠 **LangGraph** → controls agent flow and looping
* 🤖 **LLM (via LangChain)** → decides *when* to call tools

**Result**

> Ask: *“What is the square root of 81?”*
> The LLM **calls the MCP tool**, gets `9`, and replies correctly.

---

## 🧱 System Architecture

```
┌──────────────────┐
│  Streamlit UI    │  ← MCP Client
│  (User Input)    │
└─────────┬────────┘
          │
          ▼
┌────────────────────────┐
│   LangGraph Engine     │
│   (Control Flow)       │
└─────────┬──────────────┘
          │
          ▼
┌────────────────────────┐
│   LLM (LangChain)      │
│   Tool Decision Maker  │
└─────────┬──────────────┘
          │ tool call
          ▼
┌────────────────────────┐
│   MCP Tool Server      │
│   (FastMCP – Math)     │
└────────────────────────┘
```

---

## 📂 Project Structure

```
.
├── mcp_client.py   # Streamlit UI + MCP client + LangGraph logic
├── mcp_server.py   # FastMCP tool server (math operations)
├── .env            # OpenAI API key
├── README.md
```

---

## 🔹 MCP Tool Server (`mcp_server.py`)

### 🎯 Purpose

This file **exposes Python functions as MCP tools** using **FastMCP**.

These tools can be consumed by:

* LangChain agents
* LangGraph workflows
* Claude Desktop
* Any MCP‑compatible client

---

### 🧰 Tools Exposed

| Tool Name     | Description                   |
| ------------- | ----------------------------- |
| `add`         | Add two integers              |
| `multiply`    | Multiply two integers         |
| `divide`      | Safe division with validation |
| `square_root` | Square root with checks       |
| `factorial`   | Factorial with input checks   |

---

### ⚙️ How FastMCP Works

```python
mcp = FastMCP("Math")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

FastMCP automatically:

* Generates tool schemas
* Handles validation
* Exposes HTTP endpoints

---

### ▶️ Run MCP Server

```bash
python mcp_server.py
```

Server runs at:

```
http://127.0.0.1:8000/mcp
```

Transport used:

```
streamable_http
```

---

## 🔹 MCP Client + Agent (`mcp_client.py`)

### 🎯 Purpose

This file is the **brain of the system**. It:

* Accepts user input from Streamlit
* Sends queries to the LLM
* Lets the LLM decide whether tools are needed
* Executes MCP tools if required
* Returns the final answer

---

## 🧠 Core Components

### 1️⃣ MCP Client Configuration

```python
client = MultiServerMCPClient({
    "math": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8000/mcp"
    }
})
```

This tells LangChain:

* Where the MCP server lives
* How to communicate with it

---

### 2️⃣ Tool Discovery (Dynamic)

```python
tools = await client.get_tools()
```

✔ No hardcoding
✔ Auto schema loading
✔ Plug‑and‑play tools

---

### 3️⃣ LLM + Tool Binding

```python
model_with_tools = model.bind_tools(tools)
```

Now the LLM can:

* Answer directly **or**
* Call MCP tools when needed

---

### 4️⃣ LangGraph Control Flow

#### 🧩 Graph Nodes

| Node Name    | Responsibility     |
| ------------ | ------------------ |
| `call_model` | Calls the LLM      |
| `tools`      | Executes MCP tools |

#### 🔀 Decision Logic

```python
def should_continue(state):
    if last_message.tool_calls:
        return "tools"
    return END
```

✨ This is the magic:

* Tool requested → execute tools
* No tool → finish

---

### 5️⃣ Execution Loop

```
START → call_model
          ↓
        tools (if needed)
          ↓
      call_model
          ↓
         END
```

LangGraph automatically loops until **no more tool calls** remain.

---

## 🖥️ Streamlit UI

Minimal, clean UI:

* Text input for math questions
* Async LangGraph execution
* Final answer rendered cleanly

```python
st.text_input("Ask me something math‑related:")
```

---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies

```bash
pip install streamlit langchain langgraph mcp langchain-mcp-adapters python-dotenv
```

---

### 2️⃣ Set Environment Variable

Create a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

### 3️⃣ Start MCP Server

```bash
python mcp_server.py
```

---

### 4️⃣ Start Streamlit App

```bash
streamlit run mcp_client.py
```

---

## 🧪 Example Queries

| User Query              | Action Taken           |
| ----------------------- | ---------------------- |
| `What is 5 + 7?`        | Calls `add` tool       |
| `Factorial of 6`        | Calls `factorial` tool |
| `Explain prime numbers` | LLM answers directly   |
| `Square root of -9`     | Tool error surfaced    |

---

## 🧠 Key Concepts Demonstrated

* MCP as a **tool protocol**
* LangGraph for **deterministic agent control**
* LLM‑driven tool selection
* Tool execution loops
* UI and agent separation

---

## 🚀 Why This Architecture Matters

This pattern scales beautifully to:

* Multi‑agent systems
* A2A protocols
* Claude Desktop tools
* Production AI assistants

You now have:

✔ Clean separation of concerns
✔ Replaceable LLMs
✔ Pluggable tools
✔ Deterministic agent flow

---

### ⭐ If you understand this project, you understand modern agentic AI.

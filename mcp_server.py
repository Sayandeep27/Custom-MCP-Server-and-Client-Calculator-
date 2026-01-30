# Import FastMCP to create an MCP tool server
from mcp.server.fastmcp import FastMCP

# Standard math library (needed for sqrt, factorial)
import math

# Create an MCP server instance
# "Math" is the tool namespace that clients will see
mcp = FastMCP("Math")


# ----------------------------
# TOOL 1: ADDITION
# ----------------------------
@mcp.tool()
def add(a: int, b: int) -> int:
    """
    Add two numbers.
    This function will be exposed as an MCP tool.
    """
    return a + b


# ----------------------------
# TOOL 2: MULTIPLICATION
# ----------------------------
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers.
    """
    return a * b


# ----------------------------
# TOOL 3: DIVISION
# ----------------------------
@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide a by b.
    Raises an error if b is zero.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


# ----------------------------
# TOOL 4: SQUARE ROOT
# ----------------------------
@mcp.tool()
def square_root(x: float) -> float:
    """
    Return the square root of x.
    Raises error for negative numbers.
    """
    if x < 0:
        raise ValueError("Cannot take square root of a negative number.")
    return math.sqrt(x)


# ----------------------------
# TOOL 5: FACTORIAL
# ----------------------------
@mcp.tool()
def factorial(n: int) -> int:
    """
    Return factorial of n.
    Raises error for negative numbers.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.factorial(n)


# ----------------------------
# SERVER ENTRY POINT
# ----------------------------
if __name__ == "__main__":
    """
    Starts the MCP server using HTTP transport.
    This allows LangChain / LangGraph clients to call tools over HTTP.
    
    URL exposed:
    http://127.0.0.1:8000/mcp
    """
    mcp.run(transport="streamable-http")  # this is also local server but still acts as remote

    # mcp.run(transport="stdio") if local server

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MathTools")


@mcp.tool()
def add(a: float, b: float) -> float:
    """add a and b"""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """subtract a and b"""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """multiply b/w a and b"""
    return a * b


if __name__ == "__main__":
    mcp.run()

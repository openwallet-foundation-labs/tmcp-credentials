from mcp.server.fastmcp import FastMCP
from tmcp import TmcpManager

# Create an MCP server
mcp = FastMCP(
    name="tmcp-credential-checking-server",
    port=8001,
    transport_manager=TmcpManager(transport="http://localhost:8001/mcp"),
)


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="streamable-http")

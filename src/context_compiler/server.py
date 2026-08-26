from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("ContextCompiler")

@mcp.tool()
def ping() -> str:
    """A simple ping tool to verify the MCP server is running."""
    return "pong"

if __name__ == "__main__":
    # Run the server using standard input/output (stdio)
    mcp.run()

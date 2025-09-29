from .server import mcp


def main():
    """
    Initialize and run the server
    """
    print("Starting TMCP Credential Checking Server...")
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()

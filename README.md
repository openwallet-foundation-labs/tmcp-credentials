# tmcp-credentials

Install the server alongside it's depednencies:
```sh
uv pip install -e .
```

Run the server with:

```sh
run-credential-checking-server
```
OR, Alternatively:
```sh
uv run -m src.credential_checking_server
```

Then use a TMCP-enabled client to connect to it using the server's DID (see the [demo folder](https://github.com/openwallet-foundation-labs/mcp-over-tsp-python/tree/main/demo) in the TMCP repository for some TMCP-enabled clients). E.g. for fast-agent, use:

```sh
uv run fast-agent go --url <server-did-here>
```

# tmcp-credentials

Run the server with:

```sh
uv run server.py
```

Then use a TMCP-enabled client to connect to it using the server's DID (see the [demo folder](https://github.com/openwallet-foundation-labs/mcp-over-tsp-python/tree/main/demo) in the TMCP repository for some TMCP-enabled clients). E.g. for fast-agent, use:

```sh
uv run fast-agent go --url did:webvh:QmYsbUWtNNRkWM6nYLCfReYaaonD9Gfn8VzS4eneRpqM2L:did.teaspoon.world:endpoint:CredTmcpSseServer-0052270b-508a-4ab5-8091-3752fbb5ae82
```

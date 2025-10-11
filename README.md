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

### TMCP Server Testing

1. Start the TMCP server, Copy the server DID from the output, e.g. `did:webvh:QmQLrF...`

```sh
uv run -m src.credential_checking_server
```

2. Run the `examples/generate_test_credential.py` file

```sh
uv run examples/generate_test_credential.py <server_did>
```

This creates:
- `issuer_public_key.json` - Public key for the server to verify credentials
- `test_presentation.txt` - A test presentation with the submission command

3. Restart the TMCP server (close the previous session), and connect with fast-agent client.

4. In fast-agent, copy and paste the full command from `test_presentation.txt`
   
**Expected Result:**
```json
{
  "status": "success",
  "message": "Credential verified.",
  "claims": {
    "cnf": {
  ...
}
```
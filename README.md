# tmcp-credentials

Install the server alongside it's depednencies:

```sh
uv pip install -e .
```

## Running the Server

Run the server with:

```sh
run-credential-checking-server
```

OR, alternatively:

```sh
uv run -m src.credential_checking_server
```

Then use a TMCP-enabled client to connect to it using the server's DID (see the [demo folder](https://github.com/openwallet-foundation-labs/mcp-over-tsp-python/tree/main/demo) in the TMCP repository for some TMCP-enabled clients).

For fast-agent, use:

```sh
uv run fast-agent go --url <server-did-here>
```

---

## TMCP Server Demo (Credential Checking Protocol)

This section provides a complete guide to testing the credential checking server demo.

### Prerequisites

- Python 3.11+
- `uv` package manager
- [fast-agent client](https://github.com/openwallet-foundation-labs/fast-agent/)

### Complete Test Flow Example

```sh
# Terminal 1: Start server
$ uv run -m src.credential_checking_server
Server DID: did:webvh:Qmb15Uwt...

# Terminal 2: Generate credentials, 
# keep note of the generated file `test_presentation.txt`
$ uv run examples/generate_test_credential.py \
    <SERVER DID HERE> \
    "did:webvh:QmYYY:issuer.example.com" \
    "did:webvh:QmZZZ:holder.example.com"

# Terminal 1: Restart server (Ctrl+C then restart)
$ uv run -m src.credential_checking_server

# Terminal 2: Connect with fast-agent
$ uv run fast-agent go --url "did:webvh:Qmb15Uwt..."

# In fast-agent:
# First: Run the `list_required_credential` tool
> list_required_credential

# Second: Note the `nonce` you get in the output,
# Put the `nonce` in the string in `test_presentation.txt` and send it to the TMCP client.
> submit_credential format="sd-jwt" presentation="eyJ..." nonce="<nonce from step 1>"

# Expected: {"status": "success", ...}
```

### Step 1: Start the TMCP Server

Start the server and note the server DID from the output:

```sh
uv run -m src.credential_checking_server
```

> [!TIP]
> Copy the **Server DID** - you'll need it in the next step.

### Step 2: Generate Test Credentials

Run the example script to generate "demo credentials" with the server DID:

```sh
uv run examples/generate_test_credential.py \
    "<SERVER_DID HERE>" \
    "did:webvh:QmYYY:issuer.example.com" \
    "did:webvh:QmZZZ:holder.example.com"
```

**Arguments:**

| Argument | Description | Example |
|----------|-------------|---------|
| `server_did` | The verifier's DID (from Step 1) | `did:webvh:Qmb15Uwt...` |
| `issuer_did` | The credential issuer's DID | `did:webvh:QmYYY:issuer.example.com` |
| `holder_did` | The credential holder's DID | `did:webvh:QmZZZ:holder.example.com` |

**Generated Files:**

| File | Description |
|------|-------------|
| `issuer_public_key.json` | Issuer's public key for verification |
| `holder_key.json` | Holder's private key for signing |
| `test_presentation.txt` | Ready-to-use submission command |

### Step 3: Restart the Server

The server needs to reload the new `issuer_public_key.json`:

```sh
# Stop the previous server (Ctrl+C)
# Then restart:
uv run -m src.credential_checking_server
```

### Step 4: Connect with fast-agent

In a new terminal, connect to the server:

```sh
uv run fast-agent go --url <server-did-here>
```

### Step 5: Test the Tools

#### Tool 1: `get_server_did`

Get the server's DID for credential binding.

**Request:**

```sh
get_server_did
```

**Response Schema:**

```json
{
  "server_did": "did:webvh:Qmb...",
  "usage": "Use this DID as the 'aud' claim when generating credentials"
}
```

#### Tool 2: `list_required_credentials`

Get the credential requirements for accessing this service.

**Request:**

```sh
list_required_credentials
```

**Response Schema:**

```json
{
  "requirements": [
    {
      "format": "sd-jwt",
      "required_claims": [
        {
          "claim": "given_name",
          "purpose": "To verify your identity"
        },
        {
          "claim": "family_name",
          "purpose": "To verify your identity"
        }
      ],
      "trusted_issuers": [
        {
          "did": "did:webvh:QmYYY:issuer.example.com",
          "name": "Trusted Issuer",
          "description": "Registered credential issuer"
        }
      ],
      "credential_types": ["IdentityCredential"]
    }
  ],
  "presentation_definition": {
    "nonce": "abc123xyz...",
    "expires_at": "2025-12-16T12:00:00Z",
    "max_age": 300
  },
  "verifier": {
    "did": "did:webvh:Qmb15Uwt...",
    "name": "TMCP Credential Checking Server",
    "purpose": "Verify identity for service access"
  }
}
```

#### Tool 3: `submit_credential`

Submit a credential presentation for verification.

**Request:**

Copy the command from `test_presentation.txt`:

```sh
submit_credential format="sd-jwt" presentation="<JWT>~<Disclosure1>~<Disclosure2>~<KB-JWT>" nonce="test_nonce_XXXXXXXXXX"
```

**Success Response Schema:**

```json
{
  "status": "success",
  "message": "Credential verified successfully",
  "verification_result": {
    "verified_at": "2025-12-16T11:55:05Z",
    "holder": {
      "did": "did:webvh:QmZZZ:holder.example.com",
      "verified": true
    },
    "issuer": {
      "did": "did:webvh:QmYYY:issuer.example.com",
      "name": "Trusted Issuer",
      "verified": true,
      "trusted": true
    },
    "credential": {
      "issued_at": "2025-12-16T10:00:00Z",
      "expires_at": "2025-12-16T14:00:00Z",
      "type": "IdentityCredential"
    },
    "disclosed_claims": {
      "given_name": "John",
      "family_name": "Doe"
    }
  }
}
```

**Failure Response Schema:**

```json
{
  "status": "failure",
  "error": {
    "code": "INVALID_ISSUER",
    "message": "Credential issuer is not in the trusted registry",
    "details": {
      "issuer_did": "did:webvh:unknown:issuer",
      "reason": "Issuer not found in trusted registry"
    }
  },
  "verification_result": {
    "verified_at": "2025-12-16T11:55:05Z",
    "holder": {
      "verified": false
    },
    "issuer": {
      "verified": false,
      "trusted": false
    }
  }
}
```

### Error Codes

| Error Code | Cause | Resolution |
|------------|-------|------------|
| `INVALID_ISSUER` | Issuer DID not in trusted registry | Use a trusted issuer or add to registry |
| `INVALID_SIGNATURE` | Cryptographic verification failed | Regenerate credential with correct keys |
| `EXPIRED_CREDENTIAL` | Credential past expiration | Issue a new credential |
| `INVALID_HOLDER` | Holder DID mismatch | Ensure `sub` matches session client DID |
| `INVALID_AUDIENCE` | `aud` claim doesn't match server DID | Use correct server DID in presentation |
| `INVALID_NONCE` | Nonce mismatch or expired | Use the nonce from `list_required_credentials` |
| `MISSING_CLAIMS` | Required claims not disclosed | Disclose all required claims |
| `INVALID_DISCLOSURE` | Disclosure hash doesn't match | Regenerate presentation |

### Complete Test Flow Example

```sh
# Terminal 1: Start server
$ uv run -m src.credential_checking_server
Server DID: did:webvh:Qmb15Uwt...

# Terminal 2: Generate credentials, 
# keep note of the generated file `test_presentation.txt`
$ uv run examples/generate_test_credential.py \
    "did:webvh:Qmb15Uwt..." \
    "did:webvh:QmYYY:issuer.example.com" \
    "did:webvh:QmZZZ:holder.example.com"

# Terminal 1: Restart server (Ctrl+C then restart)
$ uv run -m src.credential_checking_server

# Terminal 2: Connect with fast-agent
$ uv run fast-agent go --url "did:webvh:Qmb15Uwt..."

# In fast-agent:
# First: Run the `list_required_credential` tool
> list_required_credential

# Second: Note the `nonce` you get in the output,
# Put the `nonce` in the string in `test_presentation.txt` and send it to the TMCP client.
> submit_credential format="sd-jwt" presentation="eyJ..." nonce="<nonce from step 1>"

# Expected: {"status": "success", ...}
```

## Architecture Notes

### DID-Based Key Resolution (Spec vs Current Implementation)

**Per the Specification:**
The server should resolve issuer public keys from their DIDs:

```
Credential.iss = "did:webvh:issuer.example.com"
         │
         ▼
Server resolves DID → DID Document → Public Key
         │
         ▼
Server verifies signature
```

**Current Implementation (Temporary Workaround):**
Since DID resolution for `did:webvh` is not yet implemented, the server uses a cached key file:

```
issuer_public_key.json → Server loads key → Verifies signature
```

**Files involved:**

- `issuer_public_key.json` - Temporary cache of issuer's public key
- This file will be removed once DID resolution is implemented

**TODO:**

- [ ] Implement `did:webvh` DID resolution
- [ ] Remove `issuer_public_key.json` workaround
- [ ] Update trusted issuer registry to only store DIDs

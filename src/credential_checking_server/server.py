import json
from mcp.server.fastmcp import FastMCP, Context
from tmcp import TmcpManager
from ..credential_handler import CredentialHandler, SdJwtHandler
from jwcrypto.jwk import JWK

# --- Credential Handler Setup ---
handler = CredentialHandler()
sd_jwt_handler = SdJwtHandler()
handler.register_handler(sd_jwt_handler)

try:
    with open("issuer_public_key.json", "r") as f:
        ISSUER_REGISTRY = json.load(f)
    print("Verifying Server loaded Issuer's public key.")
except FileNotFoundError:
    print(
        "Error: issuer_public_key.json not found. "
        "Run examples/generate_test_credential.py first."
    )
    exit(1)


tmcp_manager = TmcpManager(transport="http://localhost:8001/mcp")

mcp = FastMCP(
    name="tmcp-credential-checking-server",
    port=8001,
    transport_manager=tmcp_manager,
)


def resolve_issuer_public_key(issuer_did: str) -> JWK:
    # Check if this issuer is in the trusted registry
    if issuer_did != ISSUER_REGISTRY["issuer_did"]:
        raise ValueError(
            f"Issuer '{issuer_did}' is not trusted. "
            f"Expected: {ISSUER_REGISTRY['issuer_did']}"
        )

    issuer_key = JWK(**ISSUER_REGISTRY["public_key"])
    return issuer_key


@mcp.tool()
def get_server_did() -> dict:
    """Returns the server's DID for credential binding."""
    return {
        "server_did": tmcp_manager.did,
        "usage": "Use this DID as the 'aud' claim when generating credentials",
    }


@mcp.tool()
def list_required_credentials() -> dict:
    """Returns a list of supported credential formats and the claims required."""
    return {
        "requirements": [{"format": "sd-jwt", "claims": ["given_name", "family_name"]}]
    }


@mcp.tool()
async def submit_credential(
    ctx: Context, format: str, presentation: str, nonce: str
) -> dict:
    """Submits a credential presentation for verification."""
    try:

        def get_issuer_public_key(issuer_did, header_parameters):
            return resolve_issuer_public_key(issuer_did)

        # Verify the presentation
        verified_claims = handler.verify(
            cred_format=format,
            presentation=presentation,
            get_issuer_key_callback=get_issuer_public_key,
            options={
                "nonce": nonce,
                "aud": tmcp_manager.did,
            },
        )

        return {
            "status": "success",
            "message": "Credential verified.",
            "claims": verified_claims,
        }

    except Exception as e:
        return {"status": "failure", "message": str(e), "error_type": type(e).__name__}

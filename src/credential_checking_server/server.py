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
        ISSUER_PUBLIC_KEY = JWK.from_json(f.read())
    print("Verifying Server loaded Issuer's public key.")
except FileNotFoundError:
    print(
        "Error: issuer_public_key.json not found. "
        "Run tools/generate_test_credential.py first."
    )
    exit(1)


tmcp_manager = TmcpManager(transport="http://localhost:8001/mcp")

mcp = FastMCP(
    name="tmcp-credential-checking-server",
    port=8001,
    transport_manager=tmcp_manager,
)


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

        def get_issuer_public_key(issuer, header_parameters):
            return ISSUER_PUBLIC_KEY

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

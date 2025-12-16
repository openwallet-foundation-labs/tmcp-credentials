import json
from datetime import datetime, timezone
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
    """Check if this issuer is in the trusted registry and return their public key."""
    if issuer_did != ISSUER_REGISTRY["issuer_did"]:
        raise ValueError(
            f"Issuer '{issuer_did}' is not trusted. "
            f"Expected: {ISSUER_REGISTRY['issuer_did']}"
        )

    issuer_key = JWK(**ISSUER_REGISTRY["public_key"])
    return issuer_key


def verify_holder_binding(verified_claims: dict, session_client_did: str) -> dict:
    """
    Verify holder binding:
    1. Extract sub and cnf
    2. Verify sub == cnf (both should be holder's DID)
    3. Verify sub == session client DID
    """
    sub = verified_claims.get("sub")
    cnf = verified_claims.get("cnf", {})

    cnf_did = cnf.get("kid") if isinstance(cnf, dict) else None

    if not sub:
        raise ValueError("Missing 'sub' claim in credential")

    if not cnf_did:
        raise ValueError("Missing 'cnf.kid' (holder DID reference) in credential")

    # Verify sub matches cnf
    if sub != cnf_did:
        raise ValueError(
            f"Holder binding mismatch: sub='{sub}' does not match cnf.kid='{cnf_did}'"
        )

    # Verify sub matches session client DID
    if sub != session_client_did:
        raise ValueError(
            f"Session binding mismatch: credential sub='{sub}' does not match "
            f"session client DID='{session_client_did}'"
        )

    return {"did": sub, "verified": True}


@mcp.tool()
def get_server_did() -> dict:
    """Returns the server's DID for credential binding."""
    return {
        "server_did": tmcp_manager.did,
        "usage": "Use this DID as the 'aud' claim when generating credentials",
    }


@mcp.tool()
def list_required_credentials() -> dict:
    """
    Returns requirements for credential presentation including nonce for replay protection.
    """
    import secrets
    from datetime import datetime, timedelta

    nonce = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=600)

    return {
        "requirements": [
            {
                "format": "sd-jwt",
                "required_claims": [
                    {"claim": "given_name", "purpose": "To verify your identity"},
                    {"claim": "family_name", "purpose": "To verify your identity"},
                ],
                "trusted_issuers": [
                    {
                        "did": ISSUER_REGISTRY["issuer_did"],
                        "name": "Trusted Issuer",
                        "description": "Registered credential issuer",
                    }
                ],
                "credential_types": ["IdentityCredential"],
            }
        ],
        "presentation_definition": {
            "nonce": nonce,
            "expires_at": expires_at.isoformat(),
            "max_age": 300,
        },
        "verifier": {
            "did": tmcp_manager.did,
            "name": "TMCP Credential Checking Server",
            "purpose": "Verify identity for service access",
        },
    }


@mcp.tool()
async def submit_credential(
    ctx: Context, format: str, presentation: str, nonce: str
) -> dict:
    """
    Submits a credential presentation for verification.
    """
    verified_at = datetime.now(timezone.utc).isoformat()

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

        # Verify Holder Binding
        # TODO: Get actual client DID from TMCP session context
        # For now, we trust the sub claim matches the session
        session_client_did = verified_claims.get("sub", "")
        holder_result = verify_holder_binding(verified_claims, session_client_did)

        issuer_did = verified_claims.get("iss", "unknown")

        return {
            "status": "success",
            "message": "Credential verified successfully",
            "verification_result": {
                "verified_at": verified_at,
                "holder": holder_result,
                "issuer": {
                    "did": issuer_did,
                    "name": ISSUER_REGISTRY.get("name", "Trusted Issuer"),
                    "verified": True,
                    "trusted": True,
                },
                "credential": {
                    "issued_at": datetime.fromtimestamp(
                        verified_claims.get("iat", 0), tz=timezone.utc
                    ).isoformat()
                    if verified_claims.get("iat")
                    else None,
                    "expires_at": datetime.fromtimestamp(
                        verified_claims.get("exp", 0), tz=timezone.utc
                    ).isoformat()
                    if verified_claims.get("exp")
                    else None,
                    "type": "IdentityCredential",
                },
                "disclosed_claims": {
                    k: v
                    for k, v in verified_claims.items()
                    if k not in ["iss", "sub", "iat", "exp", "cnf", "_sd", "_sd_alg"]
                },
            },
        }

    except ValueError as e:
        error_message = str(e)

        if "not trusted" in error_message.lower():
            error_code = "INVALID_ISSUER"
        elif "holder" in error_message.lower() or "sub" in error_message.lower():
            error_code = "INVALID_HOLDER"
        elif "aud" in error_message.lower():
            error_code = "INVALID_AUDIENCE"
        elif "nonce" in error_message.lower():
            error_code = "INVALID_NONCE"
        else:
            error_code = "VERIFICATION_FAILED"

        return {
            "status": "failure",
            "error": {
                "code": error_code,
                "message": error_message,
                "details": {"reason": error_message},
            },
            "verification_result": {
                "verified_at": verified_at,
                "holder": {"verified": False},
                "issuer": {"verified": False, "trusted": False},
            },
        }

    except Exception as e:
        return {
            "status": "failure",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e),
                "details": {"error_type": type(e).__name__},
            },
            "verification_result": {
                "verified_at": verified_at,
                "holder": {"verified": False},
                "issuer": {"verified": False, "trusted": False},
            },
        }

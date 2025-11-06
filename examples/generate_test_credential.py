"""
Generate a test SD-JWT credential for TMCP server testing.
Usage: uv run examples/generate_test_credential.py <server_did> <issuer_did>
"""

import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from credential_handler import CredentialHandler, SdJwtHandler


def generate_credential(server_did: str, issuer_did: str):
    """Generate a test credential bound to the server DID with verifiable issuer."""
    handler = CredentialHandler()
    sd_jwt_handler = SdJwtHandler()
    handler.register_handler(sd_jwt_handler)

    # Generate keys
    keys = handler.generate_keys("sd-jwt")
    issuer_key = keys["issuer_key"]
    holder_key = keys["holder_key"]
    issuer_public_key = keys["issuer_public_key"]

    # Save issuer public key mapped to their DID
    issuer_registry = {
        "issuer_did": issuer_did,
        "public_key": json.loads(issuer_public_key.export()),
    }

    with open("issuer_public_key.json", "w") as f:
        json.dump(issuer_registry, f, indent=2)
    print("Saved issuer public key to issuer_public_key.json")

    # Create claims with holder binding
    user_claims = {
        "iss": issuer_did,
        "sub": "user123",
        "given_name": "John",
        "family_name": "Doe",
        "email": "john.doe@example.com",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "cnf": {"jwk": json.loads(holder_key.export_public())},
    }

    # Issue credential
    credential = handler.issue(
        cred_format="sd-jwt",
        user_claims=user_claims,
        issuer_key=issuer_key,
        holder_key=holder_key,
    )

    # Create presentation
    nonce = f"test_nonce_{int(time.time())}"
    disclosed_claims = {"given_name": True, "family_name": True}

    presentation = handler.create_presentation(
        cred_format="sd-jwt",
        credential=credential,
        disclosed_claims=disclosed_claims,
        holder_key=holder_key,
        options={"nonce": nonce, "aud": server_did},
    )

    # Save to file for easy testing
    with open("test_presentation.txt", "w") as f:
        f.write(f"# Issuer DID: {issuer_did}\n")
        f.write(f"# Server DID: {server_did}\n\n")
        f.write(
            f'submit_credential format="sd-jwt" presentation="{presentation}" nonce="{nonce}"\n'
        )
    print("Saved to test_presentation.txt")

    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Restart the TMCP server to load the new issuer public key")
    print("2. Connect with fast-agent and run the command from test_presentation.txt")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: uv run examples/generate_test_credential.py <server_did> <issuer_did>"
        )
        print("\nExample:")
        print(
            "  uv run examples/generate_test_credential.py \\\n"
            "    did:webvh:QmXXX:did.teaspoon.world:endpoint:tmcp-xxx \\\n"
            "    did:webvh:QmYYY:issuer.example.com"
        )
        sys.exit(1)

    generate_credential(sys.argv[1], sys.argv[2])

"""
Generate a test SD-JWT credential for TMCP server testing.
Usage: uv run examples/generate_test_credential.py <server_did> <issuer_did> <holder_did>
"""

import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sd_jwt.issuer import SDJWTIssuer
from sd_jwt.holder import SDJWTHolder
from jwcrypto.jwk import JWK


def generate_credential(server_did: str, issuer_did: str, holder_did: str):
    """Generate a test credential bound to the server DID with verifiable issuer."""

    issuer_key = JWK.generate(kty="EC", crv="P-256")
    holder_key = JWK.generate(kty="EC", crv="P-256")
    issuer_public_key = JWK.from_json(issuer_key.export_public())

    issuer_registry = {
        "issuer_did": issuer_did,
        "public_key": json.loads(issuer_public_key.export()),
    }

    with open("issuer_public_key.json", "w") as f:
        json.dump(issuer_registry, f, indent=2)

    holder_key_data = {
        "holder_did": holder_did,
        "private_key": json.loads(holder_key.export()),
    }
    with open("holder_key.json", "w") as f:
        json.dump(holder_key_data, f, indent=2)

    user_claims = {
        "iss": issuer_did,
        "sub": holder_did,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "cnf": {"kid": holder_did},
        # These will be selectively disclosable
        "given_name": "Jon",
        "family_name": "Doe",
        "email": "jondoe@mail.com",
    }

    sd_claims = {
        "given_name": "Jon",
        "family_name": "Doe",
        "email": "jondoe@mail.com",
    }

    from sd_jwt.common import SDObj

    user_claims_with_sd = {
        "iss": issuer_did,
        "sub": holder_did,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "cnf": {"kid": holder_did},
        SDObj("given_name"): "Jon",
        SDObj("family_name"): "Doe",
        SDObj("email"): "jondoe@mail.com",
    }

    issuer = SDJWTIssuer(
        user_claims=user_claims_with_sd,
        issuer_keys=issuer_key,
        holder_key=holder_key,
    )

    credential = issuer.sd_jwt_issuance

    nonce = f"test_nonce_{int(time.time())}"

    holder = SDJWTHolder(credential)

    disclosed_claims = {
        "given_name": True,
        "family_name": True,
    }

    holder.create_presentation(
        claims_to_disclose=disclosed_claims,
        nonce=nonce,
        aud=server_did,
        holder_key=holder_key,
    )

    presentation = holder.sd_jwt_presentation

    # Save to file for easy testing
    with open("test_presentation.txt", "w") as f:
        f.write(f"# Issuer DID: {issuer_did}\n")
        f.write(f"# Server DID: {server_did}\n")
        f.write(f"# Holder DID: {holder_did}\n\n")
        f.write(
            f'submit_credential format="sd-jwt" presentation="{presentation}" nonce="{nonce}"\n'
        )
    print("Saved to test_presentation.txt")

    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Restart the TMCP server to load the new issuer public key")
    print(
        "2. Connect with fast-agent and run the `list_required_credential` tool and update the nonce in test_presentation.txt"
    )
    print("3. Run the `submit_credential` command from test_presentation.txt")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: uv run examples/generate_test_credential.py <server_did> <issuer_did> <holder_did>"
        )
        print("\nExample:")
        print(
            "  uv run examples/generate_test_credential.py \\\n"
            "    did:webvh:QmXXX:did.teaspoon.world:endpoint:tmcp-xxx \\\n"
            "    did:webvh:QmYYY:issuer.example.com \\\n"
            "    did:webvh:QmZZZ:holder.example.com"
        )
        sys.exit(1)

    generate_credential(sys.argv[1], sys.argv[2], sys.argv[3])

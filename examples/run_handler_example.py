"""
Example: Using the Credential Handler to issue, present, and verify SD-JWT credentials.
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from credential_handler import CredentialHandler, SdJwtHandler


def main():
    # 1. Initialize the main handler
    main_handler = CredentialHandler()

    # 2. Register the SD-JWT handler
    sd_jwt_handler = SdJwtHandler()
    main_handler.register_handler(sd_jwt_handler)

    print(f"Supported formats: {main_handler.get_supported_formats()}")

    # 3. Generate keys
    cred_format = "sd-jwt"
    keys = main_handler.generate_keys(cred_format)
    issuer_key = keys["issuer_key"]
    holder_key = keys["holder_key"]
    issuer_public_key = keys["issuer_public_key"]

    # 4. Define user claims
    user_claims = {
        "given_name": "John",
        "family_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1-202-555-0101",
        "birthdate": "1990-01-15",
    }

    # 5. Issue credential
    print("\n=== Issuing SD-JWT Credential ===")
    issued_credential = main_handler.issue(
        cred_format,
        user_claims=user_claims,
        issuer_key=issuer_key,
        holder_key=holder_key,
    )
    print("Credential issued")

    # 6. Create presentation (selective disclosure)
    disclosed_claims = {"given_name": True, "family_name": True}
    print("\n=== Creating Presentation ===")
    print(f"Disclosing claims: {list(disclosed_claims.keys())}")

    presentation = main_handler.create_presentation(
        cred_format,
        credential=issued_credential,
        disclosed_claims=disclosed_claims,
        holder_key=holder_key,
        options={
            "nonce": "test_nonce_123",
            "aud": "https://verifier.example.com",
        },
    )
    print("\nPresentation created")

    # 7. Verify presentation
    print("\n=== Verifying Presentation ===")

    def get_issuer_public_key(issuer, header_parameters):
        return issuer_public_key

    try:
        verified_claims = main_handler.verify(
            cred_format,
            presentation=presentation,
            get_issuer_key_callback=get_issuer_public_key,
            options={
                "nonce": "test_nonce_123",
                "aud": "https://verifier.example.com",
            },
        )
        print("\nVerification successful!")
        print("\nVerified claims:")
        print(json.dumps(verified_claims, indent=2))
    except Exception as e:
        print(f"\nVerification failed: {e}")


if __name__ == "__main__":
    main()

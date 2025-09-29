import json
from credential_handler import CredentialHandler
from credential_handler import SdJwtHandler

# 1. Initialize the main handler
main_handler = CredentialHandler()

# 2. Initialize and register the SD-JWT handler
sd_jwt_handler = SdJwtHandler()
main_handler.register_handler(sd_jwt_handler)

# 3. Check supported formats
print(f"\nSupported credential formats: {main_handler.get_supported_formats()}")

# 4. Generate keys for the sd-jwt format
cred_format = "sd-jwt"
keys = main_handler.generate_keys(cred_format)
issuer_key = keys["issuer_key"]
holder_key = keys["holder_key"]
issuer_public_key = keys["issuer_public_key"]

# 5. Define user claims for a credential
user_claims = {
    "given_name": "Joe",
    "family_name": "Doe",
    "email": "johndoe@example.com",
    "phone_number": "+1-202-555-0101",
    "birthdate": "1980-01-20",
}

# 6. Issue the credential using the main handler
print("\nIssuing SD-JWT credential...")
issued_credential = main_handler.issue(
    cred_format, user_claims=user_claims, issuer_key=issuer_key, holder_key=holder_key
)
print("Credential issued successfully.")

# 7. Create a presentation
disclosed_claims = {"given_name": True, "family_name": True}
print(f"\nCreating presentation with claims: {list(disclosed_claims.keys())}")
presentation = main_handler.create_presentation(
    cred_format,
    credential=issued_credential,
    disclosed_claims=disclosed_claims,
    holder_key=holder_key,
)
print("Presentation created successfully.")

# 8. Verify the presentation
print("\nVerifying presentation...")


def get_issuer_public_key(issuer, header_parameters):
    # In a real scenario, you might look up the key based on the 'issuer'
    return issuer_public_key


try:
    verified_claims = main_handler.verify(
        cred_format,
        presentation=presentation,
        get_issuer_key_callback=get_issuer_public_key,
    )
    print("\nVerification successful! Verified claims:")
    print(json.dumps(verified_claims, indent=4))
except Exception as e:
    print(f"\nVerification failed: {e}")

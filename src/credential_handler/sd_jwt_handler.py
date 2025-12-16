from .base_handler import BaseCredentialHandler
from sd_jwt.issuer import SDJWTIssuer
from sd_jwt.holder import SDJWTHolder
from sd_jwt.verifier import SDJWTVerifier
from jwcrypto.jwk import JWK


class SdJwtHandler(BaseCredentialHandler):
    """
    Credential handler for the SD-JWT format.
    Supports selective disclosure and holder binding.
    """

    @property
    def format_name(self):
        return "sd-jwt"

    def issue_credential(self, user_claims, issuer_key, holder_key=None):
        issuer = SDJWTIssuer(user_claims, issuer_key, holder_key)
        return issuer.sd_jwt_issuance

    def create_presentation(
        self, credential, disclosed_claims, holder_key=None, options=None
    ):
        options = options or {}
        nonce = options.get("nonce")
        aud = options.get("aud")

        holder = SDJWTHolder(credential)
        holder.create_presentation(disclosed_claims, nonce, aud, holder_key)
        return holder.sd_jwt_presentation

    def verify_presentation(self, presentation, get_issuer_key_callback, options=None):
        options = options or {}

        # Ensure presentation is a string
        if isinstance(presentation, bytes):
            presentation = presentation.decode("utf-8")

        # Create verifier with expected audience and nonce
        verifier = SDJWTVerifier(
            presentation,
            get_issuer_key_callback,
            expected_aud=options.get("aud"),
            expected_nonce=options.get("nonce"),
        )

        # Return verified claims
        return verifier.get_verified_payload()

    def generate_keys(self):
        issuer_key = JWK.generate(kty="EC", crv="P-256")
        holder_key = JWK.generate(kty="EC", crv="P-256")
        issuer_public_key = JWK()
        issuer_public_key.import_key(**issuer_key.export_public(as_dict=True))

        return {
            "issuer_key": issuer_key,
            "holder_key": holder_key,
            "issuer_public_key": issuer_public_key,
        }

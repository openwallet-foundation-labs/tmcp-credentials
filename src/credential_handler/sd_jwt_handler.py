from .base_handler import BaseCredentialHandler
from sd_jwt.issuer import SDJWTIssuer
from sd_jwt.holder import SDJWTHolder
from sd_jwt.verifier import SDJWTVerifier
from sd_jwt.common import SDObj
from jwcrypto.jwk import JWK


class SdJwtHandler(BaseCredentialHandler):
    """
    Credential handler for the SD-JWT format.
    """

    @property
    def format_name(self):
        return "sd-jwt"

    def issue_credential(self, user_claims, issuer_key, holder_key=None):
        sd_user_claims = {SDObj(key): value for key, value in user_claims.items()}
        issuer = SDJWTIssuer(sd_user_claims, issuer_key, holder_key)
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
        nonce = options.get("nonce")
        aud = options.get("aud")

        verifier = SDJWTVerifier(presentation, get_issuer_key_callback, aud, nonce)
        verified_payload = verifier.get_verified_payload()

        # TODO: implement binding and checking 'aud'

        return verified_payload

    def generate_keys(self):
        issuer_key = JWK.generate(kty="EC", crv="P-256")
        holder_key = JWK.generate(kty="EC", crv="P-256")
        issuer_public_key = JWK.from_json(issuer_key.export_public())
        return {
            "issuer_key": issuer_key,
            "holder_key": holder_key,
            "issuer_public_key": issuer_public_key,
        }

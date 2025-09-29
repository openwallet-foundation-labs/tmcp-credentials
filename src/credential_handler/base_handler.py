from abc import ABC, abstractmethod


class BaseCredentialHandler(ABC):
    """
    Abstract base class for credential handlers.
    Defines the interface for issuing, presenting, and verifying credentials.
    """

    @property
    @abstractmethod
    def format_name(self):
        """The name of the credential format this handler supports (e.g., 'sd-jwt')."""
        pass

    @abstractmethod
    def issue_credential(self, user_claims, issuer_key, holder_key=None):
        """Issues a credential."""
        pass

    @abstractmethod
    def create_presentation(
        self, credential, disclosed_claims, holder_key=None, options=None
    ):
        """Creates a presentation from a credential."""
        pass

    @abstractmethod
    def verify_presentation(self, presentation, get_issuer_key_callback, options=None):
        """Verifies a credential presentation."""
        pass

    @abstractmethod
    def generate_keys(self):
        """Generates the necessary keys for the credential format."""
        pass

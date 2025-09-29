class CredentialHandler:
    """
    Main credential handler that dispatches to format-specific sub-handlers.
    """

    def __init__(self):
        self._handlers = {}

    def register_handler(self, handler):
        """Registers a new credential format handler."""
        format_name = handler.format_name
        if format_name in self._handlers:
            raise ValueError(
                f"Handler for format '{format_name}' is already registered."
            )
        self._handlers[format_name] = handler
        print(f"Handler for format '{format_name}' registered.")

    def get_supported_formats(self):
        """Returns a list of supported credential formats."""
        return list(self._handlers.keys())

    def _get_handler(self, cred_format):
        """Retrieves the handler for a given format."""
        if cred_format not in self._handlers:
            raise ValueError(
                f"Unsupported credential format: '{cred_format}'. Supported formats: {self.get_supported_formats()}"
            )
        return self._handlers[cred_format]

    def issue(self, cred_format, *args, **kwargs):
        handler = self._get_handler(cred_format)
        return handler.issue_credential(*args, **kwargs)

    def create_presentation(self, cred_format, *args, **kwargs):
        handler = self._get_handler(cred_format)
        return handler.create_presentation(*args, **kwargs)

    def verify(self, cred_format, *args, **kwargs):
        handler = self._get_handler(cred_format)
        return handler.verify_presentation(*args, **kwargs)

    def generate_keys(self, cred_format):
        handler = self._get_handler(cred_format)
        return handler.generate_keys()

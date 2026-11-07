"""OAuth authentication boundary.

Do not add personal access token support: the intended integration is the
official OAuth 2.0 flow. Exact endpoints, scopes, callback requirements, and
credential storage must be verified against current Oura documentation before
implementation.
"""


class OAuthNotConfigured(NotImplementedError):
    """Raised until the supported Oura OAuth flow is configured."""

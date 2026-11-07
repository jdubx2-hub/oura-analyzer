"""Oura OAuth 2.0 authorization-code flow with PKCE.

Credentials and rotating tokens are stored in the operating-system keychain
through the `keyring` package. No token or secret is written into the project
directory or printed to the terminal.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
import keyring

SERVICE_NAME = "oura-analyzer"
AUTHORIZE_URL = "https://cloud.ouraring.com/oauth/authorize"
TOKEN_URL = "https://api.ouraring.com/oauth/token"
REDIRECT_URI = "http://localhost:8765/callback"
CALLBACK_PATH = "/callback"
SCOPES = ("daily",)


class OAuthError(RuntimeError):
    """Raised when Oura authorization or token exchange fails."""


def _keyring_get(name: str) -> str | None:
    return keyring.get_password(SERVICE_NAME, name)


def _keyring_set(name: str, value: str) -> None:
    keyring.set_password(SERVICE_NAME, name, value)


def _keyring_delete(name: str) -> None:
    try:
        keyring.delete_password(SERVICE_NAME, name)
    except keyring.errors.PasswordDeleteError:
        pass


def _pkce_pair() -> tuple[str, str]:
    """Return a PKCE verifier and its S256 challenge."""
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def _token_request(data: dict[str, str]) -> dict:
    response = httpx.post(
        TOKEN_URL,
        data=data,
        headers={"Accept": "application/json", "User-Agent": "oura-analyzer/0.2.0"},
        timeout=30.0,
    )
    if response.is_error:
        try:
            detail = response.json().get("detail") or response.json().get("error_description")
        except (ValueError, AttributeError):
            detail = response.text[:500]
        raise OAuthError(f"Oura token request failed ({response.status_code}): {detail}")
    return response.json()


def _save_token_response(token: dict) -> None:
    """Persist rotated refresh token before the access token."""
    refresh_token = token.get("refresh_token")
    if refresh_token:
        _keyring_set("refresh_token", refresh_token)
    access_token = token.get("access_token")
    if not access_token:
        raise OAuthError("Oura's token response did not include an access_token.")
    _keyring_set("access_token", access_token)
    expires_at = time.time() + int(token.get("expires_in", 0))
    _keyring_set("expires_at", str(expires_at))
    if token.get("scope"):
        _keyring_set("granted_scope", token["scope"])


def _callback_handler(result: dict, completed: threading.Event, expected_state: str):
    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path != CALLBACK_PATH:
                self.send_error(404)
                return

            params = parse_qs(parsed.query)
            returned_state = params.get("state", [""])[0]
            if not hmac.compare_digest(returned_state, expected_state):
                result["error"] = "OAuth state did not match. Rejecting callback."
                status, message = 400, "Authorization failed: invalid state. You can close this tab."
            elif params.get("error"):
                result["error"] = params.get("error_description", params["error"])[0]
                status, message = 400, "Authorization was not completed. You can close this tab."
            elif not params.get("code"):
                result["error"] = "Oura callback did not contain an authorization code."
                status, message = 400, "Authorization failed: no code received. You can close this tab."
            else:
                result["code"] = params["code"][0]
                status, message = 200, "Oura authorization received. You can return to Terminal."

            body = (
                "<!doctype html><html><head><title>oura-analyzer</title></head>"
                f"<body><h2>{message}</h2></body></html>"
            ).encode()
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            completed.set()

        def log_message(self, format: str, *args) -> None:
            return

    return CallbackHandler


def login(client_id: str, client_secret: str, timeout_seconds: int = 300) -> None:
    """Run the local OAuth callback flow and save credentials/tokens to Keychain."""
    state = secrets.token_urlsafe(32)
    verifier, challenge = _pkce_pair()
    result: dict[str, str] = {}
    completed = threading.Event()

    handler = _callback_handler(result, completed, state)
    try:
        server = HTTPServer(("localhost", 8765), handler)
    except OSError as exc:
        raise OAuthError(
            "Could not start the callback server on localhost:8765. "
            "Is another process already using port 8765?"
        ) from exc

    server.timeout = 0.5
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    authorization_url = f"{AUTHORIZE_URL}?{urlencode(params)}"

    try:
        print("Opening Oura authorization in your browser...")
        print(f"If it does not open, visit:\n{authorization_url}")
        webbrowser.open(authorization_url)
        print(f"Waiting for Oura to redirect to {REDIRECT_URI} ...")
        if not completed.wait(timeout_seconds):
            raise OAuthError("Timed out waiting for Oura authorization callback.")
        if result.get("error"):
            raise OAuthError(result["error"])

        token = _token_request(
            {
                "grant_type": "authorization_code",
                "code": result["code"],
                "redirect_uri": REDIRECT_URI,
                "client_id": client_id,
                "client_secret": client_secret,
                "code_verifier": verifier,
            }
        )
        _keyring_set("client_id", client_id)
        _keyring_set("client_secret", client_secret)
        _save_token_response(token)
        print("Authorization successful. Credentials saved to your OS keychain.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def get_access_token() -> str:
    """Return a usable access token, refreshing it when it is close to expiry."""
    access_token = _keyring_get("access_token")
    refresh_token = _keyring_get("refresh_token")
    expires_at = float(_keyring_get("expires_at") or "0")

    if access_token and time.time() < expires_at - 60:
        return access_token

    if not refresh_token:
        raise OAuthError("No saved Oura authorization. Run: uv run oura auth login")

    client_id = _keyring_get("client_id")
    client_secret = _keyring_get("client_secret")
    if not client_id or not client_secret:
        raise OAuthError("Oura OAuth client credentials are missing. Run: uv run oura auth login")

    token = _token_request(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }
    )
    _save_token_response(token)
    return token["access_token"]


def auth_status() -> dict[str, str | bool]:
    """Return non-secret information about the saved authorization."""
    return {
        "authorized": bool(_keyring_get("access_token") and _keyring_get("refresh_token")),
        "granted_scope": _keyring_get("granted_scope") or "",
        "keychain_client_configured": bool(
            _keyring_get("client_id") and _keyring_get("client_secret")
        ),
    }

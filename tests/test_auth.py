import base64
import hashlib

from oura_analyzer.auth import _pkce_pair


def test_pkce_pair_is_valid_s256_pair() -> None:
    verifier, challenge = _pkce_pair()
    expected = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
    expected = expected.decode().rstrip("=")
    assert 43 <= len(verifier) <= 128
    assert challenge == expected

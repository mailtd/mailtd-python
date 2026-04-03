from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import Token

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Tokens:
    def __init__(self, client: _BaseClient):
        self._client = client

    def list(self) -> List[Token]:
        """List all API tokens."""
        data = self._client._request("GET", "/api/user/tokens")
        return [_from_dict(Token, t) for t in data["tokens"]]

    def create(self, name: Optional[str] = None) -> dict:
        """Create an API token. The full token value is only returned once."""
        return self._client._request("POST", "/api/user/tokens", json={"name": name or "API Token"})

    def revoke(self, token_id: str) -> None:
        """Revoke an API token."""
        self._client._request("DELETE", f"/api/user/tokens/{token_id}")

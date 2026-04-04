from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import Domain, AccountInfo, CreateAccountResult, LoginResult

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Accounts:
    def __init__(self, client: _BaseClient):
        self._client = client

    def list_domains(self) -> List[Domain]:
        """List available system domains for creating mailboxes."""
        data = self._client._request("GET", "/api/domains")
        return [_from_dict(Domain, d) for d in data["domains"]]

    def create(
        self,
        address: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
    ) -> CreateAccountResult:
        """Create a new mailbox."""
        body: dict = {"address": address}
        if password:
            body["password"] = password
        if auth_key:
            body["auth_key"] = auth_key
        return _from_dict(CreateAccountResult, self._client._request("POST", "/api/accounts", json=body))

    def login(
        self,
        address: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
    ) -> LoginResult:
        """Sign in to an existing mailbox. Returns a JWT token."""
        body: dict = {"address": address}
        if password:
            body["password"] = password
        if auth_key:
            body["auth_key"] = auth_key
        return _from_dict(LoginResult, self._client._request("POST", "/api/token", json=body))

    def get(self, account_id: str) -> AccountInfo:
        """Get mailbox info by account ID."""
        return _from_dict(AccountInfo, self._client._request("GET", f"/api/accounts/{account_id}"))

    def delete(self, account_id: str) -> None:
        """Delete a mailbox and all its emails permanently."""
        self._client._request("DELETE", f"/api/accounts/{account_id}")

    def reset_password(
        self,
        account_id: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
    ) -> None:
        """Reset a mailbox password. Invalidates all existing JWTs."""
        body: dict = {}
        if password:
            body["password"] = password
        if auth_key:
            body["auth_key"] = auth_key
        self._client._request("PUT", f"/api/accounts/{account_id}/reset-password", json=body)

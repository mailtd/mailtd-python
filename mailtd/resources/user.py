from __future__ import annotations

from typing import Optional, List, Tuple, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import ProUser, Account, EmailSummary

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class User:
    def __init__(self, client: _BaseClient):
        self._client = client

    def get_me(self) -> ProUser:
        """Get the authenticated Pro user's profile."""
        return _from_dict(ProUser, self._client._request("GET", "/api/user/me"))

    def list_accounts(self) -> List[Account]:
        """List all mailboxes under the Pro account."""
        data = self._client._request("GET", "/api/user/accounts")
        return [_from_dict(Account, a) for a in data["accounts"]]

    def delete_account(self, account_id: str) -> None:
        """Delete a mailbox under the Pro account."""
        self._client._request("DELETE", f"/api/user/accounts/{account_id}")

    def reset_account_password(
        self,
        account_id: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
    ) -> None:
        """Reset a mailbox password under the Pro account."""
        body: dict = {}
        if password:
            body["password"] = password
        if auth_key:
            body["auth_key"] = auth_key
        self._client._request("PUT", f"/api/user/accounts/{account_id}/reset-password", json=body)

    def list_account_messages(
        self, account_id: str, *, page: int = 1
    ) -> Tuple[List[EmailSummary], int]:
        """List messages for a specific mailbox under the Pro account."""
        data = self._client._request("GET", f"/api/user/accounts/{account_id}/messages", params={"page": page})
        msgs = [_from_dict(EmailSummary, m) for m in data["messages"]]
        return msgs, data["page"]

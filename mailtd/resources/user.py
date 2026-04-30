from __future__ import annotations

from typing import Optional, List, Tuple, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.crypto import _build_reset_password_body
from mailtd.types import ProUser, Account, AccountPage, EmailSummary

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class User:
    def __init__(self, client: _BaseClient):
        self._client = client

    def get_me(self) -> ProUser:
        """Get the authenticated Pro user's profile."""
        return _from_dict(ProUser, self._client._request("GET", "/api/user/me"))

    def list_accounts_page(self, *, cursor: str = "") -> AccountPage:
        """List a page of mailboxes with cursor-based pagination."""
        params = {}
        if cursor:
            params["cursor"] = cursor
        data = self._client._request("GET", "/api/user/accounts", params=params or None)
        accounts = [_from_dict(Account, a) for a in data["accounts"]]
        return AccountPage(accounts=accounts, next_cursor=data.get("next_cursor", ""))

    def list_accounts(self) -> List[Account]:
        """List all mailboxes under the Pro account.

        .. deprecated:: Use list_accounts_page() for cursor-based pagination.
        """
        return self.list_accounts_page().accounts

    def delete_account(self, account_id: str) -> None:
        """Delete a mailbox under the Pro account.

        Args:
            account_id: Account ID (UUID) or email address.
        """
        self._client._request("DELETE", f"/api/user/accounts/{account_id}")

    def reset_account_password(
        self,
        account_id: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None:
        """Reset a mailbox password under the Pro account.

        If ``password`` is supplied the SDK derives the auth_key locally; for
        UUID account IDs ``address`` must be provided so the SDK can compute
        the Argon2 salt.

        Args:
            account_id: Account ID (UUID) or email address.
            password: New password (locally derived to auth_key).
            auth_key: New auth_key (sent as-is, takes precedence over password).
            address: Required when account_id is a UUID and password is used.
        """
        body = _build_reset_password_body(
            account_id, password=password, auth_key=auth_key, address=address
        )
        self._client._request("PUT", f"/api/user/accounts/{account_id}/reset-password", json=body)

    def list_account_messages(
        self, account_id: str, *, page: int = 1
    ) -> Tuple[List[EmailSummary], int]:
        """List messages for a specific mailbox under the Pro account.

        Args:
            account_id: Account ID (UUID) or email address.
        """
        data = self._client._request("GET", f"/api/user/accounts/{account_id}/messages", params={"page": page})
        msgs = [_from_dict(EmailSummary, m) for m in data["messages"]]
        return msgs, data["page"]

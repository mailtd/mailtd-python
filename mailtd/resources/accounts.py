from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.crypto import _build_reset_password_body, derive_auth_key
from mailtd.types import Domain, AccountInfo, CreateAccountResult

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


@dataclass
class LoginResult:
    """Response from :meth:`Accounts.login`."""

    id: str
    address: str
    token: str


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
        """Create a new mailbox.

        If ``auth_key`` is set it is sent as-is. Otherwise, if ``password`` is
        set the SDK derives the auth_key locally via Argon2id (see
        :func:`mailtd.crypto.derive_auth_key`); the password never leaves the
        client process.
        """
        body: dict = {"address": address}
        if auth_key is not None:
            body["auth_key"] = auth_key
        elif password is not None:
            body["auth_key"] = derive_auth_key(address, password)

        data = self._client._request("POST", "/api/accounts", json=body)
        return _from_dict(CreateAccountResult, data)

    def login(
        self,
        address: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
    ) -> LoginResult:
        """Authenticate a mailbox and return a mailbox-scoped JWT.

        When ``password`` is supplied the SDK derives the auth_key locally; the
        password never leaves the client process.

        The returned ``token`` grants access to ``/api/accounts/{id}/*``
        endpoints when addressed by UUID. Use it with a fresh client::

            res = client.accounts.login(addr, password=pw)
            mb = MailTD(res.token)
            msgs = mb.messages.list(res.id)
        """
        if auth_key is None and password is None:
            raise ValueError("mailtd: login requires password or auth_key")
        body: dict = {"address": address}
        if auth_key is not None:
            body["auth_key"] = auth_key
        else:
            body["auth_key"] = derive_auth_key(address, password)  # type: ignore[arg-type]
        data = self._client._request("POST", "/api/token", json=body)
        return LoginResult(id=data["id"], address=data["address"], token=data["token"])

    def get(self, account_id: str) -> AccountInfo:
        """Get mailbox info.

        Args:
            account_id: Account ID (UUID) or email address.
        """
        return _from_dict(AccountInfo, self._client._request("GET", f"/api/accounts/{account_id}"))

    def delete(self, account_id: str) -> None:
        """Delete a mailbox and all its emails permanently.

        Args:
            account_id: Account ID (UUID) or email address.
        """
        self._client._request("DELETE", f"/api/accounts/{account_id}")

    def reset_password(
        self,
        account_id: str,
        *,
        password: Optional[str] = None,
        auth_key: Optional[str] = None,
        address: Optional[str] = None,
    ) -> None:
        """Reset a mailbox password. Invalidates all existing tokens.

        If ``password`` is supplied the SDK derives the auth_key locally; the
        derivation needs the mailbox's email address. If ``account_id`` is
        already an email it is used directly, otherwise ``address`` must be
        supplied.

        Args:
            account_id: Account ID (UUID) or email address.
            password: New password (locally derived to auth_key).
            auth_key: New auth_key (sent as-is, takes precedence over password).
            address: Required when account_id is a UUID and password is used.
        """
        body = _build_reset_password_body(
            account_id, password=password, auth_key=auth_key, address=address
        )
        self._client._request("PUT", f"/api/accounts/{account_id}/reset-password", json=body)

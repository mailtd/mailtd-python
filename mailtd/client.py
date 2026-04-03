from __future__ import annotations

from typing import Any, Optional, Dict, Type, TypeVar

import httpx

T = TypeVar("T")


class APIError(Exception):
    """Raised when the Mail.td API returns an error response."""

    def __init__(self, status: int, code: str):
        self.status = status
        self.code = code
        super().__init__(f"{code} (HTTP {status})")


def _from_dict(cls: Type[T], data: dict) -> T:
    """Convert a dict to a dataclass, handling field name mappings."""
    import dataclasses

    fields = {f.name for f in dataclasses.fields(cls)}
    kwargs = {}
    for key, value in data.items():
        # Map 'from' to 'from_' for Python keyword collision
        field_name = f"{key}_" if key == "from" else key
        if field_name in fields:
            kwargs[field_name] = value
    return cls(**kwargs)


class _BaseClient:
    def __init__(self, token: str, base_url: str = "https://api.mail.td"):
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._http = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[dict] = None,
        params: Optional[Dict[str, Any]] = None,
        raw: bool = False,
    ) -> Any:
        resp = self._http.request(method, path, json=json, params=params)
        if resp.status_code >= 400:
            try:
                body = resp.json()
                code = body.get("error", f"http_{resp.status_code}")
            except Exception:
                code = f"http_{resp.status_code}"
            raise APIError(resp.status_code, code)
        if resp.status_code == 204:
            return None
        if raw:
            return resp.content
        return resp.json()

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


from mailtd.resources.accounts import Accounts
from mailtd.resources.messages import Messages
from mailtd.resources.domains import Domains
from mailtd.resources.webhooks import Webhooks
from mailtd.resources.tokens import Tokens
from mailtd.resources.sandbox import Sandbox
from mailtd.resources.billing import Billing
from mailtd.resources.user import User


class MailTD(_BaseClient):
    """
    Official Mail.td API client.

    Usage::

        from mailtd import MailTD

        client = MailTD("tm_pro_...")
        account = client.accounts.create("test@mail.td", password="pass123")
        messages = client.messages.list(account.id)
    """

    def __init__(self, token: str, base_url: str = "https://api.mail.td"):
        super().__init__(token, base_url)
        self.accounts = Accounts(self)
        self.messages = Messages(self)
        self.domains = Domains(self)
        self.webhooks = Webhooks(self)
        self.tokens = Tokens(self)
        self.sandbox = Sandbox(self)
        self.billing = Billing(self)
        self.user = User(self)

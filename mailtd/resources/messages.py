from __future__ import annotations

from typing import Optional, List, Tuple, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import EmailSummary, EmailDetail, Attachment

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Messages:
    def __init__(self, client: _BaseClient):
        self._client = client

    def list(self, account_id: str, *, page: int = 1) -> Tuple[List[EmailSummary], int]:
        """List messages. Returns (messages, page). Up to 30 per page."""
        data = self._client._request("GET", f"/api/accounts/{account_id}/messages", params={"page": page})
        msgs = [_from_dict(EmailSummary, m) for m in data["messages"]]
        return msgs, data["page"]

    def get(self, account_id: str, message_id: str) -> EmailDetail:
        """Get a single message with full body and attachment metadata."""
        data = self._client._request("GET", f"/api/accounts/{account_id}/messages/{message_id}")
        data["attachments"] = [_from_dict(Attachment, a) for a in data.get("attachments", [])]
        return _from_dict(EmailDetail, data)

    def delete(self, account_id: str, message_id: str) -> None:
        """Delete a single message."""
        self._client._request("DELETE", f"/api/accounts/{account_id}/messages/{message_id}")

    def get_source(self, account_id: str, message_id: str) -> bytes:
        """Download raw EML source of a message."""
        return self._client._request("GET", f"/api/accounts/{account_id}/messages/{message_id}/source", raw=True)

    def mark_as_read(self, account_id: str, message_id: str) -> None:
        """Mark a single message as read. Idempotent."""
        self._client._request("PUT", f"/api/accounts/{account_id}/messages/{message_id}/read")

    def batch_mark_as_read(
        self,
        account_id: str,
        *,
        ids: Optional[List[str]] = None,
        all: bool = False,
    ) -> int:
        """Batch mark messages as read. Returns count of updated messages."""
        body: dict = {}
        if ids:
            body["ids"] = ids
        if all:
            body["all"] = True
        data = self._client._request("PUT", f"/api/accounts/{account_id}/messages/read", json=body)
        return data["updated"]

    def get_attachment(self, account_id: str, message_id: str, index: int) -> bytes:
        """Download an attachment by its zero-based index."""
        return self._client._request("GET", f"/api/accounts/{account_id}/messages/{message_id}/attachments/{index}", raw=True)

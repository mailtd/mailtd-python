from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import SandboxInfo, SandboxEmailSummary, EmailDetail, Attachment

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Sandbox:
    def __init__(self, client: _BaseClient):
        self._client = client

    def get_info(self) -> SandboxInfo:
        """Get sandbox status and SMTP credentials."""
        return _from_dict(SandboxInfo, self._client._request("GET", "/api/user/sandbox"))

    def list_messages(self, *, page: int = 1) -> Tuple[List[SandboxEmailSummary], int]:
        """List sandbox messages. Returns (messages, page)."""
        data = self._client._request("GET", "/api/user/sandbox/messages", params={"page": page})
        msgs = [_from_dict(SandboxEmailSummary, m) for m in data["messages"]]
        return msgs, data["page"]

    def get_message(self, message_id: str) -> EmailDetail:
        """Get a single sandbox message."""
        data = self._client._request("GET", f"/api/user/sandbox/messages/{message_id}")
        data["attachments"] = [_from_dict(Attachment, a) for a in data.get("attachments", [])]
        return _from_dict(EmailDetail, data)

    def delete_message(self, message_id: str) -> None:
        """Delete a single sandbox message."""
        self._client._request("DELETE", f"/api/user/sandbox/messages/{message_id}")

    def purge_messages(self) -> int:
        """Purge all sandbox messages. Returns count of deleted messages."""
        data = self._client._request("DELETE", "/api/user/sandbox/messages")
        return data["deleted"]

    def get_message_source(self, message_id: str) -> bytes:
        """Download raw EML source of a sandbox message."""
        return self._client._request("GET", f"/api/user/sandbox/messages/{message_id}/source", raw=True)

    def get_attachment(self, message_id: str, index: int) -> bytes:
        """Download an attachment from a sandbox message."""
        return self._client._request("GET", f"/api/user/sandbox/messages/{message_id}/attachments/{index}", raw=True)

from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import Webhook, WebhookDelivery

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Webhooks:
    def __init__(self, client: _BaseClient):
        self._client = client

    def list(self) -> List[Webhook]:
        """List all webhooks."""
        data = self._client._request("GET", "/api/user/webhooks")
        return [_from_dict(Webhook, w) for w in data["webhooks"]]

    def create(self, url: str, *, events: Optional[List[str]] = None) -> Webhook:
        """Create a webhook. URL must be HTTPS. Max 1 per user."""
        body: dict = {"url": url}
        if events is not None:
            body["events"] = events
        return _from_dict(Webhook, self._client._request("POST", "/api/user/webhooks", json=body))

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook."""
        self._client._request("DELETE", f"/api/user/webhooks/{webhook_id}")

    def rotate_secret(self, webhook_id: str) -> dict:
        """Rotate webhook signing secret. Also resets failure count."""
        return self._client._request("POST", f"/api/user/webhooks/{webhook_id}/rotate")

    def list_deliveries(self, webhook_id: str) -> List[WebhookDelivery]:
        """List delivery attempts for a webhook (last 20)."""
        data = self._client._request("GET", f"/api/user/webhooks/{webhook_id}/deliveries")
        return [_from_dict(WebhookDelivery, d) for d in data["deliveries"]]

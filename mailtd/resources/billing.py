from __future__ import annotations

from typing import TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import SubscriptionStatus, ScheduledChange

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Billing:
    def __init__(self, client: _BaseClient):
        self._client = client

    def get_status(self) -> SubscriptionStatus:
        """Get subscription status."""
        data = self._client._request("GET", "/api/user/subscription/status")
        sca = data.get("scheduled_cancel_at")
        if isinstance(sca, dict):
            data["scheduled_cancel_at"] = _from_dict(ScheduledChange, sca)
        return _from_dict(SubscriptionStatus, data)

    def cancel(self) -> dict:
        """Cancel subscription. Within 14 days: full refund. After: cancel at end of period."""
        return self._client._request("POST", "/api/user/subscription/cancel")

    def resume(self) -> dict:
        """Resume a scheduled cancellation."""
        return self._client._request("POST", "/api/user/subscription/resume")

    def get_portal_url(self) -> str:
        """Get billing portal URL for managing payment methods."""
        data = self._client._request("POST", "/api/user/billing/portal")
        return data["url"]

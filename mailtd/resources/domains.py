from __future__ import annotations

from typing import List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.types import ProDomain, DNSRecord

if TYPE_CHECKING:
    from mailtd.client import _BaseClient


class Domains:
    def __init__(self, client: _BaseClient):
        self._client = client

    def list(self) -> List[ProDomain]:
        """List custom domains."""
        data = self._client._request("GET", "/api/user/domains")
        return [_from_dict(ProDomain, d) for d in data["domains"]]

    def create(self, domain: str) -> dict:
        """Add a custom domain. Returns DNS records for verification."""
        return self._client._request("POST", "/api/user/domains", json={"domain": domain})

    def verify(self, domain_id: str) -> dict:
        """Verify domain DNS configuration."""
        return self._client._request("POST", f"/api/user/domains/{domain_id}/verify")

    def delete(self, domain_id: str) -> None:
        """Delete a custom domain."""
        self._client._request("DELETE", f"/api/user/domains/{domain_id}")

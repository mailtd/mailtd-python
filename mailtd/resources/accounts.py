from __future__ import annotations

from typing import Optional, List, TYPE_CHECKING

from mailtd.client import _from_dict
from mailtd.pow import solve_pow
from mailtd.types import Domain, AccountInfo, CreateAccountResult, LoginResult

if TYPE_CHECKING:
    from mailtd.client import _BaseClient

_DEFAULT_DIFFICULTY = 15


class Accounts:
    def __init__(self, client: _BaseClient):
        self._client = client
        self._cached_difficulty = _DEFAULT_DIFFICULTY

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

        For free users (no API token), a Proof-of-Work challenge is solved
        locally before the request is sent. If the server requires a higher
        difficulty, the challenge is re-solved once automatically.
        """
        body: dict = {"address": address}
        if password:
            body["password"] = password
        if auth_key:
            body["auth_key"] = auth_key

        # Pro users (token set) skip PoW
        if self._client._token:
            return _from_dict(
                CreateAccountResult,
                self._client._request("POST", "/api/accounts", json=body),
            )

        # Normalize address for PoW — server verifies against lowercased form.
        pow_address = address.lower().strip()

        # Free user: solve PoW locally, starting from cached difficulty.
        pow_solution = solve_pow(pow_address, self._cached_difficulty)
        body["pow"] = pow_solution

        data = self._client._request("POST", "/api/accounts", json=body)

        # Handle step-up retry
        if isinstance(data, dict) and data.get("status") == "retry":
            new_difficulty = data["required_difficulty"]
            self._cached_difficulty = new_difficulty
            step_up_token = data["token"]
            pow_solution = solve_pow(pow_address, new_difficulty)
            pow_solution["token"] = step_up_token
            body["pow"] = pow_solution
            data = self._client._request("POST", "/api/accounts", json=body)

        result = _from_dict(CreateAccountResult, data)
        if result.suggested_next_difficulty:
            self._cached_difficulty = result.suggested_next_difficulty
        return result

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

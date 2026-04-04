from __future__ import annotations
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class Domain:
    id: str
    domain: str
    default: bool
    sort_order: int


@dataclass
class AccountInfo:
    id: str
    address: str
    role: str
    quota: int
    used: int
    created_at: str


@dataclass
class Account:
    id: str
    address: str
    quota: int
    used: int
    created_at: str


@dataclass
class CreateAccountResult:
    id: str
    address: str
    token: str


@dataclass
class LoginResult:
    id: str
    address: str
    token: str


@dataclass
class Attachment:
    index: int
    filename: str
    content_type: str
    size: int


@dataclass
class EmailSummary:
    id: str
    sender: str
    from_: Optional[str]
    subject: Optional[str]
    preview_text: Optional[str]
    size: int
    is_read: bool
    created_at: str


@dataclass
class EmailDetail:
    id: str
    sender: str
    from_: Optional[str]
    subject: Optional[str]
    address: str
    size: int
    created_at: str
    text_body: Optional[str]
    html_body: Optional[str]
    attachments: List[Attachment]


@dataclass
class ProUser:
    id: str
    email: str
    plan: str
    role: str
    status: str
    max_accounts: int
    max_domains: int
    account_count: int
    domain_count: int
    created_at: str
    downgraded: bool


@dataclass
class ProDomain:
    id: str
    domain: str
    verify_status: str
    verify_token: str
    verified_at: Optional[str]
    mx_configured: bool
    created_at: str


@dataclass
class DNSRecord:
    type: str
    host: str
    value: str
    priority: Optional[int] = None
    ok: Optional[bool] = None


@dataclass
class Webhook:
    id: str
    url: str
    events: List[str]
    status: str
    created_at: str
    secret: Optional[str] = None
    failure_count: Optional[int] = None
    last_triggered_at: Optional[str] = None


@dataclass
class WebhookDelivery:
    id: str
    event_type: str
    event_id: str
    attempt: int
    created_at: str
    status_code: Optional[int] = None
    error: Optional[str] = None
    duration_ms: Optional[int] = None


@dataclass
class Token:
    id: str
    name: str
    created_at: str
    token: Optional[str] = None
    last_used_at: Optional[str] = None
    revoked_at: Optional[str] = None


@dataclass
class SandboxInfo:
    enabled: bool
    smtp_host: str
    smtp_port: int
    auth_method: str
    username: str
    note: str
    account_id: Optional[str] = None
    address: Optional[str] = None
    quota: Optional[int] = None
    used: Optional[int] = None


@dataclass
class SandboxEmailSummary:
    id: str
    sender: str
    from_: Optional[str]
    subject: Optional[str]
    preview_text: Optional[str]
    size: int
    created_at: str


@dataclass
class PoWSolution:
    t: int
    n: str
    d: int
    token: Optional[str] = None


@dataclass
class SubscriptionStatus:
    status: str
    cancel_mode: str
    scheduled_cancel_at: Optional[dict] = None

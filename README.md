# mailtd

[![PyPI version](https://img.shields.io/pypi/v/mailtd.svg)](https://pypi.org/project/mailtd/)
[![PyPI downloads](https://static.pepy.tech/badge/mailtd/month)](https://pepy.tech/project/mailtd)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Mail.td](https://mail.td) — the developer email platform for **temp mail**, **email testing**, and **SMTP sandbox**.

- **Temp Mail API** — Create and manage temporary email addresses programmatically
- **Email Testing** — Receive, inspect, and verify emails in your test suite
- **SMTP Sandbox** — Capture outbound emails in a safe sandbox environment without sending to real inboxes
- **Webhooks** — Get notified in real-time when emails arrive
- **Custom Domains** — Use your own domain for branded temporary mailboxes

## Install

```bash
pip install mailtd
```

Requires Python 3.9+.

## Quick Start

```python
from mailtd import MailTD

client = MailTD("td_...")

# Create a temporary email address
account = client.accounts.create("test@mail.td", password="mypassword")

# List messages
messages, page = client.messages.list(account.id)

# Get a message
msg = client.messages.get(account.id, messages[0].id)
print(msg.subject, msg.text_body)
```

## Use Cases

- **Automated testing** — Create temp mail addresses in CI/CD to test signup flows, OTP verification, and transactional emails
- **Email verification testing** — Validate that your app sends the right emails with the right content
- **SMTP sandbox** — Route your app's outbound SMTP to Mail.td sandbox to inspect emails without spamming real users
- **QA environments** — Give each test run its own mailbox, then tear it down

## Authentication

All API calls require a Pro API Token (`td_...`). Pass it when creating the client:

```python
# With a token string
client = MailTD("td_...")

# With custom base URL
client = MailTD("td_...", base_url="https://api.mail.td")

# As context manager
with MailTD("td_...") as client:
    messages, _ = client.messages.list(account_id)
```

## Resources

### Accounts

```python
domains = client.accounts.list_domains()
account = client.accounts.create("user@mail.td", password="pass123")
info = client.accounts.get(account_id)
client.accounts.reset_password(account_id, password="newpass")
client.accounts.delete(account_id)
```

### Messages

```python
messages, page = client.messages.list(account_id)
msg = client.messages.get(account_id, message_id)
eml = client.messages.get_source(account_id, message_id)
attachment = client.messages.get_attachment(account_id, message_id, 0)
client.messages.mark_as_read(account_id, message_id)
count = client.messages.batch_mark_as_read(account_id, all=True)
client.messages.delete(account_id, message_id)
```

### Domains (Pro)

```python
domains = client.domains.list()
result = client.domains.create("example.com")
status = client.domains.verify(domain_id)
client.domains.delete(domain_id)
```

### Webhooks (Pro)

```python
webhook = client.webhooks.create("https://example.com/hook", events=["email.received"])
deliveries = client.webhooks.list_deliveries(webhook.id)
secret = client.webhooks.rotate_secret(webhook.id)
client.webhooks.delete(webhook.id)
```

### Sandbox (Pro)

```python
info = client.sandbox.get_info()
messages, page = client.sandbox.list_messages()
msg = client.sandbox.get_message(message_id)
deleted = client.sandbox.purge_messages()
```

### Tokens (Pro)

```python
result = client.tokens.create("CI Token")
tokens = client.tokens.list()
client.tokens.revoke(token_id)
```

### Billing (Pro)

```python
status = client.billing.get_status()
client.billing.cancel()
client.billing.resume()
url = client.billing.get_portal_url()
```

### User (Pro)

```python
me = client.user.get_me()
accounts = client.user.list_accounts()
client.user.delete_account(account_id)
client.user.reset_account_password(account_id, password="newpass")
messages, page = client.user.list_account_messages(account_id)
```

## Error Handling

```python
from mailtd import MailTD, APIError

try:
    client.accounts.create("taken@mail.td", password="...")
except APIError as e:
    print(e.status)  # 409
    print(e.code)    # "address_taken"
```

## Links

- [Website](https://mail.td) — Create temp mail, email testing, SMTP sandbox
- [API Documentation](https://docs.mail.td) — Full API reference
- [Node.js SDK](https://www.npmjs.com/package/mailtd) — `npm install mailtd`
- [Go SDK](https://github.com/mailtd/mailtd-go) — `go get github.com/mailtd/mailtd-go`
- [CLI](https://github.com/mailtd/mailcx-cli) — Command-line tool

## License

MIT

# mailtd

Official Python SDK for the [Mail.td](https://mail.td) developer email platform.

## Install

```bash
pip install mailtd
```

Requires Python 3.9+.

## Quick Start

```python
from mailtd import MailTD

client = MailTD("tm_pro_...")

# Create a mailbox
account = client.accounts.create("test@mail.td", password="mypassword")

# List messages
messages, page = client.messages.list(account.id)

# Get a message
msg = client.messages.get(account.id, messages[0].id)
print(msg.subject, msg.text_body)
```

## Authentication

```python
# With a Pro API token
client = MailTD("tm_pro_...")

# With custom base URL
client = MailTD("tm_pro_...", base_url="https://api.mail.td")

# As context manager
with MailTD("tm_pro_...") as client:
    messages, _ = client.messages.list(account_id)
```

## Resources

### Accounts

```python
domains = client.accounts.list_domains()
challenge = client.accounts.get_challenge()
account = client.accounts.create("user@mail.td", password="pass123")
result = client.accounts.login("user@mail.td", password="pass123")
info = client.accounts.get(account_id)
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

## Error Handling

```python
from mailtd import MailTD, APIError

try:
    client.accounts.create("taken@mail.td", password="...")
except APIError as e:
    print(e.status)  # 409
    print(e.code)    # "address_already_exists"
```

## License

MIT

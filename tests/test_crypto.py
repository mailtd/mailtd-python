"""Tests for client-side Argon2id derivation.

Vectors are computed by ``golang.org/x/crypto/argon2`` with the same
parameters; the Mail.td backend uses the exact same library. They have been
verified against the Go and Node SDKs, so a match here proves cross-impl
parameter alignment across all three SDKs and the backend.
"""

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

from mailtd import MailTD
from mailtd.crypto import _build_reset_password_body, derive_auth_key

VECTORS = [
    (
        "alice@mail.td",
        "password123",
        "2d0b5b1cd63138ba6e5b13777000e55b5dcd8ab4286f16d2fdd3aae8948c6bcf",
    ),
    # Verifies salt = SHA256(lower(trim(address))).
    (
        "BOB@mail.td  ",
        "P@ssw0rd!",
        "5c35127b2175a8aadd1fbb16ccca66701d34b78f1f96e7caa51774159ac41060",
    ),
]


class CapturingHandler(BaseHTTPRequestHandler):
    captured = {"path": None, "method": None, "body": None}

    def _read(self):
        n = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(n) if n else b""

    def _respond(self, status, payload=None):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        body = b"" if payload is None else json.dumps(payload).encode()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_POST(self):
        raw = self._read()
        CapturingHandler.captured = {
            "path": self.path,
            "method": "POST",
            "body": json.loads(raw) if raw else None,
        }
        if self.path == "/api/accounts":
            self._respond(
                200,
                {
                    "id": "00000000-0000-0000-0000-000000000000",
                    "address": "alice@mail.td",
                    "token": "x",
                },
            )
        elif self.path == "/api/token":
            self._respond(
                200,
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "address": "alice@mail.td",
                    "token": "jwt.x.y",
                },
            )
        else:
            self._respond(204)

    def do_PUT(self):
        raw = self._read()
        CapturingHandler.captured = {
            "path": self.path,
            "method": "PUT",
            "body": json.loads(raw) if raw else None,
        }
        self._respond(204)

    def log_message(self, *args, **kw):
        pass


class _Server:
    def __enter__(self):
        self.httpd = HTTPServer(("127.0.0.1", 0), CapturingHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        port = self.httpd.server_address[1]
        self.base_url = f"http://127.0.0.1:{port}"
        CapturingHandler.captured = {"path": None, "method": None, "body": None}
        return self

    def __exit__(self, *args):
        self.httpd.shutdown()
        self.httpd.server_close()


class TestDeriveAuthKey(unittest.TestCase):
    def test_known_vectors(self):
        for address, password, expected in VECTORS:
            got = derive_auth_key(address, password)
            self.assertEqual(got, expected)
            self.assertEqual(len(got), 64)


class TestBuildResetPasswordBody(unittest.TestCase):
    def test_auth_key_passes_through(self):
        body = _build_reset_password_body(
            "anything", password=None, auth_key="a" * 64, address=None
        )
        self.assertEqual(body, {"auth_key": "a" * 64})

    def test_password_with_email_id_derives(self):
        body = _build_reset_password_body(
            "alice@mail.td", password="password123", auth_key=None, address=None
        )
        self.assertEqual(body, {"auth_key": VECTORS[0][2]})

    def test_password_with_uuid_no_address_raises(self):
        with self.assertRaisesRegex(ValueError, "address is required"):
            _build_reset_password_body(
                "11111111-1111-1111-1111-111111111111",
                password="password123",
                auth_key=None,
                address=None,
            )

    def test_password_with_uuid_and_address(self):
        body = _build_reset_password_body(
            "11111111-1111-1111-1111-111111111111",
            password="password123",
            auth_key=None,
            address="alice@mail.td",
        )
        self.assertEqual(body, {"auth_key": VECTORS[0][2]})

    def test_auth_key_wins_over_password(self):
        body = _build_reset_password_body(
            "alice@mail.td",
            password="password123",
            auth_key="b" * 64,
            address=None,
        )
        self.assertEqual(body, {"auth_key": "b" * 64})


class TestAccountsCreate(unittest.TestCase):
    def test_password_derives_locally_no_password_in_body(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            c.accounts.create("alice@mail.td", password="password123")
            cap = CapturingHandler.captured
            self.assertEqual(cap["path"], "/api/accounts")
            self.assertNotIn("password", cap["body"])
            self.assertEqual(cap["body"]["auth_key"], VECTORS[0][2])


class TestAccountsResetPassword(unittest.TestCase):
    def test_email_id_path(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            c.accounts.reset_password("alice@mail.td", password="password123")
            cap = CapturingHandler.captured
            self.assertNotIn("password", cap["body"])
            self.assertEqual(cap["body"]["auth_key"], VECTORS[0][2])

    def test_uuid_with_address(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            c.accounts.reset_password(
                "11111111-1111-1111-1111-111111111111",
                password="password123",
                address="alice@mail.td",
            )
            cap = CapturingHandler.captured
            self.assertEqual(cap["body"]["auth_key"], VECTORS[0][2])

    def test_uuid_without_address_raises(self):
        c = MailTD(base_url="http://unused")
        with self.assertRaisesRegex(ValueError, "address is required"):
            c.accounts.reset_password(
                "11111111-1111-1111-1111-111111111111",
                password="password123",
            )


class TestAccountsLogin(unittest.TestCase):
    def test_password_derives_locally(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            res = c.accounts.login("alice@mail.td", password="password123")
            cap = CapturingHandler.captured
            self.assertEqual(cap["path"], "/api/token")
            self.assertEqual(cap["method"], "POST")
            self.assertEqual(cap["body"]["address"], "alice@mail.td")
            self.assertEqual(cap["body"]["auth_key"], VECTORS[0][2])
            self.assertNotIn("password", cap["body"])
            self.assertEqual(res.token, "jwt.x.y")
            self.assertEqual(res.id, "11111111-1111-1111-1111-111111111111")

    def test_auth_key_takes_precedence(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            c.accounts.login("alice@mail.td", auth_key="a" * 64, password="ignored")
            cap = CapturingHandler.captured
            self.assertEqual(cap["body"]["auth_key"], "a" * 64)

    def test_no_creds_raises(self):
        c = MailTD(base_url="http://unused")
        with self.assertRaisesRegex(ValueError, "requires"):
            c.accounts.login("alice@mail.td")


class TestUserResetAccountPassword(unittest.TestCase):
    def test_password_derives_locally(self):
        with _Server() as srv:
            c = MailTD(base_url=srv.base_url)
            c.user.reset_account_password("alice@mail.td", password="password123")
            cap = CapturingHandler.captured
            self.assertNotIn("password", cap["body"])
            self.assertEqual(cap["body"]["auth_key"], VECTORS[0][2])


if __name__ == "__main__":
    unittest.main()

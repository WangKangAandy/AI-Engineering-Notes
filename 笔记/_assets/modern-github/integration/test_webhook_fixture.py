import hashlib
import hmac
import unittest

from webhook_fixture import Inbox, valid_signature


class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.secret = b"local-fixture-only"
        self.raw = b'{"action":"opened","repository":{"full_name":"YOUR_LOGIN/resource-nav"}}'
        self.signature = "sha256=" + hmac.new(self.secret, self.raw, hashlib.sha256).hexdigest()
        self.inbox = Inbox(self.secret, "YOUR_LOGIN/resource-nav")

    def deliver(self, **kwargs):
        args = dict(raw=self.raw, signature=self.signature, delivery="fixture-1", event="pull_request")
        args.update(kwargs)
        return self.inbox.receive(**args)

    def test_official_known_vector(self):
        self.assertTrue(valid_signature(
            b"Hello, World!", b"It's a Secret to Everybody",
            "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"))

    def test_tampered_bytes_and_wrong_secret(self):
        self.assertEqual(self.deliver(raw=self.raw + b" "), "bad-signature")
        self.assertFalse(valid_signature(self.raw, b"wrong-secret", self.signature))
        self.assertEqual(self.inbox.accepted, [])

    def test_same_delivery_has_one_effect(self):
        self.assertEqual(self.deliver(), "accepted")
        self.assertEqual(self.deliver(), "duplicate")
        self.assertEqual(len(self.inbox.accepted), 1)

    def test_changed_delivery_is_not_replay_protection(self):
        self.assertEqual(self.deliver(), "accepted")
        self.assertEqual(self.deliver(delivery="fixture-2"), "accepted")
        self.assertEqual(len(self.inbox.accepted), 2)

    def test_restart_loses_deduplication(self):
        self.deliver()
        self.inbox = Inbox(self.secret, "YOUR_LOGIN/resource-nav")
        self.assertEqual(self.deliver(), "accepted")

    def test_filter_before_effect(self):
        self.assertEqual(self.deliver(event="issues"), "ignored")
        self.assertEqual(self.deliver(event="pull_request"), "duplicate")
        self.assertEqual(self.inbox.accepted, [])

    def test_missing_signature(self):
        self.assertEqual(self.deliver(signature=""), "bad-signature")
        self.assertEqual(self.deliver(signature=None), "bad-signature")


if __name__ == "__main__":
    unittest.main(verbosity=2)

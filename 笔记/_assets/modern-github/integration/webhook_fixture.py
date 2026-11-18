"""Offline webhook validation lab; no HTTP server or GitHub writes."""
import hashlib
import hmac
import json


def valid_signature(raw: bytes, secret: bytes, signature: str) -> bool:
    expected = "sha256=" + hmac.new(secret, raw, hashlib.sha256).hexdigest()
    return isinstance(signature, str) and signature.isascii() and hmac.compare_digest(expected, signature)


class Inbox:
    """One-process teaching inbox; receipt and append are not a durable transaction."""

    def __init__(self, secret: bytes, repository: str):
        self.secret = secret
        self.repository = repository
        self.seen = set()
        self.accepted = []

    def receive(self, raw: bytes, signature: str, delivery: str, event: str) -> str:
        if not valid_signature(raw, self.secret, signature):
            return "bad-signature"
        if not delivery:
            return "missing-delivery"
        # Reserve the delivery before event/repository filtering. In a real
        # receiver this must be an atomic durable insert with a unique key.
        if delivery in self.seen:
            return "duplicate"
        self.seen.add(delivery)
        try:
            payload = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return "bad-json"
        if not isinstance(payload, dict):
            return "bad-payload"
        repo = payload.get("repository")
        if not isinstance(repo, dict) or repo.get("full_name") != self.repository:
            return "wrong-repository"
        if event != "pull_request" or payload.get("action") != "opened":
            return "ignored"
        # Only local memory changes here; no comment, network, or queue.
        self.accepted.append(payload)
        return "accepted"

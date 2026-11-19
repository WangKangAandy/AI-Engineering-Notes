"""Explicit GitHub App read/comment lab. Tokens remain in memory and are revoked."""
import argparse
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

import jwt


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "redirect refused", headers, fp)


API_OPENER = urllib.request.build_opener(NoRedirect)


def request(method, path, token, payload=None):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request("https://api.github.com" + path, data=data, method=method,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2026-03-10", "User-Agent": "resource-nav-app-lab",
                 "Content-Type": "application/json"})
    try:
        with API_OPENER.open(req, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        retry_after = exc.headers.get("Retry-After")
        remaining = exc.headers.get("X-RateLimit-Remaining")
        try:
            detail = json.loads(exc.read()).get("message", "")
        except (ValueError, OSError):
            detail = ""
        # Keep only server-provided diagnostic text; never print request headers.
        suffix = "; ".join(x for x in [detail, f"Retry-After={retry_after}" if retry_after else "",
                                         f"RateLimit-Remaining={remaining}" if remaining else ""] if x)
        raise RuntimeError(f"{method} {path}: HTTP {exc.code}" + (f"; {suffix}" if suffix else "")) from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["read", "comment"])
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--confirm", help="For comment, exact OWNER/REPO#NUMBER")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/resource-nav", args.repo) or args.pr <= 0:
        parser.error("Use your OWNER/resource-nav and a positive PR number")
    body = None
    if args.mode == "comment":
        if args.confirm != f"{args.repo}#{args.pr}" or args.body_file is None:
            parser.error("comment requires --body-file and exact --confirm OWNER/resource-nav#NUMBER")
        body = args.body_file.read_text(encoding="utf-8-sig")
        if not body.strip():
            parser.error("comment body must not be empty")
    now = int(time.time())
    app_jwt = jwt.encode({"iat": now - 60, "exp": now + 540,
                          "iss": os.environ["APP_CLIENT_ID"]},
                         Path(os.environ["APP_PRIVATE_KEY_PATH"]).read_bytes(), algorithm="RS256")
    _, app = request("GET", "/app", app_jwt)
    _, installation = request("GET", f"/repos/{args.repo}/installation", app_jwt)
    if installation["app_id"] != app["id"] or installation["account"]["login"].lower() != args.repo.split("/")[0].lower():
        raise RuntimeError("App or installation owner does not match")
    print("App:", app["slug"], "installation:", installation["id"], "target:", args.repo)
    _, result = request("POST", f'/app/installations/{installation["id"]}/access_tokens', app_jwt,
        {"repositories": ["resource-nav"], "permissions": {
            "pull_requests": "write" if args.mode == "comment" else "read"}})
    token = result["token"]
    try:
        print("Expires:", result["expires_at"], "permissions:", result["permissions"])
        _, accessible = request("GET", "/installation/repositories?per_page=100", token)
        names = [repo["full_name"].lower() for repo in accessible["repositories"]]
        if names != [args.repo.lower()]:
            raise RuntimeError("Token repository scope differs from the single requested repository")
        _, pr = request("GET", f"/repos/{args.repo}/pulls/{args.pr}", token)
        print("Read PR:", pr["html_url"], pr["title"])
        if args.mode == "comment":
            status, comment = request("POST", f"/repos/{args.repo}/issues/{args.pr}/comments", token, {"body": body})
            # Print the receipt before readback, so a subsequent failure does not hide the write.
            print("Write receipt:", status, comment["id"], comment["html_url"])
            _, observed = request("GET", f'/repos/{args.repo}/issues/comments/{comment["id"]}', token)
            if observed["body"] != body or observed["user"]["login"] != app["slug"] + "[bot]":
                raise RuntimeError("Comment readback body or identity differs; inspect receipt before retry")
            print("Readback verified:", observed["user"]["login"], observed["html_url"])
    finally:
        request("DELETE", "/installation/token", token)
        print("Installation token revoked")


if __name__ == "__main__":
    main()

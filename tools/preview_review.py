"""Read a point-in-time PR review status using the authenticated GitHub CLI.

This is a building block, not a preview publisher. A published label must be
refreshed and invalidated when the PR changes; this command alone cannot do so.
"""
import json
import re
import subprocess
import sys
import time
from datetime import datetime


REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REVIEW_STATES = {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}
WRITE_PERMISSIONS = {"admin", "maintain", "write"}


def review_evidence(reviews):
    """Canonical public review fields for comparison with the live API."""
    if not isinstance(reviews, list) or len(reviews) > 1000:
        raise ValueError('Invalid review list')
    evidence = []
    ids = set()
    for review in reviews:
        user = review.get('user') or {}
        number = review.get('id')
        fields = [review.get('state'), user.get('login'), user.get('type'),
                  review.get('commit_id'), review.get('submitted_at')]
        if (type(number) is not int or number < 1 or number in ids
                or fields[0] not in REVIEW_STATES | {'COMMENTED', 'PENDING'}
                or any(value is not None and (not isinstance(value, str) or len(value) > 255) for value in fields)):
            raise ValueError('Invalid review evidence')
        ids.add(number)
        evidence.append([number, *fields])
    return sorted(evidence, key=lambda item: item[0])


def approved_for_head(pr, reviews, permissions):
    """Conservatively classify an API snapshot, without guessing permissions."""
    try:
        if pr["state"] != "open":
            return False
        head = pr["head"]["sha"]
        author = pr["user"]["login"].casefold()
        if not re.fullmatch(r"[0-9a-f]{40}", head) or not author:
            return False
        latest = {}
        for review in reviews:
            state = review["state"]
            if state not in REVIEW_STATES | {"COMMENTED", "PENDING"}:
                return False
            if state not in REVIEW_STATES:
                continue
            user = review["user"]
            login = user["login"].casefold()
            if not login or user.get("type") != "User":
                continue
            submitted = datetime.fromisoformat(review["submitted_at"].replace("Z", "+00:00"))
            if submitted.utcoffset() is None:
                return False
            key = (submitted, int(review["id"]))
            if login not in latest or key > latest[login][0]:
                latest[login] = (key, review)
        # A current change request prevents an optimistic status even if
        # another reviewer approved. Comments do not revoke a review.
        if any(review["state"] == "CHANGES_REQUESTED" for _, review in latest.values()):
            return False
        return any(
            login != author
            and review["state"] == "APPROVED"
            and review["commit_id"] == head
            and permissions.get(login) in WRITE_PERMISSIONS
            for login, (_, review) in latest.items()
        )
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return False


def gh_api(path, paginate=False):
    command = ["gh", "api"]
    if paginate:
        command.extend(["--paginate", "--slurp"])
    result = subprocess.run(command + [path], check=True, capture_output=True, text=True, encoding="utf-8", timeout=15)
    return json.loads(result.stdout)


def snapshot(repo, number):
    if not REPO_PATTERN.fullmatch(repo) or not isinstance(number, int) or number < 1:
        raise ValueError("Invalid repository or PR number")
    base = f"repos/{repo}/pulls/{number}"
    started_at = int(time.time())
    deadline = time.monotonic() + 25
    def read(path, paginate=False):
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired('review snapshot', 25)
        result = gh_api(path, paginate=paginate) if paginate else gh_api(path)
        if time.monotonic() >= deadline:
            raise subprocess.TimeoutExpired('review snapshot', 25)
        return result
    pr = read(base)
    pages = read(base + "/reviews?per_page=100", paginate=True)
    reviews = [review for page in pages for review in page]
    if len(reviews) > 1000:
        raise ValueError('Too many reviews')
    permissions = {}
    queried = set()
    for review in reviews:
        user = review.get("user") or {}
        login = user.get("login", "")
        if (review.get("state") == "APPROVED" and user.get("type") == "User"
                and re.fullmatch(r"[A-Za-z0-9-]+", login) and login.casefold() not in queried):
            queried.add(login.casefold())
            try:
                permissions[login.casefold()] = read(f"repos/{repo}/collaborators/{login}/permission")["permission"]
            except (subprocess.SubprocessError, ValueError, KeyError):
                # Unknown permissions never count as approval.
                pass
    current = read(base)
    same_snapshot = all(pr.get(key) == current.get(key) for key in ("state", "updated_at"))
    same_snapshot = same_snapshot and pr.get("head", {}).get("sha") == current.get("head", {}).get("sha")
    same_snapshot = same_snapshot and pages == read(base + "/reviews?per_page=100", paginate=True)
    try:
        evidence = review_evidence(reviews)
    except (ValueError, TypeError, AttributeError):
        evidence = []
        same_snapshot = False
    return {
        "pr": number,
        "head": current.get("head", {}).get("sha"),
        "approved": same_snapshot and approved_for_head(pr, reviews, permissions),
        "reviews": evidence,
        "captured_at": started_at,
    }


def main():
    try:
        if len(sys.argv) != 3:
            raise ValueError("Usage: python tools/preview_review.py OWNER/REPO PR_NUMBER")
        print(json.dumps(snapshot(sys.argv[1], int(sys.argv[2])), ensure_ascii=False))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"Cannot verify review state: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


def current_base_matches(repo, pr, api):
    """Check live main independently; pull.base.sha can remain stale on GitHub."""
    try:
        base = pr['base']
        if (base['ref'] != 'main' or base['repo']['full_name'].casefold() != repo.casefold()
                or not re.fullmatch(r'[0-9a-f]{40}', base['sha'])):
            return False
        branch = api(f'repos/{repo}/branches/main')
        return branch['name'] == 'main' and branch['commit']['sha'] == base['sha']
    except (KeyError, TypeError, AttributeError):
        return False

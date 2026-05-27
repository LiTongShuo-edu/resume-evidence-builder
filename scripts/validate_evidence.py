#!/usr/bin/env python3
"""Validate evidence ledgers used to produce job-tailored resume claims."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ALLOWED_STATUSES = {"verified", "partially_verified", "unverified", "excluded"}
ALLOWED_EVIDENCE_KINDS = {
    "repository",
    "source",
    "test_record",
    "document",
    "artifact",
}


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_public_url(value: Any) -> bool:
    if not _nonempty_text(value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_ledger(data: Any, strict_resume: bool = False) -> list[str]:
    """Return structural and resume-safety errors in an evidence ledger."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["ledger: root value must be a JSON object"]

    if data.get("schema_version") != "1.0":
        errors.append("schema_version: expected '1.0'")
    if not _nonempty_text(data.get("target_role")):
        errors.append("target_role: a non-empty role name is required")

    project = data.get("project")
    projects = data.get("projects")
    if project is not None and projects is not None:
        errors.append("projects: use either 'project' or 'projects', not both")
    if projects is not None:
        if not isinstance(projects, list) or not projects:
            errors.append("projects: at least one public project is required when supplied")
        else:
            project_names: set[str] = set()
            for index, item in enumerate(projects):
                path = f"projects[{index}]"
                if not isinstance(item, dict):
                    errors.append(f"{path}: expected an object")
                    continue
                name = item.get("name")
                if not _nonempty_text(name):
                    errors.append(f"{path}.name: a non-empty name is required")
                elif name in project_names:
                    errors.append(f"{path}.name: duplicate project '{name}'")
                else:
                    project_names.add(name)
                if not _is_public_url(item.get("public_repository")):
                    errors.append(f"{path}.public_repository: an http(s) public URL is required")

    requirements = data.get("job_requirements")
    requirement_ids: set[str] = set()
    if not isinstance(requirements, list) or not requirements:
        errors.append("job_requirements: at least one requirement is required")
    else:
        for index, requirement in enumerate(requirements):
            path = f"job_requirements[{index}]"
            if not isinstance(requirement, dict):
                errors.append(f"{path}: expected an object")
                continue
            requirement_id = requirement.get("id")
            if not _nonempty_text(requirement_id):
                errors.append(f"{path}.id: a non-empty id is required")
            elif requirement_id in requirement_ids:
                errors.append(f"{path}.id: duplicate id '{requirement_id}'")
            else:
                requirement_ids.add(requirement_id)
            if not _nonempty_text(requirement.get("summary")):
                errors.append(f"{path}.summary: a non-empty summary is required")

    claims = data.get("claims")
    claim_ids: set[str] = set()
    if not isinstance(claims, list) or not claims:
        errors.append("claims: at least one claim is required")
        return errors

    for index, claim in enumerate(claims):
        path = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{path}: expected an object")
            continue

        claim_id = claim.get("id")
        if not _nonempty_text(claim_id):
            errors.append(f"{path}.id: a non-empty id is required")
        elif claim_id in claim_ids:
            errors.append(f"{path}.id: duplicate id '{claim_id}'")
        else:
            claim_ids.add(claim_id)
        if not _nonempty_text(claim.get("statement")):
            errors.append(f"{path}.statement: a non-empty statement is required")

        status = claim.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{path}.status: expected one of {sorted(ALLOWED_STATUSES)}, got {status!r}"
            )

        resume_ready = claim.get("resume_ready")
        if not isinstance(resume_ready, bool):
            errors.append(f"{path}.resume_ready: expected a boolean")
        elif resume_ready and status == "excluded":
            errors.append(f"{path}: excluded claims cannot be resume-ready")
        elif strict_resume and resume_ready and status != "verified":
            errors.append(
                f"{path}: resume-ready claims must be verified in strict mode"
            )

        mappings = claim.get("requirement_ids")
        if not isinstance(mappings, list):
            errors.append(f"{path}.requirement_ids: expected an array")
        else:
            seen_mappings: set[str] = set()
            for mapping in mappings:
                if not _nonempty_text(mapping):
                    errors.append(
                        f"{path}.requirement_ids: each referenced id must be non-empty"
                    )
                elif mapping in seen_mappings:
                    errors.append(
                        f"{path}.requirement_ids: duplicate reference '{mapping}'"
                    )
                elif mapping not in requirement_ids:
                    errors.append(
                        f"{path}.requirement_ids: unknown requirement '{mapping}'"
                    )
                seen_mappings.add(mapping)

        evidence = claim.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence: expected an array")
            evidence = []
        for evidence_index, item in enumerate(evidence):
            evidence_path = f"{path}.evidence[{evidence_index}]"
            if not isinstance(item, dict):
                errors.append(f"{evidence_path}: expected an object")
                continue
            if item.get("kind") not in ALLOWED_EVIDENCE_KINDS:
                errors.append(
                    f"{evidence_path}.kind: expected one of "
                    f"{sorted(ALLOWED_EVIDENCE_KINDS)}"
                )
            if not _nonempty_text(item.get("label")):
                errors.append(f"{evidence_path}.label: a non-empty label is required")
            if not _is_public_url(item.get("url")):
                errors.append(
                    f"{evidence_path}.url: an http(s) public URL is required"
                )
            if not _nonempty_text(item.get("supports")):
                errors.append(
                    f"{evidence_path}.supports: a non-empty support note is required"
                )

        if not _nonempty_text(claim.get("source_disclosure")):
            errors.append(
                f"{path}.source_disclosure: a non-empty disclosure is required"
            )

        if status == "verified":
            if not evidence:
                errors.append(f"{path}: verified claims require at least one evidence item")
            verification = claim.get("verification")
            if not isinstance(verification, dict):
                errors.append(f"{path}.verification: verified claims require verification")
                continue
            if not _nonempty_text(verification.get("method")):
                errors.append(
                    f"{path}.verification.method: a non-empty method is required"
                )
            if not _nonempty_text(verification.get("result")):
                errors.append(
                    f"{path}.verification.result: a non-empty result is required"
                )
            verified_on = verification.get("verified_on")
            try:
                date.fromisoformat(verified_on)
            except (TypeError, ValueError):
                errors.append(
                    f"{path}.verification.verified_on: use an ISO date (YYYY-MM-DD)"
                )

    return errors


def iter_public_urls(data: dict[str, Any]) -> Iterable[str]:
    """Yield distinct public URLs that the ledger exposes as evidence."""
    seen: set[str] = set()
    project = data.get("project")
    if isinstance(project, dict):
        repository = project.get("public_repository")
        if _is_public_url(repository) and repository not in seen:
            seen.add(repository)
            yield repository
    for project in data.get("projects", []):
        if not isinstance(project, dict):
            continue
        repository = project.get("public_repository")
        if _is_public_url(repository) and repository not in seen:
            seen.add(repository)
            yield repository
    for claim in data.get("claims", []):
        if not isinstance(claim, dict):
            continue
        for item in claim.get("evidence", []):
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if _is_public_url(url) and url not in seen:
                seen.add(url)
                yield url


def check_public_url(url: str, timeout: float = 15.0) -> str | None:
    """Return an availability error for URL, without judging its contents."""
    headers = {"User-Agent": "resume-evidence-builder/1.0"}
    for method in ("HEAD", "GET"):
        request = Request(url, headers=headers, method=method)
        try:
            with urlopen(request, timeout=timeout) as response:
                if response.status < 400:
                    return None
                return f"{url}: returned HTTP {response.status}"
        except HTTPError as exc:
            if method == "HEAD" and exc.code in {403, 405}:
                continue
            return f"{url}: returned HTTP {exc.code}"
        except URLError as exc:
            return f"{url}: unavailable ({exc.reason})"
    return f"{url}: unavailable"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="Path to an evidence ledger JSON file")
    parser.add_argument(
        "--strict-resume",
        action="store_true",
        help="Fail when a resume-ready claim is not verified.",
    )
    parser.add_argument(
        "--check-public-links",
        action="store_true",
        help="Check that HTTP(S) evidence URLs are accessible.",
    )
    args = parser.parse_args(argv)

    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: ledger does not exist: {args.ledger}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {args.ledger}: {exc}", file=sys.stderr)
        return 2

    errors = validate_ledger(data, strict_resume=args.strict_resume)
    checked_links = 0
    if not errors and args.check_public_links:
        for url in iter_public_urls(data):
            checked_links += 1
            error = check_public_url(url)
            if error:
                errors.append(error)

    if errors:
        print("Evidence ledger validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    claim_count = len(data["claims"])
    resume_count = sum(
        1
        for claim in data["claims"]
        if claim.get("resume_ready") and claim.get("status") == "verified"
    )
    print(
        f"Evidence ledger valid: {args.ledger} "
        f"({claim_count} claims; {resume_count} verified resume claims)."
    )
    if args.check_public_links:
        print(f"Public link availability checked: {checked_links} URL(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

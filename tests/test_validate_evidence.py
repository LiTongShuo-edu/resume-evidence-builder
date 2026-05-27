import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_evidence  # noqa: E402


class EvidenceLedgerValidationTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_public_example_is_valid_in_strict_mode(self):
        ledger = self.load("references/example-learningplusplus-ledger.json")
        self.assertEqual([], validate_evidence.validate_ledger(ledger, strict_resume=True))

    def test_multi_project_portfolio_is_valid_in_strict_mode(self):
        ledger = self.load("references/example-public-portfolio-ledger.json")
        self.assertEqual([], validate_evidence.validate_ledger(ledger, strict_resume=True))

    def test_verified_claim_requires_evidence(self):
        ledger = self.load("tests/fixtures/missing-evidence.json")
        errors = validate_evidence.validate_ledger(ledger)
        self.assertTrue(any("require at least one evidence item" in error for error in errors))

    def test_invalid_status_is_rejected(self):
        ledger = self.load("tests/fixtures/invalid-status.json")
        errors = validate_evidence.validate_ledger(ledger)
        self.assertTrue(any(".status:" in error for error in errors))

    def test_unverified_resume_claim_fails_strict_mode(self):
        ledger = self.load("tests/fixtures/unverified-resume.json")
        errors = validate_evidence.validate_ledger(ledger, strict_resume=True)
        self.assertTrue(any("must be verified in strict mode" in error for error in errors))

    def test_unknown_requirement_reference_is_rejected(self):
        ledger = self.load("tests/fixtures/unknown-requirement.json")
        errors = validate_evidence.validate_ledger(ledger)
        self.assertTrue(any("unknown requirement" in error for error in errors))

    def test_excluded_material_cannot_be_resume_ready(self):
        ledger = self.load("tests/fixtures/excluded-resume.json")
        errors = validate_evidence.validate_ledger(ledger, strict_resume=True)
        self.assertTrue(any("excluded claims cannot be resume-ready" in error for error in errors))

    def test_multi_project_public_links_are_enumerated_and_checked(self):
        ledger = self.load("references/example-public-portfolio-ledger.json")
        urls = list(validate_evidence.iter_public_urls(ledger))
        self.assertIn("https://github.com/LiTongShuo-edu/eye-galvo-control", urls)
        self.assertIn("https://github.com/LiTongShuo-edu/ppt-study-guide-skill", urls)
        with patch.object(validate_evidence, "check_public_url", return_value=None) as checker:
            for url in urls:
                validate_evidence.check_public_url(url)
        self.assertEqual(len(urls), checker.call_count)


if __name__ == "__main__":
    unittest.main()

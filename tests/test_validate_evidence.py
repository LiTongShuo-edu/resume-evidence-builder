import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_evidence  # noqa: E402


class EvidenceLedgerValidationTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text(encoding="utf-8"))

    def test_public_example_is_valid_in_strict_mode(self):
        ledger = self.load("references/example-learningplusplus-ledger.json")
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


if __name__ == "__main__":
    unittest.main()

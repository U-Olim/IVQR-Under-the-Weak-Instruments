"""Adversarial checks for the new verifier, never tests/executes historical estimators."""
import csv
import gzip
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evidence_verifier", ROOT / "scripts/verify_evidence.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VerificationTests(unittest.TestCase):
    def test_nonfinite_and_invalid_decisions_rejected(self):
        for bad in ("NaN", "Inf", "-inf"):
            with self.subTest(bad=bad), self.assertRaises(ValueError): v.number(bad)
        with self.assertRaises(ValueError): v.flag("unknown")

    def test_manifest_prevents_escape(self):
        for bad in ("../outside.csv", "/outside.csv", "data\\..\\outside.csv"):
            with self.subTest(bad=bad), self.assertRaises(ValueError): v.safe_member(ROOT, bad)

    def test_missing_archive_never_passes(self):
        with tempfile.TemporaryDirectory() as t:
            report = v.verify(Path(t))
            status = {r["check"]: r["status"] for r in report["checks"]}
            self.assertEqual(status["main_estimator_records"], "NOT_VERIFIABLE")
            self.assertEqual(status["finite_grid_records"], "NOT_VERIFIABLE")
            self.assertEqual(report["archived_verification"], "NOT_VERIFIABLE")

    def test_hash_tamper_and_unlisted_payload_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            p = root / "evidence.txt"
            p.write_bytes(b"frozen evidence\n")
            row = {"release_path": p.name, "release_bytes": p.stat().st_size,
                   "release_sha256": v.digest(p), "transformation": "byte-identical",
                   "source_sha256": v.digest(p)}
            with (root / "RELEASE_MANIFEST.csv").open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=row); w.writeheader(); w.writerow(row)
            self.assertEqual(v.integrity(root)["files"], 1)
            p.write_bytes(b"altered evidence\n")
            with self.assertRaises(ValueError): v.integrity(root)
            p.write_bytes(b"frozen evidence\n")
            (root / "unexpected.txt").write_text("extra payload")
            with self.assertRaises(ValueError): v.integrity(root)

    def test_changed_truth_decision_rejected(self):
        # Only a temporary copy is changed. The candidate archive is read-only.
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dest = root / "results/main/n500/results.csv.gz"
            dest.parent.mkdir(parents=True)
            rows = list(v.records(ROOT, "results/main/n500/results.csv.gz"))
            rows[0]["covered"] = "FALSE" if rows[0]["covered"] == "TRUE" else "TRUE"
            with gzip.open(dest, "wt", newline="") as f:
                w = csv.DictWriter(f, fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
            with self.assertRaisesRegex(ValueError, "Truth decision"):
                v.main_records(root)

    def test_duplicate_replication_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            dest = root / "results/main/n500/results.csv.gz"
            dest.parent.mkdir(parents=True)
            rows = list(v.records(ROOT, "results/main/n500/results.csv.gz"))
            rows.insert(1, dict(rows[0]))
            with gzip.open(dest, "wt", newline="") as f:
                w = csv.DictWriter(f, fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
            with self.assertRaisesRegex(ValueError, "Duplicate estimator record"):
                v.main_records(root)


if __name__ == "__main__": unittest.main()

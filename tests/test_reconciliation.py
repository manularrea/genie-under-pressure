import json
import unittest
from pathlib import Path
from src.fixtures import fixtures
from src.local_engine import pipeline, minor
from src.reference import reference, metrics


class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = fixtures()
        cls.expected, cls.quarantine = reference(cls.tables)
        cls.actual = pipeline(cls.tables)

    def test_full_sql_equivalence(self):
        self.assertEqual(self.expected, self.actual)

    def test_checked_in_metrics(self):
        stored = json.loads(Path("data/expected/expected_metrics.json").read_text())
        for key, value in metrics(self.actual).items():
            self.assertEqual(stored[key], value, key)

    def test_deliberate_migration_fails(self):
        bad = pipeline(self.tables, "labs/lab02/silver_START.sql")
        self.assertNotEqual(bad, self.expected)
        self.assertNotIn("EDGE_CANCELLED", {r["transaction_id"] for r in bad})
        self.assertIn("EDGE_NEXT_DAY", {r["transaction_id"] for r in bad})
        self.assertNotIn("EDGE_NULL_MERCHANT", {r["transaction_id"] for r in bad})

    def test_business_boundaries(self):
        keys = {r["transaction_id"] for r in self.actual}
        self.assertTrue({"EDGE_MIDNIGHT", "EDGE_END", "EDGE_NULL_MERCHANT", "EDGE_UNKNOWN_MERCHANT", "EDGE_CANCELLED"} <= keys)
        self.assertTrue({"EDGE_NEXT_DAY", "EDGE_PREV_DAY", "EDGE_BAD_DATE", "EDGE_BAD_AMOUNT", "EDGE_BAD_ACCOUNT"}.isdisjoint(keys))

    def test_dedup_tie_and_signed_amount(self):
        rows = {r["transaction_id"]: r for r in self.actual}
        self.assertEqual(rows["EDGE_DUP"]["amount_minor"], 7500)
        self.assertEqual(rows["EDGE_DUP"]["status"], "CANCELLED")
        self.assertEqual(rows["EDGE_TIE"]["amount_minor"], 3100)
        self.assertEqual(rows["EDGE_END"]["amount_minor"], -1234)
        self.assertEqual(rows["EDGE_MIDNIGHT"]["segment"], "PREMIUM")

    def test_quarantine_accountability(self):
        self.assertEqual({r["transaction_id"] for r in self.quarantine}, {"EDGE_BAD_DATE", "EDGE_BAD_AMOUNT", "EDGE_BAD_ACCOUNT"})

    def test_counts_and_sums_do_not_prove_equivalence(self):
        changed = [dict(r) for r in self.actual]
        changed[0]["customer_id"] = "C999"
        before, after = metrics(self.actual), metrics(changed)
        self.assertEqual(before["rows"], after["rows"])
        self.assertEqual(before["amount_minor_by_currency"], after["amount_minor_by_currency"])
        self.assertNotEqual(before["row_sha256"], after["row_sha256"])

    def test_decimal_contract(self):
        self.assertEqual(minor("-0.01"), -1)
        self.assertEqual(minor("9999999999999999.99"), 999999999999999999)
        for invalid in ("1,245.50", "1.001", "NaN", "1e3", None):
            self.assertIsNone(minor(invalid))


if __name__ == "__main__":
    unittest.main()

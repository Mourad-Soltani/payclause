"""Health tests for PayClause.

Signature: Mourad.Soltani
"""

import json
import unittest
from pathlib import Path

from payclause.engine import ClauseError, build_schedule, health


ROOT = Path(__file__).resolve().parents[1]


class HealthTests(unittest.TestCase):
    def test_health_ok(self) -> None:
        report = health()
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["signature"], "Mourad.Soltani")

    def test_sample_schedule(self) -> None:
        sample = json.loads((ROOT / "examples" / "sample.json").read_text(encoding="utf-8"))
        schedule = build_schedule(sample)
        kinds = [event["kind"] for event in schedule["events"]]
        self.assertIn("deposit_request", kinds)
        self.assertIn("late_notice", kinds)
        self.assertEqual(schedule["deposit"], "EUR 600.00")
        self.assertEqual(schedule["event_count"], 6)
        self.assertTrue(all("Subject:" in event["note"] for event in schedule["events"]))

    def test_rejects_bad_date(self) -> None:
        with self.assertRaises(ClauseError):
            build_schedule(
                {
                    "client": "Ada",
                    "project": "Site",
                    "currency": "USD",
                    "total": 100,
                    "deposit_percent": 0,
                    "net_days": 7,
                    "start_date": "01-10-2026",
                    "milestones": [{"name": "Done", "date": "2026-10-02"}],
                }
            )


if __name__ == "__main__":
    unittest.main()

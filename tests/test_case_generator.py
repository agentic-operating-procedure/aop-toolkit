import unittest
from datetime import datetime
from scripts.generate_cases import make_case


class GeneratedCaseBoundaryTests(unittest.TestCase):
    def elapsed_minutes(self, case):
        start = datetime.fromisoformat(case["started_at"].replace("Z", "+00:00"))
        end = datetime.fromisoformat(case["ended_at"].replace("Z", "+00:00"))
        return (end - start).total_seconds() / 60

    def test_duration_matches_cycle_time_across_hour_boundary(self):
        case = make_case(1, "dominant")
        self.assertEqual(self.elapsed_minutes(case), case["outcome"]["cycle_time"])
        self.assertEqual(case["ended_at"], "2026-11-02T10:17Z")

    def test_duration_matches_cycle_time_for_all_profiles(self):
        for index, profile in enumerate(
            ["dominant", "rework", "high-mttr", "priority-outage", "loopback-failure"], start=1
        ):
            with self.subTest(profile=profile):
                case = make_case(index, profile)
                self.assertEqual(self.elapsed_minutes(case), case["outcome"]["cycle_time"])

    def test_generator_deterministic_for_case(self):
        self.assertEqual(make_case(7, "rework"), make_case(7, "rework"))


if __name__ == "__main__":
    unittest.main()

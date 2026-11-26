import unittest
from scripts.validate_case_cycle_time import validate_case


def make_case(start="2026-11-02T09:01Z", end="2026-11-02T09:17Z", cycle=16):
    return {
        "case_id": "TEST-1",
        "started_at": start,
        "ended_at": end,
        "outcome": {"cycle_time": cycle},
    }


class CycleTimeValidationTests(unittest.TestCase):
    def test_correct_elapsed_minutes_pass(self):
        self.assertEqual(validate_case(make_case()), [])

    def test_mismatched_duration_fails(self):
        self.assertTrue(validate_case(make_case(cycle=76)))

    def test_timezone_missing_fails(self):
        self.assertTrue(validate_case(make_case(start="2026-11-02T09:01")))

    def test_end_before_start_fails(self):
        self.assertTrue(validate_case(make_case(start="2026-11-02T09:17", end="2026-11-02T09:01")))


if __name__ == "__main__":
    unittest.main()

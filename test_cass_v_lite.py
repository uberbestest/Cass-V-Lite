import unittest

from cass_v_lite import SECTION_ORDER, evaluate_cass_v_lite


class CassVLiteTests(unittest.TestCase):
    def test_clean_system_passes(self) -> None:
        text = (
            "Objective: Preserve archival record accuracy. "
            "The system must keep original source entries unchanged. "
            "It should reject edits that remove cited evidence."
        )
        output = evaluate_cass_v_lite(text)
        self.assertIn("Invariant Check:\nPASS", output)
        self.assertIn("Minimal Repair:\nNo repair required", output)
        self.assertIn("Confidence:\nMEDIUM", output)

    def test_proxy_heavy_system_fails_with_proxy_isolation(self) -> None:
        text = (
            "Goal: Improve student learning. "
            "The program optimizes for test score growth, rankings, and completion metrics. "
            "Bonuses reward score maximization."
        )
        output = evaluate_cass_v_lite(text)
        self.assertIn("Invariant Check:\nFAIL", output)
        self.assertIn("- Proxy Substitution", output)
        self.assertIn("monitoring signals only", output)
        self.assertIn("Confidence:\nHIGH", output)

    def test_ambiguous_objective_drops_confidence(self) -> None:
        text = (
            "Increase retention and engagement across the platform. "
            "Use dashboards and metrics to guide improvement."
        )
        output = evaluate_cass_v_lite(text)
        self.assertIn("Invariant Check:\nFAIL", output)
        self.assertIn("- Objective Ambiguity Collapse", output)
        self.assertIn("Confidence:\nLOW", output)

    def test_over_optimized_system_reinforces_constraints(self) -> None:
        text = (
            "Objective: Keep customer support accurate. "
            "Optimize for ticket throughput and lower handling time. "
            "Scale resolution volume aggressively."
        )
        output = evaluate_cass_v_lite(text)
        self.assertIn("Invariant Check:\nFAIL", output)
        self.assertIn("- Optimization Drift", output)
        self.assertIn("- Constraint Erosion", output)
        self.assertIn("original objective", output)

    def test_output_contract_is_exactly_ordered(self) -> None:
        text = "Objective: Preserve data integrity."
        output = evaluate_cass_v_lite(text)
        positions = [output.index(section) for section in SECTION_ORDER]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()

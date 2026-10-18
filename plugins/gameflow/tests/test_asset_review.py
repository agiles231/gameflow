#!/usr/bin/env python3
"""Exercise optional review independently from task acceptance and Blender access."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/asset_review.py"
spec = importlib.util.spec_from_file_location("asset_review", SCRIPT)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewTests(unittest.TestCase):
    def test_window_history_and_idempotence(self):
        q = review.empty_queue()
        for n in range(7):
            review.enqueue(q, f"A{n}", f"T{n}", f"R{n}", f"{n}.glb", "same timestamp")
        self.assertEqual([e["asset_id"] for e in review.selection(q)], ["A6", "A5", "A4", "A3", "A2"])
        review.enqueue(q, "A1", "T1", "R1", "1.glb", "later timestamp")
        self.assertEqual(len(q["entries"]), 7)
        review.decide(q, "A6", "R6", "approved", "Looks good", "now")
        self.assertEqual([e["asset_id"] for e in review.selection(q)], ["A5", "A4", "A3", "A2", "A1"])
        review.enqueue(q, "A6", "T6", "R6", "6.glb", "later")
        self.assertEqual(q["entries"][-1]["status"], "approved")
        review.enqueue(q, "A6", "T6", "R6-new", "6-new.glb", "later")
        self.assertEqual(review.selection(q)[0]["revision"], "R6-new")
        self.assertFalse(q["entries"][-2]["current"])
        review.validate(q)

    def test_explicit_decisions_and_unknown_metadata(self):
        q = review.empty_queue()
        q["custom"] = {"preserve": True}
        review.enqueue(q, "A", "T", "R", "a.glb", "now")
        with self.assertRaises(ValueError):
            review.decide(q, "A", "R", "approved", "", "now")
        review.decide(q, "A", "R", "disapproved", "Branches look wrong", "now")
        self.assertEqual(review.selection(q), [])
        self.assertEqual(q["entries"][0]["task_id"], "T")
        self.assertEqual(q["custom"], {"preserve": True})
        self.assertEqual(len(q["entries"][0]["decisions"]), 1)
        review.validate(q)

    def test_invalid_state_is_rejected(self):
        q = review.empty_queue()
        review.enqueue(q, "A", "T", "R", "a.glb", "now")
        q["entries"][0]["status"] = []
        with self.assertRaises(ValueError):
            review.validate(q)
        q["entries"][0]["status"] = "pending"
        q["entries"].append(dict(q["entries"][0], revision="R2"))
        with self.assertRaises(ValueError):
            review.validate(q)

    def test_cli_lifecycle_and_exact_presentation(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            def run(*args, succeeds=True):
                result = subprocess.run([sys.executable, str(SCRIPT), "--project", folder, *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0 if succeeds else 1, result.stderr)
                return result
            run("select")
            self.assertFalse((project / ".gameflow").exists())
            run("enqueue", "--asset-id", "A", "--task-id", "T", "--revision", "R", "--artifact", "a.glb")
            shown = project / "shown.json"
            shown.write_text(json.dumps([{"asset_id": "A", "revision": "R"}]))
            run("present", "--status", "shown", "--reason", "Opened and framed", "--selection", str(shown))
            run("enqueue", "--asset-id", "A", "--task-id", "T", "--revision", "R2", "--artifact", "a2.glb")
            run("present", "--status", "shown", "--reason", "Stale scene", "--selection", str(shown), succeeds=False)
            result = run("decide", "--asset-id", "A", "--revision", "R", "--status", "disapproved", "--feedback", "Old issue")
            self.assertIn("record_historical_feedback_only", result.stdout)
            result = run("decide", "--asset-id", "A", "--revision", "R2", "--status", "disapproved", "--feedback", "Still wrong")
            self.assertIn("reopen_original_task_interactively", result.stdout)
            run("present", "--status", "deferred", "--reason", "User owns Blender")
            self.assertFalse((project / ".gameflow/tasks").exists())
            run("validate")


if __name__ == "__main__":
    unittest.main()

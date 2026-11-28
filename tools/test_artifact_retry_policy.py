"""Tests for the pure preview artifact download retry policy and its CLI."""
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from tools.artifact_retry_policy import (
    BACKOFF_SECONDS,
    CATEGORY_DIGEST_MISMATCH,
    CATEGORY_ID_NOT_FOUND,
    CATEGORY_NAME_NOT_FOUND,
    CATEGORY_PERMISSION_OR_404,
    CATEGORY_SUCCESS,
    CATEGORY_UNKNOWN,
    MAX_ATTEMPTS,
    classify_failure,
    decide,
    main,
)

SUCCESS_TEXTS = (None, "", "success", "succeeded")


class DecideTests(unittest.TestCase):
    def test_success_needs_no_retry(self):
        for text in SUCCESS_TEXTS:
            with self.subTest(text=text):
                decision = decide(1, text)
                self.assertEqual(decision.category, CATEGORY_SUCCESS)
                self.assertFalse(decision.retry)
                self.assertEqual(decision.wait_seconds, 0)
                self.assertEqual(decision.action, "success")
                self.assertIn("succeeded", decision.reason)

    def test_name_not_found_retries_with_5_then_10_seconds(self):
        text = (
            "Unable to find any artifacts for the associated workflow: "
            "no artifact named wiki-preview-37-abc is listed for run 123 (attempt 1)"
        )
        first = decide(1, text)
        self.assertEqual(first.category, CATEGORY_NAME_NOT_FOUND)
        self.assertTrue(first.retry)
        self.assertEqual(first.wait_seconds, BACKOFF_SECONDS[0])
        self.assertEqual(first.action, "retry")
        self.assertEqual(first.attempts_remaining, MAX_ATTEMPTS - 1)

        second = decide(2, text)
        self.assertTrue(second.retry)
        self.assertEqual(second.wait_seconds, BACKOFF_SECONDS[1])

    def test_id_not_found_is_transient(self):
        for text in (
            "No artifacts found",
            "No artifacts found for artifact ID 14651138977",
            "No artifact was found with the provided ID",
        ):
            with self.subTest(text=text):
                decision = decide(1, text)
                self.assertEqual(decision.category, CATEGORY_ID_NOT_FOUND)
                self.assertTrue(decision.retry)
                self.assertEqual(decision.wait_seconds, 5)

    def test_permission_and_http_404_fail_immediately(self):
        for text in (
            "Resource not accessible by integration",
            "gh: HTTP 403: Resource not accessible by integration",
            "HTTP 401: Bad credentials",
            "Permission denied while listing artifact wiki-preview-37-abc for run 123: Forbidden",
            "Artifact listing returned HTTP 404 for run 123 artifact wiki-preview-37-abc: Not Found",
        ):
            with self.subTest(text=text):
                decision = decide(1, text)
                self.assertEqual(decision.category, CATEGORY_PERMISSION_OR_404)
                self.assertFalse(decision.retry)
                self.assertEqual(decision.wait_seconds, 0)
                self.assertEqual(decision.action, "fail")
                self.assertIn("not retrying", decision.reason)

    def test_digest_mismatch_fails_immediately(self):
        for text in (
            "Digest mismatch on attempt 1: uploaded abc123, downloaded def456",
            "download-artifact: digest-mismatch: error",
            "The downloaded archive checksum mismatch was detected",
            "Digest validation failed for artifact(s): wiki-preview-37-abc. Use 'digest-mismatch: warn' to continue on mismatch.",
        ):
            with self.subTest(text=text):
                decision = decide(2, text)
                self.assertEqual(decision.category, CATEGORY_DIGEST_MISMATCH)
                self.assertFalse(decision.retry)
                self.assertEqual(decision.wait_seconds, 0)
                self.assertEqual(decision.action, "fail")

    def test_attempt_budget_is_exhausted_after_three(self):
        text = "Download attempt 3 failed without a classified cause"
        third = decide(MAX_ATTEMPTS, text)
        self.assertEqual(third.category, CATEGORY_UNKNOWN)
        self.assertFalse(third.retry)
        self.assertEqual(third.wait_seconds, 0)
        self.assertEqual(third.action, "fail")
        self.assertIn("budget is exhausted", third.reason)
        self.assertEqual(third.attempts_remaining, 0)

        beyond = decide(MAX_ATTEMPTS + 1, text)
        self.assertFalse(beyond.retry)
        self.assertEqual(beyond.wait_seconds, 0)

    def test_waited_seconds_prevents_double_waiting(self):
        text = "Unable to find any artifacts for the associated workflow"
        partial = decide(2, text, waited_seconds=4)
        self.assertTrue(partial.retry)
        self.assertEqual(partial.wait_seconds, BACKOFF_SECONDS[1] - 4)
        already_waited = decide(2, text, waited_seconds=BACKOFF_SECONDS[1])
        self.assertTrue(already_waited.retry)
        self.assertEqual(already_waited.wait_seconds, 0)

    def test_unknown_failure_is_retried_but_bounded(self):
        decision = decide(1, "something unexpected happened while extracting")
        self.assertEqual(decision.category, CATEGORY_UNKNOWN)
        self.assertTrue(decision.retry)
        self.assertEqual(decision.wait_seconds, 5)
        self.assertFalse(decide(3, "something unexpected happened while extracting").retry)

    def test_invalid_arguments_are_rejected(self):
        for attempt in (0, -1):
            with self.subTest(attempt=attempt):
                with self.assertRaises(ValueError):
                    decide(attempt, "No artifacts found")
        with self.assertRaises(TypeError):
            decide(1, "No artifacts found", waited_seconds=1.5)
        with self.assertRaises(ValueError):
            decide(1, "No artifacts found", waited_seconds=-1)

    def test_workflow_canonical_texts_classify_as_intended(self):
        cases = {
            "Download attempt 1 reported failure although the downloaded file exists and matches the recorded upload SHA-256; treating as transient": (
                CATEGORY_UNKNOWN,
                True,
            ),
            "Artifact named wiki-preview-37-abc is listed for run 123, but the download failed before an extracted file could be verified; treating the download transport error as transient (attempt 1)": (
                CATEGORY_UNKNOWN,
                True,
            ),
            "Unable to download artifact(s): Artifact not found for name: wiki-preview-37-abc": (
                CATEGORY_NAME_NOT_FOUND,
                True,
            ),
            "No artifacts found for ID: 14651138977": (
                CATEGORY_ID_NOT_FOUND,
                True,
            ),
            "Permission denied while listing artifact wiki-preview-37-abc for run 123: HTTP 403": (
                CATEGORY_PERMISSION_OR_404,
                False,
            ),
            "Artifact listing returned HTTP 404 for run 123 artifact wiki-preview-37-abc: Not Found": (
                CATEGORY_PERMISSION_OR_404,
                False,
            ),
            "Digest mismatch on attempt 1: uploaded abc, downloaded def": (
                CATEGORY_DIGEST_MISMATCH,
                False,
            ),
        }
        for text, (category, retry) in cases.items():
            with self.subTest(text=text):
                self.assertEqual(classify_failure(text), category)
                self.assertEqual(decide(1, text).retry, retry)


class CliTests(unittest.TestCase):
    def run_cli(self, argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            return main(argv), stdout.getvalue()

    def test_retry_exit_code_outputs_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failure = root / "failure.txt"
            failure.write_text("Unable to find any artifacts for the associated workflow", encoding="utf-8")
            output = root / "github-output.txt"
            summary = root / "summary.md"
            code, stdout = self.run_cli(
                [
                    "--attempt",
                    "1",
                    "--failure-file",
                    str(failure),
                    "--github-output",
                    str(output),
                    "--summary-file",
                    str(summary),
                ]
            )
            self.assertEqual(code, 0, stdout)
            self.assertIn("::warning::", stdout)
            lines = output.read_text(encoding="utf-8").splitlines()
            self.assertIn("retry=true", lines)
            self.assertIn("wait_seconds=5", lines)
            self.assertIn(f"category={CATEGORY_NAME_NOT_FOUND}", lines)
            bullet = summary.read_text(encoding="utf-8")
            self.assertIn("Attempt 1: failed (name-not-found); waiting 5s", bullet)
            self.assertIn("category=name-not-found", output.read_text(encoding="utf-8"))

    def test_non_retryable_failure_exits_nonzero_unless_diagnose_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            failure = root / "failure.txt"
            failure.write_text("Digest mismatch: uploaded abc, downloaded def", encoding="utf-8")
            args = ["--attempt", "1", "--failure-file", str(failure)]
            code, stdout = self.run_cli(args)
            self.assertEqual(code, 1)
            self.assertIn("::error::", stdout)

            code, stdout = self.run_cli(args + ["--diagnose-only"])
            self.assertEqual(code, 0)
            self.assertIn("::error::", stdout)

    def test_exhausted_attempts_exit_nonzero(self):
        code, _ = self.run_cli(["--attempt", str(MAX_ATTEMPTS), "--failure-text", "no artifacts found"])
        self.assertEqual(code, 1)

    def test_success_exits_zero_and_reports_no_retry(self):
        code, stdout = self.run_cli(["--attempt", "1", "--failure-text", "success"])
        self.assertEqual(code, 0)
        self.assertIn("no retry needed", stdout)

    def test_missing_failure_file_and_bad_attempt_report_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist.txt"
            code, stdout = self.run_cli(["--attempt", "1", "--failure-file", str(missing)])
            self.assertEqual(code, 2)
            self.assertIn("::error::", stdout)
        code, stdout = self.run_cli(["--attempt", "0", "--failure-text", "No artifacts found"])
        self.assertEqual(code, 2)
        self.assertIn("::error::", stdout)


if __name__ == "__main__":
    unittest.main()

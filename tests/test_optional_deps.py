# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


class OptionalDepsImportErrorTestCase(unittest.TestCase):
    """Durable coverage for #3: embedding scorers must not fail the
    suite when optional deps are absent — they skip, and the scorer
    itself raises a helpful ImportError."""

    def test_bert_score_raises_helpful_error_when_missing(self):
        from vizseq.scorers.bert_score import BERTScoreScorer, _clear_bert_scorer_cache

        _clear_bert_scorer_cache()
        # Hide bert_score even if installed in this env.
        with patch.dict(sys.modules, {"bert_score": None}):
            # Force ImportError path: import finds None entry.
            # Also need to ensure importlib finds no spec.
            orig_find_spec = importlib.util.find_spec

            def fake_find_spec(name, *a, **kw):
                if name == "bert_score":
                    return None
                return orig_find_spec(name, *a, **kw)

            with patch.object(importlib.util, "find_spec", side_effect=fake_find_spec):
                scorer = BERTScoreScorer(corpus_level=True, sent_level=False, n_workers=1)
                with self.assertRaises(ImportError) as ctx:
                    scorer.score(["hello"], [["hello"]])
                self.assertIn("vizseq[embeddings]", str(ctx.exception))
        _clear_bert_scorer_cache()

    def test_laser_raises_helpful_error_when_missing(self):
        from vizseq.scorers.laser import LaserScorer

        # vizseq.scorers.laser caches _setup_complete — reset it.
        import vizseq.scorers.laser as laser_mod

        orig_complete = laser_mod._setup_complete
        laser_mod._setup_complete = False
        try:
            with patch.dict(sys.modules, {"laserembeddings": None}):
                orig_find_spec = importlib.util.find_spec

                def fake_find_spec(name, *a, **kw):
                    if name == "laserembeddings":
                        return None
                    return orig_find_spec(name, *a, **kw)

                with patch.object(importlib.util, "find_spec", side_effect=fake_find_spec):
                    scorer = LaserScorer(corpus_level=True, sent_level=False)
                    with self.assertRaises(ImportError) as ctx:
                        scorer.score(["hello"], [["hallo"]])
                    self.assertIn("vizseq[embeddings]", str(ctx.exception))
        finally:
            laser_mod._setup_complete = orig_complete

    def test_bert_score_test_case_is_skipped_when_dep_missing(self):
        from tests.scorers.test_bert_score import BERTScoreScorerTestCase

        # The class should carry skip metadata when bert_score absent.
        # unittest.skipUnless sets __unittest_skip__ / __unittest_skip_why__
        # based on the condition at import time. Verify the decorator exists
        # by checking the skip reason mentions embeddings.
        if importlib.util.find_spec("bert_score") is None:
            self.assertTrue(getattr(BERTScoreScorerTestCase, "__unittest_skip__", False))
            self.assertIn("embeddings", getattr(BERTScoreScorerTestCase, "__unittest_skip_why__", ""))
        else:
            self.skipTest("bert_score is installed — skip behaviour not exercised")

    def test_laser_test_case_is_skipped_when_dep_missing(self):
        from tests.scorers.test_laser import LaserScorerTestCase

        if importlib.util.find_spec("laserembeddings") is None:
            self.assertTrue(getattr(LaserScorerTestCase, "__unittest_skip__", False))
            self.assertIn("embeddings", getattr(LaserScorerTestCase, "__unittest_skip_why__", ""))
        else:
            self.skipTest("laserembeddings is installed — skip behaviour not exercised")

    def test_bert_score_reuse_tests_are_not_skipped(self):
        """Mock-based BERTScore cache tests must run without the extra."""
        from tests.scorers.test_bert_score import BERTScoreScorerReuseTestCase

        # These tests use fakes via patch.dict, so they must NOT be skipped.
        self.assertFalse(getattr(BERTScoreScorerReuseTestCase, "__unittest_skip__", False))


class RuffConfigTestCase(unittest.TestCase):
    """Durable coverage for #1: ruff is configured and known B/C
    warnings stay fixed."""

    def test_pyproject_has_ruff_config(self):
        toml = Path("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("[tool.ruff]", toml)
        self.assertIn("[tool.ruff.lint]", toml)

    def test_no_regressed_b007_c401_c416(self):
        import subprocess

        result = subprocess.run(
            [".venv/bin/ruff", "check", "vizseq", "--select", "B007,C401,C416"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"ruff B007/C401/C416 should pass after #1 fixes:\n{result.stdout}{result.stderr}",
        )

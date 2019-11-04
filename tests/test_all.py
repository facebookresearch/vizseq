# Copyright (c) Facebook, Inc. and its affiliates.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#


if __name__ == '__main__':
    import unittest
    from tests.scorers import (test_bleu, test_chrf, test_bp, test_bert_score,
                               test_cider, test_gleu, test_laser, test_meteor,
                               test_nist, test_ribes, test_rouge_1,
                               test_rouge_2, test_rouge_l, test_ter, test_wer,
                               test_wer_del, test_wer_ins, test_wer_sub)

    # initialize the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    for m in [
        test_bleu, test_chrf, test_bp, test_bert_score, test_cider, test_gleu,
        test_laser, test_meteor, test_nist, test_ribes, test_rouge_1,
        test_rouge_2, test_rouge_l, test_ter, test_wer, test_wer_del,
        test_wer_ins, test_wer_sub
    ]:
        suite.addTests(loader.loadTestsFromModule(m))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)

"""Regression checks for 12/24-word modes and repeated words.
Run from project root: python3 -m unittest discover -s tests -v
"""
import importlib.util
import itertools
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('xrprecover', ROOT / 'xrprecover.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)


class SupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.phrase12 = x.MNEMO.to_mnemonic(bytes(16))
        cls.phrase24 = x.MNEMO.to_mnemonic(bytes(32))
        cls.words12 = cls.phrase12.split()
        cls.words24 = cls.phrase24.split()
        cls.addr12 = x.derive_xrp_address(cls.phrase12)
        cls.addr24 = x.derive_xrp_address(cls.phrase24)

    def fake_scan(self, function, *args, limit=50, **kwargs):
        snapshot = {}
        def capture(name, total, candidates, config, *a, **kw):
            snapshot.update(name=name, total=total, config=config,
                            sample=list(itertools.islice(candidates, limit)))
            return []
        with patch.object(x, 'run_search', capture):
            function(*args, **kwargs)
        self.assertIn('config', snapshot)
        return snapshot

    def test_valid_bip39_12_and_24(self):
        for words in (self.words12, self.words24):
            packed = x.pack_indices(x.prepare_words(words))
            self.assertTrue(x.checksum_valid(packed, len(words)))
            self.assertTrue(x.MNEMO.check(' '.join(words)))
        self.assertNotEqual(self.addr12, self.addr24)

    def test_24word_reference_derived_address(self):
        self.assertEqual(x.derive_xrp_address(self.phrase24), x._reference_xrp_address(self.phrase24))

    def test_24word_wrong_word_modes_1_10_11(self):
        words = self.words24.copy()
        words[0] = 'not_in_bip39'
        for fn in (x.scan_positions_for_address, x.scan_two_positions_for_address,
                   x.scan_three_positions_for_address):
            result = self.fake_scan(fn, words, self.addr24, ('abandon','ability'), limit=2)
            self.assertEqual(result['config']['length'], 24)
            self.assertGreater(result['total'], 0)

    def test_missing_position_mode8_24(self):
        words = self.words24.copy()
        words[-1] = '?'
        snapshot = self.fake_scan(x.recover_missing_positions, words, self.addr24,
                                  (self.words24[-1], 'abandon'))
        self.assertEqual(snapshot['total'], 2)
        self.assertEqual(snapshot['config']['length'], 24)
        self.assertEqual(snapshot['config']['shifts'], (0,))

    def test_trailing_modes_2_3_13_24(self):
        pool = (self.words24[-1], 'abandon')
        a = self.fake_scan(x.search_address_pattern, self.words24[:-1], self.addr24,
                           pool, word_count=24)
        self.assertEqual(a['config']['length'], 24)
        b = self.fake_scan(x.find_missing_words, self.words24[:-1], 1, pool)
        self.assertEqual(b['config']['length'], 24)
        c = self.fake_scan(x.find_missing_words, self.words24[:-1], 1, pool,
                           target_address=self.addr24)
        self.assertEqual(c['config']['length'], 24)

    def test_mode3_allows_repeated_known_words_and_pool(self):
        known = ['abandon']*23
        a = self.fake_scan(x.find_missing_words, known, 1, ('abandon', 'art'))
        self.assertEqual(a['total'], 2)
        self.assertEqual(a['sample'], [(0,), (x.WORD_INDEX['art'],)])

    def test_mode6_repeated_word_multiset(self):
        a = self.fake_scan(x.descramble_seed, ['abandon']*23+['art'], ('abandon','art'), limit=30)
        self.assertEqual(a['total'], 24)
        self.assertEqual(len(a['sample']), 24)
        self.assertEqual(len(set(a['sample'])), 24)

    def test_mode14_repeated_input(self):
        a = self.fake_scan(x.scan_permuted_one_wrong_word,
                           ['abandon']*24, self.addr24, ('ability',), limit=30)
        self.assertEqual(a['total'], 24)
        self.assertEqual(len(set(a['sample'])), 24)

    def test_mode15_repeated_input_and_replacement(self):
        a = self.fake_scan(x.scan_permuted_two_wrong_words,
                           ['abandon']*24, self.addr24, ('ability',), limit=280)
        self.assertEqual(a['total'], 276)
        self.assertEqual(len(set(a['sample'])), 276)

    def test_mode16_repeated_words(self):
        a = self.fake_scan(x.recover_permuted_missing_positions,
                           ['abandon']*23+['?'], self.addr24, ('abandon',), limit=2)
        self.assertEqual(a['total'], 1)
        self.assertEqual(a['config']['length'], 24)

    def test_24_row_tokenlist_modes_9_and_12(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/'tokens.txt'
            path.write_text('\n'.join(f'^{i}^{word}' for i, word in enumerate(self.words24, 1))+'\n')
            fixed, floating = x.load_tokenlist(path)
            self.assertEqual(len(fixed), 24)
            self.assertEqual(len(floating), 0)
            self.assertEqual(list(x.tokenlist_candidate_indices(fixed, floating)),
                             [tuple(x.prepare_words(self.words24))])
            a = self.fake_scan(x.search_tokenlist_file, path, self.addr24)
            b = self.fake_scan(x.find_valid_tokenlist_seeds, path)
            self.assertEqual((a['config']['length'], b['config']['length']), (24, 24))

    def test_generate_24word_strength(self):
        with patch.object(x, 'derive_xrp_address', return_value=self.addr24), \
             patch('builtins.open', unittest.mock.mock_open()):
            result = x.generate_new_seed(24)
        self.assertEqual(len(result.split()), 24)
        self.assertTrue(x.MNEMO.check(result))


if __name__ == '__main__':
    unittest.main()

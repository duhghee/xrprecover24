# 12 / 24-word and repeated-word support

This branch extends modes 1–16 to BIP-39 12- and 24-word phrases. Repeated
BIP-39 words are accepted (they are legal in both lengths).

- Modes 1, 4–6, 8, 10–11, 14–16 derive phrase length from supplied words.
- Modes 3 and 13 derive length from `known words + --num-missing` (12 or 24).
- Modes 9 and 12 infer length from tokenlist rows (12 or 24); anchors up to `^24^word`.
- Mode 2 defaults to 12; use `--words 24` to search a 24-word suffix.
- Mode 7 defaults to 12; use `--words 24` to generate a synthetic 24-word mnemonic.

Example (non-secret generated fixture):

    python3 xrprecover.py --mode 7 --words 24

**Search-size warning:** 24! and even 12! are astronomically large. Modes
6/14/15/16 are exhaustive generators, not feasible complete scans for typical
24-word inputs. The Mode 16 exact progress-count computation can itself be
expensive for large missing-word pools. For testing use tiny candidate lists.

BIP-39 has 4 checksum bits at 12 words and 8 at 24 words. The derivation path
remains m/44'/144'/0'/0/0 and the passphrase remains empty.

Do not share or use real funded-wallet phrases in tests. Existing 12-word output
files and command-line flags are retained.

## Regression tests

    python3 -m pip install -r requirements.txt
    python3 -m unittest discover -s tests -v

The added test module exercises repeated-word and 24-word data paths; the
existing older test scripts may assert the former distinct-word restriction and
must be updated rather than treated as current specifications.

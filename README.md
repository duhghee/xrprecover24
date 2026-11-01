# XRPRecover

Offline-oriented XRP classic-address recovery and testing for **12- or 24-word English BIP-39 mnemonic phrases**. All **16 modes** accept repeated words where their inputs permit them; repeated words are valid BIP-39. Use only for wallets you own or are authorized to recover.

> **Security:** A mnemonic is a private secret. Work offline, avoid passing real phrases in shell arguments (they can be recorded in history/process listings), and protect all result files. XRPRecover neither checks XRP Ledger balances nor moves funds, and cannot guarantee recovery.

## Supported formats and limitations

- 12 words: 128-bit entropy plus a **4-bit** BIP-39 checksum; 24 words: 256-bit entropy plus an **8-bit** checksum. Other mnemonic lengths (15, 18, 21) are not supported.
- Repeated English BIP-39 words are **allowed** in all modes. Permutation generators avoid emitting identical rearrangements of the same multiset.
- Uses the **empty BIP-39 passphrase**. Address-matching modes use XRP classic `r...` addresses at `m/44'/144'/0'/0/0`; Mode 5 additionally displays indices `/0` through `/9`. It does not recover XRPL family seeds beginning `s`.
- `--words 24` is used for **Mode 2** (trailing-word pattern matching) and **Mode 7** (generation); most other modes derive their length from 12 or 24 supplied words/positions, `known + --num-missing`, or tokenlist row count.
- A search that permutes 24 words can be astronomically large. **24! ≈ 6.2 × 10²³**; do not assume that supporting a mode makes completing its full search feasible. Counting and enumerating large Mode 16 searches can also be expensive. There is **no persistent checkpoint/resume** mechanism.

## Installation

Ubuntu (run from the extracted project directory):

```bash
sudo apt update
sudo apt install -y python3-venv python3-tk build-essential
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python xrprecover.py
```

Windows Command Prompt:

```cmd
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python xrprecover.py
```

## Running a mode

```bash
python xrprecover.py --help
python xrprecover.py --mode 7 --words 24
python xrprecover.py --mode 7 --words 12
python xrprecover.py --mode 4 --mnemonic "12 or 24 synthetic BIP39 words"
```

The last example is a placeholder, not a valid mnemonic. Prefer interactive prompts for sensitive words. Other options include `--address`, `--pattern`, `--num-missing`, `--tokenlist`, `--processes`, `--batch-size`, `--worker N/TOTAL`, `--output`, `--pbkdf2-backend {auto,reference}` and `--allow-print` (Mode 13). Consult `python xrprecover.py --help` for authoritative option names.

## All 16 modes

| Mode | Function | 12-/24-word input handling |
| --- | --- | --- |
| 1 | Replace one wrong word at any fixed position; address match | Length from supplied words |
| 2 | Find trailing words matching an address suffix or complete address | `--words 12` (default) or `--words 24` |
| 3 | Write checksum-valid completions for missing trailing words | Known words + `--num-missing` = 12 or 24; **no address check** |
| 4 | Validate a mnemonic and show first XRP address | Length from supplied words |
| 5 | Show first ten XRP addresses | Length from supplied words |
| 6 | Enumerate checksum-valid word-order rearrangements | Length from supplied words; duplicates allowed |
| 7 | Generate a new mnemonic and address | `--words 12` (default) or `--words 24` |
| 8 | Fill 1–4 `?` words at known positions; address match | 12 or 24 positional entries |
| 9 | Match an address from fixed/floating tokenlist rows | Exactly 12 or 24 populated rows |
| 10 | Replace two wrong words at fixed positions; address match | Length from supplied words |
| 11 | Replace three wrong words at fixed positions; address match | Length from supplied words |
| 12 | Write checksum-valid tokenlist combinations | Exactly 12 or 24 populated rows; **no address check** |
| 13 | Match an address from missing trailing words | Known words + `--num-missing` = 12 or 24 |
| 14 | Change one word occurrence and permute all positions; address match | Length from supplied words; duplicates allowed |
| 15 | Change two word occurrences and permute all positions; address match | Length from supplied words; duplicates allowed |
| 16 | Fill 1–4 `?` words and permute all positions; address match | 12 or 24 entries; duplicates allowed |

Modes 14 and 15 operate on word **occurrences** and use multiset-aware permutations; replacement sets can contain repeated words. Modes 3, 6, 12 produce potentially large plaintext output files. Mode 7 writes a newly generated mnemonic to `new_seed.txt`, which must be secured.

## Tokenlists: 12 or 24 rows

Modes 9 and 12 take `--tokenlist tokenlist.txt`. Each nonempty, noncomment line contains either fixed-position alternatives (e.g., `^1^abandon ^1^ability`) or floating alternatives (e.g., `about above`). Exactly **12 or 24** populated lines are required; fixed anchors run from `^1^` to `^24^`. Empty rows are not wildcards; repeated words across positions are allowed.

**GUI limitation:** The bundled `tokenlist.py` editor currently exposes **12 rows only**. To use a 24-word tokenlist, create/edit a UTF-8 text file manually with 24 populated lines. See [README_tokenlist.md](README_tokenlist.md) for the exact format.

## AVX2 acceleration

Optional Linux x86-64 AVX2 PBKDF2 acceleration is built and benchmarked locally. Its native input limit is **128 UTF-8 bytes after normalization**, not a fixed word count: 24-word mnemonics often exceed this limit and **fall back to the reference PBKDF2 backend**. No native build is necessary for correctness. See [README_AVX2.md](README_AVX2.md).

## Testing

```bash
python -m unittest discover -s tests -v
```

The included new regression tests cover 12-/24-word and repeated-word paths. Previous third-party/local test scripts may assert the old distinct-word restriction and must be revised. Passing tests does not establish exhaustive correctness for factorial-sized searches or long-duration operation.

## Additional documentation

- [Readme.txt](Readme.txt) — detailed mode behavior, outputs, CLI, and safety notes
- [README_tokenlist.md](README_tokenlist.md) — tokenlist format and the 12-row GUI limitation
- [README_AVX2.md](README_AVX2.md) — native accelerator build, benchmarking, fallback
- [README_24_WORD_SUPPORT.md](README_24_WORD_SUPPORT.md) — change summary and additional limitations

Do not publish real mnemonic phrases or output files in version control, issues, logs, screenshots or cloud-synced folders.

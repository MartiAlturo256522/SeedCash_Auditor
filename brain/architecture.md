# Architecture

SeedCash keeps the SeedSigner shape and replaces the Bitcoin stack. Module facts below are the map. Checks live in `brain/invariants.md`. The SeedSigner comparison questions live in `brain/delta-checklist.md`.

## What stayed

- Stateless signer, seed in RAM, camera in, QR out, joystick UI, Python process started by a Buildroot image.
- PSBT as the unsigned container. UR `crypto-psbt` as the animated transport.
- The view loop: scan, review screens, sign, animate the signed PSBT back out.

## What was replaced

- embit is gone. Parsing and signing are local code in `psbt_parser.py` and `psbt_signer.py`.
- The coin is Bitcoin Cash. The account path is `m/44'/145'/0'`.
- Sighash is BIP-143 with FORKID. The allowlist is `0x41` (`ALL|FORKID`) and `0x61` (`ALL|FORKID|UTXOS`).
- Schnorr uses `python-ecdsa` RFC6979. The extra-entropy tag is an invariant, not a slogan.
- CashTokens ride in the output script. A prefix byte `0xef` starts a token. Genesis category id is the prevout txid of an input that spends vout 0.
- P2SH20 is HASH160. P2SH32 is HASH256 (double SHA-256), 35-byte script `aa 20 <32> 87`.
- QR intake in `DecodeQR.detect_segment_type` is `UR:CRYPTO-PSBT` plus a 16-byte CompactSeedQR. Settings QR, address QR, and message signing are not in that detector.

## Review path

`ScanView` accepts every type the detector knows. Subclasses can override `is_valid_qr_type`.

After parse, token and address screens run, then `BCHPSBTOverviewView`, then `PSBTMathView`. `controller.py` turns a missing next destination into `NotYetImplementedView`.

Signing goes through `BitcoinCashSigner.signed_psbt`. The outgoing PSBT adds `PSBT_IN_PARTIAL_SIG`. `validate_signed_psbt` checks that the unsigned transaction and the output value and script did not change. `clear()` runs in a `finally`.

## Consensus facts the signer has to match

- `nLockTime` is active when any input sequence is not `0xffffffff`.
- BIP-68 CSV applies when the transaction version is at least 2. Sequence is not Bitcoin Core RBF.
- For a token input, the token prefix sits before the CompactSize of `scriptCode`. The CompactSize covers the locking script only. `hashOutputs` and `hashUtxos` cover the wire `CTxOut`, where the prefix is inside the script length.
- A new category on an output is a genesis. The category id has to be the reversed prevout txid of some input that spends index 0.

## Package pin

`requirements.txt` pins `ecdsa==0.18.0`. The OS package variable to compare is `PYTHON_ECDSA_VERSION`. Both belong to `INV-ECDSA-PIN-MATCH`.

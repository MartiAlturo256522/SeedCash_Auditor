# BCH facts

Consensus and format facts for the specialists. A finding that contradicts this file is dropped. This file does not contain a transaction.

- Signing is BIP-143 with FORKID. SeedCash allows `0x41` (ALL|FORKID) and `0x61` (ALL|FORKID|UTXOS). The bytes that are allowed live in `brain/pin.md`.
- A sequence is not Core replace-by-fee. Locktime is active when any sequence is not `0xffffffff`. BIP-68 relative locktime applies when the transaction version is at least 2.
- The token prefix is written before the CompactSize of `scriptCode`, and that CompactSize covers the locking script only. `hashOutputs` and `hashUtxos` use the wire `CTxOut`.
- P2SH20 is HASH160 and the locking script is 23 bytes. P2SH32 is HASH256 and the locking script is 35 bytes.
- A genesis category id is the reversed prevout txid of an input that spends output index 0.
- Amounts are integer satoshis. A float or a four-decimal quantize is a display question, not a consensus rule.
- The BCH Schnorr tag cited for the nonce is 16 bytes. A shorter tag changes the nonce. The signature equation can still verify. That is `spec-deviation` unless a separate sentence shows an honest node rejects it.
- PSBT here is BIP-174 plus the v2 count keys and the proprietary range. Input key `0x00` is the parent transaction. Input key `0x01` is the witness UTXO. Output key `0x36` is compared to the token prefix in the script that will be signed. A partial signature is added on the way out under the derived pubkey.
- An unknown PSBT key must not change the bytes the screen reviewed.
- The account path lives in `brain/pin.md`. A fingerprint match is not a proof of the pubkey.
- The outgoing UR for a transaction is the signed PSBT. A seed, an xprv, or a passphrase does not belong in that encoding. CompactSeedQR is an inbound 16-byte path, separate from the PSBT UR.

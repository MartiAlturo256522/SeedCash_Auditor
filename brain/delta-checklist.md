# SeedSigner delta

Questions for the delta lane. A pass is a code answer, not a memory of SeedSigner 0.8.7. The baseline tag is in `brain/pin.md`. Do not read `/Users/martialturorequena/seedsigner-project/seedsigner` as that baseline.

### DL-SETTINGS-QR

Is there still a settings QR that can change the network or turn off seed warnings, and does applying it reset omitted keys to defaults?

Pass: the detector no longer accepts a settings payload, and no other parser applies a partial settings document.

### DL-COMPACT-32

Does a 32-byte QR still count as a CompactSeedQR?

Pass: only the 16-byte branch remains, and a 32-byte payload is not turned into a mnemonic.

### DL-NUMERIC-SEEDQR

Does a numeric SeedQR (wordlist indexes as digits) still decode?

Pass: the detector does not classify digit strings as seeds.

### DL-LEGACY-FEE

SeedSigner never called `PSBT.verify()` on legacy inputs, so a lied prevout value could understate the fee. Does SeedCash bind the prevout value it displays to the parent transaction it hashes?

Pass: a parent tx whose txid does not match is rejected, and the value inside the sighash is that parent's value. The witness-key ordering is `INV-WITNESS-UTXO-PRECEDENCE`, not this question.

### DL-SINGLE-SIG-CHANGE

SeedSigner re-derived single-sig change and discarded the PSBT on mismatch. Does SeedCash still re-derive an output it thinks is change?

Pass: answer from the view code. If the re-derivation is gone, say so, and leave the judgment to `INV-CHANGE-DETECTION`.

### DL-OPRETURN-SLICE

SeedSigner displayed OP_RETURN as `data[3:]` and kept one output. Does SeedCash still slice a push that way?

Pass: the screen shows the script bytes it parsed, and the slice `data[3:]` is gone. Whether an OP_RETURN-only transaction can be signed is `INV-OPRETURN-PATH`.

### DL-MESSAGE-SIGN

Is arbitrary message signing still in the detector and the menu?

Pass: no message-sign QR type and no view that signs an attacker-chosen hash outside a PSBT.

### DL-EMBIT-SIGHASH

embit refused `SIGHASH_NONE`, `SINGLE`, and `ANYONECANPAY` inside `sign_with`. What enforces that in SeedCash now?

Pass: name the allowlist function. The contents of the allowlist are `INV-SIGHASH-ALLOWLIST`.

### DL-SETTINGS-RESET

Can a partial configuration document replace omitted keys with defaults that weaken a warning?

Pass: either no such document exists, or omitted keys are left untouched.

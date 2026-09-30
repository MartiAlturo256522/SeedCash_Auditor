# Invariants

This file is the only home for a check. Skills, agents, and the corpus point here. A row is a hypothesis about the pin in `brain/pin.md` until a later run re-reads the function.

- pin_commit: 364cccc

Status `open` means the check was observed broken at that commit. Status `closed` means the check was observed present. Status `unchecked` means the question is real and the lines were not finished. `file_ready: yes` is allowed only on `open`, and only when an upstream issue would be the right next step.

### INV-SIGHASH-ALLOWLIST

- lane: signer
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_signer.py` `ALLOWED_SIGHASH`

`ALLOWED_SIGHASH` is `0x41` and `0x61`. `_get_sighash_type` and `create_sighash` both refuse anything else. `SIGHASH_ALL` without FORKID, `NONE`, `SINGLE`, and `ANYONECANPAY` are outside the set. The pass condition is that both functions keep that refusal, and that a hash type already present on the input cannot bypass it.

### INV-SIGHASH-PREIMAGE

- lane: signer
- impact: invalid-signature
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_signer.py` `create_sighash`

For a token input the token prefix is written before the CompactSize of `scriptCode`, and that CompactSize covers the locking script only. `hashOutputs` and `hashUtxos` use the wire script (`full_script`), so the prefix sits inside that length. The pass condition is that this layout is unchanged and that a non-token input still sighashes the locking script alone. This row does not claim libauth vectors were executed.

### INV-SCHNORR-TAG

- lane: signer
- impact: spec-deviation
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_signer.py` `_sign_schnorr`

`_sign_schnorr` calls RFC6979 with `extra_entropy=b"Schnorr+SHA256 "` (15 bytes, one trailing space). The tag cited for BCH Schnorr is 16 bytes, with two trailing spaces. The nonce changes. The signature equation in the same function still hashes `r || compressed pubkey || msg`, so an honest verifier that checks the equation accepts the signature. The pass condition is a 16-byte tag. The finding has to say that chain verification of the equation is unaffected.

### INV-REDEEM-BINDING

- lane: signer
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_signer.py` `validate_redeem_script`

`validate_redeem_script` accepts a redeem only when it hashes to the P2SH20 (HASH160) or P2SH32 (HASH256) script on the spent output, and `validate_multisig_redeem_script` accepts only a standard m-of-n with 33-byte or 65-byte keys and `OP_CHECKMULTISIG`. P2SH-P2PKH and CashScript fail closed. The pass condition is that both checks still run before a redeem is used as `scriptCode`.

### INV-DERIVATION-BINDING

- lane: signer
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_signer.py` `find_derivation_path`

On the first BIP32 derivation whose fingerprint equals `master_fingerprint`, the function returns that path and does not compare `key[1:]` to the derived pubkey. `signed_psbt` then signs with the key at that path and stores the partial signature under the derived pubkey. There is no account-path allowlist. The sighash is still `0x41` or `0x61`, so the signature commits to the transaction that was parsed. The pass condition is: derived pubkey equals the pubkey in the key, and the path is inside the account in `brain/pin.md`.

### INV-SIGNED-PSBT-ROUNDTRIP

- lane: signer
- impact: wysiwys
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_signer.py` `validate_signed_psbt`

After reassembly, the unsigned transaction bytes must match, the output count must match, and each output value and `full_script` must match the reviewed transaction. `clear()` runs in the `finally` of `signed_psbt`. The pass condition is that a signature is not returned when this comparison fails.

### INV-UTXO-REQUIRED

- lane: signer
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_parser.py` `build_transaction`

`build_transaction` raises when `resolve_spent_output` returns nothing. `signed_psbt` still `continue`s when `spent_output` is missing. The pass condition is the raise on the path the UI actually signs, and a re-read that `signed_psbt` cannot be reached without `build_transaction`. If that call order disappears, this row reopens.

### INV-PARENT-TXID

- lane: cashtoken
- impact: wysiwys
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_parser.py` `build_transaction`

When key `0x00` is present, its double-SHA256 is compared to `prev_txid` and a mismatch raises. `resolve_spent_output` does the same comparison only when `prev_txid` is passed in. `build_transaction` calls `resolve_spent_output` without that argument. The pass condition is the raise in the `0x00` loop. Which value is signed when key `0x01` is also present is `INV-WITNESS-UTXO-PRECEDENCE`.

### INV-TOKEN-VARINT

- lane: cashtoken
- impact: invalid-signature
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_parser.py` `read_token_varint`

Token amounts go through `read_token_varint`, which rejects a non-minimal CompactSize. General transaction varints still use `read_varint`. The pass condition is that a token amount cannot be encoded with an overlong length.

### INV-TOKEN-PREFIX-REJECT

- lane: cashtoken
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_parser.py` `parse_transaction`

A script that starts with `0xef` and does not parse as a token raises `invalid token prefix`. `parse_token_script` rejects the reserved capability bit, a capability above 2, a commitment without an NFT, an amount of 0, and a commitment length of 0 or above 40. The pass condition is that those inputs raise before a token object is shown or signed.

### INV-GENESIS-VOUT0

- lane: cashtoken
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/psbt_parser.py` `build_transaction`

An output category that is not on an input is treated as genesis. It is rejected unless some input spends prevout index 0 and that input's reversed prevout txid is the category id. The pass condition is that a new category cannot be signed without such an input.

### INV-KEY36-CROSSCHECK

- lane: cashtoken
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_parser.py` `parse_psbt`

Output key `0x36` has to parse as a token prefix or the parser raises. It is not compared to the token prefix inside the unsigned transaction's script. The pass condition is that a present `0x36` prefix equals the prefix in the output script that will be signed, or that the key is ignored for display.

### INV-NFT-CATEGORY-WALK

- lane: wysiwys
- impact: theft
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/views/psbt_views.py` `PSBTNFTAddressDetailsView.run`

After the last output of the current category, the next category index advances only while `category_num` is below `get_nft_count(self.category_id)` minus one, on the genesis inputs or on the outputs. That count is for the current category. A later category is not opened. Those outputs remain inside `hashOutputs`, so a signature can cover NFT moves the walk never showed. The pass condition is that the walk advances by category, the way the FT walk does, and that every category on an output is shown before the overview.

### INV-FT-CATEGORY-WALK

- lane: wysiwys
- impact: theft
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/views/psbt_views.py` `PSBTAddressDetailsView`

The fungible-token review advances using the length of the category-id list, not the token count inside the current category. The pass condition is that a category after the first is still opened when the first category has a single output.

### INV-PARSE-FULL-CONSUME

- lane: cashtoken
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_parser.py` `parse_transaction`

The function reads a 4-byte slice for locktime and returns. It does not require that the cursor consumed the buffer, and it does not require that four locktime bytes were present. Trailing bytes are ignored. The pass condition is `pos == len(tx_bytes)` after a 4-byte locktime.

### INV-OVERVIEW-AMOUNT

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/views/psbt_views.py` `BCHPSBTOverviewView.run`

The overview screen is called with `inputs_amount=psbt_parser.output_amount`. `output_amount` is the sum of output values, including change. The pass condition is that the headline input amount is `total_input_amount` (or the property the screen actually documents as the sum of inputs).

### INV-BCHAMOUNT-QUANTIZE

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/gui/components.py` `BchAmount.__post_init__`

When `total_sats > 1e8`, the component builds `Decimal(self.total_sats / 1e8)` and quantizes to four decimal places (`Decimal("0.1234")`). Amounts inside the BCH supply fit in the float mantissa; the loss is the four-decimal quantize, which hides a gap under 10000 sats. The pass condition is integer satoshis all the way to the glyph, or a decimal built from the integer with enough places to show one sat.

### INV-CHANGE-DETECTION

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/views/psbt_views.py` `PSBTAddressDetailsView`

No output is re-derived from the seed. Every cashaddr is titled `Will Send`. The pass condition is that an output the loaded seed can spend is labeled as change and is not presented as a payment, or that the UI states in one sentence that change is not detected. Multisig cosigners are `INV-MULTISIG-DISPLAY`.

### INV-MULTISIG-DISPLAY

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_signer.py` `validate_multisig_redeem_script`

The redeem script is checked for template and hash. The review screens do not show the cosigner pubkeys or the m-of-n policy. The pass condition is a screen that shows `m`, `n`, and the cosigner pubkeys before the user can sign.

### INV-LOCKTIME-SEQUENCE-DISPLAY

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/views/psbt_views.py` `BCHPSBTOverviewView.run`

`nLockTime` and the input sequences are inside sighash `0x41` and `0x61`, so they cannot change after a signature. The review screens do not show them. On Bitcoin Cash a sequence is not Core RBF; locktime is active when any sequence is not `0xffffffff`. The pass condition is that locktime, and any sequence that is not final, are shown before the sign button.

### INV-OPRETURN-PATH

- lane: wysiwys
- impact: fail-open
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/controller.py` destination fallback

`PSBTMathView` returns no destination when no cashaddr output exists. The controller maps a missing destination to `NotYetImplementedView`, so an OP_RETURN-only or P2PK-only transaction does not reach signing. When at least one cashaddr exists, OP_RETURN, P2PK, and unknown outputs are shown later via `full_script`. The pass condition is that those outputs cannot be signed unseen. Re-open this row if a cashaddr can be paired with an unseen `full_script`.

### INV-WITNESS-UTXO-PRECEDENCE

- lane: wysiwys
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/psbt_parser.py` `resolve_spent_output`

The resolver returns on the first key `0x00` or key `0x01`. A witness UTXO placed first supplies the value and the script that are displayed and sighashed, even if a parent transaction with the matching txid is also present. BIP-143 commits to that claimed amount, so a lie makes the signature invalid for the real UTXO. This is a display disagreement that fails closed on chain. It is not a valid spend of a different amount. The pass condition is: prefer a parent whose txid matches, and reject the input when both keys exist and disagree.

### INV-CASHADDR-PREFIX

- lane: wysiwys
- impact: wysiwys
- status_at_pin: unchecked
- file_ready: no
- where: `src/seedcash/views/psbt_views.py` address render

The displayed cashaddr prefix (`bitcoincash:` or a test prefix) has to be the prefix for the network whose script will be signed. The pass condition is one network value used both for the glyph and for the script. This row was not finished at the pin.

### INV-COMPACT-SEEDQR

- lane: qr
- impact: custody
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/decode_qr.py` `detect_segment_type`

Any 16-byte QR is `SEED__COMPACTSEEDQR` before a UTF-8 or UR decode is attempted. There is no format magic. `SeedQrDecoder` turns those bytes into a BIP-39 mnemonic. `ScanView.is_valid_qr_type` returns true. The pass condition is that opaque 16-byte input is not a seed unless the user opened an import-seed action and confirmed the words. Subclasses that override `is_valid_qr_type` have to be listed in the finding.

### INV-QR-SHELL

- lane: qr
- impact: airgap
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/helpers/qr.py` `qrimage_io`

`qrimage_io` builds a shell command string and runs it with `subprocess.call(..., shell=True)`. The data argument is interpolated into that string. The process that signs is the process that renders. The pass condition is an argument vector with `shell` left false, and the data passed as one argument. The finding names the call. It does not include a command string.

### INV-BYTEWORDS-CRC

- lane: qr
- impact: wysiwys
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/helpers/ur2/bytewords.py` `decode`

The body checksum is computed and the comparison that would raise `Invalid Bytewords` is commented out. Fountain decode still checks the message CRC on a multipart payload. The pass condition is that the comparison runs for every style, including a single-part UR that never enters the fountain decoder. The finding has to say which of those two paths the auditor re-read.

### INV-FOUNTAIN-SINGLE-PART

- lane: qr
- impact: wysiwys
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/helpers/ur2/ur_decoder.py` `receive_part`

A single-part UR is rejected when a fountain decode is already in progress and not complete. A single-part that arrives before any multipart frame still completes. The pass condition is the mid-stream rejection. Re-open if a completed fountain can still be replaced by a later single-part.

### INV-UR-MAX-SEQ

- lane: qr
- impact: griefing
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/helpers/ur2/fountain_decoder.py` sequence length

`seq_len` has to sit inside `1..MAX_SEQ_LEN`, and `MAX_SEQ_LEN` in `constants.py` is 10000. The pass condition is that a larger declared length is rejected before parts are stored.

### INV-BIP39-NFKD

- lane: custody
- impact: custody
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/models/bip39.py` `generate_hexa_seed`

The mnemonic and the passphrase are UTF-8 encoded and passed to PBKDF2-HMAC-SHA512 (2048 rounds, salt `mnemonic` + passphrase, 64 bytes) with no NFKD normalization. The English wordlist is ASCII, so the mnemonic side is a no-op. A non-ASCII passphrase diverges from BIP-39 and restores to a different seed in a compliant wallet. The pass condition is NFKD on both strings before the encode.

### INV-XPUB-CHECKSUM

- lane: custody
- impact: custody
- status_at_pin: closed
- file_ready: no
- where: `src/seedcash/models/bip44.py` `xpub_decode`

`xpub_decode` and `xpriv_decode` check the 4-byte checksum. The pass condition is that a corrupted xpub or xpriv raises before it is displayed or used as a cosigner.

### INV-SEED-RAM

- lane: custody
- impact: custody
- status_at_pin: unchecked
- file_ready: no
- where: `src/seedcash/models/seed.py` seed object

The seed and the passphrase should exist only in process memory, with no write to the SD card, swap, or a core dump. This row was not finished at the pin. The pass condition is a negative search for seed writes plus the image's swap and core-pattern settings.

### INV-MEMORY-ZEROIZE

- lane: custody
- impact: custody
- status_at_pin: open
- file_ready: no
- where: `src/seedcash/models/psbt_signer.py` `clear`

`clear` drops the Python references to the private key and the chain code. It does not wipe the bytes. CPython does not promise that the heap copies are gone. The pass condition is an explicit wipe of the key material the signer allocated, or a documented acceptance that a powered running device is outside the threat model. This row is not issue-ready: it is inherited by this class of device and needs a design decision, not a one-line patch.

### INV-ENTROPY

- lane: custody
- impact: custody
- status_at_pin: unchecked
- file_ready: no
- where: `src/seedcash/models/bip39.py` `generate_random_seed`

`generate_random_seed` is documented as OS random. The pass condition is `os.urandom` (or an equal CSPRNG) for generated mnemonics, and a separate answer for any dice or camera generator that still exists. Camera entropy mixed with a public serial and `time.time()` would fail this row. It was not finished at the pin.

### INV-KERNEL-NET

- lane: os
- impact: airgap
- status_at_pin: open
- file_ready: yes
- where: `opt/pi0/board/kernel.config` `CONFIG_NET`

The pi0, pi2, pi02w, and pi4 fragments (and their `-dev` boards) contain the line `# CONFIG_NET=y`. That is a comment. The line that disables the stack is `# CONFIG_NET is not set`. `olddefconfig` can turn `CONFIG_NET` back on because the kernel default is enabled. This row is the source fragment only. It is not a measurement of a built image. The pass condition is the `is not set` form in every production fragment, and a built `.config` that matches. The built image is `INV-IMAGE-NET`.

### INV-IMAGE-NET

- lane: os
- impact: airgap
- status_at_pin: unchecked
- file_ready: no
- where: built image `.config`

A flashed image, or the Buildroot output `.config`, has to show networking compiled out and no network init script installed. This row was not finished at the pin. A pass on `INV-KERNEL-NET` does not close this row.

### INV-OS-LAG

- lane: os
- impact: supply-chain
- status_at_pin: open
- file_ready: yes
- where: `brain/pin.md` `os_commit`

At the pin, the app commit is `364cccc` (2026-09-25) and the OS commit is `355b94f8` (2026-06-25). The image that boots is not the app tree that was reviewed. The pass condition is that the OS commit the operator builds is the commit named next to the app commit in the release notes, and that this file's pin records both.

### INV-VERSION-STRING

- lane: os
- impact: display
- status_at_pin: open
- file_ready: yes
- where: `src/seedcash/controller.py` `Controller.VERSION`

`Controller.VERSION` is the string `0.8.6` while `git describe` at the pin is `v.1.0.0-161-g364cccc`. The pass condition is that the string the UI shows is the commit or the release the operator can compare to this repo.

### INV-ECDSA-PIN-MATCH

- lane: os
- impact: supply-chain
- status_at_pin: closed
- file_ready: no
- where: `requirements.txt` `ecdsa`

The app pins `ecdsa==0.18.0`. The OS package `PYTHON_ECDSA_VERSION` at the pin is `0.18.0`. Schnorr nonce generation depends on that library's RFC6979. The pass condition is that the two pins are the same version whenever either file changes.

### INV-ROOT-PROCESS

- lane: os
- impact: airgap
- status_at_pin: open
- file_ready: no
- where: seedcash-os start script

The signer process runs as root. That is the inherited image design. It becomes material together with `INV-QR-SHELL` or with a network stack. The pass condition is an unprivileged user for the Python process, or a written acceptance that stays valid only while `INV-QR-SHELL` and `INV-IMAGE-NET` are closed. Not issue-ready on its own.

### INV-ROOT-SHADOW

- lane: os
- impact: airgap
- status_at_pin: unchecked
- file_ready: no
- where: rootfs overlay `etc/shadow`

The login password and the shadow entry have to be checked on the overlay that the image actually installs. A defconfig password is not the shadow line. This row was not finished at the pin. The pass condition is a locked root password in the installed shadow, and no network service that could use a password.

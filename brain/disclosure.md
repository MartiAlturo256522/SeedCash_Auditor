# Disclosure

This file is the only writing rule for findings, reports, and GitHub issues.

A finding has all of these, and nothing else:

- The check that is missing or wrong, named as a function and a condition.
- The impact class, taken from the enum in `schemas/finding.schema.json`.
- The file and the function.
- The commit that was open while the lines were read.
- A fix direction: the condition the code should enforce.
- A short quotation of the check itself, enough to find it again.

A finding does not include:

- A transaction, script, or QR that triggers the check.
- A command line, a shell metacharacter sequence, or a payload.
- A section titled with reproduction, proof of concept, exploit, or payload.
- A guess copied from a commit message, a docstring, or an older report. The lines win.

Impact classes mean:

- `theft` — a valid signature can move funds or tokens the user was not shown.
- `wysiwys` — the screen and the bytes that get signed disagree, whether or not the resulting transaction confirms.
- `invalid-signature` — the device produces a signature that honest consensus will reject.
- `griefing` — the device refuses, loops, or emits an unconfirmable transaction, and funds stay put.
- `fail-open` — an error path continues into signing or into a weaker review.
- `custody` — a seed, passphrase, or backup restores to a different key than the user expects.
- `airgap` — a path onto or off the device that is not the camera and the display.
- `supply-chain` — the image, the package pin, or the boot config can differ from the tree that was read.
- `spec-deviation` — the bytes differ from the cited consensus or BIP rule, and chain validity still needs a separate sentence.
- `display` — a label, version, or amount is wrong, and the signed bytes are unaffected.

When a class is `spec-deviation` or `invalid-signature`, the finding says whether an honest node still accepts the signature. Those two classes are not `theft`.

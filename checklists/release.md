# Release checklist

Run this before an image is handed to someone who will load a seed. The checks themselves stay in `brain/invariants.md`. This list is only the order.

1. `python3 tools/lint_brain.py` exits 0.
2. `git rev-parse HEAD` in the app tree and in the OS tree. Write both into `brain/pin.md` if they moved, in the same commit as any invariant you reclassified.
3. Run `reverify-corpus` against those two trees. A row that flips from `open` to a real pass gets `status_at_pin: closed` only after you have read the function.
4. Run `audit-seedcash` when the app commit moved by more than a reverify, or when `closed` signer, CashToken, or QR rows might have been touched.
5. `Controller.VERSION` equals the release the user can see (`INV-VERSION-STRING`).
6. `requirements.txt` `ecdsa` and the OS `PYTHON_ECDSA_VERSION` are the same (`INV-ECDSA-PIN-MATCH`).
7. The production kernel fragments use `# CONFIG_NET is not set`, and a built `.config` was opened for `INV-IMAGE-NET`.
8. No confirmed finding with `issue_ready` true is left undrafted. Drafts stay drafts until `brain/issue-policy.md` is satisfied.

An image built from an OS commit older than the app commit you reviewed does not close `INV-OS-LAG`.

# Review layers

Three read-only layers run after the specialist lanes, in this order. Each layer sees only the findings the previous layer kept. The workflow drops a finding when a layer is missing, fails, sets `keep` false, or returns empty `evidence`. A drop is not a pass, and it is not a license to rewrite the finding into a different bug.

None of these layers writes a triggering transaction, a command, or a payload. The impact classes are defined in `brain/disclosure.md`.

### Quote

Question: is the broken check still in the named function?

Open the finding's file under `target_root`. If that path is not there, open it under `os_root`. `keep` is true only when `evidence` quotes the lines that make the check fail. `keep` is false when the function now implements the check, when the quote is not in the file, or when the file cannot be opened.

This layer does not judge severity and does not trace callers.

### Reach

Question: can that check affect a signature, a seed, or the air gap on a path a user can hit?

Do not re-litigate the quote. Read callers with grep. `keep` is true only when `evidence` names the caller or the image path that was opened.

`keep` is false when a parser or the controller rejects the input before signing, when the branch is dead, or when the behavior is not in this tree. A SeedSigner behavior that this tree removed is a false positive.

An `os` finding is reached through the image build: the kernel fragment, the start script, or the package pin. Do not drop it for lack of a Python caller.

### Impact

Question: does the impact class match `brain/disclosure.md` for the fate of the signature?

Do not re-open the quote or the reach. `keep` is false when the class overclaims:

- A signature that honest consensus rejects is `wysiwys` or `invalid-signature`, not `theft`.
- A tag or encoding difference that still verifies is `spec-deviation`, not `theft`.
- A version string or label that does not change the signed bytes is `display`.
- A note whose invariant says `file_ready: no` stays a note. Do not promote it to `theft`.

When the bug is real and the class is one step too hot, `keep` is true and `impact_class` is the honest class from the disclosure enum. An empty or invented class leaves the specialist's class unchanged. `evidence` names the disclosure rule that was applied.

`issue_ready` stays false when the finding already has it false, and becomes false when the invariant says `file_ready: no`. This layer does not turn it true. Quote and Reach copy `issue_ready` through and leave `impact_class` empty.

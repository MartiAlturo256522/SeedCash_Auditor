# SeedSigner lessons

What years of SeedSigner review taught this project to re-check. The experience perspective reads this file, then the public issues and discussions on `SeedSigner/seedsigner`. A lesson is a check to compare. It is not a procedure.

Copy a conclusion, a file, and a fix direction. Do not copy a reproduction, a command, or a payload from an issue or a forum post.

- Multisig change classification can fail open when the global xpubs are missing or do not derive, and a same-shaped output is treated as change before the descriptor is checked.
- A legacy input that never verifies the previous output can show a fee the signed bytes do not match.
- An OP_RETURN display that assumes one push opcode can hide the rest of the script.
- A settings QR that fills omitted keys with defaults can change the network and silence a seed warning.
- A QR renderer that builds a shell command can mix untrusted bytes into the signer process. The finding names the call.
- CompactSeedQR has no magic. Any 16 bytes can be treated as entropy if the decoder runs before the user asked to import a seed.
- A BIP-39 passphrase that is not NFKD-normalized restores to a different seed in a wallet that follows the BIP.
- A kernel line that is only a comment does not disable the network stack. The image, not the comment, is the air gap.
- A version string that is not the commit on the device makes two builds look like one.
- Dropping a Python reference is not a wipe of key material.
- Entropy mixed with a public serial or the wall clock is not a seed generator.
- The animated QR that leaves the device is the signed transaction. The seed QR is a different, inbound type. An encoder that accepts a seed object on the outbound path is the bug.

When SeedSigner closed one of these and SeedCash still has it, the finding stays open and names the lesson. When SeedCash already enforces it, the finding is a false positive.

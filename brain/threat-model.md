# Threat model

SeedCash is a Bitcoin Cash air-gapped signer. The seed is supposed to live in RAM. The camera is the data input. The display is the data output. A coordinator the user does not trust builds the PSBT.

## Assets

- The seed and the passphrase.
- A signature that honest BCH consensus will accept.
- The equality between the screen and the bytes inside that signature.
- The air gap of the running image.

## Adversaries

- A coordinator that builds a hostile PSBT or a hostile UR.
- A QR in the room that is not the PSBT the user meant to scan. Any 16-byte payload is in this class. See `INV-COMPACT-SEEDQR`.
- A person who can change the SD card, the Buildroot config, or a vendored Python package.
- A person with the running device. A person with the powered-off device is in scope only for "is the seed still on the card".

## Load-bearing assumptions

Each one is an invariant, not a slogan. The lane that owns it is in `brain/invariants.md`.

- Sighash is only `0x41` or `0x61`, so the signature commits to every output.
- The review walks every output the sighash commits to.
- Amounts and scripts on the screen are the amounts and scripts inside the preimage.
- The seed leaves the device only as a signature, and only by QR.
- The running image has no network stack. A comment in `kernel.config` is not that proof.

## What this model does not cover

Breaking BCH consensus, glitching the chip, and stealing a seed the user never loaded. Those are named here so a hunt does not wander into them and call the gap a SeedCash bug.

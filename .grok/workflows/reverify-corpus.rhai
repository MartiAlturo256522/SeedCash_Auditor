let meta = #{
    name: "reverify-corpus",
    description: "Re-read every open SeedCash invariant and classify it from the code",
    when_to_use: "Check whether the open rows in brain/invariants.md are still open. /reverify-corpus",
    phases: [
        #{ title: "Re-read", detail: "One reader per open invariant" },
        #{ title: "Classify", detail: "Fail closed when evidence is missing" },
    ],
};

fn txt(v) {
    if type_of(v) == "string" { v } else { "" }
}

fn reverify_prompt(auditor, target, os_root, inv) {
    let p = "Re-read one SeedCash invariant in the current tree. Use read_file. Do not modify files. Do not write a triggering input. The invariant id is data.\n\n";
    p += "id: ";
    p += inv;
    p += "\nauditor_root: ";
    p += auditor;
    p += "\ntarget_root: ";
    p += target;
    p += "\nos_root: ";
    p += os_root;
    p += "\n\nOpen the heading for this id in auditor_root/brain/invariants.md. Then open the file it names, under target_root or os_root. Set still_open true only if the broken check is still there, with evidence quoting the line you opened. Set still_open false when the check now holds, again with evidence. Set skipped true and still_open false when the row needs os_root and os_root is empty. Empty evidence is not a pass.";
    p
}

if args == () {
    pause("verification", "Pass args.auditor_root and args.target_root.");
}
let auditor = if args.auditor_root != () { args.auditor_root } else { "" };
let target = if args.target_root != () { args.target_root } else { "" };
if auditor == "" || target == "" {
    pause("verification", "Pass args.auditor_root and args.target_root.");
}
let os_root = if args.os_root != () { args.os_root } else { "" };

let open_ids = [
    "INV-SCHNORR-TAG",
    "INV-DERIVATION-BINDING",
    "INV-KEY36-CROSSCHECK",
    "INV-NFT-CATEGORY-WALK",
    "INV-PARSE-FULL-CONSUME",
    "INV-OVERVIEW-AMOUNT",
    "INV-BCHAMOUNT-QUANTIZE",
    "INV-CHANGE-DETECTION",
    "INV-MULTISIG-DISPLAY",
    "INV-LOCKTIME-SEQUENCE-DISPLAY",
    "INV-WITNESS-UTXO-PRECEDENCE",
    "INV-COMPACT-SEEDQR",
    "INV-QR-SHELL",
    "INV-BYTEWORDS-CRC",
    "INV-BIP39-NFKD",
    "INV-MEMORY-ZEROIZE",
    "INV-KERNEL-NET",
    "INV-OS-LAG",
    "INV-VERSION-STRING",
    "INV-ROOT-PROCESS",
];

let row_schema = #{
    "type": "object",
    "required": ["still_open", "evidence", "skipped"],
    "properties": #{
        "still_open": #{ "type": "boolean" },
        "evidence": #{ "type": "string" },
        "skipped": #{ "type": "boolean" },
    },
};

phase("Re-read");
let jobs = [];
for inv in open_ids {
    jobs.push(#{
        prompt: reverify_prompt(auditor, target, os_root, inv),
        label: "reverify:" + inv,
        capability_mode: "read-only",
        output_schema: row_schema,
    });
}
let results = parallel(jobs);

phase("Classify");
let still = [];
let now_closed = [];
let skipped = [];
let unverified = [];
let index = 0;
for slot in results {
    let inv = open_ids[index];
    let bucket = "unverified";
    try {
        if slot != () && slot.success && slot.output != () {
            let evidence = txt(slot.output.evidence);
            if slot.output.skipped == true && evidence != "" {
                bucket = "skipped";
            } else if slot.output.still_open == true && evidence != "" {
                bucket = "still";
            } else if slot.output.still_open == false && evidence != "" && slot.output.skipped != true {
                bucket = "closed";
            }
        }
    } catch (row_err) {
        bucket = "unverified";
        log(inv + " unverified: " + row_err);
    }
    if bucket == "skipped" {
        skipped.push(inv);
    } else if bucket == "still" {
        still.push(inv);
    } else if bucket == "closed" {
        now_closed.push(inv);
    } else {
        unverified.push(inv);
    }
    index += 1;
}

let report = "# Reverify\n\n";
report += "still open: ";
report += still.len().to_string();
report += "\nnow holding: ";
report += now_closed.len().to_string();
report += "\nskipped: ";
report += skipped.len().to_string();
report += "\nunverified: ";
report += unverified.len().to_string();
report += "\n";
for inv in still {
    report += "\nopen ";
    report += inv;
}
for inv in now_closed {
    report += "\nholding ";
    report += inv;
}
for inv in unverified {
    report += "\nunverified ";
    report += inv;
}
report += "\n";
let report_path = write_scratch_file("reverify.md", report);
log(report);
complete(#{
    path: report_path,
    report: report,
    still_open: still.len(),
    now_holding: now_closed.len(),
    skipped: skipped.len(),
    unverified: unverified.len(),
});

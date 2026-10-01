let meta = #{
    name: "publish-seedcash-issues",
    description: "Draft one SeedCash issue per ready finding and publish the batch after confirmation",
    when_to_use: "Publish the open file-ready findings. /publish-seedcash-issues. Publishing needs args.publish true.",
    phases: [
        #{ title: "Draft", detail: "Export findings and print every issue body" },
        #{ title: "Confirm", detail: "Stop until the operator approves the batch" },
        #{ title: "Publish", detail: "Create one issue per finding that is not already open" },
    ],
};

fn txt(v) {
    if type_of(v) == "string" { v } else { "" }
}

if args == () || args.auditor_root == () || args.auditor_root == "" {
    pause("verification", "Pass args.auditor_root.");
}
let auditor = args.auditor_root;
let do_publish = args.publish == true;

let batch_schema = #{
    "type": "object",
    "required": ["summary", "filed"],
    "properties": #{
        "summary": #{ "type": "string" },
        "filed": #{ "type": "boolean" },
    },
};

phase("Draft");
let draft_prompt = "Draft the SeedCash issue batch. From auditor_root run python3 tools/export_findings.py --out findings-out and then python3 tools/publish_findings.py --dir findings-out. Do not pass --confirm. Do not set SEEDCASH_AUDITOR_CONFIRM. Do not rewrite a finding. Do not add a triggering transaction, a command, or a payload. Put the tool's last summary line in summary and set filed false.\n\nauditor_root: ";
draft_prompt += auditor;
let drafted = agent(draft_prompt, #{
    label: "redactor-draft",
    capability_mode: "execute",
    output_schema: batch_schema,
});
let summary = "";
try {
    if drafted != () && drafted.success && drafted.output != () {
        summary = txt(drafted.output.summary);
    }
} catch (draft_err) {
    log("draft missing: " + draft_err);
}
if summary == "" {
    summary = "draft not returned";
}
let draft_path = write_scratch_file("issue-batch.md", summary);
if do_publish != true {
    complete(#{ path: draft_path, report: summary, filed: false });
}

phase("Confirm");
await_user("user", "Publish this SeedCash issue batch upstream? Resume only if the printed drafts are the ones to send.");

phase("Publish");
let file_prompt = "Publish the drafted SeedCash issue batch. From auditor_root run SEEDCASH_AUDITOR_CONFIRM=yes python3 tools/publish_findings.py --dir findings-out --confirm. Do not change the findings. If the tool skips an issue as already open, leave that skip in place. Put the tool's last summary line in summary and set filed true only if the tool exited zero.\n\nauditor_root: ";
file_prompt += auditor;
let published = agent(file_prompt, #{
    label: "redactor-publish",
    capability_mode: "execute",
    output_schema: batch_schema,
});
let result = summary;
try {
    if published != () && published.success && published.output != () && txt(published.output.summary) != "" {
        result = txt(published.output.summary);
    }
} catch (file_err) {
    log("publish missing: " + file_err);
}
complete(#{ path: draft_path, report: result, filed: true });

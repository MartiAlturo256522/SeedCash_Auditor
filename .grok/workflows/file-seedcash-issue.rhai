let meta = #{
    name: "file-seedcash-issue",
    description: "Draft one SeedCash audit issue and file it only after confirmation",
    when_to_use: "Draft or file one confirmed finding. /file-seedcash-issue with args.finding. Filing also needs args.file true.",
    phases: [
        #{ title: "Draft", detail: "Render the issue from the finding" },
        #{ title: "Confirm", detail: "Stop until the operator approves the draft" },
        #{ title: "File", detail: "Call gh through the dry-run tool" },
    ],
};

fn txt(v) {
    if type_of(v) == "string" { v } else { "" }
}

if args == () {
    pause("verification", "Pass args.auditor_root and args.finding.");
}
let auditor = if args.auditor_root != () { args.auditor_root } else { "" };
let finding = if args.finding != () { args.finding } else { "" };
if auditor == "" || finding == "" {
    pause("verification", "Pass args.auditor_root and args.finding.");
}
let repo = if args.repo != () { args.repo } else { "" };
let do_file = args.file == true;

let issue_schema = #{
    "type": "object",
    "required": ["title", "body", "issue_ready", "refuse_reason"],
    "properties": #{
        "title": #{ "type": "string" },
        "body": #{ "type": "string" },
        "issue_ready": #{ "type": "boolean" },
        "refuse_reason": #{ "type": "string" },
    },
};

phase("Draft");
let prompt = "Draft one SeedCash issue by running the repo tool, not by rewriting the finding. From auditor_root run python3 tools/file_issue.py --finding <the finding path>. Do not pass --confirm. Do not set SEEDCASH_AUDITOR_CONFIRM. If the tool prints refused, set issue_ready false and put that line in refuse_reason. If the tool prints a title and a body, copy the title and the body through, and set issue_ready true. Do not add a section the tool did not print.\n\n";
prompt += "auditor_root: ";
prompt += auditor;
prompt += "\nfinding: ";
prompt += finding;
prompt += "\nrepo: ";
prompt += repo;
let clerk = agent(prompt, #{
    label: "issue-clerk",
    capability_mode: "execute",
    output_schema: issue_schema,
});

let title = "";
let body = "";
let ready = false;
try {
    if clerk != () && clerk.success && clerk.output != () {
        title = txt(clerk.output.title);
        body = txt(clerk.output.body);
        if clerk.output.issue_ready == true {
            ready = true;
        }
        if txt(clerk.output.refuse_reason) != "" {
            log("clerk: " + txt(clerk.output.refuse_reason));
        }
    }
} catch (draft_err) {
    log("clerk output missing: " + draft_err);
}
if title == "" {
    title = "undrafted";
}
let draft = "# ";
draft += title;
draft += "\n\n";
draft += body;
draft += "\n";
let draft_path = write_scratch_file("issue-draft.md", draft);
log("draft written");

if do_file != true {
    complete(#{ path: draft_path, report: draft, filed: false, title: title });
}
if ready != true {
    log("not filing: the draft tool did not mark the issue ready");
    complete(#{ path: draft_path, report: draft, filed: false, title: title });
}

phase("Confirm");
await_user("user", "File this drafted SeedCash issue upstream? Resume only if this draft is the one to send.");

phase("File");
let file_prompt = "File one already drafted SeedCash issue by running the repo tool. From auditor_root run: SEEDCASH_AUDITOR_CONFIRM=yes python3 tools/file_issue.py --finding <finding>";
if repo != "" {
    file_prompt += " --repo ";
    file_prompt += repo;
}
file_prompt += " --confirm\nDo not change the finding. If the tool prints refused, stop and report that text.\n\nauditor_root: ";
file_prompt += auditor;
file_prompt += "\nfinding: ";
file_prompt += finding;
let filed = agent(file_prompt, #{
    label: "issue-filer",
    capability_mode: "execute",
});
let filed_text = "";
try {
    if filed != () && filed.success {
        filed_text = txt(filed.output);
    }
} catch (file_err) {
    log("filer failed: " + file_err);
}
complete(#{ path: draft_path, report: draft, filed: true, title: title, result: filed_text });

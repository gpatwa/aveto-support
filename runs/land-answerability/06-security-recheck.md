# Stage 7: Security re-check (land-answerability)

- Role: Security & Privacy. Depth: **standard** (Charter C7.1, not lowered).
- Base: `bca0e40` (slice 7's review base). Head: `14303a0` (branch `claude/land-answerability`).
- Scope: the S5 fix (`.claude/skills/aveto-judge-seen/SKILL.md`, `seen_payload.py`, `tests/test_judge_seen_skill.py`) and every non-run file changed since `bca0e40`.
- Not done, by the brief: no judge or model spawn, no gate re-run, no code change, no commit, no push.

## 1. Evidence

### 1.1 Invariants and method files
- `.agentic/SAFETY_INVARIANTS.md` vs `git show bca0e40:.agentic/SAFETY_INVARIANTS.md`: `cmp` reports **identical**; sha256 `8900da14fe2672752c6145d3be53db33584637a68cbc5b232388dcd0748d11fd` for both. INV-4 and INV-5 are byte-identical to slice 7's approved text (Charter C5.1, C5.2 hold). No diff to report.
- `git diff --stat bca0e40 HEAD -- <path>` is **empty** for: `aveto_support/judge.py`, `aveto_support/judge_eval.py`, `aveto_support/__main__.py` (whole file, so the judge parts too), `tools/judge_run.py`, `prompts/`, `.claude/agents/aveto-answerability-judge.md`, `.claude/skills/aveto-judge/`. The same command over `aveto_support tools prompts index .claude/hooks pyproject.toml uv.lock .gitignore` is also empty.
- Non-run code/config changed since `bca0e40`: `.claude/skills/aveto-judge-seen/{SKILL.md,seen_payload.py}` (the S5 fix), `.claude/agents/release-manager.md` (+13, pack v23 from `main`; `git diff main HEAD -- .claude/agents/release-manager.md .claude/protocols .claude/commands .claude/agentic.config.json` is empty, so it is identical to `main`), `evals/retrieval-heldout-5*.toml` (slice 7's fifth set, commits `b692ffc`, `c0da63e`, `9b28c08`, data, not this slice's).
- `.claude/settings.json`: `cmp` against `git show main:.claude/settings.json` reports **identical** (code-review F1 fix holds). Its only change since `bca0e40` is main's `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

### 1.2 The S5 fix
- `SKILL.md:9` is now `` !`uv run -q --project "${CLAUDE_PROJECT_DIR}" python "${CLAUDE_SKILL_DIR}/seen_payload.py"` ``: no `$ARGUMENTS`, no `$0`, no quote around caller text. `allowed-tools` lost its trailing ` *`.
- It is the **only** `!` shell line in `.claude/skills`, `.claude/commands`, `.claude/agents` (grep for `` !` `` and `$ARGUMENTS`/`$N`). The other `$ARGUMENTS` uses (`/aveto-judge` prompt text, `agentic-*` commands) are prompt text, not shell, and `/aveto-judge` is unchanged since `bca0e40`.
- `seen_payload.py`: any argv refused with a fixed line, exit 2. The id comes only from `.aveto-judge/seen-id` (gitignored, `.gitignore:17`, `git check-ignore` confirms). `read_id` refuses a symlink, a non-regular file, non-ASCII, and over 64 bytes; `prepare` refuses CR/LF, anything not `^r[0-9]{3}$` (fullmatch), and ids not in `key.toml`, before any write. The only subprocess is a fixed argv list with no shell.
- Harness behaviour (read from the installed Claude Code 2.1.302 binary with `strings`, not executed): when a skill has no `$ARGUMENTS` placeholder, the harness appends `ARGUMENTS: <args>` to the skill text **before** it extracts `` !` `` commands, but each substituted or appended argument goes through an escaper (`zP`) that rewrites `` !` `` to `` ! ` `` and a leading `!` to `\!`, and is wrapped in sentinel characters. So in this version an argument cannot form a new shell line. See A2.

### 1.3 Hostile-id probes (scratchpad script, helper imported, temp dirs only)
| input in `seen-id` | result |
|---|---|
| fullwidth digits `r１０１`, Arabic-Indic digits, BOM prefix | refused (ASCII decode) |
| `r101\0`, `r101\r\n`, `r101\n\n`, ` r101` | refused (regex) |
| 64 bytes (`r101` + 60 LF), 65 bytes, 1 MB | refused |
| `../../etc/passwd`, `/etc/passwd` | refused (regex; no path built from it) |
| directory, FIFO (no hang), symlink to `/dev/stdin` | refused |
| `r101`, `r101\n` | accepted, writes `q/r101.txt` only |
| `seen-id` inside a symlinked parent directory | followed; content still validated (A3) |
| pre-planted symlink at `q/r102.txt` | followed: target overwritten with the committed public question text (A3, unchanged since slice 7) |

`uv run pytest tests/test_judge_seen_skill.py`: **73 passed, 2 deselected** (the `model`-marked ones). See R1 for one case that passes for the wrong reason.

### 1.4 `.aveto-judge/seen-id` abuse
- Whoever can write it (the operator, or a session with Write) can only select one of the committed key ids; the question text comes from the committed batch file, never from `seen-id`. The worst effect is choosing a different committed public eval question: an eval-integrity matter, not a security one, and stage 7 attributes every scored transcript by exact payload hash.
- `judge-apply` deletes only the files it is named (`delete_transport_files`, unchanged), so a leftover `seen-id` neither breaks nor is read by the product.

### 1.5 Secrets, PII, permissions
- Committed non-run files in the diff (20): no e-mail address, no API-key/JWT/AWS/GitHub/Slack/private-key pattern, no UUID. `runs/land-answerability/`: none either. Over all added lines since `bca0e40`: 0 key-like strings; the owner's e-mail appears nowhere; the only UUIDs are Claude Code session/scratchpad ids in slice 7's run records, already classified "not credentials" by slice 7's review (section 7 there).
- No `.env`, credential or key file added; `settings.local.json` is not committed.
- S6: no `seen_payload` permission rule exists in any settings file under `/Users/gopalpatwa/opt/aveto-support/.claude/` (worktrees included) or `~/.claude/settings.json`; the main checkout has no `settings.local.json`. The worktree's `.claude/settings.local.json` (gitignored) holds exactly the C6.P list. See A4.

### 1.6 Docs claims about S5 and S6
- README:181-184, `CURRENT_MVP_STATUS.md`:54-56, `ARCHITECTURE.md`:20, 169-171, 239-240, runbook:14-17: "S5 fixed, `/aveto-judge-seen` takes no caller text, write the id to `.aveto-judge/seen-id`, run with no argument, `/aveto-judge` unchanged" is **true** (1.1, 1.2). "The S6 rule was deleted" is **true** (1.5).
- Stale but not false: runbook item 6 (line 63) still says "`.claude/settings.local.json` (S6) ... Removing it is the owner's", and ADR 0008:27 still shows `/aveto-judge-seen <run id>` as the registered usage (A5).

## 2. Findings

| id | severity | file:line | what | suggested fix (engineers own it) |
|---|---|---|---|---|
| R1 | **required-fix** (not a security hole; fix before the PR is opened) | `tests/test_judge_seen_skill.py:105` (`"r001\n"` in `HOSTILE`), used by `test_refuses_bad_ids` (`:131-140`) | `"r001\n"` is a value the helper **accepts by design** (`read_id` strips one trailing LF, `test_read_id_accepts_one_trailing_newline`). The case passes only because `judge-input` then fails in this worktree, which has no `index/` or `models/` (`refused: judge-input failed (exit 2)`). Probe with the main checkout's `index/` and `models/` linked in: `main([], seen-id="r001\n")` prints the payload and returns **0**. So on a checkout that has them (the owner's main checkout does) this case fails, and on every run it calls `main` with the default `SEEN`, writing the committed `runs/docs-answerability-2/judge-check/q/r001.txt` (same bytes, so `git status` stays clean) and starting the product's `judge-input`. 01-s5-fix.md's "22 hostile values ... no q/ file" is untrue for this case. REVIEW.md's "a test that passes without asserting what its name says". | Drop `"r001\n"` from `HOSTILE` (it is covered as an accepted value by `test_read_id_accepts_one_trailing_newline`), or keep it out of the refusal tests. Optionally make `main` take `seen` so the refusal tests cannot reach the real tree. Within Charter C5.3 (tests). |
| A1 | advisory | `.claude/skills/aveto-judge-seen/SKILL.md:7` | `allowed-tools: Bash(uv run -q --project * python ${CLAUDE_SKILL_DIR}/seen_payload.py)` keeps a wildcard **inside** the command (REVIEW.md's S6 class). By the documented `*` semantics it pre-approves e.g. `--project /any --with <pkg>` or `--python /any`, i.e. arbitrary code. Not reachable today: the only command run under it is the fixed `!` line, the forked judge has no Bash (deny list + hook), and arguments cannot form a `!` line (1.2). Pre-existing from slice 7; this slice narrowed it (trailing `*` removed). | A later slice pins it (e.g. the literal project path, or drop `--project` and rely on cwd). |
| A2 | advisory | `01-s5-fix.md:8`, `tests/test_judge_seen_skill.py:175-202` | "No harness substitution behaviour is relied on" is slightly overstated. The template has no caller text, but Claude Code still **appends** `ARGUMENTS: <args>` to the skill text before extracting `` !` `` lines; it is the harness's own escaping (Claude Code 2.1.302, read from the binary, not executed) that stops an argument such as `` !`cmd` `` from becoming a shell line. `test_shell_line_has_no_caller_text` replaces `$ARGUMENTS` in the template only, so it cannot show the appended line is inert. Residual is small: even if an injected line ran, it would need to match A1's rule to skip the prompt. | Record the reliance in the end review; optionally add `disable-model-invocation: true` in a later slice so only the operator's typing reaches the skill (S4/F12 stays as slice 7 left it). |
| A3 | advisory | `seen_payload.py:59-61`, `:79` | `prepare` writes `q/<id>.txt` with `write_text`, which follows a pre-planted symlink (probe: target overwritten with the public question text). `read_id` checks only the last path component for a symlink, and `is_symlink`/`open` is a check-then-use pair. All need a local writer already in the tree; the id content is still validated, and the written text is committed public eval data. Unchanged since slice 7 (the `q/` write) apart from `read_id`. | A later slice opens with `O_NOFOLLOW` (as `judge.read_reply` does) for both the id read and the `q/` write. |
| A4 | advisory | `.claude/settings.local.json` (worktree, gitignored, Charter C6.P) | The run's local rules include `Bash(uv run pytest *)` (runs any Python file without a prompt: `uv run pytest /any/file.py`), `Bash(git branch *)` (includes `-D`) and `Bash(git diff *)` (`--output=<path>` writes files). Same class as S6 (arbitrary code without a prompt in a session that reads untrusted payloads), owner-approved by C6.P, not shipped (code-review F1 moved it out of `settings.json`). | Delete the file when the run ends; say so in the end review. |
| A5 | advisory | `docs/runbooks/answerability-judge.md:63`; `docs/adr/0008-operator-run-answerability-judge.md:27` | Runbook rollback item 6 still names `settings.local.json` as "(S6)"; the S6 rule is gone and the file now holds the C6.P rules. ADR 0008 still shows `/aveto-judge-seen <run id>`. Neither is false about the shipped code's safety; both mislead a later reader. | Reword item 6 ("the run's local rules, C6.P; S6's rule was deleted 2026-10-16"); add a one-line note to ADR 0008 that the seen skill now reads `.aveto-judge/seen-id`. |

No blocker.

## 3. Confirmations

- **Safety invariants the slice touches:** INV-4 and INV-5 are byte-identical to `bca0e40` and still true as worded; the S5 qualification slice 7 put on INV-5 ("only for a question its key file lists by run id") now holds without depending on how the harness quotes an argument (subject to A2). INV-1 (nothing posts): no product code changed. INV-3: untouched.
- **Audit events:** none removed or weakened. The product is unchanged; the helper still writes `q/<id>.txt` and discards `judge-input`'s stderr as before; refusals stay one fixed line on stdout and stderr with exit 2.
- **Adapter boundary:** no placeholder became a real client; no model client, network call or dependency added. The judge stays `claude-sonnet-5-5`, zero tools (agent file unchanged).
- **Agentic surfaces:** caller text no longer reaches a shell (1.2); `seen-id` is data validated before use (1.3, 1.4); no tool was added to any agent; the forked skill's permission is A1's, unchanged in reach.
- **Secrets / PII:** none in the diff (1.5).
- **Charter C5.3:** the skill changes stay within "remove caller text from the `!` line" plus the tests; every other method file is byte-identical to `bca0e40`.

## 4. Verdict

**PASS. Go to the Release Gate.** No blocker. R1 is a required fix to a test, not to a safety property: it should be fixed before the pull request is opened, or the end review must say why not, because it fails on a checkout that has `index/` and `models/`. A1 to A5 go to the end review and a later slice.

## Handoff

- **To:** Release Manager (Release Gate, tier 3).
- **Read:** this file; R1 (track it as fixed with its commit, or carried with a reason); A2 and A4 for the end review.
- **Not done here:** no harness run of the skill, no spawn, no gate re-run, no code change, no commit, no push.

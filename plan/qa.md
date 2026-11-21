# BLOG quality assurance

A fresh session on the Mac Mini checks the default branch. The QA report identifies the tested commit. The issue for each check includes the steps and expected results.

## Requirements

| ID | Expected result | Source | Evidence |
|---|---|---|---|
| FR-01 | Each open item has one GitHub issue. The Inbox keeps its original text. | [Business case §4](00-business-case.md#s4), SC1 | #139 compares the old rows, live issues and Inbox |
| FR-02 | The audit comment and decision log preserve Pascal’s answers. The agent guide points to the current queue. | [§3](00-business-case.md#s3), SC2 | #139 follows the route and opens the decision links |
| FR-03 | A fresh preview serves each verification URL. The menu opens at 639 px and gives way to the desktop links at 640 px. | [§7](00-business-case.md#s7), [§8](00-business-case.md#s8), SC7 | #142 checks both widths and six feature recipes |
| NFR-01 | The Mini builds a fresh checkout with the locked dependencies. | [§7](00-business-case.md#s7), SC7 | #135 provides setup. Each W01 QA session verifies the checkout |
| FR-04 | A green signoff applies only to its exact commit. A different head still runs the required checks. | [§8](00-business-case.md#s8), SC8 | #144 and #146 exercise the merge fixtures |
| FR-05 | A completed deployment reports the expected commit. A different or missing commit fails verification. | [§8](00-business-case.md#s8), SC8 | #146 checks the provider fixtures without deploying |
| FR-06 | A completed production deployment that waits for a result also checks the public site. A failed live check produces a failure. | [§8](00-business-case.md#s8), SC8 | #146 combines provider fixtures with read-only public requests |
| FR-07 | The disabled edit link disappears. The five Ghost scripts remain available in the archive with their history. | [§7](00-business-case.md#s7), SC6 | #141 checks a built page, the schema and the archive |
| FR-08 | The five unused public images disappear. A new unreferenced public image fails the image check. | [§7](00-business-case.md#s7), SC6 | #141 exercises the image check with a scratch copy |
| FR-09 | Both themes meet the text contrast threshold. Interface labels use Québec French. The gallery renders cleanly. | [§5](00-business-case.md#s5), SC3 | W02 screenshots and emitted interface checks |
| FR-10 | Each of the 41 old event URLs leads to its own existing article. | [§5](00-business-case.md#s5), SC4 | W02 local redirect checks and W02B public checks |
| FR-11 | Published articles expose the selected language. The six vacancies keep their pages. The home page features the selected five posts. | [§6](00-business-case.md#s6), SC5 | W02 compares #149 with rendered pages, listings, RSS and search |
| FR-12 | Each editorial rule names the check that enforces it. | [§9](00-business-case.md#s9), SC9 | W02 cross-checks the public guide against the named checks |
| FR-13 | The authorized revision matches the provider record. Public URLs pass their checks. | [§10](00-business-case.md#s10), SC10 | W02B records the commit and the public results |
| FR-14 | Later work has one issue per outcome and a defined proof before implementation. | [§11](00-business-case.md#s11), SC11 | #139 checks the queue. W03 and W04 define feature checks at their reviews |

## Environments

| Environment | Use | Access and tools |
|---|---|---|
| Mac Mini | Independent QA on a clean checkout of the default branch | Fleet QA role, GitHub CLI, Git, Just, Node, Bun and uv. Issue #135 verifies the versions and Chromium launch |
| Local preview on the Mini | Reader checks and browser evidence | [verify-blog](../.claude/skills/verify-blog/SKILL.md) starts the preview and reports its URL |
| Local provider fixtures | Merge, deploy and failure cases | The script tests use fixture sites and simulated provider responses |
| Public site | Read-only release evidence | The public checks use HTTP. The deployment record supplies the commit |

## Steps

Run only the rows for the QA issue under test. The feature recipes live under `.claude/skills/verify-blog/features/`. Run the commands from the checkout root.

| Step | After | Check | Expected result |
|---|---|---|---|
| Prepare | #135 | In a fresh Mini checkout of the default branch, run `git rev-parse HEAD` and `bun install --frozen-lockfile --ignore-scripts` | The report names the commit. Installation succeeds |
| Baseline | Prepare | `just check` | Exit 0 |
| Queue | Baseline | Run the six queue and decision checks in #139 | Every old row has a disposition. Each historical decision links its evidence |
| Merge and deploy | Baseline | `just check --only scripts` and the individual checks in #144 or #146 | Matching and mismatched commit cases produce their specified results |
| Public reads | Merge and deploy, #145 | `just verify-live` and the failing base URL in #146 | The public site passes. The bad base fails within the time limit |
| Cleanup checks | Baseline | Run the archive, image and schema scenarios in #141 in the scratch checkout | The valid build passes. Each invalid fixture fails for the expected reason |
| Launch | Baseline | `uv run .claude/skills/verify-blog/scripts/site.py up` | The command prints the preview URL |
| Doctor | Launch | `uv run .claude/skills/verify-blog/scripts/site.py doctor` | Exit 0 for the current checkout |
| Reader checks | Doctor | Use the six Playwright fallback recipes and both viewport widths in #142 | All six journeys pass. The menu state changes at the specified width |
| Evidence | Applicable checks | Record the revision, outcomes, commands and any findings on the QA issue | Each verdict can be checked against the observed result. Browser checks include the screenshot and accessibility text |
| Stop preview | Reader checks | `uv run .claude/skills/verify-blog/scripts/site.py down` | The owned preview stops. The evidence remains available |

Future waves add their exact scenarios when the wave becomes active. Release QA repeats the public checks against the approved revision.

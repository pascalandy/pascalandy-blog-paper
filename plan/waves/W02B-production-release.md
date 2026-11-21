---
id: W02B
project: BLOG
status: proposed
label: wave:W02B
skill_version: "3.1.0"
executor: human
---

# W02B: production release

## Goal

Publish the reader changes after the W02 results and Pascal’s release decision are available.

## Exit criteria

- [ ] Sevalla reports the full commit that Pascal authorized (SC10)
- [ ] The public home page, feeds, newest post and all 41 old links pass the live checks (SC4, SC8, SC10)

## Scope

- Existing release issue [#151](https://github.com/pascalandy/pascalandy-blog-paper/issues/151) retains the history of E09. Expand it at the wave review.
- The release waits for passing QA on #147, #148, #149 and #150. The four closed epics supply that evidence. Pascal receives the screenshots before authorizing the production change.
- The authorization identifies the revision. If the branch advances, the release needs evidence and approval for the new revision.
- Independent QA on the Mini checks the public URLs after deployment. The provider’s commit record and the public responses answer different questions (D005).

## Changes since original plan

D016 moves the existing release issue after W02. The human decision can now use the finished preview.

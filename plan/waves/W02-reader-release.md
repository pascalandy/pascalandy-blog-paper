---
id: W02
project: BLOG
status: planned
label: wave:W02
skill_version: "3.1.0"
executor: agent
---

# W02: reader-release

## Goal

A local preview shows the finished reader experience. W02B publishes the accepted revision.

## Exit criteria

- [ ] In both themes, the text and link colors reach their contrast thresholds, a `just check` row proves it, and no listed English interface string remains (SC3)
- [ ] Each of the 41 old `/blog/cryptoinmontreal-NN/` URLs leads to its `/blog/cim-NN/` page, in the static build and through the preview (SC4)
- [ ] Each post on the lists below carries `lang: en` or the `void` tag, and the home page shows the 5 featured posts (SC5)
- [ ] `src/data/blog/dev_workflows/editorial-rules.md` states each editorial rule and names its check (SC9)

## Epics

### E05: Every page reads clearly, in French, in both themes → #147

- Traces: [BC §5](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s5), SC3
- Executor: agent
- Problem (CMO): The light orange reads at 3.70:1 on cream. Tag counts read at 1.96:1. Some interface controls still use English. Two gallery links print a stray closing parenthesis.
- Outcome (FMO): The light primary color uses lightness 0.56 in `src/config.ts`. Normal text, including counts, meets 4.5:1 in both themes. Prose links retain a visible, thinner underline in the primary color.
- Verification: compute the foreground and background contrast in both themes. The build check fails below the required text contrast.
- Québec French applies to the footer, featured heading, copy button and confirmation, social link titles, RSS title and 404 title. The check reads the emitted controls and scripts without scanning quoted post text.
- Gallery: `cryptoinmontreal-photo.md` renders both image links without the extra parenthesis. The QA evidence includes desktop and phone screenshots in both themes.

- Dependencies: #127 provides the viewport checks. W02B uses the screenshots.

### E06: Old URLs reach their new pages → #148

- Traces: [BC §5](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s5), SC4
- Executor: agent
- Problem (CMO): Commit `d6b2d99` renamed 41 event posts. External links still use their former addresses.
- Outcome (FMO): Astro emits a static redirect page for each old address. The browser reads its HTML refresh and reaches the existing article.
- Pairing: use the 41 renames in `d6b2d99`. Each `/blog/cryptoinmontreal-NN/` targets its own `/blog/cim-NN/`.
- Build proof: the HTML checker recognizes exactly these redirect pages. A missing page, wrong number or missing target fails. All ordinary pages still use the full metadata rules.
- Reader proof: request each old URL on the preview. Read the actual redirect target and require the expected article to return 200. Issue #151 repeats this check on production.

- Dependencies: #145 defines `just verify-live`. E08 documents the redirect rule. W02B uses the 41 verified pairs.

### E07: The blog roll shows the chosen posts, each in its language → #149

- Traces: [BC §6](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s6), SC5
- Executor: agent
- Problem (CMO): Published articles inherit the Québec French default. Old vacancies can still appear in the blog listing. The home page has no featured posts.
- Outcome (FMO): The English files below publish with `<html lang="en">` and `og:locale=en_US`. French pages retain `fr-CA` and `fr_CA`. The six vacancies get the `void` tag. This tag preserves their URLs and removes them from the blog listing and RSS.
- Featured posts: set `featured: true` on the following five articles. Their links must appear together in the featured section of the home page.
  - `lekt-le-lecteur`
  - `pourquoi-se-donner-la-peine-decrire`
  - `pourquoi-jaime-vous-tutoyer`
  - `le-multitache-une-legende-urbaine-qui-a-trop-dure`
  - `comment-reprendre-le-dessus-quand-le-rythme-accelere`

- English articles at `69f7877` (38 files directly under `src/data/blog/`):
  - `10-stages-of-the-lifecycle-of-a-business.md`
  - `assetv-my-new-blockchain-project-idea.md`
  - `bitcoin-and-canadian-taxation-of-cryptocurrencies-full-video.md`
  - `ci-cd-scenario.md`
  - `cim-17.md`
  - `cim-20.md`
  - `cim-28.md`
  - `cim-33.md`
  - `cim-35.md`
  - `cim-36.md`
  - `cim-37.md`
  - `contributing-to-our-github-project.md`
  - `contributor-code-of-conduct-on-github.md`
  - `dper.md`
  - `each-day-traditional-social-networks-are-disconnecting-from-you.md`
  - `golf-r-parts.md`
  - `googler-comme-si-ta-vie-depend.md`
  - `how-do-i-help-organisations-to-thrive-as-a-full-stack-architect.md`
  - `i-am-the-bridge-maker.md`
  - `iphone-home-page.md`
  - `looking-for-a-geeky-node-developer-ghost.md`
  - `minimal-tech-bckpck.md`
  - `my-dca-definite-chief-aim.md`
  - `my-personality-type-entp-a-debater.md`
  - `my-productivity-hacks-to-fight-procrastination.md`
  - `need-a-geeky-ghost-theme-developer-zurb-html5-css.md`
  - `poste-danalyste-daffaires-systeme-2015-10-19.md`
  - `satoshi-nakamoto-announce-the-creation-of-bitcoin-this-is-how-it-started.md`
  - `setup-a-continuous-integration-continuous-deployment-environment.md`
  - `shady-twitter.md`
  - `the-blockchain-impact-by-naval-ravikant.md`
  - `the-lean-way-to-start-something.md`
  - `thermodynamic-neutrality.md`
  - `traefik-demo-docker-stack-and-play-with-docker.md`
  - `what-is-a-now-page.md`
  - `what-is-the-gnu-gpl-license.md`
  - `when-bitcoin-miners-decide-to-mine-something-else.md`
  - `when-crypto-currencies-smart-contracts-iot-ai-sleep-together.md`
- The nine published guides under `src/data/blog/dev_workflows/` also use English. The new editorial guide in E08 uses English.
- Old vacancies (6 files under `src/data/blog/`):
  - `copywriter-recherche-pour-communiquer-lessence-dune-nouvelle-startup.md`
  - `looking-for-a-geeky-node-developer-ghost.md`
  - `need-a-geeky-ghost-theme-developer-zurb-html5-css.md`
  - `poste-danalyste-daffaires-systeme-2015-10-19.md`
  - `setup-a-continuous-integration-continuous-deployment-environment.md`
  - `traducteur-ou-traductrice-passionne-e-des-mots-et-geek-de-preference-anglais-vers-le-francais.md`
- Language examples: the Bell vacancy has a French introduction and an English job description. The iPhone photo has an English title and description.
- The sale notice `photos-pneus-a-vendre.md` has French terms and a quoted English specification. The page keeps French.
- The language lists cover published pages. Drafts stay excluded from the build. An ad already tagged `void` needs no second tag.
- Proof: each vacancy still opens by its existing URL. No vacancy appears on any numbered blog page or in the RSS feed.
- Search proof: the Pagefind index accounts for every published post. The French search page must still find a known English article and a French article.
- Dependencies: #127 supplies the preview checks. E08 documents the resulting language, listing and featured rules. W02B publishes the result.

### E08: The editorial rules are on one page, and each rule names its check → #150

- Traces: [BC §9](https://github.com/pascalandy/pascalandy-blog-paper/blob/main/plan/00-business-case.md#s9), SC9
- Executor: agent
- Problem (CMO): Authors must consult the schema, tag guide, frontmatter guide and agent instructions to understand the publishing rules.
- Outcome (FMO): The English guide at `src/data/blog/dev_workflows/editorial-rules.md` describes the reader-visible effect of each rule. It names the schema rule or check that proves the effect. A missing check gets a focused fixture.
- Cover hidden tags, drafts, the 15-minute publication window, featured articles, language metadata and legacy redirects. The agent guide links to the published guide.
- Dependencies: E06 (#148) supplies the redirect rule. E07 (#149) supplies the tested post lists. W02B uses the results for release.

## Changes since original plan

D015 fixes the post lists. D016 moves production work to W02B. Readers can verify the changes on a preview before Pascal authorizes release.

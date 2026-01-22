# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [0.2.1](https://github.com/pascalandy/pascalandy-blog-paper/compare/pascalandy-blog-paper-v0.2.0...pascalandy-blog-paper-v0.2.1) (2026-01-22)


### Features

* **ci:** add workflow_dispatch trigger for manual runs ([#37](https://github.com/pascalandy/pascalandy-blog-paper/issues/37)) ([25e1043](https://github.com/pascalandy/pascalandy-blog-paper/commit/25e10434df765feb463024e789efb0eab9e2907e))


### Bug Fixes

* **ci:** always run CI on PRs to satisfy required checks ([#39](https://github.com/pascalandy/pascalandy-blog-paper/issues/39)) ([1e9b05a](https://github.com/pascalandy/pascalandy-blog-paper/commit/1e9b05a993e78375f4de960c69383901cd9b9cf1))
* **ci:** include CHANGELOG.md in CI triggers for release PRs ([#38](https://github.com/pascalandy/pascalandy-blog-paper/issues/38)) ([def8636](https://github.com/pascalandy/pascalandy-blog-paper/commit/def8636685554a97e58ce8539d80278d95f91408))

## [0.2.0](https://github.com/pascalandy/pascalandy-blog-paper/compare/pascalandy-blog-paper-v0.1.0...pascalandy-blog-paper-v0.2.0) (2026-01-22)


### ⚠ BREAKING CHANGES

* add pagefind for static search ([#458](https://github.com/pascalandy/pascalandy-blog-paper/issues/458))
* remove react dependency for UI interactions ([#457](https://github.com/pascalandy/pascalandy-blog-paper/issues/457))
* upgrade to Tailwind CSS v4
* separate config and constants
* update import alias to `@/*`
* update blog directory to `src/data/blog`
* upgrade Astro to v5 and related packages

### Features

* add archives page with configurable menu ([#386](https://github.com/pascalandy/pascalandy-blog-paper/issues/386)) ([7573617](https://github.com/pascalandy/pascalandy-blog-paper/commit/7573617e798642da0a70bea54845df01fcb9802f))
* add auto-merge to release-please workflow ([#32](https://github.com/pascalandy/pascalandy-blog-paper/issues/32)) ([16dadae](https://github.com/pascalandy/pascalandy-blog-paper/commit/16dadaefcfaa645fdbb90ab374f37b45c4f3d55d))
* add code-snippets for content creation ([#206](https://github.com/pascalandy/pascalandy-blog-paper/issues/206)) ([14e2936](https://github.com/pascalandy/pascalandy-blog-paper/commit/14e29366087fcb846b766fcb8d8454dbc2d9705a))
* add copy buttons for code blocks ([#217](https://github.com/pascalandy/pascalandy-blog-paper/issues/217)) ([6e7d76a](https://github.com/pascalandy/pascalandy-blog-paper/commit/6e7d76a0d35f2050a585ef8a36fe852e830e5367))
* add docker-compose file ([#174](https://github.com/pascalandy/pascalandy-blog-paper/issues/174)) ([fb3fa98](https://github.com/pascalandy/pascalandy-blog-paper/commit/fb3fa98936d76331869641014d5b4568a84d8d42))
* add E2E visual test matrix specification ([#28](https://github.com/pascalandy/pascalandy-blog-paper/issues/28)) ([e872a05](https://github.com/pascalandy/pascalandy-blog-paper/commit/e872a05056cc24b06db1d037cc9a91a5ec2a59d6))
* add edit post feature in blog posts ([#384](https://github.com/pascalandy/pascalandy-blog-paper/issues/384)) ([0bc8eee](https://github.com/pascalandy/pascalandy-blog-paper/commit/0bc8eeeac818eb2d8aac089a646993500c1fd8d9))
* add elegant-luxury and claude themes, set claude as active ([68cae6d](https://github.com/pascalandy/pascalandy-blog-paper/commit/68cae6d56c37eb79b9ec0ff05aa47bda05018a38))
* add file name transformer for fenced code blocks ([#535](https://github.com/pascalandy/pascalandy-blog-paper/issues/535)) ([cb8a479](https://github.com/pascalandy/pascalandy-blog-paper/commit/cb8a4794bedb0cf2808dabc07df57b7e98955d88))
* add git hooks for quality checks via Lefthook ([#1](https://github.com/pascalandy/pascalandy-blog-paper/issues/1)) ([396b354](https://github.com/pascalandy/pascalandy-blog-paper/commit/396b3545824b167787bf7e35561a589289310788))
* add global and per-post timezone support ([#491](https://github.com/pascalandy/pascalandy-blog-paper/issues/491)) ([5cff7c5](https://github.com/pascalandy/pascalandy-blog-paper/commit/5cff7c50b91790c1bfc8d3328c5e84712513908a)), closes [#466](https://github.com/pascalandy/pascalandy-blog-paper/issues/466)
* add heading links to PostDetails page ([#232](https://github.com/pascalandy/pascalandy-blog-paper/issues/232)) ([742baff](https://github.com/pascalandy/pascalandy-blog-paper/commit/742baff2c9bd47e0762f5d65f5b47a4d28014175))
* add image optimization and viewport prefetch ([e4b39e0](https://github.com/pascalandy/pascalandy-blog-paper/commit/e4b39e0d096d9fa734e5e18d2194c238e74dedc4))
* add image optimization and viewport prefetch ([#4](https://github.com/pascalandy/pascalandy-blog-paper/issues/4)) ([aba1e44](https://github.com/pascalandy/pascalandy-blog-paper/commit/aba1e4446355649e560f3ea710171e5bdb0cfa72))
* add JSON-LD structured data ([#260](https://github.com/pascalandy/pascalandy-blog-paper/issues/260)) ([8fbb0b4](https://github.com/pascalandy/pascalandy-blog-paper/commit/8fbb0b4d85852d6c3f931b94aae90425b678b890))
* add modified datetime in blog posts ([80e67a1](https://github.com/pascalandy/pascalandy-blog-paper/commit/80e67a1dcad19394d7b466472f3c674470db8e0c))
* add number of posts config for home page ([#281](https://github.com/pascalandy/pascalandy-blog-paper/issues/281)) ([0d5ea52](https://github.com/pascalandy/pascalandy-blog-paper/commit/0d5ea52c23d185c1bbdebd4ecda2b010f05e7744))
* add pagefind for static search ([#458](https://github.com/pascalandy/pascalandy-blog-paper/issues/458)) ([9119125](https://github.com/pascalandy/pascalandy-blog-paper/commit/9119125643c3d8668b23a44918835ddce544112e))
* add pagination in tag posts ([#201](https://github.com/pascalandy/pascalandy-blog-paper/issues/201)) ([581826a](https://github.com/pascalandy/pascalandy-blog-paper/commit/581826a5affd03d12416a5ac7d28ed17d53eac8d))
* add pencil icon before suggestion changes text ([#405](https://github.com/pascalandy/pascalandy-blog-paper/issues/405)) ([ec10609](https://github.com/pascalandy/pascalandy-blog-paper/commit/ec1060978c894e1fae753b305638edefb4161d18))
* add prev/next links at the bottom of blog post ([#372](https://github.com/pascalandy/pascalandy-blog-paper/issues/372)) ([29eff36](https://github.com/pascalandy/pascalandy-blog-paper/commit/29eff36794fc4e6d995611fad3aa9c1b3a3c67eb)), closes [#358](https://github.com/pascalandy/pascalandy-blog-paper/issues/358)
* add RTL language support ([#531](https://github.com/pascalandy/pascalandy-blog-paper/issues/531)) ([38ebf6e](https://github.com/pascalandy/pascalandy-blog-paper/commit/38ebf6e1b6712e4dcc81e94b2c816ebbe2e69e15))
* add scroll indicator in blog posts ([#249](https://github.com/pascalandy/pascalandy-blog-paper/issues/249)) ([8e022c7](https://github.com/pascalandy/pascalandy-blog-paper/commit/8e022c7b5ab6751432fee34adc23e30f2ec8b74c))
* add shadcn/ui compatible theme system with tweakcn support ([ed004f2](https://github.com/pascalandy/pascalandy-blog-paper/commit/ed004f2db62d604dd7c8e7c953293f20f3751429))
* add share links in blog post ([#215](https://github.com/pascalandy/pascalandy-blog-paper/issues/215)) ([1e2c5e8](https://github.com/pascalandy/pascalandy-blog-paper/commit/1e2c5e82d8e573d70a340e378659fa52be84df3d))
* add Shiki transformers for better syntax highlighting ([#534](https://github.com/pascalandy/pascalandy-blog-paper/issues/534)) ([76e15b5](https://github.com/pascalandy/pascalandy-blog-paper/commit/76e15b55e3949bcf39783017be70959548343d90)), closes [#210](https://github.com/pascalandy/pascalandy-blog-paper/issues/210)
* allow blog posts to be organized by subdirectories ([feaf5e1](https://github.com/pascalandy/pascalandy-blog-paper/commit/feaf5e122acdd4aac3c589290d86343040bc3bb2))
* automatic TOC generation in layout ([34bfd9a](https://github.com/pascalandy/pascalandy-blog-paper/commit/34bfd9a522aabf643de0d0561b8b7b822cac5dac))
* change font to JetBrains Mono ([11bbadc](https://github.com/pascalandy/pascalandy-blog-paper/commit/11bbadc5bc13ca4a38821cc3e5303a46fe95befe))
* **ci:** add GitHub Secret Scanning config ([b14eb8b](https://github.com/pascalandy/pascalandy-blog-paper/commit/b14eb8b8bd8235efc7bce1fee53edd4896b8a5b8))
* **ci:** add Gitleaks workflow for secret scanning ([4364e80](https://github.com/pascalandy/pascalandy-blog-paper/commit/4364e801edd7cdd566e3f6d33183d610d2b7d210))
* **ci:** add label-triggered preview deployment to Sevalla ([#25](https://github.com/pascalandy/pascalandy-blog-paper/issues/25)) ([d8f5c36](https://github.com/pascalandy/pascalandy-blog-paper/commit/d8f5c36281d3454b1f8bc6e5d205ae5dedf6e03c))
* **ci:** add Renovate, Release Drafter, and PR Labeler ([96909cb](https://github.com/pascalandy/pascalandy-blog-paper/commit/96909cb537e1370d5893198dd82dc895b937a5ad))
* **ci:** add Sevalla deployment after tests pass ([55a3cb2](https://github.com/pascalandy/pascalandy-blog-paper/commit/55a3cb2d2d1aa3b9e280f09c02e92b1f680df99c))
* **ci:** replace release-drafter with release-please ([#26](https://github.com/pascalandy/pascalandy-blog-paper/issues/26)) ([d894499](https://github.com/pascalandy/pascalandy-blog-paper/commit/d894499cb2bcca085c513444b084014b74d7f483))
* **config:** update site configuration for personal blog ([a51ee89](https://github.com/pascalandy/pascalandy-blog-paper/commit/a51ee89c38529e5430aa57090a734b4dae1dcfe9))
* dynamically generate robots.txt ([6352353](https://github.com/pascalandy/pascalandy-blog-paper/commit/63523534703c1f95ac070452001070e2c3f74d5d))
* enhance file name transformer with additional options ([#555](https://github.com/pascalandy/pascalandy-blog-paper/issues/555)) ([c863c82](https://github.com/pascalandy/pascalandy-blog-paper/commit/c863c8219dffdae37aa8c57a77aa9b4b370a375c))
* **header:** replace text logo with PascalAndy icon ([44cab6c](https://github.com/pascalandy/pascalandy-blog-paper/commit/44cab6c3a73c00893d5bf14a497f59b12e0f5402))
* hide posts in Prod with future pubDatetime  ([#234](https://github.com/pascalandy/pascalandy-blog-paper/issues/234)) ([3efa05c](https://github.com/pascalandy/pascalandy-blog-paper/commit/3efa05cc101688c32fc531af0122023d3ce82f08))
* **homepage:** add banner image and remove recent posts section ([db9d922](https://github.com/pascalandy/pascalandy-blog-paper/commit/db9d922edba90c59a82777efb1e5cb4741022d1e))
* **homepage:** use legacy 2017 banner image ([#30](https://github.com/pascalandy/pascalandy-blog-paper/issues/30)) ([288c26b](https://github.com/pascalandy/pascalandy-blog-paper/commit/288c26beef0fe4ac3cd349b050c3379a1041f29c))
* **hooks:** add build validation and enable parallel execution ([f100585](https://github.com/pascalandy/pascalandy-blog-paper/commit/f100585fb3112be9bfedfef9b58de9b4ea079f25))
* **icons:** add PascalAndy icon ([0312cae](https://github.com/pascalandy/pascalandy-blog-paper/commit/0312cae68a409f4cbbe372fbcfce9cc81ba54588))
* implement back-to-top button in blog post page ([c526157](https://github.com/pascalandy/pascalandy-blog-paper/commit/c526157118b69ff68e3a653eee68428a791a7d9f)), closes [#156](https://github.com/pascalandy/pascalandy-blog-paper/issues/156)
* improve back-to-top button behavior ([#520](https://github.com/pascalandy/pascalandy-blog-paper/issues/520)) ([4d01654](https://github.com/pascalandy/pascalandy-blog-paper/commit/4d01654471f744962b73c68fe97e3f096a50a1dc))
* integrate Astro fonts API with Google Sans Code font ([#602](https://github.com/pascalandy/pascalandy-blog-paper/issues/602)) ([698295d](https://github.com/pascalandy/pascalandy-blog-paper/commit/698295d23dfd43aaf161b00cab267893ef4399de))
* make heading links keyboard focusable ([#275](https://github.com/pascalandy/pascalandy-blog-paper/issues/275)) ([7b045a0](https://github.com/pascalandy/pascalandy-blog-paper/commit/7b045a0be8895e9440224cc222d47be91ca1172c))
* **nav:** replace About text with chess knight icon ([ca6eeae](https://github.com/pascalandy/pascalandy-blog-paper/commit/ca6eeae8af2f4d5f11d94377706bbaaef7166564))
* replace slugified title with unslugified tag name ([#198](https://github.com/pascalandy/pascalandy-blog-paper/issues/198)) ([b05b8fb](https://github.com/pascalandy/pascalandy-blog-paper/commit/b05b8fb842b43f4f6462b425cb46d835579cbcfb)), closes [#179](https://github.com/pascalandy/pascalandy-blog-paper/issues/179)
* **scripts:** add image link validation tool ([1e31cdb](https://github.com/pascalandy/pascalandy-blog-paper/commit/1e31cdb6da1d154650016468436286ccba87af78))
* **scripts:** add strict mode for CI to broken refs fixer ([b1fd79f](https://github.com/pascalandy/pascalandy-blog-paper/commit/b1fd79f142408e4d4ced48f010ab710729c33508))
* **socials:** update social links to Pascal Andy accounts ([4f5cb6d](https://github.com/pascalandy/pascalandy-blog-paper/commit/4f5cb6dfcdaa7c6c28bb8a2b50d6d236e84347f8))
* support light/dark theme in code blocks ([#327](https://github.com/pascalandy/pascalandy-blog-paper/issues/327)) ([9de19c2](https://github.com/pascalandy/pascalandy-blog-paper/commit/9de19c2c681955fdb64203f104ea2395f3b40af7))
* **tags:** add tag config system with display names and descriptions ([e833e6a](https://github.com/pascalandy/pascalandy-blog-paper/commit/e833e6ac26da8f519a87a625c2f394f11158de76))
* **ui:** update header navigation and homepage content ([dd548fe](https://github.com/pascalandy/pascalandy-blog-paper/commit/dd548fef5e796b75e5c94a7e8bb4ca7744fa1e66))
* update back button logic ([79c7df4](https://github.com/pascalandy/pascalandy-blog-paper/commit/79c7df45e5800ad21e5cfe793e79842803a66dba))


### Bug Fixes

* [#133](https://github.com/pascalandy/pascalandy-blog-paper/issues/133) update LOCALE config to cover overall locales ([cd02b04](https://github.com/pascalandy/pascalandy-blog-paper/commit/cd02b047d2b5e3b4a2940c0ff30568cdebcec0b8))
* **a11y:** remove aria-labels from non-interactive elements ([#346](https://github.com/pascalandy/pascalandy-blog-paper/issues/346)) ([8762650](https://github.com/pascalandy/pascalandy-blog-paper/commit/8762650c603a264a03ec16fd0e445229c2663a6f)), closes [#263](https://github.com/pascalandy/pascalandy-blog-paper/issues/263)
* **a11y:** resolve accessibility issues ([940deb6](https://github.com/pascalandy/pascalandy-blog-paper/commit/940deb6d3f25aac2abf0a57008b66942185ea2ab))
* add $CURRENT_TIMEZONE_OFFSET in custom code snippets ([#264](https://github.com/pascalandy/pascalandy-blog-paper/issues/264)) ([c00a3aa](https://github.com/pascalandy/pascalandy-blog-paper/commit/c00a3aa5dc4706a4f833266a0b24bca1253ccce4))
* add an option to disable dynamic OG image generation ([#476](https://github.com/pascalandy/pascalandy-blog-paper/issues/476)) ([6749f62](https://github.com/pascalandy/pascalandy-blog-paper/commit/6749f62015c321f2bb224cc34a3e53115cdf3587))
* add author url in Google JSON-LD conditionally ([b995f4d](https://github.com/pascalandy/pascalandy-blog-paper/commit/b995f4dadaeddcc24ac35195c5c1f71cbd83a09b))
* add autofocus in search bar and update search result title style ([#603](https://github.com/pascalandy/pascalandy-blog-paper/issues/603)) ([c61a755](https://github.com/pascalandy/pascalandy-blog-paper/commit/c61a75575d3251f4eb82fc38365874ff6c5013ef))
* add font-weight param in og image card style ([#453](https://github.com/pascalandy/pascalandy-blog-paper/issues/453)) ([e08618a](https://github.com/pascalandy/pascalandy-blog-paper/commit/e08618ad3c03bfe95de428a6b5904f0ad0347c33))
* add inline-block class to post title for improved view transition animation ([#420](https://github.com/pascalandy/pascalandy-blog-paper/issues/420)) ([43387b0](https://github.com/pascalandy/pascalandy-blog-paper/commit/43387b0d9480c019fa7c1d47150ad3d54feb181f))
* add missing posts sorting ([#383](https://github.com/pascalandy/pascalandy-blog-paper/issues/383)) ([94ede9b](https://github.com/pascalandy/pascalandy-blog-paper/commit/94ede9bb17e01b9a998e31f388713ce2a94227d6))
* add scroll offset for anchor targets ([#506](https://github.com/pascalandy/pascalandy-blog-paper/issues/506)) ([ae80e99](https://github.com/pascalandy/pascalandy-blog-paper/commit/ae80e995a5ccb90a95b0e1b1531ec6f0f12d3a01))
* add SITE.title in PostDetails title tag for consistent look ([#247](https://github.com/pascalandy/pascalandy-blog-paper/issues/247)) ([556df2d](https://github.com/pascalandy/pascalandy-blog-paper/commit/556df2d21af7ad7d89e2de67c27381097d7022bf))
* add trailing slash to links to avoid extra redirects ([#246](https://github.com/pascalandy/pascalandy-blog-paper/issues/246)) ([b3a1d9d](https://github.com/pascalandy/pascalandy-blog-paper/commit/b3a1d9d369fe76f13bbe379691d99fd0a40c892b))
* add types for constants to avoid type errors when empty ([#501](https://github.com/pascalandy/pascalandy-blog-paper/issues/501)) ([bd94860](https://github.com/pascalandy/pascalandy-blog-paper/commit/bd948604be841a6819048276d23f77acb6f90d7c))
* adding data-theme to tailwind config ([#319](https://github.com/pascalandy/pascalandy-blog-paper/issues/319)) ([569e53e](https://github.com/pascalandy/pascalandy-blog-paper/commit/569e53ef0de4a7cd187f24b32ac220e4f24b18b1)), closes [#288](https://github.com/pascalandy/pascalandy-blog-paper/issues/288)
* adjust nav bar alignment in heading ([#492](https://github.com/pascalandy/pascalandy-blog-paper/issues/492)) ([793eafa](https://github.com/pascalandy/pascalandy-blog-paper/commit/793eafa96581cdd3fafbbf671e62989520a5718b))
* align vertically in header nav ([#460](https://github.com/pascalandy/pascalandy-blog-paper/issues/460)) ([673c009](https://github.com/pascalandy/pascalandy-blog-paper/commit/673c00969ea9b2de6593299d64fa1479a1b85e1b))
* anchor oveflow on small screen size ([d025c91](https://github.com/pascalandy/pascalandy-blog-paper/commit/d025c914d91a9b7969c8db4bd6a700723ef86a39))
* apply Prettier formatting to 8 blog posts ([50168d8](https://github.com/pascalandy/pascalandy-blog-paper/commit/50168d8651e98f62e9c835463c8bfdb58006e885))
* avoid `undefined` when passing class-name as prop ([#270](https://github.com/pascalandy/pascalandy-blog-paper/issues/270)) ([e252506](https://github.com/pascalandy/pascalandy-blog-paper/commit/e252506493a96bc0acb638cb98a8314d60a2bee8))
* **blog:** correct file reference in reading time guide ([#359](https://github.com/pascalandy/pascalandy-blog-paper/issues/359)) ([ec373c3](https://github.com/pascalandy/pascalandy-blog-paper/commit/ec373c33693ded230818c49e329c70647a041901))
* broken editPost link and update editPost logic  ([#487](https://github.com/pascalandy/pascalandy-blog-paper/issues/487)) ([2774045](https://github.com/pascalandy/pascalandy-blog-paper/commit/2774045045cbec1d18f3e0094e918d7c3b923cf6))
* broken typography in about layout ([#541](https://github.com/pascalandy/pascalandy-blog-paper/issues/541)) ([5fb3b25](https://github.com/pascalandy/pascalandy-blog-paper/commit/5fb3b25acb9ec0e413c20e0abc56e9799ef49b8e))
* **content:** repair broken blog posts and update maturity report ([#18](https://github.com/pascalandy/pascalandy-blog-paper/issues/18)) ([876aeb5](https://github.com/pascalandy/pascalandy-blog-paper/commit/876aeb5d2eccb321e680c1434a6930dc3dcd2529))
* **content:** standardize TL;DR sections in CryptoInMontreal posts ([#15](https://github.com/pascalandy/pascalandy-blog-paper/issues/15)) ([f8b9d22](https://github.com/pascalandy/pascalandy-blog-paper/commit/f8b9d2263016e2fcf78135c7d4d97c394d6f882e))
* **content:** update linkedin profile page frontmatter ([#20](https://github.com/pascalandy/pascalandy-blog-paper/issues/20)) ([a5de09a](https://github.com/pascalandy/pascalandy-blog-paper/commit/a5de09a9ba8422877e9916de5122232463a98ff4))
* correct Google Fonts API URL construction for proper weight fetching ([a4a5ced](https://github.com/pascalandy/pascalandy-blog-paper/commit/a4a5ced8a6ba424ebc3cf74d4539f752316757cd))
* correct lockfile name and narrow cache key pattern ([a562371](https://github.com/pascalandy/pascalandy-blog-paper/commit/a562371a393df5c2229591f2516cb1fc3ac7d1a9))
* decode unicode tag chars in breadcrumb ([#175](https://github.com/pascalandy/pascalandy-blog-paper/issues/175)) ([058c790](https://github.com/pascalandy/pascalandy-blog-paper/commit/058c790d26cbeab286679a8a8e3bad6c14042d6d))
* display `Updated` in posts only when modDatetime &gt; pubDatetime ([#258](https://github.com/pascalandy/pascalandy-blog-paper/issues/258)) ([25a640b](https://github.com/pascalandy/pascalandy-blog-paper/commit/25a640b7287365dc344106e9be8d99bfe604aa1a))
* **docs:** update giscus blog post ([#392](https://github.com/pascalandy/pascalandy-blog-paper/issues/392)) ([c11b2a2](https://github.com/pascalandy/pascalandy-blog-paper/commit/c11b2a2960fe8880e21a232a878a855904c8ccf4))
* ensure only one search bar is displayed on nav link clicks ([#489](https://github.com/pascalandy/pascalandy-blog-paper/issues/489)) ([a397677](https://github.com/pascalandy/pascalandy-blog-paper/commit/a397677d842c818f6eb956fd08fd82d7ded822f2)), closes [#465](https://github.com/pascalandy/pascalandy-blog-paper/issues/465)
* exclude `/archives` from sitemap if it is disabled ([#425](https://github.com/pascalandy/pascalandy-blog-paper/issues/425)) ([c2e2dbd](https://github.com/pascalandy/pascalandy-blog-paper/commit/c2e2dbda3005752be6703c9c85661612e7c215c5))
* focus search input on mount ([#414](https://github.com/pascalandy/pascalandy-blog-paper/issues/414)) ([63fe796](https://github.com/pascalandy/pascalandy-blog-paper/commit/63fe796eace411404ebf5ef5d55b8b90172b736e))
* **icons:** adjust archive icon vertical alignment ([f632c11](https://github.com/pascalandy/pascalandy-blog-paper/commit/f632c1151f6c2202e76c9ed5b816a3abf04a3a32))
* ignore  in eslint ([b4ae4cd](https://github.com/pascalandy/pascalandy-blog-paper/commit/b4ae4cde049677be97e3a03815b9127d452e5416))
* improve back-to-top button to adapt layout changes properly ([#527](https://github.com/pascalandy/pascalandy-blog-paper/issues/527)) ([0cc647c](https://github.com/pascalandy/pascalandy-blog-paper/commit/0cc647c3d3c107001585852acb4b3d9680a03fa9))
* improve inline code and code block styling with theme colors ([ced84ae](https://github.com/pascalandy/pascalandy-blog-paper/commit/ced84aebaec7a8efc5f81bd1c06a123e2545c6e4))
* improve Tag component by making it entire component clickable ([#598](https://github.com/pascalandy/pascalandy-blog-paper/issues/598)) ([f5f863f](https://github.com/pascalandy/pascalandy-blog-paper/commit/f5f863f9d2b9bbfebc57c6c850e8c315047398bc))
* initial light mode flash in dark mode ([#488](https://github.com/pascalandy/pascalandy-blog-paper/issues/488)) ([5e92a3d](https://github.com/pascalandy/pascalandy-blog-paper/commit/5e92a3d4da972956d1f7d5f5f1c6140884979197))
* **layout:** use 100svh for min-height on body instead of 100vh ([79d569d](https://github.com/pascalandy/pascalandy-blog-paper/commit/79d569d053036f2113519f41b0d257523d035b76)), closes [#127](https://github.com/pascalandy/pascalandy-blog-paper/issues/127)
* make heading anchors in article visible on mobile ([#537](https://github.com/pascalandy/pascalandy-blog-paper/issues/537)) ([4c2aebc](https://github.com/pascalandy/pascalandy-blog-paper/commit/4c2aebc304e64e572b7a059226db5cf89567d64a))
* make post date/edit more subtle with smaller text ([02511aa](https://github.com/pascalandy/pascalandy-blog-paper/commit/02511aa497506050e16b121d60caa1523d8fb451))
* make post header vertical bar respect global settings ([#562](https://github.com/pascalandy/pascalandy-blog-paper/issues/562)) ([d7e209d](https://github.com/pascalandy/pascalandy-blog-paper/commit/d7e209d20238a29335d6afd8d5bdba230a2ef068))
* **makefile:** enable pipefail to stop chain on piped command failure ([a0e4390](https://github.com/pascalandy/pascalandy-blog-paper/commit/a0e439017e5c04e20bdf98a3aaa85f4e9d2036f6))
* move intro paragraphs before TOC to prevent remark-collapse hiding them ([a1a5232](https://github.com/pascalandy/pascalandy-blog-paper/commit/a1a5232867a1afb24627a0fe442dbe5724811695))
* navigation flicker on Android when in dark mode ([#494](https://github.com/pascalandy/pascalandy-blog-paper/issues/494)) ([77709ab](https://github.com/pascalandy/pascalandy-blog-paper/commit/77709ab7c01a76a232842129724a60c94d0dc50f))
* **og-images:** wrap Buffer in Uint8Array for Response body ([#568](https://github.com/pascalandy/pascalandy-blog-paper/issues/568)) ([aad5ac6](https://github.com/pascalandy/pascalandy-blog-paper/commit/aad5ac67e43e44a7fcdaabac4f7358e0ef4d2eb2)), closes [#560](https://github.com/pascalandy/pascalandy-blog-paper/issues/560)
* **og:** add the missing SITE.website to loadGoogleFonts  ([#360](https://github.com/pascalandy/pascalandy-blog-paper/issues/360)) ([28f886b](https://github.com/pascalandy/pascalandy-blog-paper/commit/28f886b4d6908c8f70a97878466abe0056a5b40b))
* prevent overflow by adding line breaks in table codes ([#485](https://github.com/pascalandy/pascalandy-blog-paper/issues/485)) ([48f200f](https://github.com/pascalandy/pascalandy-blog-paper/commit/48f200f4442ff00d5d4676db22ef4f1b71bf2f7d))
* reduce margin-bottom on markdown images ([#235](https://github.com/pascalandy/pascalandy-blog-paper/issues/235)) ([1331795](https://github.com/pascalandy/pascalandy-blog-paper/commit/1331795a4965aab5c47581c223f32f3ea2cd71ab))
* remove extra padding if lightAndDarkMode is false ([#230](https://github.com/pascalandy/pascalandy-blog-paper/issues/230)) ([742314e](https://github.com/pascalandy/pascalandy-blog-paper/commit/742314e0ac350a70ce1cc256e858c8de9c9153f6))
* remove extra padding in fenced code blocks ([#540](https://github.com/pascalandy/pascalandy-blog-paper/issues/540)) ([0d9a7bb](https://github.com/pascalandy/pascalandy-blog-paper/commit/0d9a7bbd939458f0a3cc75da11afa428da139d07)), closes [#539](https://github.com/pascalandy/pascalandy-blog-paper/issues/539)
* remove recent posts section if there's no post ([#238](https://github.com/pascalandy/pascalandy-blog-paper/issues/238)) ([629dbfd](https://github.com/pascalandy/pascalandy-blog-paper/commit/629dbfda5b99a71e629dbbf1845c3ceba5ac97e0)), closes [#204](https://github.com/pascalandy/pascalandy-blog-paper/issues/204)
* remove time from post datetime display ([#546](https://github.com/pascalandy/pascalandy-blog-paper/issues/546)) ([a9b9c3a](https://github.com/pascalandy/pascalandy-blog-paper/commit/a9b9c3acbf474589a5f6ad111cb7654f63c8bf65))
* remove unused `ogImage` size validation ([#462](https://github.com/pascalandy/pascalandy-blog-paper/issues/462)) ([212fd5c](https://github.com/pascalandy/pascalandy-blog-paper/commit/212fd5c550a2b3765a34058a57b28eadd7104ad9))
* remove unused back url in the card url ([61c6ec8](https://github.com/pascalandy/pascalandy-blog-paper/commit/61c6ec81b8e302d059393fb3a7d413d2be3189af))
* remove unused imports to pass ESLint ([fc21479](https://github.com/pascalandy/pascalandy-blog-paper/commit/fc214794311ea7d92842769a71c0a62222d26aaf))
* replace broken prev/next links with correct paths ([#533](https://github.com/pascalandy/pascalandy-blog-paper/issues/533)) ([b07ee5c](https://github.com/pascalandy/pascalandy-blog-paper/commit/b07ee5cdcc9b6d6a864f441b291410eb745f0fba))
* replace hardcoded bg-black/text-white with theme colors ([9842c7b](https://github.com/pascalandy/pascalandy-blog-paper/commit/9842c7bf07cff64852b9ce8f4e60460087e3a369))
* replace twitter with x ([#407](https://github.com/pascalandy/pascalandy-blog-paper/issues/407)) ([cac8ba0](https://github.com/pascalandy/pascalandy-blog-paper/commit/cac8ba05f41976aaf83189fdaf53304e05e015b7))
* resolve broken line break in inline code ([#237](https://github.com/pascalandy/pascalandy-blog-paper/issues/237)) ([ece0682](https://github.com/pascalandy/pascalandy-blog-paper/commit/ece0682adce387f2a169185680cdf372a457e938))
* resolve non-latin char issue in generated OG images ([#318](https://github.com/pascalandy/pascalandy-blog-paper/issues/318)) ([2f82feb](https://github.com/pascalandy/pascalandy-blog-paper/commit/2f82febff4d1af582106be0cc3d618da2d08f600))
* **search:** autofocus input on page load ([#17](https://github.com/pascalandy/pascalandy-blog-paper/issues/17)) ([e2cbc9b](https://github.com/pascalandy/pascalandy-blog-paper/commit/e2cbc9b4761dbdb3d57e07cff3fc44d0ea6bc026))
* show light/dark button according to site setting ([39ed489](https://github.com/pascalandy/pascalandy-blog-paper/commit/39ed4898a3513551a7a46a557cb9b86f4dd1b312))
* simplify post typography and layout ([c4c76e6](https://github.com/pascalandy/pascalandy-blog-paper/commit/c4c76e62bfe23b97cc0a412b4645a0d84d8e8e20))
* skip invalid code block metadata without key-value pairs ([#561](https://github.com/pascalandy/pascalandy-blog-paper/issues/561)) ([c5a34c7](https://github.com/pascalandy/pascalandy-blog-paper/commit/c5a34c783821375e438ec4a1e5e0098ddf1357e2))
* soften code block border with 50% opacity ([eb09618](https://github.com/pascalandy/pascalandy-blog-paper/commit/eb096186adbfa404384c7e4707ef5d3c4eb967e1))
* solve invisible text code block issue in light-mode ([#163](https://github.com/pascalandy/pascalandy-blog-paper/issues/163)) ([64b3a28](https://github.com/pascalandy/pascalandy-blog-paper/commit/64b3a286e6e3ff1dff7cf4ca0fc8fafc222cabcd))
* solve modDatetime type errors ([d929ce1](https://github.com/pascalandy/pascalandy-blog-paper/commit/d929ce1fefd5c509a83b44439324b57249066be7))
* sort archive posts by pubDatetime ([#415](https://github.com/pascalandy/pascalandy-blog-paper/issues/415)) ([b9ef735](https://github.com/pascalandy/pascalandy-blog-paper/commit/b9ef735d68ab88c830c32007f965efd41f98ee2c))
* style TOC with same background as code blocks ([3cff0fe](https://github.com/pascalandy/pascalandy-blog-paper/commit/3cff0feb724840f95e82600c53f7ee2f2ec8cd09))
* tighten list item spacing ([0a89427](https://github.com/pascalandy/pascalandy-blog-paper/commit/0a894276f99512b8ee091bf915eacdff4eebe6c2))
* typo in astro-paper-v5 blog post ([#556](https://github.com/pascalandy/pascalandy-blog-paper/issues/556)) ([5d47275](https://github.com/pascalandy/pascalandy-blog-paper/commit/5d47275687e9905c20fc466409d11b8461f57cb6))
* typos across codebase ([#543](https://github.com/pascalandy/pascalandy-blog-paper/issues/543)) ([9ee01aa](https://github.com/pascalandy/pascalandy-blog-paper/commit/9ee01aafa23e76853f841c546e908edc52622aee))
* update back button to redirect to home when no route history ([#241](https://github.com/pascalandy/pascalandy-blog-paper/issues/241)) ([8f75f0a](https://github.com/pascalandy/pascalandy-blog-paper/commit/8f75f0a5e75778a60e8030bb45b19289c0af502e))
* update blog table padding ([98bff0a](https://github.com/pascalandy/pascalandy-blog-paper/commit/98bff0a8761abec96748216da07a5d470fcce76d))
* update docker-compose ([#475](https://github.com/pascalandy/pascalandy-blog-paper/issues/475)) ([ec59d11](https://github.com/pascalandy/pascalandy-blog-paper/commit/ec59d1109eafe988d8e5ffbc3e983b4e3e0495ce))
* update edit post link styling and text ([#545](https://github.com/pascalandy/pascalandy-blog-paper/issues/545)) ([fa37a47](https://github.com/pascalandy/pascalandy-blog-paper/commit/fa37a477d05bf115ede1a8d23300e7942f7de573))
* update fix_broken_refs.py for src/assets image paths ([9f1f6f7](https://github.com/pascalandy/pascalandy-blog-paper/commit/9f1f6f7bdaa70fc007f4d60dae05b90fd7fc41c9))
* update heading alignment and font-size ([#473](https://github.com/pascalandy/pascalandy-blog-paper/issues/473)) ([21bcca8](https://github.com/pascalandy/pascalandy-blog-paper/commit/21bcca85ac39e3ca81a19ab5f6e8fcc9108d7bfa))
* update import location in giscus example ([#474](https://github.com/pascalandy/pascalandy-blog-paper/issues/474)) ([0016dd5](https://github.com/pascalandy/pascalandy-blog-paper/commit/0016dd55d114d0bb33b72a26858c4bb6a0ffb00c))
* update incorrect typo in predefined-color-schemes.md ([#245](https://github.com/pascalandy/pascalandy-blog-paper/issues/245)) ([c9150f2](https://github.com/pascalandy/pascalandy-blog-paper/commit/c9150f2774bd8143fc5fd4ec7b4bf86c6a4d4669))
* update rss pubDate to prioritize modDatetime if exists ([20536b0](https://github.com/pascalandy/pascalandy-blog-paper/commit/20536b0562a3a69b3e376cb6fcb32a819a300551))
* update syntax highlighting transformer styles ([#558](https://github.com/pascalandy/pascalandy-blog-paper/issues/558)) ([493c671](https://github.com/pascalandy/pascalandy-blog-paper/commit/493c671e0fea6f1dcd8c6224f991c57698197bc5))
* update twitter ShareLink title ([43f7160](https://github.com/pascalandy/pascalandy-blog-paper/commit/43f716054b210a50f5b3cc63e282b160c5c4d0ef))
* use correct astro-code variable names, different bg for light/dark ([3b6c3c0](https://github.com/pascalandy/pascalandy-blog-paper/commit/3b6c3c04bab759ef852960bb12ec1a539a0280f4))
* use muted background for code blocks, remove hardcoded colors ([95b7371](https://github.com/pascalandy/pascalandy-blog-paper/commit/95b73711446dc692b71f8cf5b42e70dd1c4d3dfd))
* use muted for lighter code block bg in light mode ([cc71e33](https://github.com/pascalandy/pascalandy-blog-paper/commit/cc71e3332a4d9e7f72abcd171cad16bf7f15ac05))
* use relative oklch for subtler code block background ([98d8d6c](https://github.com/pascalandy/pascalandy-blog-paper/commit/98d8d6c5fbb72f1ccae0d9a0c384d166616ab03c))
* use tag name for display in tags page ([#438](https://github.com/pascalandy/pascalandy-blog-paper/issues/438)) ([a56b28b](https://github.com/pascalandy/pascalandy-blog-paper/commit/a56b28bc2c852dc602b9aa44d8c272bf84aea169))


### Performance Improvements

* **ci:** parallelize jobs and fix blog post validation ([6fbc062](https://github.com/pascalandy/pascalandy-blog-paper/commit/6fbc0623358c6ed343b5b4c501a79610c695b1d0))
* preload font and load theme script asynchronously ([#380](https://github.com/pascalandy/pascalandy-blog-paper/issues/380)) ([cbbb3eb](https://github.com/pascalandy/pascalandy-blog-paper/commit/cbbb3eb1e1d0f48473330fa9d258554bfa68f2fd))


### Reverts

* keep 2019 og-legacy images in public folder ([d9956fb](https://github.com/pascalandy/pascalandy-blog-paper/commit/d9956fb8ebb0409c78efc1eadf5846f27906131e))
* undo last 2 commits to return to b4d1397 ([5065659](https://github.com/pascalandy/pascalandy-blog-paper/commit/5065659817b5e59a09a313b1c0a209988d250737))


### Code Refactoring

* remove react dependency for UI interactions ([#457](https://github.com/pascalandy/pascalandy-blog-paper/issues/457)) ([3542917](https://github.com/pascalandy/pascalandy-blog-paper/commit/35429176e0c7ab6571f7dbbb660ebe4762febb61))
* separate config and constants ([a2b88e1](https://github.com/pascalandy/pascalandy-blog-paper/commit/a2b88e124750d0deb41106be144ef8f14f3af1b2))
* update blog directory to `src/data/blog` ([594adda](https://github.com/pascalandy/pascalandy-blog-paper/commit/594addaec1309607c43c5511d426a1dea962028a))


### Build System

* update import alias to `@/*` ([9023103](https://github.com/pascalandy/pascalandy-blog-paper/commit/90231031a516b45d352845e40383c90d81873d76))
* upgrade Astro to v5 and related packages ([cc936ca](https://github.com/pascalandy/pascalandy-blog-paper/commit/cc936ca5e44b3b244f4b8cca351dc27b6fa9dc0b))
* upgrade to Tailwind CSS v4 ([172e14b](https://github.com/pascalandy/pascalandy-blog-paper/commit/172e14b5f497ce8d6e610ebd36e9a24c74fc5957))

## [5.6.0](https://github.com/pascalandy/pascalandy-blog-paper/compare/v5.5.1...v5.6.0) (2026-01-21)


### Features

* add E2E visual test matrix specification ([#28](https://github.com/pascalandy/pascalandy-blog-paper/issues/28)) ([e872a05](https://github.com/pascalandy/pascalandy-blog-paper/commit/e872a05056cc24b06db1d037cc9a91a5ec2a59d6))
* add elegant-luxury and claude themes, set claude as active ([68cae6d](https://github.com/pascalandy/pascalandy-blog-paper/commit/68cae6d56c37eb79b9ec0ff05aa47bda05018a38))
* add git hooks for quality checks via Lefthook ([#1](https://github.com/pascalandy/pascalandy-blog-paper/issues/1)) ([396b354](https://github.com/pascalandy/pascalandy-blog-paper/commit/396b3545824b167787bf7e35561a589289310788))
* add image optimization and viewport prefetch ([e4b39e0](https://github.com/pascalandy/pascalandy-blog-paper/commit/e4b39e0d096d9fa734e5e18d2194c238e74dedc4))
* add image optimization and viewport prefetch ([#4](https://github.com/pascalandy/pascalandy-blog-paper/issues/4)) ([aba1e44](https://github.com/pascalandy/pascalandy-blog-paper/commit/aba1e4446355649e560f3ea710171e5bdb0cfa72))
* add shadcn/ui compatible theme system with tweakcn support ([ed004f2](https://github.com/pascalandy/pascalandy-blog-paper/commit/ed004f2db62d604dd7c8e7c953293f20f3751429))
* automatic TOC generation in layout ([34bfd9a](https://github.com/pascalandy/pascalandy-blog-paper/commit/34bfd9a522aabf643de0d0561b8b7b822cac5dac))
* change font to JetBrains Mono ([11bbadc](https://github.com/pascalandy/pascalandy-blog-paper/commit/11bbadc5bc13ca4a38821cc3e5303a46fe95befe))
* **ci:** add GitHub Secret Scanning config ([b14eb8b](https://github.com/pascalandy/pascalandy-blog-paper/commit/b14eb8b8bd8235efc7bce1fee53edd4896b8a5b8))
* **ci:** add Gitleaks workflow for secret scanning ([4364e80](https://github.com/pascalandy/pascalandy-blog-paper/commit/4364e801edd7cdd566e3f6d33183d610d2b7d210))
* **ci:** add label-triggered preview deployment to Sevalla ([#25](https://github.com/pascalandy/pascalandy-blog-paper/issues/25)) ([d8f5c36](https://github.com/pascalandy/pascalandy-blog-paper/commit/d8f5c36281d3454b1f8bc6e5d205ae5dedf6e03c))
* **ci:** add Renovate, Release Drafter, and PR Labeler ([96909cb](https://github.com/pascalandy/pascalandy-blog-paper/commit/96909cb537e1370d5893198dd82dc895b937a5ad))
* **ci:** add Sevalla deployment after tests pass ([55a3cb2](https://github.com/pascalandy/pascalandy-blog-paper/commit/55a3cb2d2d1aa3b9e280f09c02e92b1f680df99c))
* **ci:** replace release-drafter with release-please ([#26](https://github.com/pascalandy/pascalandy-blog-paper/issues/26)) ([d894499](https://github.com/pascalandy/pascalandy-blog-paper/commit/d894499cb2bcca085c513444b084014b74d7f483))
* **config:** update site configuration for personal blog ([a51ee89](https://github.com/pascalandy/pascalandy-blog-paper/commit/a51ee89c38529e5430aa57090a734b4dae1dcfe9))
* **header:** replace text logo with PascalAndy icon ([44cab6c](https://github.com/pascalandy/pascalandy-blog-paper/commit/44cab6c3a73c00893d5bf14a497f59b12e0f5402))
* **homepage:** add banner image and remove recent posts section ([db9d922](https://github.com/pascalandy/pascalandy-blog-paper/commit/db9d922edba90c59a82777efb1e5cb4741022d1e))
* **homepage:** use legacy 2017 banner image ([#30](https://github.com/pascalandy/pascalandy-blog-paper/issues/30)) ([288c26b](https://github.com/pascalandy/pascalandy-blog-paper/commit/288c26beef0fe4ac3cd349b050c3379a1041f29c))
* **hooks:** add build validation and enable parallel execution ([f100585](https://github.com/pascalandy/pascalandy-blog-paper/commit/f100585fb3112be9bfedfef9b58de9b4ea079f25))
* **icons:** add PascalAndy icon ([0312cae](https://github.com/pascalandy/pascalandy-blog-paper/commit/0312cae68a409f4cbbe372fbcfce9cc81ba54588))
* integrate Astro fonts API with Google Sans Code font ([#602](https://github.com/pascalandy/pascalandy-blog-paper/issues/602)) ([698295d](https://github.com/pascalandy/pascalandy-blog-paper/commit/698295d23dfd43aaf161b00cab267893ef4399de))
* **nav:** replace About text with chess knight icon ([ca6eeae](https://github.com/pascalandy/pascalandy-blog-paper/commit/ca6eeae8af2f4d5f11d94377706bbaaef7166564))
* **scripts:** add image link validation tool ([1e31cdb](https://github.com/pascalandy/pascalandy-blog-paper/commit/1e31cdb6da1d154650016468436286ccba87af78))
* **scripts:** add strict mode for CI to broken refs fixer ([b1fd79f](https://github.com/pascalandy/pascalandy-blog-paper/commit/b1fd79f142408e4d4ced48f010ab710729c33508))
* **socials:** update social links to Pascal Andy accounts ([4f5cb6d](https://github.com/pascalandy/pascalandy-blog-paper/commit/4f5cb6dfcdaa7c6c28bb8a2b50d6d236e84347f8))
* **tags:** add tag config system with display names and descriptions ([e833e6a](https://github.com/pascalandy/pascalandy-blog-paper/commit/e833e6ac26da8f519a87a625c2f394f11158de76))
* **ui:** update header navigation and homepage content ([dd548fe](https://github.com/pascalandy/pascalandy-blog-paper/commit/dd548fef5e796b75e5c94a7e8bb4ca7744fa1e66))


### Bug Fixes

* add autofocus in search bar and update search result title style ([#603](https://github.com/pascalandy/pascalandy-blog-paper/issues/603)) ([c61a755](https://github.com/pascalandy/pascalandy-blog-paper/commit/c61a75575d3251f4eb82fc38365874ff6c5013ef))
* apply Prettier formatting to 8 blog posts ([50168d8](https://github.com/pascalandy/pascalandy-blog-paper/commit/50168d8651e98f62e9c835463c8bfdb58006e885))
* **content:** repair broken blog posts and update maturity report ([#18](https://github.com/pascalandy/pascalandy-blog-paper/issues/18)) ([876aeb5](https://github.com/pascalandy/pascalandy-blog-paper/commit/876aeb5d2eccb321e680c1434a6930dc3dcd2529))
* **content:** standardize TL;DR sections in CryptoInMontreal posts ([#15](https://github.com/pascalandy/pascalandy-blog-paper/issues/15)) ([f8b9d22](https://github.com/pascalandy/pascalandy-blog-paper/commit/f8b9d2263016e2fcf78135c7d4d97c394d6f882e))
* **content:** update linkedin profile page frontmatter ([#20](https://github.com/pascalandy/pascalandy-blog-paper/issues/20)) ([a5de09a](https://github.com/pascalandy/pascalandy-blog-paper/commit/a5de09a9ba8422877e9916de5122232463a98ff4))
* correct lockfile name and narrow cache key pattern ([a562371](https://github.com/pascalandy/pascalandy-blog-paper/commit/a562371a393df5c2229591f2516cb1fc3ac7d1a9))
* **icons:** adjust archive icon vertical alignment ([f632c11](https://github.com/pascalandy/pascalandy-blog-paper/commit/f632c1151f6c2202e76c9ed5b816a3abf04a3a32))
* improve inline code and code block styling with theme colors ([ced84ae](https://github.com/pascalandy/pascalandy-blog-paper/commit/ced84aebaec7a8efc5f81bd1c06a123e2545c6e4))
* make post date/edit more subtle with smaller text ([02511aa](https://github.com/pascalandy/pascalandy-blog-paper/commit/02511aa497506050e16b121d60caa1523d8fb451))
* **makefile:** enable pipefail to stop chain on piped command failure ([a0e4390](https://github.com/pascalandy/pascalandy-blog-paper/commit/a0e439017e5c04e20bdf98a3aaa85f4e9d2036f6))
* move intro paragraphs before TOC to prevent remark-collapse hiding them ([a1a5232](https://github.com/pascalandy/pascalandy-blog-paper/commit/a1a5232867a1afb24627a0fe442dbe5724811695))
* remove unused imports to pass ESLint ([fc21479](https://github.com/pascalandy/pascalandy-blog-paper/commit/fc214794311ea7d92842769a71c0a62222d26aaf))
* replace hardcoded bg-black/text-white with theme colors ([9842c7b](https://github.com/pascalandy/pascalandy-blog-paper/commit/9842c7bf07cff64852b9ce8f4e60460087e3a369))
* **search:** autofocus input on page load ([#17](https://github.com/pascalandy/pascalandy-blog-paper/issues/17)) ([e2cbc9b](https://github.com/pascalandy/pascalandy-blog-paper/commit/e2cbc9b4761dbdb3d57e07cff3fc44d0ea6bc026))
* simplify post typography and layout ([c4c76e6](https://github.com/pascalandy/pascalandy-blog-paper/commit/c4c76e62bfe23b97cc0a412b4645a0d84d8e8e20))
* soften code block border with 50% opacity ([eb09618](https://github.com/pascalandy/pascalandy-blog-paper/commit/eb096186adbfa404384c7e4707ef5d3c4eb967e1))
* style TOC with same background as code blocks ([3cff0fe](https://github.com/pascalandy/pascalandy-blog-paper/commit/3cff0feb724840f95e82600c53f7ee2f2ec8cd09))
* tighten list item spacing ([0a89427](https://github.com/pascalandy/pascalandy-blog-paper/commit/0a894276f99512b8ee091bf915eacdff4eebe6c2))
* update fix_broken_refs.py for src/assets image paths ([9f1f6f7](https://github.com/pascalandy/pascalandy-blog-paper/commit/9f1f6f7bdaa70fc007f4d60dae05b90fd7fc41c9))
* use correct astro-code variable names, different bg for light/dark ([3b6c3c0](https://github.com/pascalandy/pascalandy-blog-paper/commit/3b6c3c04bab759ef852960bb12ec1a539a0280f4))
* use muted background for code blocks, remove hardcoded colors ([95b7371](https://github.com/pascalandy/pascalandy-blog-paper/commit/95b73711446dc692b71f8cf5b42e70dd1c4d3dfd))
* use muted for lighter code block bg in light mode ([cc71e33](https://github.com/pascalandy/pascalandy-blog-paper/commit/cc71e3332a4d9e7f72abcd171cad16bf7f15ac05))
* use relative oklch for subtler code block background ([98d8d6c](https://github.com/pascalandy/pascalandy-blog-paper/commit/98d8d6c5fbb72f1ccae0d9a0c384d166616ab03c))


### Performance Improvements

* **ci:** parallelize jobs and fix blog post validation ([6fbc062](https://github.com/pascalandy/pascalandy-blog-paper/commit/6fbc0623358c6ed343b5b4c501a79610c695b1d0))


### Reverts

* keep 2019 og-legacy images in public folder ([d9956fb](https://github.com/pascalandy/pascalandy-blog-paper/commit/d9956fb8ebb0409c78efc1eadf5846f27906131e))
* undo last 2 commits to return to b4d1397 ([5065659](https://github.com/pascalandy/pascalandy-blog-paper/commit/5065659817b5e59a09a313b1c0a209988d250737))

## v5.5.1 (2026-01-08)

### Fix

- improve Tag component by making it entire component clickable (#598)
- **og-images**: wrap Buffer in Uint8Array for Response body (#568)
- make post header vertical bar respect global settings (#562)
- skip invalid code block metadata without key-value pairs (#561)

### Refactor

- update component props and improve types (#600)
- improve props usage and dynamic rendering in LinkButton (#599)
- improve semantic by replacing decorative hr with borders (#597)

## v5.5.0 (2025-07-12)

### Feat

- enhance file name transformer with additional options (#555)

### Fix

- update syntax highlighting transformer styles (#558)
- typo in astro-paper-v5 blog post (#556)

## v5.4.3 (2025-06-21)

### Fix

- remove time from post datetime display (#546)
- update edit post link styling and text (#545)
- typos across codebase (#543)

## v5.4.2 (2025-06-15)

### Fix

- broken typography in about layout (#541)
- remove extra padding in fenced code blocks (#540)

## v5.4.1 (2025-06-14)

### Fix

- make heading anchors in article visible on mobile (#537)

### Refactor

- update tailwind typography css overrides (#538)

## v5.4.0 (2025-06-14)

### Feat

- add file name transformer for fenced code blocks (#535)
- add RTL language support (#531)
- add Shiki transformers for better syntax highlighting (#534)

### Fix

- replace broken prev/next links with correct paths (#533)

## v5.3.0 (2025-06-11)

### Feat

- improve back-to-top button behavior (#520)(#527)

### Fix

- navigation flicker on Android when in dark mode (#494)
- add scroll offset for anchor targets (#506)
- add types for constants to avoid type errors when empty (#501)
- update heading alignment and font-size (#473)

### Refactor

- extract redundant max-width into utility (#525)
- use new astro env (#507)

## v5.2.0 (2025-03-22)

### Feat

- add global and per-post timezone support (#491)

### Fix

- adjust nav bar alignment in heading (#492)
- ensure only one search bar is displayed on nav link clicks (#489)

## v5.1.1 (2025-03-20)

### Fix

- initial light mode flash in dark mode (#488)
- broken editPost link and update editPost logic  (#487)
- prevent overflow by adding line breaks in table codes (#485)

## v5.1.0 (2025-03-18)

### Feat

- allow blog posts to be organized by subdirectories

### Other

- update blog post creation guide
- upgrade astro and dependencies

## v5.0.1 (2025-03-12)

### Fix

- update docker-compose (#475)
- update import location in giscus example (#474)
- add an option to disable dynamic OG image generation (#476)
- remove unused `ogImage` size validation (#462)
- correct Google Fonts API URL construction for proper weight fetching
- align vertically in header nav (#460)
- add font-weight param in og image card style (#453)

### Docs

- update giscus integration guide for AstroPaper v5 (#472)
- update color schemes guide for AstroPaper v5 (#469)
- update LaTeX equations guide in Astro blog posts (#461)

## v5.0.0 (2025-03-08)

### Feat

- add pagefind for static search (#458)
- update back button logic

### Fix

- ignore  in eslint
- update blog table padding
- remove unused back url in the card url
- show light/dark button according to site setting
- add author url in Google JSON-LD conditionally

### Refactor

- remove react dependency for UI interactions (#457)
- separate config and constants
- update import alias in files
- update blog directory to `src/data/blog`


- upgrade to Tailwind CSS v4
- update import alias to `@/*`
- upgrade Astro to v5 and related packages

## v4.8.0 (2025-02-08)

### Feat

- add pencil icon before suggestion changes text (#405)

### Fix

- use tag name for display in tags page (#438)
- exclude `/archives` from sitemap if it is disabled (#425)
- add inline-block class to post title for improved view transition animation (#420)
- sort archive posts by pubDatetime (#415)
- focus search input on mount (#414)
- replace twitter with x (#407)

## v4.7.0 (2024-10-15)

### Feat

- add archives page with configurable menu (#386)

## v4.6.0 (2024-10-13)

### Feat

- add edit post feature in blog posts (#384)

### Refactor

- remove duplicate [page].astro (#389)

## v4.5.1 (2024-10-02)

### Fix

- **docs**: update giscus blog post (#392)
- add missing posts sorting (#383)

## v4.5.0 (2024-09-16)

### Feat

- add prev/next links at the bottom of blog post (#372)

### Fix

- **og**: add the missing SITE.website to loadGoogleFonts  (#360)
- **blog**: correct file reference in reading time guide (#359)

### Refactor

- replace pagination logic with Astro built-in pagination (#376)

### Perf

- preload font and load theme script asynchronously (#380)

## v4.4.0 (2024-08-19)

### Content Layer API

- upgrade Astro and use Content Layer API (#355)

### Others

- upgrade ESLint to v9 and update configurations (#356)
- replace github-slugger with lodash.kebabcase (#357)

## v4.3.2 (2024-08-17)

### Fix

- **a11y**: remove aria-labels from non-interactive elements (#346)

### Refactor

- update tailwind classes to v3 syntax (#345)
- remove commented codes

### Others

- docs: update estimated reading time blog post (#354)
- docs: add instructions for Google Site Verification in AstroPaper (#353)
- docs: update pre-commit hook blog post (#344)
- ci: add CI workflow (#340)

## v4.3.1 (2024-07-27)

### Fix

- resolve non-latin char issue in generated OG images (#318)

## v4.3.0 (2024-07-27)

### Feat

- support light/dark theme in code blocks (#327)
- add number of posts config for home page (#281)
- make heading links keyboard focusable (#275)
- add JSON-LD structured data (#260)
- add scroll indicator in blog posts (#249)

### Fix

- adding data-theme to tailwind config (#319)
- avoid `undefined` when passing class-name as prop (#270)
- add $CURRENT_TIMEZONE_OFFSET in custom code snippets (#264)
- display `Updated` in posts only when modDatetime > pubDatetime (#258)
- add SITE.title in PostDetails title tag for consistent look (#247)
- add trailing slash to links to avoid extra redirects (#246)
- update incorrect typo in predefined-color-schemes.md (#245)

### Refactor

- remove trailing commas in tsconfig.json (#325)
- remove redundant role in article element (#323)
- avoid using unnecessary class-name in the pagination component (#274)
- update post detail script codes
- update code formatting with prettier

## [4.2.0](https://github.com/satnaing/astro-paper/compare/v4.1.0...v4.2.0) (2024-01-22)

### Features

* add heading links to PostDetails page ([#232](https://github.com/satnaing/astro-paper/issues/232)) ([742baff](https://github.com/satnaing/astro-paper/commit/742baff2c9bd47e0762f5d65f5b47a4d28014175))
* hide posts in Prod with future pubDatetime  ([#234](https://github.com/satnaing/astro-paper/issues/234)) ([3efa05c](https://github.com/satnaing/astro-paper/commit/3efa05cc101688c32fc531af0122023d3ce82f08))

### Bug Fixes

* remove extra padding if lightAndDarkMode is false ([#230](https://github.com/satnaing/astro-paper/issues/230)) ([742314e](https://github.com/satnaing/astro-paper/commit/742314e0ac350a70ce1cc256e858c8de9c9153f6))
* reduce margin-bottom on markdown images ([#235](https://github.com/satnaing/astro-paper/issues/235)) ([1331795](https://github.com/satnaing/astro-paper/commit/1331795a4965aab5c47581c223f32f3ea2cd71ab))
* resolve broken line break in inline code ([#237](https://github.com/satnaing/astro-paper/issues/237)) ([ece0682](https://github.com/satnaing/astro-paper/commit/ece0682adce387f2a169185680cdf372a457e938))
* remove recent posts section if there's no post ([#238](https://github.com/satnaing/astro-paper/issues/238)) ([629dbfd](https://github.com/satnaing/astro-paper/commit/629dbfda5b99a71e629dbbf1845c3ceba5ac97e0)), closes [#204](https://github.com/satnaing/astro-paper/issues/204)
* update back button to redirect to home when no route history ([#241](https://github.com/satnaing/astro-paper/issues/241)) ([8f75f0a](https://github.com/satnaing/astro-paper/commit/8f75f0a5e75778a60e8030bb45b19289c0af502e))

### Others

* upgrade astro and other dependencies ([e903b69](https://github.com/satnaing/astro-paper/commit/e903b699cd947301256de1e62ae0ad2d1dcd3c2b))
* update code formatting with prettier ([424c422](https://github.com/satnaing/astro-paper/commit/424c422392d836516bfbb6004a234a1a57930be1))
* add astro extension in lint-staged code formatting ([d41bb69](https://github.com/satnaing/astro-paper/commit/d41bb69cd8f441caa773a07d911adb3ade54b493))
* update outdated prettier script ([1281b93](https://github.com/satnaing/astro-paper/commit/1281b9340a6bebd67628a8d4c56f318701ffde47))

## [4.1.0](https://github.com/satnaing/astro-paper/compare/v4.0.0...v4.1.0) (2024-01-10)

### Features

* update Astro and other dependencies ([f70a0b7](https://github.com/satnaing/astro-paper/commit/f70a0b78ed44350f6d1b00153ea0cc5b7d285043)) ([034dd39](https://github.com/satnaing/astro-paper/commit/034dd394abd4df5cb95fcfe975749cc535a6c05c))
* add share links in blog post ([#215](https://github.com/satnaing/astro-paper/issues/215))
* add copy buttons for code blocks ([#217](https://github.com/satnaing/astro-paper/issues/217))

### Bug Fixes

* resolve accessibility issues ([#226](https://github.com/satnaing/astro-paper/issues/226))
* solve modDatetime type errors ([#214](https://github.com/satnaing/astro-paper/issues/214))
* remove SocialObjects type and update SocialObjects type ([#225](https://github.com/satnaing/astro-paper/issues/225))

### Others

* adds blog post for how to add a social icon ([#221](https://github.com/satnaing/astro-paper/issues/221)) 
* updates the hook post with a smarter updateHook ([#222](https://github.com/satnaing/astro-paper/issues/222))
* update breadcrumbs delimiter to "»" ([#213](https://github.com/satnaing/astro-paper/issues/213))

## [4.0.0](https://github.com/satnaing/astro-paper/compare/v3.0.0...v4.0.0) (2024-01-04)


### ⚠ BREAKING CHANGES

* Astro v4 upgrade

### Features

* add code-snippets for content creation ([#206](https://github.com/satnaing/astro-paper/issues/206)) ([bb2f290](https://github.com/satnaing/astro-paper/commit/bb2f29008a96a0333e4c3adda202d20909728dfe))
* add docker-compose file ([#174](https://github.com/satnaing/astro-paper/issues/174)) ([fb3fa98](https://github.com/satnaing/astro-paper/commit/fb3fa98936d76331869641014d5b4568a84d8d42)), closes [#172](https://github.com/satnaing/astro-paper/issues/172)
* add image validation to schema ([e9d4303](https://github.com/satnaing/astro-paper/commit/e9d4303219bf312bc3955bb8af9aedb0eadb17cc))
* add modified datetime in blog posts ([80e67a1](https://github.com/satnaing/astro-paper/commit/80e67a1dcad19394d7b466472f3c674470db8e0c)), closes [#134](https://github.com/satnaing/astro-paper/issues/134)
* add pagination in tag posts ([#201](https://github.com/satnaing/astro-paper/issues/201)) ([581826a](https://github.com/satnaing/astro-paper/commit/581826a5affd03d12416a5ac7d28ed17d53eac8d)), closes [#152](https://github.com/satnaing/astro-paper/issues/152)
* add transition effect if light/dark changes ([a060cb5](https://github.com/satnaing/astro-paper/commit/a060cb5c87f733c455ea247d72f88095f1ca769c))
* add view transitions for card on search page ([#118](https://github.com/satnaing/astro-paper/issues/118)) ([6c7d04f](https://github.com/satnaing/astro-paper/commit/6c7d04fa12d006379157cf876c2826f606f124e9))
* add ViewTransitions from Astro ([cbdaa59](https://github.com/satnaing/astro-paper/commit/cbdaa59baea1c5c5497227dd2fb276e8cf88b936)), closes [#96](https://github.com/satnaing/astro-paper/issues/96)
* default post author to site author ([20c8970](https://github.com/satnaing/astro-paper/commit/20c89709ada7e7c3f49460d6690d02999ba86d17))
* dynamically generate robots.txt ([6352353](https://github.com/satnaing/astro-paper/commit/63523534703c1f95ac070452001070e2c3f74d5d))
* generate og image using templates ([3032c18](https://github.com/satnaing/astro-paper/commit/3032c18321dfd4f001bc86c094881219bd2e22b7))
* implement back-to-top button in blog post page ([c526157](https://github.com/satnaing/astro-paper/commit/c526157118b69ff68e3a653eee68428a791a7d9f)), closes [#156](https://github.com/satnaing/astro-paper/issues/156)
* og image routes ([300d014](https://github.com/satnaing/astro-paper/commit/300d014fd7a83f52020bdc21976de8487eb41f63))
* replace slugified title with unslugified tag name ([#198](https://github.com/satnaing/astro-paper/issues/198)) ([b05b8fb](https://github.com/satnaing/astro-paper/commit/b05b8fb842b43f4f6462b425cb46d835579cbcfb)), closes [#179](https://github.com/satnaing/astro-paper/issues/179)
* support custom canonical URLs ([#83](https://github.com/satnaing/astro-paper/issues/83)) ([4687bd5](https://github.com/satnaing/astro-paper/commit/4687bd516b16970fc4d163c1202b28f29818a582))
* update theme-color tag on theme switch ([f253776](https://github.com/satnaing/astro-paper/commit/f25377674ebc10f496ef6e5729b931d61ec67832))


### Bug Fixes

* [#133](https://github.com/satnaing/astro-paper/issues/133) update LOCALE config to cover overall locales ([cd02b04](https://github.com/satnaing/astro-paper/commit/cd02b047d2b5e3b4a2940c0ff30568cdebcec0b8))
* [#72](https://github.com/satnaing/astro-paper/issues/72) replace SITE.website with a URL in astro.config site value ([26ecd17](https://github.com/satnaing/astro-paper/commit/26ecd173ddec1075abb6ede9bbb62572b9f74b33))
* anchor overflow on small screen size ([d025c91](https://github.com/satnaing/astro-paper/commit/d025c914d91a9b7969c8db4bd6a700723ef86a39))
* **css:** text wrap in code blocks ([0c92492](https://github.com/satnaing/astro-paper/commit/0c92492959bed20f144d5d949116891d61c8e098))
* decode unicode tag chars in breadcrumb ([#175](https://github.com/satnaing/astro-paper/issues/175)) ([058c790](https://github.com/satnaing/astro-paper/commit/058c790d26cbeab286679a8a8e3bad6c14042d6d))
* get og image url correctly ([7f3edbd](https://github.com/satnaing/astro-paper/commit/7f3edbdecdce597d15e562e7d497d69af505d550))
* **layout:** use 100svh for min-height on body instead of 100vh ([79d569d](https://github.com/satnaing/astro-paper/commit/79d569d053036f2113519f41b0d257523d035b76)), closes [#127](https://github.com/satnaing/astro-paper/issues/127)
* og image src ([6dffcf3](https://github.com/satnaing/astro-paper/commit/6dffcf3cb36a0dab6549ee249fe426b4ee931b06))
* prevent white flash in dark mode when navigate ([9eeb8fc](https://github.com/satnaing/astro-paper/commit/9eeb8fc76ecfd45b79ab716305f1916491649c95))
* remove empty string as ogImage ([b03b722](https://github.com/satnaing/astro-paper/commit/b03b7223694b4c215c6fce0a45ed4f03178081f4))
* resolve single-line code block wrapping issue ([#121](https://github.com/satnaing/astro-paper/issues/121)) ([0af3251](https://github.com/satnaing/astro-paper/commit/0af32518b343430dd8510470efd3806509337de7))
* solve invisible text code block issue in light-mode ([#163](https://github.com/satnaing/astro-paper/issues/163)) ([64b3a28](https://github.com/satnaing/astro-paper/commit/64b3a286e6e3ff1dff7cf4ca0fc8fafc222cabcd))
* sort posts in [tag] page ([#101](https://github.com/satnaing/astro-paper/issues/101)) ([b571816](https://github.com/satnaing/astro-paper/commit/b571816dcddc72a07147389090502c09025b28a6))
* update auto-gen OG images to allow special char usage in title ([1933a6b](https://github.com/satnaing/astro-paper/commit/1933a6beae7b4e2558b808d1f8a5c124f1244138)), closes [#103](https://github.com/satnaing/astro-paper/issues/103) [#88](https://github.com/satnaing/astro-paper/issues/88)
* update rss pubDate to prioritize modDatetime if exists ([e1514b4](https://github.com/satnaing/astro-paper/commit/e1514b41024bc10bcafcc4af548a6ebe0e093468))
* update tailwind base styles config ([#116](https://github.com/satnaing/astro-paper/issues/116)) ([4a03558](https://github.com/satnaing/astro-paper/commit/4a0355865081d07d05d9d758f520e411952a1063))
* update title of the blog nowrap ([87b3e5b](https://github.com/satnaing/astro-paper/commit/87b3e5b8cd7d424b3e43e6d5abed6d21195aa759))


* build!(deps): upgrade Astro and related packages to v4 ([a1d3ddd](https://github.com/satnaing/astro-paper/commit/a1d3ddd18591843a35b3c05be762e1f8af1b8fb0)), closes [#187](https://github.com/satnaing/astro-paper/issues/187)

## [3.0.0](https://github.com/satnaing/astro-paper/compare/v2.3.0...v3.0.0) (2023-09-25)

### ⚠ BREAKING CHANGES

* Astro v3

> Check the AstroPaper v3 in [this blog post](https://astro-paper.pages.dev/posts/astro-paper-v3/)

### Features

* upgrade to astro v3 ([8fda50f](https://github.com/satnaing/astro-paper/commit/8fda50f5ddb7130b7954ad217eed1848094ee33c)), closes [#111](https://github.com/satnaing/astro-paper/issues/111)
* add view transitions for card on search page ([#118](https://github.com/satnaing/astro-paper/issues/118)) ([b873ed5](https://github.com/satnaing/astro-paper/commit/b873ed5a07e746404960690669e8960c2a4c628d))
* add ViewTransitions from Astro ([9703e54](https://github.com/satnaing/astro-paper/commit/9703e54ca4264b0437e06c45bbcc53a7a7d1e106)), closes [#96](https://github.com/satnaing/astro-paper/issues/96)
([b873ed5](https://github.com/satnaing/astro-paper/commit/b873ed5a07e746404960690669e8960c2a4c628d)), closes [#96](https://github.com/satnaing/astro-paper/issues/96)
* generate OG image using templates ([0f82206](https://github.com/satnaing/astro-paper/commit/0f822060cec82b218b568e9ef311fe6adc8b7a1e))
* support custom canonical URLs ([#83](https://github.com/satnaing/astro-paper/issues/83)) ([4687bd5](https://github.com/satnaing/astro-paper/commit/4687bd516b16970fc4d163c1202b28f29818a582))
* update theme-color tag on theme switch ([b5f5418](https://github.com/satnaing/astro-paper/commit/b5f54180c8645113ae4e177f3ebb97e1947dc9e2))
* use new og images in layout ([ec3c691](https://github.com/satnaing/astro-paper/commit/ec3c69114f7344b27797853e2e5a573feb5c63fc))


### Bug Fixes

* replace SITE.website with a URL in astro.config site value ([26ecd17](https://github.com/satnaing/astro-paper/commit/26ecd173ddec1075abb6ede9bbb62572b9f74b33)), fixes [#72](https://github.com/satnaing/astro-paper/issues/72)
* **css:** make code scrollable in code blocks ([0c92492](https://github.com/satnaing/astro-paper/commit/0c92492959bed20f144d5d949116891d61c8e098))
* remove empty string as ogImage ([5259994](https://github.com/satnaing/astro-paper/commit/5259994525b0b67a584b4268a3fbb74258871a3a))
* resolve single-line code block wrapping issue ([#121](https://github.com/satnaing/astro-paper/issues/121)) ([8f08018](https://github.com/satnaing/astro-paper/commit/8f0801836a589133932dc5a450060fd2f16daf74))
* sort posts in [tag] page ([#101](https://github.com/satnaing/astro-paper/issues/101)) ([b571816](https://github.com/satnaing/astro-paper/commit/b571816dcddc72a07147389090502c09025b28a6))
* update auto-gen OG images to allow special char usage in title ([f26bf85](https://github.com/satnaing/astro-paper/commit/f26bf8581288523a0d6021a141cdada685fbce46)), closes [#103](https://github.com/satnaing/astro-paper/issues/103) [#88](https://github.com/satnaing/astro-paper/issues/88)
* update tailwind base styles config ([#116](https://github.com/satnaing/astro-paper/issues/116)) ([98a2bb6](https://github.com/satnaing/astro-paper/commit/98a2bb682af2773d6af7782a6592e9b9fab79b3b))
* update title of the blog nowrap ([2df71b9](https://github.com/satnaing/astro-paper/commit/2df71b9b4587c7a2438f483e8365ef5b8a502ce7))

## [2.3.0](https://github.com/satnaing/astro-paper/compare/v2.2.0...v2.3.0) (2023-05-15)


### Features

* add locale configuration for Datetime component ([#59](https://github.com/satnaing/astro-paper/issues/59)) ([0e9f709](https://github.com/satnaing/astro-paper/commit/0e9f709c5dbd9a75aaf33e7994e88216fd56d8be))


### Bug Fixes

* add missing sitemap in head ([#69](https://github.com/satnaing/astro-paper/issues/69)) ([f6ac810](https://github.com/satnaing/astro-paper/commit/f6ac8104b2ba20de3b71eb5dde395e5adce9dfe7))
* build error astro@2.1.4 && update astro@2.1.5 ([#49](https://github.com/satnaing/astro-paper/issues/49)) ([dd4fd98](https://github.com/satnaing/astro-paper/commit/dd4fd989722cbcb3e98045e808a32292cf555900))
* **ignore:** added yarn directories to ignorefiles ([f3e9cd5](https://github.com/satnaing/astro-paper/commit/f3e9cd51479fd41f3c0e8863ac13c77d6daa2605))
* replace history entries when searching ([#62](https://github.com/satnaing/astro-paper/issues/62)) ([a57f343](https://github.com/satnaing/astro-paper/commit/a57f3439f801c1d41256a8a46bd319c17dff86f1))
* slugify tags in post detail page ([49d7f77](https://github.com/satnaing/astro-paper/commit/49d7f77a86987c00d211090301b662e21a27ce17))
* sort rss feed from latest to oldest ([#38](https://github.com/satnaing/astro-paper/issues/38)) ([9e62b63](https://github.com/satnaing/astro-paper/commit/9e62b637e8ddb65f5f274fd0154191212dda0590))
* tailwind jsdoc for intellisense ([99709dd](https://github.com/satnaing/astro-paper/commit/99709dd3aa2329220a497f7038b7ab069d389847))
* update lint-staged configuration ([e654c03](https://github.com/satnaing/astro-paper/commit/e654c0308c26ccffdd0a4abc50f0adb99c76d9ca)), closes [#52](https://github.com/satnaing/astro-paper/issues/52)
* update menu element with svg and refactor toggle logic ([0f76424](https://github.com/satnaing/astro-paper/commit/0f764242fea14565798085447d8524b4bf05f76a))

## [2.2.0](https://github.com/satnaing/astro-paper/compare/v2.1.0...v2.2.0) (2023-03-16)


### Features

* generate og images in png format ([#43](https://github.com/satnaing/astro-paper/issues/43)) ([27507d1](https://github.com/satnaing/astro-paper/commit/27507d1d78531901c20a17d9ce72728c6cbb521e)), closes [#40](https://github.com/satnaing/astro-paper/issues/40)


### Bug Fixes

* add plugin-search-dir in prettier write for pnpm ([e49ca61](https://github.com/satnaing/astro-paper/commit/e49ca61d6b7048a8e8b2f50b1d947fd91eaca3eb)), ([37b54af](https://github.com/satnaing/astro-paper/commit/37b54afd9471eb35588e09f1f33ae1634732b02c)), closes [#34](https://github.com/satnaing/astro-paper/issues/34)
* correct typo in blog posts ([cbce54b](https://github.com/satnaing/astro-paper/commit/cbce54bd1cf951c36a8603db8f7a8487481fc7f1)), closes [#35](https://github.com/satnaing/astro-paper/issues/35)
* slugifyAll typo ([bcae985](https://github.com/satnaing/astro-paper/commit/bcae9856712773887664bb3a3392e1ebfd78607b))

### Others

* update Astro to v2.1.3 and enable type checking in dev ([329bc22](https://github.com/satnaing/astro-paper/commit/329bc22e97892e5687a841d580215c8fb2d44aa1))
* add jampack for performance optimization ([#46](https://github.com/satnaing/astro-paper/pull/46)) ([b9254c1](https://github.com/satnaing/astro-paper/commit/b9254c15f1b382c2f3900b3371abce8975768dd9))

## [2.1.0](https://github.com/satnaing/astro-paper/compare/v2.0.0...v2.1.0) (2023-02-08)


### Features

* add ESLint and update linting errors ([#26](https://github.com/satnaing/astro-paper/issues/26)) ([a9631d0](https://github.com/satnaing/astro-paper/commit/a9631d0e1e65ac4339c6b4d806b3a17928fa2b62))


### Bug Fixes

* make schema(s) strict ([#23](https://github.com/satnaing/astro-paper/issues/23)) ([dc026b3](https://github.com/satnaing/astro-paper/commit/dc026b38defa760d77eddcddb1d4f12fdf8fff99))
* fix typo and remove unnecessary comments ([#24](https://github.com/satnaing/astro-paper/pull/24)) ([d9a2ffe](https://github.com/satnaing/astro-paper/commit/d9a2ffe9096e2419a740c5b98b57323fbf2f2cb0)) ([#25](https://github.com/satnaing/astro-paper/pull/25)) ([29e0776](https://github.com/satnaing/astro-paper/commit/29e07761f78fa24b307601bf2272a61e084a468b))
* update dependencies

## [2.0.0](https://github.com/satnaing/astro-paper/compare/v1.4.0...v2.0.0) (2023-01-31)


### ⚠ BREAKING CHANGES

Check the AstroPaper v2 in [this blog post](https://astro-paper.pages.dev/posts/astro-paper-2/)

* **deps:** Migration of Astro to version 2

### Features

* add Mastodon social link ([2ec3912](https://github.com/satnaing/astro-paper/commit/2ec39128c65fd0b1dafd6aebd48ac3068f40f9c5))
* add new predefined color scheme 'astro dark' ([bc263b6](https://github.com/satnaing/astro-paper/commit/bc263b6eac00fbc8ec62481f2ec0317ee11bc83a))
* define blog schema and add blog collection ([b420e68](https://github.com/satnaing/astro-paper/commit/b420e688ca3a197a7e4ea2591193fd09da817ec7))


### Bug Fixes

* add embedFont option for Satori ([9322123](https://github.com/satnaing/astro-paper/commit/93221239ddaebaa9ab183871cf978548ea8d0ea5))
* exclude draft posts in specific tag page ([c192cd8](https://github.com/satnaing/astro-paper/commit/c192cd8e5042d4481bcb0d0389866cf4a969aa8d))
* fix broken tags in PostDetails page ([a61fd45](https://github.com/satnaing/astro-paper/commit/a61fd455594932c66380a358b81b8bebb9d604cc))
* fix typo in title and slug ([945acf4](https://github.com/satnaing/astro-paper/commit/945acf4260e0ea79bde8b180835049eda07d3e6a))
* hide social links section if no link is active ([42eb018](https://github.com/satnaing/astro-paper/commit/42eb0188896a8475a7fbb894775e5500ca8b7d35)), closes [#16](https://github.com/satnaing/astro-paper/issues/16)
* make the last part of breadcrumb lowercase in specific tag page ([c556202](https://github.com/satnaing/astro-paper/commit/c556202c972f1f9fed9af0ba6abf199e7deccc5f))
* resolve initial onChange input value bug ([bf4f687](https://github.com/satnaing/astro-paper/commit/bf4f687d2d87cfeef96141c5324d02c37766845b))
* update card bg color ([8a99601](https://github.com/satnaing/astro-paper/commit/8a99601e93f90c0870a22aa4a8ea8b7ff1b76a98))
* use default-og for twitter card ([9434d85](https://github.com/satnaing/astro-paper/commit/9434d850e1f41f0802de5706c4c5712e5b5def9d))


### build

* **deps:** bump astro and its packages to v2 ([5f279b3](https://github.com/satnaing/astro-paper/commit/5f279b34f88bd94bed820d16c1e1d5e95859045f))

## [1.4.0](https://github.com/satnaing/astro-paper/compare/v1.3.0...v1.4.0) (2022-12-28)


### Features

* generate dynamic og image for blog posts ([#15](https://github.com/satnaing/astro-paper/issues/15)) ([ce3f1dc](https://github.com/satnaing/astro-paper/commit/ce3f1dc4a0df8f196dce37de1c976870e9c97279))


### Bug Fixes

* fix grammar mistake ([02faff9](https://github.com/satnaing/astro-paper/commit/02faff9fbd4444144eeb139ae62850ec5a980dd3))

## [1.3.0](https://github.com/satnaing/astro-paper/compare/v1.2.1...v1.3.0) (2022-12-07)


### Features

* update mobile nav to be accessible ([46ea4aa](https://github.com/satnaing/astro-paper/commit/46ea4aa49a49a3d21ca5ce1cee1b51f0108c13f0))

### [1.2.1](https://github.com/satnaing/astro-paper/compare/v1.2.0...v1.2.1) (2022-12-02)


### Bug Fixes

* disable access to draft posts via url ([1c2821e](https://github.com/satnaing/astro-paper/commit/1c2821e4df65bee7126aed17244bb6590b1163d8))
* display '0 results' instead of '0 result' in Search ([eceb289](https://github.com/satnaing/astro-paper/commit/eceb2895623cffefc65671fdfc343fa5e4c01cdb))
* displays featured section only if featured posts exist ([e0f93da](https://github.com/satnaing/astro-paper/commit/e0f93dab02024d65ddb69925a21e8d8598a036e9))
* fix calculating draft posts in totalPages ([19e34a0](https://github.com/satnaing/astro-paper/commit/19e34a0801019df8681d1d4e80f678989cf2457c))
* hide pagination when there's only 1 page ([6b35c7f](https://github.com/satnaing/astro-paper/commit/6b35c7fc2f63bb16aaefc140029b1eae1235cc44))

## [1.2.0](https://github.com/satnaing/astro-paper/compare/v1.1.3...v1.2.0) (2022-11-28)


### Features

* improve accessibility including voiceover ([5860254](https://github.com/satnaing/astro-paper/commit/5860254ea99996e466f2e521f033763961b6faa6))
* add linkTitle in social links ([c9f796f](https://github.com/satnaing/astro-paper/commit/c9f796f4e63f1cf6b32b7874ae5e3810598a230c))


### Updates

* move toggle theme codes from `layouts/Layout.astro` to `toggle-theme.js` ([5860254](https://github.com/satnaing/astro-paper/commit/5860254ea99996e466f2e521f033763961b6faa6))
* delete `utils/formatDatetime.ts` and replaced with `FormattedDatetime` inside `components/Datetime.tsx` ([0eeed8e](https://github.com/satnaing/astro-paper/commit/0eeed8e870781d9b4a447c51e3055ccb2f359d8a))
* 'toggling light and dark mode' code is remove from `src/components/Header.astro` and is rewritten in `public/toggle-theme.js` file. ([2ba459b](https://github.com/satnaing/astro-paper/commit/2ba459b4131a11a68a5fd818a278c474c1888cde)) ([0eeed8e](https://github.com/satnaing/astro-paper/commit/0eeed8e870781d9b4a447c51e3055ccb2f359d8a))
* update previous and next button disabled state ([408fc4c](https://github.com/satnaing/astro-paper/commit/408fc4c7aa5a246fe82a6e85d119b36ee1f1ffc3))
* **typo:** rename Linkedin to LinkedIn ([307b55f](https://github.com/satnaing/astro-paper/commit/307b55ff0f6cb86a4fa4152c635d6acb39d1512f))
* update patch and minor dependencies ([3b0ab75](https://github.com/satnaing/astro-paper/commit/3b0ab7555f506a8a0b825ca9691fdb221e481adb)) ([c3a6e4e](https://github.com/satnaing/astro-paper/commit/c3a6e4e81d1f79efc17d451486ff560dccb8ddf0))

### [1.1.3](https://github.com/satnaing/astro-paper/compare/v1.1.2...v1.1.3) (2022-11-11)


### Bug Fixes

* fix broken post links and hide draft posts in rss feed ([b83c906](https://github.com/satnaing/astro-paper/commit/b83c906262cb5e1f045ac50f2401527c0b64074c))

### [1.1.2](https://github.com/satnaing/astro-paper/compare/v1.1.1...v1.1.2) (2022-11-04)


### Bug Fixes

* fix heading style in posts/<page-num> layouts ([5eeea66](https://github.com/satnaing/astro-paper/commit/5eeea6639e79f93c3d0917bc827dfd37a23d041c))
* fix missing TailwindCSS dependency ([e7807ab](https://github.com/satnaing/astro-paper/commit/e7807ab94e12898ab85b955132c5d908956c8945)), closes [#6](https://github.com/satnaing/astro-paper/issues/6)
* show search result only if input is more than one char ([f7fb032](https://github.com/satnaing/astro-paper/commit/f7fb032e604bd704adc19400e000c9584a6fdb43))

### [1.1.1](https://github.com/satnaing/astro-paper/compare/v1.1.0...v1.1.1) (2022-10-30)


### Updates

* update github-slugger by @AkaraChen in https://github.com/satnaing/astro-paper/pull/5
* move '@types/react' to dev dependencies ([3697a59](https://github.com/satnaing/astro-paper/commit/3697a59f1ab8b58af7d41c2ef4aa8ba97b9ad1e2))
* update dependencies

## [1.1.0](https://github.com/satnaing/astro-paper/compare/v1.0.1...v1.1.0) (2022-10-18)

### Features

* improve search functionality ([33bab9c](https://github.com/satnaing/astro-paper/commit/33bab9c489d74e1b53109d5f1e8f3586cfcb9433))
* add CHANGELOG ([adb331e](https://github.com/satnaing/astro-paper/commit/adb331e219d122be696fb390ae41f0afaa5a76b9))
* add prettier and husky ([d6dd818](https://github.com/satnaing/astro-paper/commit/d6dd8185f28cfae967cf90c9020580ebce5c36fd) | [80aee6b](https://github.com/satnaing/astro-paper/commit/80aee6bedbc1e40650411b0695f5365902d3b9e2))

### Bug Fixes

* fix markdown lint warnings by updating headers ([ad14dc5](https://github.com/satnaing/astro-paper/commit/ad14dc580fbf886f5de95705ec7910c7c3b46bf0))
* fix markdown warnings by adding alt texts ([3260641](https://github.com/satnaing/astro-paper/commit/326064111cbb7d356659252dd7ddd42dbd2d7e56))
* extract Social component to avoid duplication ([7ef631f](https://github.com/satnaing/astro-paper/commit/7ef631fe35dc57db1c84e7c3c92969fa23ccd42b))
* update glob to have access to sub directories under content/ ([a256ded](https://github.com/satnaing/astro-paper/commit/a256dedb73aaf018cedf764f38843ad176b27058))

## [1.0.1](https://github.com/satnaing/astro-paper/compare/v1.0.0...v1.0.1) (2022-09-27) Initial Release

### Features

- Fully responsive & accessible
- Pagination & draft post
- Light & dark color schemes
- 19 social link icons
- Fuzzy search
- Sitemap & RSS feed
- 5 predefined themes

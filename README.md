# Personal Portfolio and Technical Blog

The site is built with Hugo, deployed to GitHub Pages from the `hugo-site`
branch, and can also be served from a Raspberry Pi with Caddy.

## Content pipeline

The repository includes a research-first, human-in-the-loop workflow for turning
a quick idea into a reviewed, permanent post:

```text
private idea + key points
        -> private research brief + source ledger
        -> grounded Hugo draft
        -> edit + private ChatGPT Sites preview + review
        -> explicit ship
        -> GitHub hugo-site branch + Raspberry Pi
```

Ideas, research briefs, editorial reviews, and the rendered preview repository
live under `.blog/`, which is intentionally ignored by Git. Drafts live in
`content/blogs/` with `draft: true`; the publish command commits only the selected
post. A draft is never pushed to the production branch as part of previewing.

### One-time setup on the Raspberry Pi

Install Git, Python 3.11+, rsync, Hugo extended, and the Codex CLI. Then:

```bash
git submodule update --init --recursive
codex login
chmod +x scripts/blog
./scripts/blog --help
```

Codex reuses the CLI login for local non-interactive research and generation. No
API key is stored in this repository. The private preview Site is already linked
through `.openai/hosting.json`; keep that file in the repository.

### Mobile-first workflow

The easiest entry point is a ChatGPT/Codex task with access to this repository.
A request can be as simple as:

> New article idea: running small language models on a Raspberry Pi. Preserve
> these points: cold-start time mattered more than token speed; separate my
> measurements from general claims. Research it, draft it, and give me a private
> preview link.

`AGENTS.md` tells Codex how to translate that request into the commands below.
The author still controls the key points, edits, and final publish decision.

### Command-line workflow

Capture an idea. Use `--kind nugget` for a short post:

```bash
./scripts/blog idea "What surprised me about running an LLM on a Pi" \
  --kind article \
  --point "Cold starts mattered more than token speed." \
  --point "Separate my measurements from general claims." \
  --notes "I will add the exact hardware and measurements during editing."
```

Research the idea independently. This uses Codex live web search, prefers primary
sources, challenges the initial premise, and writes both a machine-readable
ledger and an editable Markdown brief under `.blog/research/`:

```bash
./scripts/blog research .blog/ideas/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
```

Generate the Hugo draft from the idea, research brief, and `EDITORIAL.md`:

```bash
./scripts/blog draft .blog/ideas/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
```

`draft` automatically runs research if it has not been run yet. Use
`--refresh-research` when the subject has changed or sources may be stale.

Edit the Markdown in `content/blogs/`, run the checks, and optionally ask Codex
for an editorial report that re-verifies time-sensitive claims:

```bash
./scripts/blog check content/blogs/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
./scripts/blog review content/blogs/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
```

For the mobile preview, prepare an isolated static package:

```bash
./scripts/blog preview-build content/blogs/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
```

Then ask Codex in ChatGPT to **deploy the prepared preview privately with
ChatGPT Sites**. Codex uploads only `.blog/sites-preview`, returns the direct
article URL, and keeps the Site owner-only. The stable Site is
`abhinand-blog-drafts.reachabhinandjha.chatgpt.site`; each deployment creates a
new version at the same address. Sites publishing is performed through the
ChatGPT/Codex Sites integration, not by `scripts/blog` or a long-lived API token.

For local development, run `./scripts/blog preview-local`. It binds to localhost
by default and is not useful directly from a phone unless a separate network or
SSH tunnel is configured.

When the post is genuinely ready, ship exactly that file:

```bash
./scripts/blog ship content/blogs/2026-09-06-what-surprised-me-about-running-an-llm-on-a-pi.md
```

After confirmation, `ship` marks the post live, rejects unresolved TODOs, runs a
clean production build, commits only that Markdown file, pushes to
`origin/hugo-site`, and syncs the verified build to `/var/www/hugo` for Caddy.
GitHub Actions independently rebuilds and deploys GitHub Pages from the pushed
`hugo-site` source.

For a GitHub-only machine, skip the Caddy update with `--no-deploy`. For a local
test that creates a commit without external side effects, use both `--no-push`
and `--no-deploy`.

Environment overrides are available for Pi-specific paths and commands:

- `BLOG_WEB_ROOT` (default `/var/www/hugo`)
- `BLOG_WEB_OWNER` (default `caddy:caddy`)
- `BLOG_BRANCH` (default `hugo-site`)
- `BLOG_REMOTE` (default `origin`)
- `BLOG_HUGO_BIN`, `BLOG_CODEX_BIN`, and `BLOG_SUDO_BIN`

The editorial voice, post formats, sourcing rules, and publish checklist live in
`EDITORIAL.md`. Edit that file first as the writing style develops.

## Build manually

```bash
hugo server -D
hugo --gc --minify
```

Built with Hugo.

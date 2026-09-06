# Blog workflow instructions

This repository is Abhinand's Hugo site. Markdown in `content/blogs/` is the
source of truth. Follow `EDITORIAL.md` whenever creating or editing a post.

## Content workflow

- When Abhinand shares an article idea, capture it with
  `./scripts/blog idea "<title>" --kind article|nugget --point "<key point>"`
  and repeat `--point` for each required idea. Put remaining context in
  `--notes`.
- Research before writing with `./scripts/blog research <idea-file>`. Research
  must use live web search, prefer primary sources, test the author's premise,
  and save a private source ledger. `draft` automatically performs this step
  when no research exists.
- Generate the first draft with `./scripts/blog draft <idea-file>`. The command
  writes a Hugo draft from the idea, research brief, and `EDITORIAL.md`.
- Keep generated posts as `draft: true` until Abhinand explicitly says they are
  ready to publish.
- Use `./scripts/blog check <post>` for the mechanical quality gate and
  `./scripts/blog review <post>` for optional editorial feedback.
- For a mobile preview, run `./scripts/blog preview-build <post>`. Then use the
  Sites building and hosting skills on `.blog/sites-preview`, reuse the
  `project_id` from the repository's `.openai/hosting.json`, deploy the saved
  version privately, and return the direct `/blogs/<slug>/` URL. Never deploy a
  draft Site with public or shared access.
- Use `./scripts/blog preview-local` only for a localhost development preview.
- Run `./scripts/blog ship <post>` only when Abhinand explicitly asks to
  publish or ship that post. This is an external action: it can commit, push to
  GitHub, and update the Raspberry Pi web root.
- Production is the `hugo-site` branch. Never push preview history or draft
  content to that branch.
- Never publish every draft as a batch. Ship only the post named by the user.

## Editorial guardrails

- Do not invent personal experiences, results, opinions, quotes, benchmarks,
  or tool usage. Mark missing first-person details for the author to supply.
- Verify time-sensitive technical claims and link to primary sources.
- Prefer concrete examples, honest tradeoffs, and a clear point of view over a
  generic survey of a topic.
- Do not add secrets, private URLs, API keys, personal notes, or `.blog/`
  contents to Git.
- Preserve unrelated working-tree changes.

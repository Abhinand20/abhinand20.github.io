from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
BLOG = PROJECT / "scripts" / "blog"


class BlogPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "content" / "blogs").mkdir(parents=True)
        schemas = self.root / ".codex" / "schemas"
        schemas.mkdir(parents=True)
        shutil.copy(PROJECT / ".codex" / "schemas" / "blog-research.schema.json", schemas)
        shutil.copy(PROJECT / ".codex" / "schemas" / "blog-draft.schema.json", schemas)
        shutil.copy(PROJECT / ".codex" / "schemas" / "blog-review.schema.json", schemas)
        (self.root / "EDITORIAL.md").write_text("Be accurate.\n", encoding="utf-8")
        hosting = self.root / ".openai" / "hosting.json"
        hosting.parent.mkdir(parents=True)
        hosting.write_text(
            '{"project_id":"appgprj_test","static":{"directory":"dist"}}\n',
            encoding="utf-8",
        )
        self.env = os.environ | {"BLOG_ROOT": str(self.root)}

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_blog(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(BLOG), *args],
            cwd=self.root,
            env=self.env,
            check=check,
            text=True,
            capture_output=True,
        )

    def executable(self, name: str, body: str) -> Path:
        path = self.root / name
        path.write_text("#!/bin/sh\nset -eu\n" + body, encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_idea_is_private_and_structured(self) -> None:
        result = self.run_blog(
            "idea",
            "A tiny local AI experiment",
            "--kind",
            "nugget",
            "--notes",
            "Measure the cold-start latency.",
            "--point",
            "Separate model loading from first-token latency.",
        )
        path = self.root / result.stdout.splitlines()[0]
        text = path.read_text(encoding="utf-8")
        self.assertIn('kind: "nugget"', text)
        self.assertIn('status: "idea"', text)
        self.assertIn("Measure the cold-start latency.", text)
        self.assertIn("Separate model loading from first-token latency.", text)

    def test_draft_uses_structured_codex_output(self) -> None:
        idea = self.run_blog("idea", "Useful AI tool", "--notes", "Explain the mechanism.")
        idea_path = idea.stdout.splitlines()[0]
        fake = self.executable(
            "fake-codex",
            """out=''
schema=''
printf '%s\\n' "$*" >> "$PWD/fake-codex.log"
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--output-last-message" ]; then out="$2"; shift 2
  elif [ "$1" = "--output-schema" ]; then schema="$2"; shift 2
  else shift
  fi
done
case "$schema" in
  *blog-research.schema.json)
    printf '%s' '{"working_thesis":"The mechanism is useful when its tradeoffs are understood.","reader_value":"Readers get a grounded decision rule.","findings":[{"claim":"The official guide explains the mechanism.","why_it_matters":"It establishes intended behavior.","evidence":"The guide documents it directly.","source_urls":["https://example.com/docs"],"confidence":"high"},{"claim":"The repository shows the implementation.","why_it_matters":"It makes the details inspectable.","evidence":"The source is publicly available.","source_urls":["https://example.com/repo"],"confidence":"high"}],"counterpoints":[{"point":"The feature has operational tradeoffs.","source_urls":["https://example.com/design"]}],"open_questions":["What did the author observe personally?"],"suggested_outline":[{"heading":"Mechanism","purpose":"Explain how it works.","points":["Trace the main path."]},{"heading":"Tradeoffs","purpose":"Give a decision rule.","points":["State the constraints."]}],"sources":[{"title":"Official docs","url":"https://example.com/docs","publisher":"Example","published_or_updated":"2026","relevance":"Primary behavior documentation."},{"title":"Repository","url":"https://example.com/repo","publisher":"Example","published_or_updated":"2026","relevance":"Primary source code."},{"title":"Design notes","url":"https://example.com/design","publisher":"Example","published_or_updated":"2026","relevance":"Primary design tradeoffs."},{"title":"Release notes","url":"https://example.com/releases","publisher":"Example","published_or_updated":"2026","relevance":"Primary version history."}]}' > "$out"
    ;;
  *)
    printf '%s' '{"description":"A focused description","categories":["AI"],"tags":["tools"],"body_markdown":"This draft explains a useful mechanism using the [official guide](https://example.com/docs) and its [source repository](https://example.com/repo). Together they provide enough concrete evidence to ground the explanation and show readers the important implementation tradeoffs."}' > "$out"
    ;;
esac
""",
        )
        self.env["BLOG_CODEX_BIN"] = str(fake)
        result = self.run_blog("draft", idea_path)
        draft_line = next(line for line in result.stdout.splitlines() if line.startswith("content/blogs/"))
        draft = self.root / draft_line
        text = draft.read_text(encoding="utf-8")
        self.assertIn("draft: true", text)
        self.assertIn('content_kind: "article"', text)
        self.assertIn("A focused description", text)
        self.assertIn("This draft explains", text)
        self.assertTrue((self.root / ".blog" / "research" / f"{Path(idea_path).stem}.json").is_file())
        self.assertIn("--search exec", (self.root / "fake-codex.log").read_text(encoding="utf-8"))

    def test_preview_build_is_isolated_and_includes_the_named_draft(self) -> None:
        post = self.root / "content" / "blogs" / "2026-09-06-private-preview.md"
        post.write_text(
            """---
title: "Private preview"
date: "2026-09-06T10:00:00-07:00"
lastmod: "2026-09-06T10:00:00-07:00"
draft: true
description: "A private mobile preview"
categories: ["AI"]
tags: ["preview"]
content_kind: "nugget"
---

This draft has enough useful words to pass the preview validation gate. It remains unpublished while Hugo renders a complete private copy of the site. The isolated package can then be uploaded to the owner-only preview host without committing this source Markdown file to the production branch.
""",
            encoding="utf-8",
        )
        fake_hugo = self.executable(
            "fake-hugo-preview",
            """dest=''
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--destination" ]; then dest="$2"; shift 2; else shift; fi
done
mkdir -p "$dest/blogs/2026-09-06-private-preview"
printf '%s' '<html>home</html>' > "$dest/index.html"
printf '%s' '<html>draft</html>' > "$dest/blogs/2026-09-06-private-preview/index.html"
""",
        )
        self.env["BLOG_HUGO_BIN"] = str(fake_hugo)

        result = self.run_blog("preview-build", str(post))

        preview = self.root / ".blog" / "sites-preview"
        self.assertTrue((preview / "dist" / "index.html").is_file())
        self.assertEqual(
            json.loads((preview / ".openai" / "hosting.json").read_text(encoding="utf-8"))[
                "project_id"
            ],
            "appgprj_test",
        )
        self.assertIn("/blogs/2026-09-06-private-preview/", result.stdout)

    def test_ship_builds_and_commits_only_the_post(self) -> None:
        post = self.root / "content" / "blogs" / "2026-09-06-test-post.md"
        post.write_text(
            """---
title: "Test post"
date: "2026-09-06T10:00:00-07:00"
lastmod: "2026-09-06T10:00:00-07:00"
draft: true
description: "A useful test post"
categories: ["AI"]
tags: ["testing"]
content_kind: "nugget"
---

This is a concrete draft with enough words to exercise the publishing gate. It explains how the test pipeline validates metadata, builds the Hugo site, marks one post live, and commits exactly that selected source file without staging unrelated work from the repository.
""",
            encoding="utf-8",
        )
        fake_hugo = self.executable(
            "fake-hugo",
            """dest=''
while [ "$#" -gt 0 ]; do
  if [ "$1" = "--destination" ]; then dest="$2"; shift 2; else shift; fi
done
mkdir -p "$dest"
printf '%s' '<html>ok</html>' > "$dest/index.html"
""",
        )
        self.env["BLOG_HUGO_BIN"] = str(fake_hugo)
        subprocess.run(["git", "init", "-b", "hugo-site"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        (self.root / "unrelated.txt").write_text("leave me alone\n", encoding="utf-8")

        self.run_blog("ship", str(post), "--yes", "--no-push", "--no-deploy")

        self.assertIn("draft: false", post.read_text(encoding="utf-8"))
        committed = subprocess.run(
            ["git", "show", "--pretty=", "--name-only", "HEAD"],
            cwd=self.root,
            check=True,
            text=True,
            capture_output=True,
        ).stdout.splitlines()
        self.assertEqual(committed, ["content/blogs/2026-09-06-test-post.md"])
        self.assertTrue((self.root / "unrelated.txt").exists())

    def test_failed_build_restores_draft_status(self) -> None:
        post = self.root / "content" / "blogs" / "2026-09-06-build-failure.md"
        original = """---
title: "Build failure"
date: "2026-09-06T10:00:00-07:00"
lastmod: "2026-09-06T10:00:00-07:00"
draft: true
description: "Exercise a failed build"
categories: ["AI"]
tags: ["testing"]
content_kind: "nugget"
---

This draft contains enough concrete words for validation, but the fake Hugo command fails deliberately. The publishing workflow must restore the original draft status so a build problem can never leave an unverified post looking ready for a later accidental deployment or commit.
"""
        post.write_text(original, encoding="utf-8")
        fake_hugo = self.executable("failing-hugo", "exit 17\n")
        self.env["BLOG_HUGO_BIN"] = str(fake_hugo)
        subprocess.run(["git", "init", "-b", "hugo-site"], cwd=self.root, check=True, capture_output=True)

        result = self.run_blog(
            "ship",
            str(post),
            "--yes",
            "--no-push",
            "--no-deploy",
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(post.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()

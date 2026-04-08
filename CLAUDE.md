# CLAUDE.md — Portfolio Site Implementation Reference

## Overview

Personal portfolio website for Abhinand Jha, built with **Hugo** (v0.145.0 extended). The site uses a dual-theme architecture — a custom local theme (`minimalistic`) layered on top of the upstream `hugo-bearblog` submodule theme. The compiled `public/` output is committed to the repo and served statically.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Static site generator | Hugo v0.145.0 (extended) |
| Primary theme | `themes/minimalistic` (local, custom) |
| Base theme | `themes/hugo-bearblog` (git submodule) |
| CSS framework | Tailwind CSS (loaded via CDN at runtime) |
| Icons | Devicon (CDN) |
| Font | Space Grotesk (Google Fonts) |
| Analytics | Google Analytics 4 (`G-C0RTF18BT4`) |
| CI/CD | GitHub Actions → GitHub Pages |

---

## Repository Structure

```
.
├── hugo.toml                  # Main site config (all content data lives here)
├── go.mod / go.sum            # Hugo module manifests (Go module system)
├── archetypes/default.md      # Template for new content files
├── content/                   # Markdown source pages
│   ├── experience.md
│   ├── projects.md
│   ├── contact.md
│   └── blogs/                 # Blog posts (2022–2023)
│       ├── _index.md
│       └── *.md
├── layouts/                   # Site-level layout overrides (blogs section)
│   └── blogs/
│       ├── baseof.html
│       ├── list.html
│       └── single.html
├── static/                    # Static assets copied verbatim to public/
│   ├── images/
│   ├── assets/                # PDF resume (CV_Abhinand.pdf)
│   └── favicon_io/
├── themes/
│   ├── minimalistic/          # Primary custom theme (local)
│   └── hugo-bearblog/         # Upstream base theme (git submodule)
├── public/                    # Pre-built site output (committed)
├── resources/_gen/            # Hugo asset pipeline cache
└── .github/workflows/hugo.yaml
```

---

## Configuration

All site content (experience, projects, education) is declared directly in `hugo.toml` via `[[params.*]]` arrays — there are **no separate data files**. To add or edit content, edit `hugo.toml`.

Key config values:

```toml
baseURL = ""          # Empty; resolved at build time
relativeURLs = true   # All URLs are relative (important for self-hosting)
canonifyURLs = true   # Converts relative to absolute using baseURL at build

theme = ['minimalistic', 'hugo-bearblog']   # Merge order: minimalistic wins
```

The `resume_link` param points to `assets/CV_Abhinand.pdf` under `static/assets/`.

---

## Theme Architecture

### Theme Merge Order

Hugo merges themes left-to-right in the `theme` array, with **earlier entries taking priority**. `minimalistic` overrides any conflicting layout from `hugo-bearblog`.

### `themes/minimalistic/` (Primary Theme)

All visual design lives here. Key files:

| File | Purpose |
|---|---|
| `layouts/_default/baseof.html` | Root HTML shell; loads Tailwind CDN, Devicon CDN, Google Fonts, inline FOUC-fix styles, and dark mode init script |
| `layouts/partials/header.html` | Responsive nav with hamburger menu + live local time display; contains Google Analytics tag |
| `layouts/partials/footer.html` | Site footer |
| `layouts/index.html` | Homepage layout |
| `layouts/_default/experience.html` | Timeline-style work/education history |
| `layouts/_default/projects.html` | Project card grid |
| `layouts/_default/contact.html` | Contact page |
| `layouts/_default/blogs.html` | Blog listing |
| `layouts/blogs/single.html` | Individual blog post |
| `assets/css/main.css` | Tailwind directives + custom component classes |
| `tailwind.config.js` | Tailwind config scoped to `layouts/**/*.html` and `content/**/*.{html,md}` |

**Note:** Tailwind is loaded via CDN (`https://cdn.tailwindcss.com?plugins=typography`) at runtime rather than being compiled at build time. The `assets/css/main.css` with Tailwind directives exists but is not part of the CDN-based pipeline.

### Dark Mode

The site defaults to dark mode (`#121212` background). An inline `<script>` in `baseof.html` reads `localStorage['color-theme']` before paint to prevent flash of unstyled content (FOUC). The theme toggle wires to `#theme-toggle` button if present.

### Animated Tech Carousel

The homepage features a scrolling tech icon carousel using a CSS `@keyframes scroll` animation (`translateX 0 → -100%` over 20s linear, infinite). The `.tech-track:hover` pauses the animation.

---

## Content Model

### Pages

Each section page (`experience.md`, `projects.md`, `contact.md`) is a simple Markdown file whose front matter sets the `layout` to the corresponding `_default` template. All structured data (roles, descriptions, projects) is in `hugo.toml`.

### Blog Posts

Located in `content/blogs/`. Standard Hugo single pages rendered by `layouts/blogs/single.html`. Tagged with `categories` and `tags` taxonomies; term listings are generated automatically.

### Taxonomies

```toml
[taxonomies]
  category = "categories"
  tag = "tags"
```

Both taxonomy types are active; term list pages are generated under `/categories/` and `/tags/`.

---

## Building the Site

### Prerequisites

- Hugo extended v0.145.0+
- Dart Sass (for Sass compilation if needed)
- Git (with submodule support)

### Local Development

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>

# Serve with live reload
hugo server

# Build for production
hugo --gc --minify
```

The `--gc` flag cleans unused cache files; `--minify` minifies HTML/CSS/JS output.

### Hugo Module Note

`go.mod` declares module `github.com/prxshetty/hugo-prxshetty` and lists `hugo-blog-awesome` as an indirect dependency. This appears to be a leftover from a scaffolding template — the active themes are the local `minimalistic` theme and the `hugo-bearblog` git submodule, neither of which is a Hugo module.

---

## CI/CD — GitHub Actions

Workflow: `.github/workflows/hugo.yaml`

- **Trigger:** Push to `hugo-site` branch (plus manual `workflow_dispatch`)
- **Hugo version:** `0.145.0` (extended, downloaded as `.deb`)
- **Dart Sass:** installed via `snap`
- **Submodules:** fetched recursively (`actions/checkout@v4` with `submodules: recursive`)
- **Build:** `hugo --gc --minify --baseURL <pages-url>`
- **Cache:** Hugo build cache stored in `$RUNNER_TEMP/hugo_cache`, keyed per run with fallback to `hugo-` prefix
- **Deploy:** `public/` uploaded via `actions/upload-pages-artifact@v3` → `actions/deploy-pages@v4` to GitHub Pages

The `public/` directory is also committed directly to the repo (pre-built output), so the site can be served from the committed files without running Hugo.

---

## Hosting

The site is self-hosted on a **Raspberry Pi** and made publicly accessible via a **Cloudflare Tunnel** (reverse proxy), eliminating the need to expose a port directly on the home network or configure port forwarding.

### Architecture

```
Internet → Cloudflare Edge → Cloudflare Tunnel (cloudflared) → Raspberry Pi → Static file server
```

Cloudflare handles TLS termination, DDoS protection, and caching at the edge. The `cloudflared` daemon on the Pi maintains an outbound tunnel to Cloudflare's network, so no inbound firewall rules are needed.

### Static File Server

The pre-built `public/` directory is served by **Caddy** running on the Raspberry Pi. Caddy is configured to serve the static files from the `public/` directory on a local port, and the Cloudflare Tunnel proxies requests to that address.

Caddy is configured at `/etc/caddy/Caddyfile`, serving files from `/var/www/hugo` on port 80:

```
:80 {
    root * /var/www/hugo
    file_server
}
```

The site's built output (`public/`) should be synced or copied to `/var/www/hugo` on the Pi when deploying updates.

### systemd Service Management

The Caddy server and the `cloudflared` tunnel daemon are both managed as **systemd services** so they start automatically on boot and restart on failure.

**Caddy service** (`/etc/systemd/system/caddy.service`):

```ini
[Unit]
Description=Caddy static site server
After=network.target

[Service]
Type=notify
User=caddy
ExecStart=/usr/bin/caddy run --config /etc/caddy/Caddyfile
ExecReload=/usr/bin/caddy reload --config /etc/caddy/Caddyfile
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Example cloudflared tunnel service** (`/etc/systemd/system/cloudflared.service`):

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/cloudflared tunnel run
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Common systemd Commands

```bash
# Enable services to start on boot
sudo systemctl enable portfolio cloudflared

# Start / stop / restart
sudo systemctl start portfolio
sudo systemctl restart cloudflared

# Check status and recent logs
sudo systemctl status portfolio
journalctl -u cloudflared -f

# Reload systemd after editing unit files
sudo systemctl daemon-reload
```

- DNS for the domain is managed through Cloudflare; the tunnel creates a `CNAME` record pointing to `<tunnel-id>.cfargotunnel.com`.
- Because `relativeURLs = true` and `canonifyURLs = true` are set in `hugo.toml`, the pre-built `public/` output works correctly regardless of the domain it is served from.

### Updating the Site

To deploy new content to the Pi:

```bash
# On the Pi: pull latest public/ output and restart nothing (static files are served directly)
cd /home/pi/abhinand20.github.io
git pull origin hugo-site
# No restart needed — the server reads files from disk on each request
```

---

## Key Design Decisions

- **Pre-built `public/` committed to repo:** Allows the Pi to serve the site simply by pulling the repo — no Hugo install required on the server.
- **Tailwind via CDN:** Avoids a Node.js build step on the Pi; trades a small runtime load for build simplicity.
- **All structured content in `hugo.toml`:** Keeps the content model flat and easy to update without touching template files.
- **`relativeURLs = true`:** Ensures the site works correctly when served from any domain or subdirectory, which is important for the self-hosted setup.

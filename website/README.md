# Website

This website is built using [Docusaurus 3](https://docusaurus.io/), a modern static website generator.

## Requirements

Node.js **20 or 22**. A `.nvmrc` is provided, so `nvm use` picks the right one.

> **Node 24 is not supported yet.** Docusaurus 3.10 segfaults during `build` on Node 24
> (reproducible with a stock `create-docusaurus` site, so it is an upstream issue rather
> than anything specific to this site). Use Node 22 LTS until that is fixed upstream.

## Installation

```bash
npm ci
```

## Local Development

```bash
npm start
```

This command starts a local development server and opens up a browser window. Most changes are
reflected live without having to restart the server.

## Build

```bash
npm run build
npm run serve   # preview the production build locally
```

This command generates static content into the `build` directory and can be served using any
static content hosting service.

The build treats broken links and broken anchors as errors, so a bad cross-reference fails CI
rather than shipping a dead link.

## Deployment

Deployment is automated: pushes to `main` that touch `website/**` are built and published to
GitHub Pages by [`.github/workflows/website.yml`](../.github/workflows/website.yml). The same
workflow builds (without deploying) on pull requests.

This requires the repository's **Settings → Pages → Build and deployment → Source** to be set to
**GitHub Actions**. To deploy by hand instead, `npm run deploy` still pushes to the `gh-pages`
branch:

```bash
GIT_USER=<Your GitHub username> USE_SSH=1 npm run deploy
```

## Search

Search is provided by
[`@easyops-cn/docusaurus-search-local`](https://github.com/easyops-cn/docusaurus-search-local),
which builds an offline index at build time. It needs no Algolia account or API key, but the
index only exists in production builds — search is unavailable under `npm start`.

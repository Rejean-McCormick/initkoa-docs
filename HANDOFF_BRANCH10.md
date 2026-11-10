# HANDOFF — Branch 10: initkoa-docs portal

**Role:** derived documentation view; C0 source remains canonical. **Status:** OFFLINE_MIRROR_TESTED, not deployed.

## Input and output

- **Source:** `kOA-Digital-Ecosystem/docs/target/` at a reviewer-approved exact ref.
- **Generator:** `scripts/sync_koa_target.py` → `docs/final-system/` (Markdown, source SHA per page, `_MANIFEST.json`); rewrites internal relative target-doc links.
- **Site navigation:** first section in `mkdocs.yml` and generated wiki nav section from `scripts/sync_wikis.py`.

## Validation

`python scripts/sync_koa_target.py --verify-bundle`; `python scripts/sync_koa_target.py --source-dir <C0/docs/target> --check`; and `python -m unittest discover -s tests -q` (3 tests) pass. Complete MkDocs strict build **not run** (dependencies missing). The source archive lacked `assets/images/LogoK.svg`; its dead theme-logo reference has been removed pending owner branding.

## Next owner decisions

Confirm C0 source ref, public disclosure policy, offline mirror refresh policy, MkDocs strict build in CI, and authority to deploy to GitHub Pages. Existing wiki aggregation remains independent; no extra project sources are treated as normative via this mirror.

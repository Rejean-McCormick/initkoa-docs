# Final-system documentation mirror

The directory [`final-system/`](final-system/index.md) is a **derived, source-attributed copy** of the C0 `docs/target/` target design. It contains 24 functional chains, 53 owner roles and 26 proposed target boundaries. It is not a production status dashboard.

**Offline refresh from an exact local C0 tree:**

```bash
python scripts/sync_koa_target.py --source-dir ../kOA_Digital_Ecosystem/docs/target --source-ref <verified-git-ref> --write
python scripts/sync_koa_target.py --source-dir ../kOA_Digital_Ecosystem/docs/target --source-ref <verified-git-ref> --check
python scripts/sync_koa_target.py --verify-bundle
```

The MkDocs build uses the checked-in mirror and independently syncs older wiki sources. The site deployment is a separate GitHub Pages workflow; no tool here commits to C0 or deploys without its configured CI/action permissions. Generated pages should not be edited directly. Validate source version, consent, and disclosure before updating the public release.

**Theme asset note:** The supplied portal snapshot did not contain its configured `assets/images/LogoK.svg`; the missing logo setting was removed to avoid a broken theme resource. Restore owner-approved branding only after providing the actual asset.

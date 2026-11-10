> **Final-system design mirror** · Canonical source: [`docs/target/functional-chains/06-qualification-and-acceptance.md`](https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem/blob/main/docs/target/functional-chains/06-qualification-and-acceptance.md) · SHA-256 `a6433d84d401541e1bd891c33078bb51ffbd44bb87e3a39444a46d619b91cee0`. Design intent is not deployment proof.

# 06 — Qualification and acceptance

**Status:** `TARGET_DESIGN`.

Levels: `TARGET_DESIGN`, `SOURCE_OBSERVED`, `OWNER_TESTED`, `CROSS_OWNER_QUALIFIED`, `RELEASE_AUTHORIZED`, `DEPLOYED_OBSERVED`. Never promote a level merely because a code file or CI workflow is present.

Every boundary requires exact revision pins, positive/negative schema fixtures, authorization denial, source integrity checks, changed-intent replay rejection, pending-versus-terminal reconciliation, private/public classification, dependent-service failure and rollback.

A full composed chain is qualified only when all its required producer/consumer pairs pass together on the selected environment/profile. The 53 snapshot hashes only prove offline bytes were captured.

[Functional chain index](index.md) · [Repository coverage](05-repository-coverage.md) · [Acceptance](06-qualification-and-acceptance.md)

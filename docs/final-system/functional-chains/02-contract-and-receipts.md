> **Final-system design mirror** · Canonical source: [`docs/target/functional-chains/02-contract-and-receipts.md`](https://github.com/Rejean-McCormick/kOA-Digital-Ecosystem/blob/main/docs/target/functional-chains/02-contract-and-receipts.md) · SHA-256 `cf52c056fdf82477b84cf28c412b4b3d07ede5d591a95631e6a149f43df6f32f`. Design intent is not deployment proof.

# 02 — Contract and receipts

**Status:** `TARGET_DESIGN`.

A cross-owner interface must specify sender/recipient identities, principal and tenant, versioned schema, source digest, classification, data bounds, producer disclosure rule, receiver admission, idempotency key and replay window, terminal success/failure semantics and recovery.

**Receipt fields (conceptual):** boundary ID, producer revision, receiver revision, request hash, tenant, actor, admission outcome, terminal effect state, immutable output reference, verifier and observation time. An accepted message is never proof of a succeeded external effect. Same-intent replay must be idempotent; same key with altered intent is a conflict.

[Functional chain index](index.md) · [Repository coverage](05-repository-coverage.md) · [Acceptance](06-qualification-and-acceptance.md)

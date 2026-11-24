<!-- kOA Doc Server · Docs IA · lot 01 · source datée, non-certifiante -->
# Documentation IA — initkoa-docs (portail MkDocs)

**Périmètre :** Portail public de lecture et miroir attribué du final-system kOA et de wikis approuvés.

**Origine :** snapshot local documenté (20 novembre 2026, ou archive complémentaire). Les chemins et versions actifs sont à vérifier sur le poste avant toute modification.

**Autorité :** Les documents C0 et propriétaires sont les sources; ce dépôt est un miroir en lecture. La publication GitHub Pages reste une décision du propriétaire du portail.

## Ordre de lecture conseillé à un agent

1. [`docs/index.md`](../../docs/index.md) — Page d’entrée et limites.
2. [`mkdocs.yml`](../../mkdocs.yml) — Navigation et thème.
3. [`scripts/sync_koa_target.py`](../../scripts/sync_koa_target.py) — Miroir C0 local attribué.
4. [`scripts/sync_wikis.py`](../../scripts/sync_wikis.py) — Synchronisation des wikis.
5. [`docs/final-system/_MANIFEST.json`](../../docs/final-system/_MANIFEST.json) — Provenance des pages dérivées.
6. [`tests/test_final_system_sync.py`](../../tests/test_final_system_sync.py) — Tests du miroir.

## Documents produits par cet overlay

- [`AI_CONTEXT.md`](AI_CONTEXT.md) — limites, parcours et points de contrôle.
- `PROFIL_INGENIERIE.md` — produit **sur demande** à partir d'un scan RepoSurveyor du code local; ce fichier n'est pas fourni par le lot rédactionnel.
- `AGENTS.md` à la racine — consignes de dépôt existantes conservées ou nouvelles si elles n'existaient pas.

## Règles transversales

- Une capture documentaire n'établit ni conformité, ni maturité, ni disponibilité en production.
- Ne pas remplacer contrats, ADR, README ou preuves propriétaires par cette aide de navigation.
- Nouveau Framework v11 : lire le profil effectivement adopté; ne jamais imposer une migration par défaut.

## Procédure opérationnelle proposée (lot 04)

- [`OPERATIONS.md`](OPERATIONS.md) — parcours concret et points de contrôle à vérifier avant tout effet.

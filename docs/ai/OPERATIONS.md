<!-- kOA Doc Server · Docs IA · lot 04 · proposition non certifiante -->
# Procédure IA — initkoa-docs

**Objet :** Portail MkDocs : miroir public attribué.

**Source de rédaction :** `docs-initkoa-org_Code_snapshot.zip` (capture datée). Ce document ne déclare pas que les commandes ont été exécutées sur le poste local.

## Parcours recommandé

1. Ne jamais éditer un contrat propriétaire dans la copie du portail pour faire autorité.
2. Utiliser `scripts/sync_koa_target.py` pour dériver les pages C0 depuis une source locale identifiée; vérifier `_MANIFEST.json` et les empreintes.
3. Utiliser `scripts/sync_wikis.py` uniquement pour la synchronisation des wikis accessibles, sans confondre leurs droits et leurs contenus avec ceux des dépôts de code.
4. Avant publication, expurger les preuves privées et conserver la provenance source/révision.
5. L’application Doc Server lit et exporte; la publication du portail reste une décision propre à `initkoa-docs`.

## Documents propriétaires à consulter

`mkdocs.yml`, `scripts/sync_koa_target.py`, `scripts/sync_wikis.py`, `docs/final-system/_MANIFEST.json`.

## Vérifications avant effet

- Confirmer la racine, la révision et les versions du dépôt réellement installé.
- Ne pas substituer la présente fiche aux `AGENTS.md`, contrats, ADR et validations propriétaires.
- Ne pas copier de secrets, données privées, rapports de maturité ou sauvegardes dans un ZIP public.
- Exécuter tout diagnostic, synchronisation ou publication **seulement après décision explicite**; préserver les rapports existants.
- Le Framework v11 demeure **facultatif et non bloquant** pour Doc Server.

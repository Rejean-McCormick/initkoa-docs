<!-- kOA Doc Server · Docs IA · lot 01 · source datée, non-certifiante -->
# Documentation IA — initkoa-docs (portail MkDocs)

**Périmètre :** Portail public de lecture et miroir attribué du final-system kOA et de wikis approuvés.

**Origine :** snapshot local documenté (20 novembre 2026, ou archive complémentaire). Les chemins et versions actifs sont à vérifier sur le poste avant toute modification.

**Autorité :** Les documents C0 et propriétaires sont les sources; ce dépôt est un miroir en lecture. La publication GitHub Pages reste une décision du propriétaire du portail.

## Méthode de travail IA

1. Lire les sources propriétaires et le miroir exact avant de retoucher la navigation du portail.
2. Garder les liens, empreintes et commits de provenance lors de l’import C0.
3. N’intégrer des pages Wiki que si le propriétaire a autorisé cette publication.
4. Vérifier les tests et la construction locale avant toute publication publique.

## Entrées et validations attestées par les sources

- `python -m unittest discover -s tests -v`
- `python scripts/sync_koa_target.py --help`
- `python scripts/sync_wikis.py  # nécessite l’accès Git et les sources wiki; ne pas lancer sans autorisation`

*Avant exécution, vérifier les préconditions locales et les effets possibles de la commande. Les commandes sont des points d’entrée documentés, pas des validations effectuées par cet overlay.*

## Frontières à ne jamais franchir

- Ne pas confondre page publique et contrat normatif du propriétaire.
- Ne pas exposer de rapports privés kOADiag/GitHub Audit par publication du miroir.
- Le rôle public de `initkoa-docs` est conservé même si Doc Server le pilote.

## Incertitudes et limites explicites

- La navigation reçue contient des comptes historiques (53 rôles); ne pas la présenter comme le portefeuille C0 actuel de 55 sans source datée.

## Sources à relire

- [`docs/index.md`](../../docs/index.md) — Page d’entrée et limites.
- [`mkdocs.yml`](../../mkdocs.yml) — Navigation et thème.
- [`scripts/sync_koa_target.py`](../../scripts/sync_koa_target.py) — Miroir C0 local attribué.
- [`scripts/sync_wikis.py`](../../scripts/sync_wikis.py) — Synchronisation des wikis.
- [`docs/final-system/_MANIFEST.json`](../../docs/final-system/_MANIFEST.json) — Provenance des pages dérivées.
- [`tests/test_final_system_sync.py`](../../tests/test_final_system_sync.py) — Tests du miroir.

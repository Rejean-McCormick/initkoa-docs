# Agent navigation — initkoa-docs (portail MkDocs)

Ce fichier ajoute des consignes de navigation. Il ne remplace aucun contrat ni preuve propriétaire.

## Avant de modifier quoi que ce soit

1. Lire [`docs/ai/INDEX.md`](docs/ai/INDEX.md) et [`docs/ai/AI_CONTEXT.md`](docs/ai/AI_CONTEXT.md).
2. Identifier le fichier propriétaire de l’autorité, le profil adopté et le périmètre exact.
3. Ne jamais traiter une capture SmartDump comme un état de déploiement ou un commit vérifié.
4. Séparer observation, validation native, qualification indépendante, publication et activation.
5. Préserver sources, preuves, versions et sauvegardes; ne pas promouvoir les nouveaux résultats sans revue explicite.

**Périmètre spécifique :** Les documents C0 et propriétaires sont les sources; ce dépôt est un miroir en lecture. La publication GitHub Pages reste une décision du propriétaire du portail.

**Vérifications pertinentes :**
- `python -m unittest discover -s tests -v`
- `python scripts/sync_koa_target.py --help`
- `python scripts/sync_wikis.py  # nécessite l’accès Git et les sources wiki; ne pas lancer sans autorisation`

Les règles historiques et consignes de portée plus étroite du dépôt priment sur cet index généré.

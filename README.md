# SFS RP Stock Exchange

wip

### A implémenter

- Frais de transaction (pour éviter les pump&dump ils devront être plus forts que les variations aléatoires du marché sur quelques minutes)
- Variations aléatoires du marché toutes les minutes de .01%
- Chaque agence a son action, son ticker (tout est stocké dans une DB) et a chaque mission le cours varie
- Acheter/vendre des parts d'agence
- En tant que chef d'agence, pouvoir définir la part de l'agence qu'on souhaite mettre en bourse et définir le prix initial d'une action etc.
- Affichage de graphe en courbes pour le cours des actions, et en secteurs pour la représentation des différents actionnaires.

### Commandes a faire

- achat/vente de parts
- /solde: voir son portefeuille d'actions
- /topagences: top des agences les plus cotées
- /topargent: top des plus riches du serveur (économie)
- /bourse ~agence~ : affiche le cours d'une agence
- /boursetotal: affiche la moyenne de la bourse (savoir si l'économie se porte bien)
- Error Handling des fautes de frappe dans les tickers etc.
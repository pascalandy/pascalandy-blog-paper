---
author: Pascal Andy
date_created: 2014-01-01
title: "Le moon shot sur lequel les banques doivent mettre leur jetons."
draft: true
tags:
  - crypto
ogImage: ../../assets/images/og-legacy/2019/04/pascalandy-com_header_2017-04-10_14h46.jpg
description: 'Si je suis le PDG de la BanqueZYX demain matin, notre "moon shot" est de faire en sorte que l’identité des gens soit sur un DLT (decentralized ledger...'
---

Si je suis le PDG de la BanqueZYX demain matin, notre "moon shot" est de faire en sorte que l’identité des gens soit sur un DLT (decentralized ledger technology).

> Ce qui distingue notre banque des autres, c'est la qualité de nos contrats-autonomes, la fluidité de nos processus, et notre faculté à éliminer la friction avec son client.

Le but est de minimiser la friction entre l’usager et l’entreprise. Comment ? En standardisant de façon décentralisée l’identité des gens et des organisations. Selon moi, c’est le plus grand coup que la BanqueZYX puisse faire.

Cet article prend pour acquis que le lecteur maitrise ces concepts qui sont à la base du blockchain

- un wallet
- générer de clé publique et privée
- le hash (SHA-256)
- merkle tree (agrégation de hash)
- signature cryptographique

### L'usager aux commandes

La force de ce concept est que c’est l'usager qui est en contrôle de ses données. C'est lui qui décide ce qu’il veut partager aux entités qui le questionne. Que ce soit pour un prêt auto, l'assurances d'un maison, l'assurances vie, une côte de crédit ou la BanqueZYX, le processus est le même. C’est très coûteux de qualifier les gens selon leur passé et selon leurs comportements.

### Le concept

Prenons l'example d'un prêt auto. L'usager veut faire un prêt. À chaque fois qu'il veut créer un **contrat** (un prêt, un contrat d'assurances, un investissements, un contrat chez Hydro-Québec, télécom, etc) il génère une **nouvelle clé publique** qui est utilisé par l'institution à partir de son wallet. Par example l'adresse:

- `14pc4onAhzLL2WihY9otBtXoYCTo2qp3ZM` est pour le contrat du prêt auto.
- `1NY5AZGvH41Dv3BkEMVXpwnQy6aes1ASYb` est pour le contrat de l'assurance de l'auto.

Une requête pour faire la demande de la côte de crédit de l'utilisateur est lancée par la BanqueZYX.

L’usager reçoit une notification sur son wallet et donne le droit spontané de consommer certaines (nom, âge, adresse, tel, date de naissance) informations pour une période donnée (une fois unique, pour 30 jours, un an, etc.).

Ces informations ne sont jamais partagé en clair n'y individuellement. C'est l'empreinte digital de l'information, la hash, qui est partagé. Encore mieux, c'est l'agrégation des hash (l'arbre de Merkle) qui est partagé.

Durant la requête, le bureau des passeports du Canada peut **signer** le fait que cette personne possède une citoyenneté Canadienne. Encore une fois, le numéro d'assurance social n'a pas à être partager. C'est le hash du numéro d'assurance social qui est valider avec celui du l'utilisateur.

On valide aussi le hash des autres données tel que la date de naissance, le nom à la naissance, le sexe biologique. Puis on fait un arbre de Merkle pour comparer le hash final de la validation avec le bureau des passeports du Canada.

Ça concorde. Checkpoint du bureau des passeports du Canada. Done en 4 secondes.

Le GRC **signe** qu'aucun mandat d'arrestation et en cours pour cette personne. La SQ, le FBI, Interpol font la même chose. Checkpoint, done en 4 secondes.

Visa **signe** le niveau de risque d'emprunt de cette personne. Mastercard et les autres service de cartes de crédits font la même chose. heckpoint, done en 4 secondes.

Le bureau de la SAAQ **signe** que cette personne possède un dossier de conduite en bonne et due forme. Checkpoint, done en 4 secondes.

Je suppose dans mon example qu'il n'y a plus de Equifax & TransUnion qui sont des cancers sur lesquelles les banques dépendent actuellement. Les contrats autonome remplacent totalement ces entités dans mon exemple.

Au final, la BanqueZYX qui doit valider la côte de crédit d’un usager n’a pas à conserver les données personnelles de l'utilisateur pour faire cette requête. C'est la beauté de ce système. Ceci est facile à faire à partir du moment où l’usager peut partager activement ses données personnelle sous forme de hash (et de hash de hash (arbre de Merkle)).

C’est la **réponse** du risque (i.e. une note de 1 à 9), qui importe à la BanqueZYX. Toutes les autres de l'utilisateurs n'ont PAS à être sauvegardées par l'institution.

L’idée de profiter d'un lac de données (big data) de l’ensemble des utilisateurs fonctionne encore. Ces données sont liées à la clé publique (i.e. `14pc4onAhzLL2WihY9otBtXoYCTo2qp3ZM`) de l'utilisateur. Ceci a aussi l’avantage que les BD de l’entreprise sont semi-privées par défaut. Donc l'identité des clients est sécurisé part défaut. La BD ne possède qu'on hash pour identifié une personne.

Au final nous avons fait plusieurs checkpoint pour validé l'identité de l'utilisateur puis nous avons inférer son risque.

### C’est le résultat de l’enquête de crédit qui compte

La magie de ce que je raconte est qu’une formule pour évaluer le risque tel que PA = PD X PCD X ECD peut-être exécutée dans un smart contract (je préfère dire un contrat autonome).

Le résultat PA est partagé SUR DEMANDE de l’usager vers l’entité. L’entité n’a en fait besoin que de savoir si PA réponds aux critères d’acceptation (le prêt est accordé ou non).

Disons que le financement de l’auto est sur 36 mois, on pourra exécuter un second contrat autonome afin que la BanqueZYX puisse accéder à certaines informations de l’usager jusqu’à ce que le prêt soit payé en entier.

_Un contrat autonome c’est seulement des conditions exécutées par une application de façon décentralisée. C’est comme programmer les règles d’un jeu tel que le Tic-Tac-Toc. Il faut déterminer les règles du jeu, quelles sont les conditions pour débuter/terminer une partie et quoi faire une fois la partie terminée._

Revenons à notre exemple.

Le gros coup pour la BanqueZYX ici est que faire affaire avec la BanqueZYX devient sans friction pour l’usager. Du vrai libre-service sur tous les produits et services offerts par BanqueZYX.

Les produits offerts sont consommés par l’usager à travers un contrat autonome.

Les analystes d’affaires et les directeurs de produits peuvent ensuite mettre en place des contrats autonomes sur le marché très rapidement.

Tout d'un coup, ce qui distingue une banque d'une autre, c'est la qualité de ses contrats-autonomes, la fluidité de ses processus, et sa faculté à minimiser la friction avec son client.

Dès que BanqueZYX offre ceci, il y aura un mouvement marqué des parts de marché vers celle-ci. J’en suis certain.

### Les commodités

Avec les banques centrales qui injectent des milliards dès que l'économie va mal, on se rend compte que les institutions bancaires (et beaucoup d'autres corporations) sont des utilitaires.

Quand ça va bien, on garde les profits. Quand ça va mal, on demande à tous les citoyens de faire leur pars on donnant une partie de leur taxes afin que le système de bonus basé sur le prix de l'action continue de bien récompenser ses employés. Meilleur plan d'affaires ever.

### Phase #2

Le 2e niveau de cette idée et de faire en sorte de devenir LA plateforme sur laquelle d’autres entreprises peuvent interagir avec l’identité. Ainsi d’autres entreprises peuvent consommer l’identité de l’usager sur demande. C’est comme devenir le TCP-IP de l’identité.

### Phase #3

Le 3e niveau est que les utilisateurs sont dans Decentralized autonomous organization et des machines. À ce point, chaque machine à son propre compte/wallet chez Banques XYZ. Et cette machine à sa propre côte de crédit.

Maintenant toute la mécanique de ce que je viens de raconter peut sembler flou. Et pourtant je vois très bien comment nous pourrions y arriver. Ça te tente d'en parler? Vient à notre [prochain meetup](/tags/crypto-in-montreal/).

P.S. _On ne peut plus se fier sur Equifax et leur black box pour juger qui est un bon ou un mauvais citoyen. De plus, les gens d’Equifax nous ont montré qu’ils ne peuvent pas gérer nos données sans se faire solidement pirater à laisser traîner nos informations personnelles partout sur le web. Les systèmes centralisés sont voués à être piratés. Pour voir l’étendue des dégâts: [haveibeenpwned.com](https://haveibeenpwned.com/)_

---
title: "backlog"
tags:
  - dev-notes
date_created: 2026-01-14
author: Pascal Andy
description: "BACKLOG, todo"
---

# BACKLOG

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Liens: soulignement trop épais → amincir + utiliser couleur primaire

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Choisir mes 5 meilleurs posts, les relire, les mettre en avant
- http://localhost:4320/blog/lekt-le-lecteur/
- http://localhost:4320/blog/pourquoi-se-donner-la-peine-decrire/?
- http://localhost:4320/blog/pourquoi-jaime-vous-tutoyer/
- http://localhost:4320/blog/le-multitache-une-legende-urbaine-qui-a-trop-dure/
- http://localhost:4320/blog/comment-reprendre-le-dessus-quand-le-rythme-accelere/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

𝚊𝚐𝚎𝚗𝚝-𝚋𝚛𝚘𝚠𝚜𝚎𝚛 -𝚙 𝚒𝚘𝚜 𝚘𝚙𝚎𝚗

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Sitemap Astro + mini audit SEO
Tu as deux items "sitemap" + "SEO ?". C'est un levier net pour l'indexation. On peut:

Ajouter l'intégration sitemap Astro
Faire un mini‑audit (meta tags, canonical, og/twitter, robots, schema)

Supprimer "Share this post on"
Nettoyage simple et répétitif. Je peux identifier tous les posts concernés et retirer le bloc.

Nettoyage des assets non utilisés
Ça évite d'embarquer du poids mort. On peut lister les assets non référencés et exclure le pattern pascalandy-com_header*.

Header image par défaut
Changement plus "branding". Tu as un besoin clair: image seule, cohérente avec la marque. On peut définir une direction visuelle et produire/choisir l'image.

Mettre en avant 5 meilleurs posts
Impact éditorial fort mais demande ton choix. Je peux préparer une shortlist basée sur tags/engagement si tu veux.

Items à clarifier

"star ac est un projet" → c'est un contenu à écrire, une page à créer, ou un tag à structurer ?
"Graphite (git stacking)" → tu veux évaluer l'outil ou l'adopter dans le workflow ?
"Rester en contact par courriel" → tu veux un nouveau composant form + copy ?
Dis-moi quel lot tu veux attaquer en premier, et si tu veux que j'enchaîne directement avec une implémentation.

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Graphite (git stacking) — graphite.com
https://graphite.com

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Rester en contact 
par courriel : faire une nouvelle forme

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

star ac est un projet

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

mettre à jour l'image header par défault

En ce moment, ça ne fait pas de sens de la conserver puisque mon logo, c'est la chaise avec le mot Pascal Indi écrit. et ensuite de ça on a l'image d'une main en nature et ensuite j'ai un autre texte qui crée le blog de Pascal Indy, l'homme et les relations technologiques. donc je ne veux pas de texte là-dedans Je veux seulement une image qui... on produit une image de marque de mon blog. 

attention à : La génération pas de casque... celle née avant 1990

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Add MCP, maybe ? 
MCP Astro AI — docs.astro.build/en/guides/build-with-ai/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Some posts have a section at the end called : "Share this post on:"
So first identify this post and then delete this part. 

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

Double check if there are assets (src/assets) that exists that are not linked to any posts. 

example:
Would copy: dev_to_import/images_to_Import/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg
-> src/assets/images/og-legacy/2021/05/pascalandy-com_header_2020-07-16_10h11.jpg

so exclude the  
do not copy these pics with this pattern "pascalandy-com_header\*"

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

https://docs.astro.build/en/guides/integrations-guide/sitemap/

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=

SEO — 0o0o quoi exactement? audit? meta tags? schema?

Ajouter sitemap Astro

=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=—=


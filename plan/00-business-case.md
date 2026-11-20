# Blog pascalandy.com : ce qui est fermé et ce qui reste

Document source du plan, en lecture seule. Copié le 2026-11-19 de la carte de suivi privée de Pascal, après un bilan de réalité et une ronde de décisions avec lui. Le plan d'audit d'origine est l'issue #103 de ce dépôt. Les ancres `s1` à `s12` restent stables pour les lignes `Traces` du plan.

<a id="s1"></a>

## 1. Contexte

Un audit de `main` du 2026-11-12 a produit 11 PR, puis des ajouts (#104 à #125), tous fusionnés. Le 2026-11-19, Pascal a tranché les questions R1 à R20 et B10 à B43 du plan #103. La seule chose urgente, le déploiement, est faite. Ce qui reste vide le reste de l'audit. Pascal intervient à trois moments : les captures d'écran, les deux listes et le redéploiement.

<a id="s2"></a>

## 2. Fermé

**Avant le 2026-11-19** (12 au 18 novembre, tout est fusionné dans `main`)

- Les 11 PR de l'audit (#104 à #114) : métadonnées et dates en français, code mort retiré, 178 images orphelines supprimées, documentation remise à jour
- Le menu mobile, les correctifs de la revue et `just check` plus rapide (#115 à #117)
- Les libellés de l'interface en français, les tests du schéma et quelques outils (#118 à #122)
- La règle de fusion clarifiée et le jeton de déploiement pris dans la voûte (#123 à #125)

**Le 2026-11-19**

- Le site public sert `main` à `cb723c8`. Il était resté sur un build du 22 octobre. Vérifié par curl : Astro v7.4.8, `lang="fr-CA"`, « 13 août 2018 », RSS et sitemap en 200
- 20 branches mortes supprimées, après une sauvegarde `git bundle` sur om1. Il reste `main`, `evidence/103` et `evidence/103-phase3`

<a id="s3"></a>

## 3. Décisions tranchées le 2026-11-19, pas encore appliquées

- R20 : on garde l'orange, assombri en thème clair (option B, `primary` à 0,56)
- R3 : les 41 vieilles URL `cryptoinmontreal-NN` redirigent vers les pages `cim-NN`, avec des redirections Astro vérifiées par `just check`
- R13 : les posts en anglais reçoivent `lang: en`. Pascal confirme la liste
- R15 : les vieilles offres d'emploi reçoivent le tag `void`. Pascal confirme la liste
- B13 : 5 posts en vedette sur l'accueil
- Fermés : B15 (pas de formulaire d'abonnement), B17 (Graphite, on garde `gh stack`) et B10 (les guides de développement restent publics)
- R10 : une seule file de travail, les issues GitHub étiquetées selon `label-for-issues`. `backlog.md` ne garde que l'Inbox
- R9 : les 5 scripts Ghost sont archivés, pas supprimés. Pas d'export Ghost, donc les 28 dates incertaines (B37) restent telles quelles
- R5 : `just merge` réutilise un signoff déjà vert sur le même commit (#84)
- B38 : les 5 images orphelines de `public/og-legacy/` sont supprimées, et la vérification des images s'étend à `public/`
- R16 : le bouton « Modifier » hérité d'AstroPaper est retiré
- R7 : AGENTS.md nomme CodeRabbit à la place de Greptile
- R8 et R11 : on ferme les tickets AVIF (#89, #90) et les 5 post-mortems, et on supprime les étiquettes `autorelease`
- R17 : on ne fait rien pour les images en double

<a id="s4"></a>

## 4. Étape 1 : ranger

Rien ne change pour les lecteurs. Ça passe en premier pour que tout le reste parte d'une liste propre.

- Transformer le backlog en issues GitHub étiquetées, et créer les étiquettes canoniques manquantes
- Fermer ce qui est déjà réglé : le ticket Vite (#98), les tickets AVIF (#89, #90), les 5 post-mortems, B10, B15 et B17
- Mettre AGENTS.md et le journal des décisions à jour avec les décisions du 2026-11-19
- Consigner les réponses de Pascal dans un commentaire sur #103

<a id="s5"></a>

## 5. Étape 2 : ce que voient les lecteurs

- Le contraste en thème clair (R20)
- Les dernières chaînes anglaises : `All Right Reserved`, `Featured`, `Copy`, `404 Not Found`, etc. (B42)
- La parenthèse en trop dans la galerie (B39)
- Les redirections des 41 vieilles URL (R3)
- 👤 Pascal approuve les captures d'écran

<a id="s6"></a>

## 6. Étape 3 : le contenu

- Marquer les posts anglais (R13)
- Retirer les offres d'emploi de la liste du blog avec `void` (R15)
- Mettre les 5 posts en vedette (B13)
- 👤 Pascal confirme les deux listes, posts anglais et offres d'emploi

<a id="s7"></a>

## 7. Étape 4 : le nettoyage du code

Invisible pour les lecteurs.

- Retirer le bouton « Modifier » (R16)
- Archiver les scripts Ghost dans `scripts/archive/ghost-migration/` (R9)
- Supprimer les 5 images orphelines de `public/` et étendre la vérification à ce dossier (B38)
- Ajouter les largeurs 639 et 640 px à verify-blog, puis retirer les vieux plans de tests (R18)

<a id="s8"></a>

## 8. Étape 5 : l'outillage

- `just merge` ne relance plus la vérification inutilement (R5)
- Les URL de verify-blog finissent toutes par `/` (B41, y compris `tags.md` et `theme.md`)
- Une vérification automatique du site après chaque déploiement, qui compare aussi le commit déployé (B43)

<a id="s9"></a>

## 9. Étape 6 : les règles éditoriales

- Une page `editorial-rules.md` qui explique `void`, les brouillons, les dates futures, la mise en vedette, la langue et les redirections, avec la vérification de chaque règle

<a id="s10"></a>

## 10. Étape 7 : redéployer

- 👤 Pascal dit « déploie »

<a id="s11"></a>

## 11. Plus tard, chacune devient une issue sans échéance

- Installer le CLI Cloudflare officiel le plus récent, puis corriger la redirection `www` qui perd le chemin (R2)
- Redessiner le logo de la chaise œuf en SVG avec `currentColor`, puis le mettre dans l'en-tête (B14). Source actuelle : `logo-chaise-dark-long.png`, 600 × 135 px, pixelisé
- Enquêter sur l'agent qui tiendra les dépendances à jour : Renovate, Dependabot ou un autre, et comment il passe la barrière du `signoff` (R6)
- Ajouter le contenu de Star Academy (B16)
- Trouver comment faire le QA en format téléphone sur le Mac (B18)
- Faible priorité : les mises à jour de bibliothèques (B28 à B31) et le petit outillage (B24, B33, B36)

<a id="s12"></a>

## 12. Hors de ce dépôt

- La version de Node d'om1 se règle dans `dotfiles` (R4)

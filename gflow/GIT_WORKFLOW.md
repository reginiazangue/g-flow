# Workflow Git & Pipeline CI/CD — G-Flow

Ce document explique **comment le code circule**, de l'écriture d'une ligne sur la machine d'un développeur jusqu'à sa mise en ligne sur `gflow.kmstest.online`. Pour la présentation du projet (fonctionnalités, stack, installation), voir le [README.md](./README.md).

## 1. Vue d'ensemble du pipeline
Développeur (local)
│ git push
▼
GitHub (dépôt KMSEntreprises/Gestion-dechets)
│ déclenche automatiquement
▼
GitHub Actions (CI) ── flake8 → pytest → bandit
│ si tout est vert
▼
Merge dans main
│
▼
Serveur cPanel ── git pull (manuel) → Passenger recharge l'app
│
▼
https://gflow.kmstest.online (production)


Trois systèmes distincts travaillent ensemble : **Git** (historique du code), **GitHub Actions** (vérifications automatiques), et **cPanel/Passenger** (exécution réelle du site). Comprendre où s'arrête chacun évite les confusions les plus fréquentes.

## 2. Git : l'historique du code

Git ne fait qu'une chose : suivre l'évolution des fichiers dans le temps, sous forme de "commits" (des photos successives du projet).

### Branches utilisées

| Branche | Rôle |
|---|---|
| `main` | Toujours stable. C'est cette version qui doit pouvoir être déployée à tout moment. |
| `feature/nom-fonctionnalité` | Une branche isolée par tâche en cours, pour ne jamais toucher directement à `main`. |

### Pourquoi isoler le travail dans une branche ?

Si tu modifies directement `main` et que ton code contient un bug, la version "de référence" du projet est cassée pour tout le monde. En travaillant dans une branche séparée, `main` reste toujours fiable, et ton travail n'est fusionné qu'une fois vérifié.

### Cycle de contribution

```bash
# Toujours partir d'une base à jour
git checkout main
git pull origin main

# Créer une branche pour la tâche en cours
git checkout -b feature/ajout-messagerie

# Travailler, committer par petites étapes logiques
git add .
git commit -m "feat: ajoute le modèle Message et sa vue d'envoi"

# Envoyer la branche sur GitHub
git push origin feature/ajout-messagerie
```

Ensuite, ouvrir une **Pull Request** (PR) sur GitHub, de `feature/ajout-messagerie` vers `main`. C'est ce document qui déclenche la suite du pipeline.

### Convention de messages de commit

<type>: <description courte au présent>


| Type | Utilisation |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `docs` | Documentation uniquement |
| `refactor` | Réorganisation du code sans changement de comportement |
| `test` | Ajout/modification de tests |
| `chore` | Tâches techniques (dépendances, config) |

Un historique de commits clair permet de comprendre *pourquoi* un changement a été fait, des mois plus tard, sans avoir à relire tout le code.

## 3. GitHub Actions : la CI (Intégration Continue)

Dès qu'une Pull Request est ouverte (ou qu'un push a lieu), GitHub exécute automatiquement les scripts définis dans `.github/workflows/`, sur une machine temporaire fournie par GitHub — **pas** sur le serveur de production. C'est une vérification, pas un déploiement.

### Les 3 contrôles automatiques

**1. `flake8` — qualité du style de code**
Vérifie que le code Python respecte des conventions communes (indentation, longueur de ligne, imports inutilisés...). Un code inconsistant devient vite illisible en équipe ; flake8 impose une base commune sans débat humain à chaque relecture.

**2. `pytest` — les tests automatisés**
Exécute la suite de tests du projet (dossier `tests/`). Chaque test vérifie qu'une fonctionnalité précise se comporte comme attendu. Si un changement casse silencieusement une fonctionnalité existante, un test qui échoue l'annonce immédiatement — avant que ça n'atteigne la production.

**3. `bandit` — analyse de sécurité statique**
Scanne le code à la recherche de failles de sécurité connues (mots de passe en dur, usage dangereux de certaines fonctions, etc.), sans exécuter le code. C'est un filet de sécurité automatique, complémentaire à la relecture humaine.

### Pourquoi c'est important de ne pas ignorer un échec CI

Si l'un des trois contrôles échoue sur une Pull Request, ça signifie concrètement que la fusionner dans `main` risquerait de casser quelque chose en production. La règle : **on ne merge pas une PR dont la CI est rouge**, même si "ça a l'air de marcher en local".

## 4. La Pull Request : la revue humaine

La CI vérifie automatiquement ; la Pull Request permet en plus une **revue humaine** :

1. Un autre contributeur relit les changements
2. Il peut commenter, demander des ajustements
3. Une fois la CI verte et la relecture approuvée, la PR est fusionnée (*merge*) dans `main`

C'est le moment où le code passe du statut "en cours de développement" à "fait partie de la version officielle du projet".

## 5. De `main` à la production : le déploiement

C'est ici que ça diffère de beaucoup de tutoriels classiques : **il n'y a pas (encore) de déploiement automatique vers cPanel**. Le passage de `main` (sur GitHub) vers `gflow.kmstest.online` (le serveur réel) est une étape **manuelle**, volontairement séparée de la CI.

### Pourquoi le code est sur le serveur via Git, et pas juste "uploadé"

Plutôt que d'envoyer des fichiers un par un par FTP (source d'erreurs, pas de suivi des versions), le serveur cPanel possède sa propre copie du dépôt Git, connectée à GitHub. Ça permet de mettre à jour tout le projet en une seule commande, et de toujours savoir exactement quelle version est en ligne.

### Comment la connexion serveur ↔ GitHub a été établie

Le dépôt étant privé, GitHub doit vérifier que le serveur a le droit d'y accéder. Ça se fait via une **clé SSH de déploiement** :

1. Une paire de clés est générée directement sur le serveur cPanel (`SSH Access → Manage SSH Keys`) : une clé **privée** (reste sur le serveur, jamais partagée) et une clé **publique** (peut être partagée sans risque).
2. La clé publique est ajoutée dans GitHub, sur le dépôt (`Settings → Deploy keys`), en accès **lecture seule** — le serveur peut récupérer le code, mais ne peut pas le modifier.
3. Le clonage se fait avec une URL au format SSH :

git@github.com:KMSEntreprises/Gestion-dechets.git

   Quand cette URL est utilisée, Git présente automatiquement la clé privée du serveur ; GitHub la reconnaît grâce à la clé publique enregistrée, et autorise l'accès — sans mot de passe ni token à saisir.

### Mettre à jour la production après un merge

```bash
# Sur le serveur (terminal SSH, ou via l'outil Git Version Control de cPanel)
cd ~/gflow.kmstest.online
git pull origin main
```

Cette commande ne fait que **récupérer** les nouveaux fichiers. Il faut ensuite indiquer à Passenger de recharger l'application :

1. cPanel → **Application Manager**
2. Repérer l'application `gflow`
3. Cliquer sur **Restart** (ou re-déployer)

Sans cette dernière étape, le serveur continue de faire tourner l'ancienne version du code en mémoire, même si les fichiers ont été mis à jour sur le disque.

### Les variables d'environnement ne voyagent jamais avec le code

`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS` ne sont **jamais** stockées dans le dépôt Git (elles sont dans `.gitignore` via le fichier `.env`). Elles sont configurées séparément, à chaque environnement :

| Environnement | Où sont configurées les variables |
|---|---|
| Local (développement) | Fichier `.env`, basé sur `.env.example` |
| Production (cPanel) | `Application Manager → Environment Variables` |

**Conséquence pratique importante :** si le dépôt est un jour transféré, dupliqué, ou cloné vers un nouvel emplacement, ces variables ne suivent **pas automatiquement** — elles doivent être recréées manuellement à chaque nouvel endroit.

## 6. Historique : Render

Avant le passage à cPanel, `main` déclenchait un déploiement **automatique** vers Render : à chaque merge, une image Docker était reconstruite et redéployée sans action manuelle (CD complet). Cette configuration existe toujours dans les fichiers du projet (`Dockerfile`, `render.yaml`) mais n'est plus l'environnement actif.

La différence clé avec cPanel : sur Render, tout se passait automatiquement après le merge ; sur cPanel, le `git pull` + redémarrage Passenger doivent être déclenchés manuellement.

## 7. Bonnes pratiques à retenir

- Ne jamais committer `.env` avec de vraies valeurs — seul `.env.example` (avec des valeurs factices) est versionné.
- Ne jamais partager une clé privée SSH, un token GitHub, ou une valeur de `SECRET_KEY`, même temporairement.
- Toujours faire `git pull origin main` avant de créer une nouvelle branche, pour ne pas travailler sur une base obsolète.
- Vérifier `flake8` et `pytest` en local avant de pousser, pour éviter les allers-retours inutiles sur la CI.
- Après tout `git pull` sur le serveur, ne pas oublier l'étape **Restart** dans Application Manager — c'est l'étape la plus souvent oubliée.
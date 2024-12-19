# automate-cellulaire

V1 de la simulation de foule, sous forme d'automate cellulaire.

## Description

Ce projet simule le comportement d'une foule en utilisant un automate cellulaire. Chaque cellule représente une personne et les règles de transition définissent comment les personnes se déplacent et interagissent.
On peut, pour le moment ajouter 4 groupes de personnes distinctes chaque groupe attirés par un objectif différent. On peut également ajouter des obstacles, des portes et des producteurs de nouvelles cellules.

## Installation

1. Clonez le dépôt :

   git clone -url-du-repo-
2. créez un environnement virtuel :

   python3 -m venv env
3. Activez l'environnement virtuel :

    source env/bin/activate
4. Installez les dépendances :

    pip install -r requirements.txt
5. Lancez le programme :

    python3 game.py

## Utilisation

Au sein de la simulation, on trouvera un menu permettant de choisir les paramètres de la simulation.
Les modes de création de grille sont les suivants :

- Random: les automates et murs sont placées aléatoirement sur la grille. La probabilité d'apparition des automates et des murs est définie par l'utilisateur dans les paramètres.
- Custom: l'utilisateur peut placer les objets à la souris :
  - P : Place un automate
  - W : Place un mur
  - E : Supprime un objet
  - D : ajoute une porte
  - R : ajoute un producteur
  - 1 : Déplace l'objectif 1
  - 2 : Déplace l'objectif 2
  - 3 : Déplace l'objectif 3
  - 4 : Déplace l'objectif 4

- Durant la simulation, on peut utiliser les touches suivantes :
  - Echap : Quitter la simulation
  - P : Place un automate
  - W : Place un mur
  - E : Supprime un objet
  - D : ajoute une porte
  - R : ajoute un producteur
  - 1 : Déplace l'objectif 1
  - 2 : Déplace l'objectif 2
  - 3 : Déplace l'objectif 3
  - 4 : Déplace l'objectif 4
  - 9 : Change toutes les cellules du groupe 1 en un autre groupe
  - 8 : Change toutes les cellules du groupe 2 en un autre groupe
  - 7 : Change toutes les cellules du groupe 3 en un autre groupe
  - 6 : Change toutes les cellules du groupe 4 en un autre groupe
  - 9 + shift : Change des cellules des groupes 2, 3, 4 en groupe 1
  - 8 + shift : Change des cellules des groupes 1, 3, 4 en groupe 2
  - 7 + shift : Change des cellules des groupes 1, 2, 4 en groupe 3
  - 6 + shift : Change des cellules des groupes 1, 2, 3 en groupe 4

- Paramètres de la simulation :
  - colonnes : nombre de colonnes de la grille
  - lignes : nombre de lignes de la grille
  - eta : Coefficient dirigeant les automates vers leur objectif, plus eta est grand, plus les automates sont attirés par leur objectif
  - Parallel : 0 pour des déplacements cellule après cellule, 1 pour des déplacements en parallèle avec gestion du conflit
  - mu : Coefficient de friction (entre 0 et 1), plus mu est grand, plus la chance qu'un conflit entre 2 cellules (veulent accéder à la même case) soit résolu par une cellule qui va dans cette case, sinon, les 2 cellules ne bougent pas.
  - nu : Coefficient d'inerties, plus nu est grand, plus le fait de rester sur place est défavorisé.
  - grad_coeff : Coefficient de gradient des obstacles, plus grad_coeff est grand, plus les automates sont repoussés par les obstacles
  - proba_player : probabilité (entre 0 et 1) d'apparition d'un automate lors de la création de la grille
  - proba_wall : probabilité d'apparition (entre 0 et 1) d'un mur lors de la création de la grille
  - classes : nombre de groupes de personnes
  - Productor : 1 pour activer la production de nouvelles cellules, 0 sinon (cela enlèvera une classe de cellules pour la remplacer par un producteur)
  - coeff_prod : Coefficient de production de nouvelles cellules, plus coeff_prod est grand, plus de nouvelles cellules sont produites
  - exit : 1 pour activer la sortie, 0 sinon
  - change_place : Probabilité que 2 cellules voulant échanger de places le fassent

## Fonctionnement de l'automate cellulaire

### 1. Prise en compte des cellules accessibles

L'algorithme commence par identifier les cellules voisines valides. Les cellules prises en compte sont :

- Les **cellules vides**.
- Les **portes** (si présentes).
- Les **cellules occupées par d'autres joueurs** uniquement si une règle de changement de place est activée.
Les **murs** ou autres obstacles fixes ne sont jamais inclus.

L'objectif est de calculer pour chaque cellule une probabilité d'être choisie, comme expliqué ci-dessous.

### 2. Calcul des probabilités et choix via Softmax

Pour chaque cellule voisine valide, une probabilité de se déplacer vers celle-ci est calculée à l’aide de la formule **Softmax**. Cette probabilité est basée sur un score, qui peut dépendre de plusieurs facteurs :

- **Distance à un attracteur** : La cellule est plus probable (et donc son score plus élevé) si elle est plus proche de la destination cible.
- **Champ dynamique** (si activé) : Les cellules ayant un champ plus élevé sont priorisées (ex. : zones déjà fréquentées).
- **Effets d’inertie** : Une cellule est pénalisée si elle a été récemment visitée ou se situe sous le joueur actuel, pour éviter les allers-retours.

Le score est donc calculé comme suit : `score(cellule) = grad_coeff * grad(cellule) + eta * dist(cellule) + nu * iner(cellule)`, où `grad`, `dist` et `iner` sont les fonctions de gradient, de distance et d’inertie respectivement.

- **Formule Softmax** :
La probabilité d’aller dans une cellule est calculée comme suit :

```
P(cellule) = exp(score(cellule) / T) / Σ exp(score(cellule) / T)
```

Où :

- `P(cellule)` est la probabilité d’aller dans la cellule.
- `score(cellule)` est le score associé à la cellule.
- `T` est un paramètre de température qui contrôle la dispersion des probabilités. Plus `T` est grand, plus les probabilités son
- t uniformes.
  
T est calculé comme suit : (self.grille.nb_colonnes + self.grille.nb_lignes)**0.3
Cela permet premièrement de faire des grilles de n'importe quelle taille, car, lorsque la grille est trop grande, certaines cellules ont des probabilités qui ne sont pas calculées à cause de la limite de calcul de la fonction exponentielle. De plus, cela permet de ne pas avoir des probabilités trop faibles, car, si T est trop grand, les probabilités sont trop proches les unes des autres et le mouvement est stochastique.

La somme de toutes les probabilités est normalisée à 1, et la cellule est choisie de manière aléatoire en fonction de ces probabilités.

### 3. Gestion des conflits entre joueurs

Lorsque plusieurs joueurs souhaitent occuper la même cellule, deux approches sont possibles :

1. **Non parallèle** :
   - Les joueurs sont triés aléatoirement dans une liste (appelée liste de priorité).
   - Les déplacements sont résolus séquentiellement, en suivant l’ordre de cette liste.

2. **Parallèle** :
   - Une "matrice de conflit" est mise à jour pour suivre les déplacements souhaités.
   - Si plusieurs joueurs veulent une même cellule, un choix aléatoire est effectué pour décider lequel y va.
   - De même, selon le coefficient mu (probabilité que cet évènement arrive), il est possible que les joueurs ne bougent pas. Cela permet de simuler des comportements plus réalistes, où les gens se laissent passer ou se bloquent mutuellement dans une foule, ce qui est appelé "friction".

### 4. Gradation et obstacles

Une matrice de **gradation** est utilisée pour modéliser :

- La **distance à un attracteur** (par exemple, une porte). Les cellules proches de l’attracteur ont un score plus grand et auront plus de chance d'être selectionnées. On peut créer plusieurs classes de joueurs avec des objectifs différents. Cette distance est plus ou moins prise en compte en fonction du coefficient eta. (eta nul signifie que les automates ne sont pas attirés par leur objectif et ont donc un mouvement stochastique)
- Les **obstacles** (murs) qui augmentent le coût d’un déplacement dans leur direction.
Cette gradation oriente les joueurs vers des chemins optimaux tout en contournant les obstacles. Cette gradation est plus ou moins prise en compte en fonction du coefficient grad_coeff. (grad_coeff nul signifie que les automates ne sont pas repoussés par les obstacles)

Cela crée alors des "champs" d'attractivité ou de répulsion, qui influencent les choix des joueurs. On peut observer des phénomènes de "foule" ou de "flux" qui se forment naturellement.

### 5. Champs dynamiques et diffusion

Un **champ dynamique** est calculé pour chaque classe de joueur. Lorsqu’un joueur traverse une cellule, celle-ci voit son champ augmenter, ce qui influence les choix des autres joueurs dans la zone.

Une **diffusion** du champ est également appliquée pour simuler la propagation des influences (similaire à un champ de potentiel). La diffusion est atténuée par un phénomène de "décroissance" au fil du temps.

Cela permet de simuler des comportements réalistes, où les gens suivent des chemins déjà tracés par d’autres.

La formule de diffusion est la suivante : `champ(t+1) = champ(t) * (1 - Diffusion) + Diffusion * moyenne_voisins(champ(t))`, où `moyenne_voisins` est la moyenne des champs des voisins de la cellule.
Lorsqu'un joueur passe sur une cellule, le champ est augmenté de 1.

Peut être désactiver et plus ou moins amplifié en mettant le paramètre Diffusion à 0.

### 6. Gestion des blocages et changement de place

Pour éviter qu’un joueur reste bloqué :

- Une **pénalité est appliquée** sur la cellule située directement sous le joueur, l’encourageant à bouger. 
- Une **pénalité temporaire** est également attribuée aux cellules récemment visitées, pour éviter les allers-retours répétitifs, créant ainsi un comportement plus fluide et "humain".

Ces pénalités sont plus ou moins prises en compte en fonction du coefficient nu. (nu nul signifie que les automates ne sont pas pénalisés pour rester sur place).

Enfin, si la règle de changement de place est activée (paramètre change_place), les joueurs peuvent échanger leurs positions avec une probabilité donnée par le paramètre, ce qui permet à un joueur bloqué dans une foule de "remonter". Cela permet de simuler des comportements réalistes, où les gens se laissent passer dans une foule.

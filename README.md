# automate-cellulaire

V1 de la simulation de foule, sous forme d'automate cellulaire.

## Description

Ce projet simule le comportement d'une foule en utilisant un automate cellulaire. Chaque cellule représente une personne et les règles de transition définissent comment les personnes se déplacent et interagissent.
On peut, pour le moment ajouter 4 groupes de personnes distinctes chaque groupe attirés par un objectif différent

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

Durant la simulation, on peut utiliser les touches suivantes :
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

Paramètres de la simulation :
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



    


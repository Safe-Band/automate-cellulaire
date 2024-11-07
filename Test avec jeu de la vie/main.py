from CellularObjects import Cellule, Grille, AutomateCellulaire

def main():
    jeu = AutomateCellulaire(60, 30)
    jeu.jouer(100)

if __name__ == "__main__":
    main()
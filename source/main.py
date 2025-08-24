#!/usr/bin/env python3

# La ligne ci-dessus permet de lancer le script Python sur un système UNIX
# Ne pas oublier de changer les droits d'exécution du fichier par un chmod (ex: chmod 777)

# Projet main.py
# Fichier run.py
# Point d'entrée du projet

from mistralai import Mistral
import os
import curses

def display_menu(stdscr):
    
    curses.curs_set(0)
    curses.use_default_colors()

    # Liste des options du menu
    menu_items = ["Test d'un LLM local", "Lecture de fichiers", "---", "---", "---"]
    current_row = 0

    while True:
        stdscr.clear()
        # Afficher le menu
        stdscr.addstr(0, 2, "- OIA Menu principal")
        for idx, item in enumerate(menu_items):
            if idx == current_row:
                # Mettre en surbrillance l'élément sélectionné
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(idx + 1, 2, item)
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 1, 2, item)

        # Rafraîchir l'écran
        stdscr.refresh()

        # Attendre une entrée utilisateur
        key = stdscr.getch()

        # Gestion des touches fléchées
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(menu_items) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return current_row

    # Restaurer les paramètres du terminal
    stdscr.keypad(False)
    curses.curs_set(1)

if __name__ == '__main__':
    print(curses.wrapper(display_menu))
#!/usr/bin/env python3

# La ligne ci-dessus permet de lancer le script Python sur un système UNIX
# Ne pas oublier de changer les droits d'exécution du fichier par un chmod (ex: chmod 777)

# Projet main.py
# Fichier run.py
# Point d'entrée du projet

from mistralai import Mistral
import os

api_key = "eWvlh2Yoke60YJajF2iLGUXFoEjBnX9E"
model = "mistral-small-latest"

client = Mistral(api_key=api_key)

def start():
    lechat_response = client.chat.complete(
        model = model,
        messages = [{
            "role":"user",
            "content":"Calcule l'intégrale de 0 à 100 de la fonction x^2"
            }]
    )

    print(lechat_response.choices[0].message.content)


if __name__ == '__main__':
    start()
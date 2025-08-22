#!/bin/bash

# Réalise une installation propre des environnement Python

# Nom de l'environnement virtuel
VENV_NAME="pam-exp-penv"
PYTHON="python3"

sudo apt-get update
sudo apt-get install $PYTHON
sudo apt-get install -y python3.10-venv
sudo apt-get install pip

# Vérifier si l'environnement virtuel existe déjà
if [ -d "$VENV_NAME" ]; then
    echo "L'environnement virtuel '$VENV_NAME' existe déjà."
else
    echo "Création de l'environnement virtuel '$VENV_NAME'..."
    $PYTHON -m venv $VENV_NAME
    if [ $? -ne 0 ]; then
        echo "Erreur lors de la création de l'environnement virtuel."
        exit 1
    fi
    echo "Environnement virtuel '$VENV_NAME' créé avec succès."
fi

# Activer l'environnement virtuel
source $VENV_NAME/bin/activate

# Installer dans l'environnement virtuel les différents paquetages Pyhthon
pip install mistralai
pip install ollama
pip install pdf2image

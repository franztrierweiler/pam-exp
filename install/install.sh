#!/bin/bash

# Réalise une installation propre des environnement Python

# Nom de l'environnement virtuel
VENV_NAME="pam-exp-penv"
PYTHON="python3"

sudo apt-get update
sudo apt-get install $PYTHON
sudo apt-get install -y python3.10-venv

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

# Vérifier si pip est installé
if ! command -v pip &> /dev/null; then
    echo "pip n'est pas installé dans l'environnement virtuel. Installation en cours via apt-get..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3-pip
        if [ $? -ne 0 ]; then
            echo "Erreur : Impossible d'installer python3-pip via apt-get."
            exit 1
        fi
        # S'assurer que pip est disponible dans l'environnement virtuel
        $PYTHON -m ensurepip --upgrade
        $PYTHON -m pip install --upgrade pip
        echo "pip installé avec succès."
    else
        echo "Erreur : Gestionnaire de paquets 'apt-get' non trouvé. Veuillez installer pip manuellement."
        exit 1
    fi
else
    echo "pip est déjà installé."
fi

# Activer l'environnement virtuel
source $VENV_NAME/bin/activate

# Vérifier si mistralai est installé
if pip show mistralai &> /dev/null; then
    echo "La bibliothèque 'mistralai' est déjà installée."
else
    echo "Installation de la bibliothèque 'mistralai'..."
    pip install mistralai
    if [ $? -ne 0 ]; then
        echo "Erreur lors de l'installation de 'mistralai'."
        exit 1
    fi
    echo "Bibliothèque 'mistralai' installée avec succès."
fi

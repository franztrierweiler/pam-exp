import os
from pdf2image import convert_from_path
from tqdm import tqdm

# Définir les répertoires
INPUT_DIR = "input_pdf_files"
OUTPUT_DIR = "output_image"

def task_turn_pdf_into_pictures():

    # Créer le répertoire de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    # Lister tous les fichiers PDF dans le répertoire d'entrée
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.pdf')]
    pdf_files.sort()  # Trier pour un ordre prévisible

    # Nombre total de PDF à traiter
    total_pdfs = len(pdf_files)

    # Itérer sur les PDF avec une barre de progression
    for i, pdf_file in enumerate(tqdm(pdf_files, desc="Traitement des PDF", unit="fichier")):
        # Créer le sous-répertoire PDF1, PDF2, etc.
        sub_dir_name = f"PDF{i+1}"
        sub_dir_path = os.path.join(OUTPUT_DIR, sub_dir_name)
        os.makedirs(sub_dir_path, exist_ok=True)
        
        # Chemin complet du PDF
        pdf_path = os.path.join(input_dir, pdf_file)
        
        # Convertir le PDF en images (une par page)
        images = convert_from_path(pdf_path)
        
        # Sauvegarder chaque image dans le sous-répertoire
        for j, image in enumerate(images):
            image_path = os.path.join(sub_dir_path, f"page{j+1}.jpg")
            image.save(image_path, "JPEG")
        
        # Afficher le compteur (intégré dans tqdm, mais on peut ajouter un print si needed)
        # tqdm gère déjà la progression : "Traitement des PDF:  X/Y [temps écoulé]"

if __name__ == "__main__":
    # Example usage when running the script directly
    print("Ceci est un module, je ne peux pas être invoqué par le nom de mon fichier")
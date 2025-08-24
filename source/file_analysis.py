import ollama
import base64
from pathlib import Path
import json
import time
import logging
import concurrent.futures
import os

model_choisi = "mistral-small3.2"

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def reset_model() :
    print("Je vais rénitialiser le modèle")
    #os.system("ollama rm " + model_choisi)
    #os.system("ollama pull " + model_choisi)
    print("C'est fait !")

def is_non_null_json(json_data):
    """Check if a JSON has at least one non-null field."""
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        res = any(value != "null" for key, value in data.items())
        print(res)
        return res
    except json.JSONDecodeError:
        logging.error(f"Erreur de décodage JSON : {json_data}")
        return True

def get_nom_beneficiaire(json_data):
    """Extract the 'Nom du bénéficiaire' field from a JSON."""
    try:
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        return data.get("Nom du bénéficiaire")
    except json.JSONDecodeError:
        logging.error(f"Erreur de décodage JSON : {json_data}")
        return None

def reset_json_to_null():
    schema = {
            "type": "object",
            "properties": {
                "Nom du bénéficiaire": {"type": "string"},
                "Date de naissance": {"type": "string"},
                "Numéro de contrat" : {"type": "string"},
                "Numéro d'adhérent": {"type": "string"},
                "Numéro d'entrée": {"type": "string"},
                "Référence contrat" : {"type": "string"},
                "Date d'entrée": {"type": "string"},
                "Nom du centre hospitalier / clinique / GH / CH / Hôpital": {"type": "string"}
            },
            "required": [
                "Nom du bénéficiaire",
                "Date de naissance",
                "Numéro de contrat",
                "Numéro d'adhérent",
                "Numéro d'entrée",
                "Référence contrat",
                "Date d'entrée",
                "Nom du centre hospitalier / clinique / GH / CH / Hôpital"
            ],
            "additionalProperties": False
        }
    """Create a JSON with all fields set to null and return it as a formatted string."""
    null_json = {key: "null" for key in schema["properties"]}
    return null_json  # Return as dict to avoid re-serialization issues

def validate_json(result):
    """Validate JSON and return parsed data or null JSON on failure."""
    try:
        if isinstance(result, str):
            return json.loads(result)
        return result
    except json.JSONDecodeError as e:
        logging.error(f"JSON invalide détecté : {result}. Erreur : {e}")
        return reset_json_to_null()

def call_ollama_with_timeout(img_path, prompt, schema, timeout=120, prework = False):
    """Call ollama.chat with a timeout and return the result or trigger a second prompt."""
    def ollama_call():
        return ollama.chat(
            model=model_choisi,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_path]
                }
            ],
            format=schema if prework == False else "",
            stream=False
        )

    def second_prompt_call():
        logging.warning("Timeout détecté, lancement du second prompt.")
        return ollama.chat(
            model=model_choisi,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_path]
                }
            ],
            format=schema if prework == False else "",
            stream=False
        )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(ollama_call)
        try:
            result = future.result(timeout=timeout)
            return result["message"]["content"]
        except concurrent.futures.TimeoutError:
            logging.warning(f"Le premier appel API a dépassé {timeout} secondes pour l'image. J'enlève et remets llama3.2-vision")
            time.sleep(1)
            # Execute the second prompt
            try:
                reset_model()
                result = future.result(timeout=75)
                return result["message"]["content"]
            except concurrent.futures.TimeoutError:
                logging.warning(f"Le deuxième appel API a dépassé {timeout} secondes pour l'image.")
                # Execute the second prompt
                return ""
            return result["message"]["content"]

def analyse(j):
    print("\n\n\n\n")
    # Define paths
    input_dir = Path(f"./images_extraites/PDF{j}/")
    output_dir = Path("./output_json/")
    output_file = output_dir / f"text_analysis{j}.json"

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all JPEG images in the directory
    image_paths = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.jpeg"))

    # Analyze each image individually
    image_results = []
    # Define the JSON schema
    schema = {
        "type": "object",
        "properties": {
            "Prénom du bénéficiaire": {"type": "string"},
            "Nom du bénéficiaire": {"type": "string"},
            "Date de naissance": {"type": "string"},
            "Référence / Numéro d'adhérent": {"type": "string"},
            "Numéro d'entrée / Numéro de dossier": {"type": "string"},
            "Date d'entrée / Date de prise en charge": {"type": "string"},
            "Numéro de sécurité sociale": {"type": "string"},
            "Numéro Finess": {"type": "string"},
            "Nom du centre hospitalier / clinique / GH / CH / Hôpital": {"type": "string"}
        },
        "required": [
            "Prénom du bénéficiaire",
            "Nom du bénéficiaire",
            "Date de naissance",
            "Référence / Numéro d'adhérent",
            "Numéro d'entrée / Numéro de dossier",
            "Date d'entrée / Date de prise en charge",
            "Numéro de sécurité sociale",
            "Numéro Finess",
            "Nom du centre hospitalier / clinique / GH / CH / Hôpital"
        ],
        "additionalProperties": False
    }

    for img_path in image_paths:
        logging.info(f"Traitement de l'image : {img_path}")

        prompt = '''
            1. **Consigne** 
            Tu vas analyser une image fournie. Une seule image contient des informations pertinentes, tandis que les autres contiennent des informations inutiles liées à une mutuelle. Ta tâche est d'extraire avec une extrême précision et sans erreur les informations importantes présentes dans l'image pertinente, en suivant les instructions ci-dessous. Si l'image ne contient aucune des informations demandées, renvoie un JSON avec toutes les valeurs à "null".

            2. **Règles spécifiques** :
            - Si une donnée est absente ou non identifiable dans l'image, attribue-lui la valeur "null".
            - Les nombres peuvent inclure des points comme séparateurs (par exemple, 12.345.678).
            - Ignore les informations non pertinentes, comme celles liées à la mutuelle.
            - Surtout n'invente absolument aucune donnée, même celles que tu n'as pas trouvées dans l'image.
            - Si tu ne trouve pas le nom du bénéficiaire dans l'image, renvoie le json avec tous les champs à "null".
            - Ne confonds pas le nom du bénéficiaire avec le nom de la mutuelle.

            3. **Points d'attention**
            - Ne confonds surtout pas les 0 et les O, la seule différence est que les O sont légèrement plus large que les 0.
            - Ne confonds surtout pas les Z et les 2, la seule différence est que le haut du Z est plus droit que le haut du 2.
            - Ne confonds surtout pas les 5 et des S, la seule différence est que certains côtés du 5 sont plus droit que le S.
            - Le numéro de sécurité sociale du bénéficiaire peut aussi être appelé N°S.S, N.N.I. ou encore Numéro INSEE.
            - Ne confonds pas le prénom du bénéficiaire avec celui de l'assuré.

            4. **Format de la réponse** :
            - Renvoie un fichier JSON avec tous les champs dans l'ordre suivant :
                ```json
                {
                "Prénom du bénéficiaire": "valeur ou null",
                "Nom du bénéficiaire": "valeur ou null",
                "Date de naissance": "DD/MM/YYYY ou null",
                "Référence / Numéro d'adhérent": "valeur ou null, il peut y avoir des lettres",
                "Numéro d'entrée / Numéro de dossier": "valeur ou null",
                "Date d'entrée / Date de prise en charge": "DD/MM/YYYY ou null",
                "Numéro de sécurité sociale": "valeur ou null",
                "Numéro Finess": "valeur ou null",
                "Nom du centre hospitalier / Clinique / GH / CH / Hôpital": "valeur ou null"
                }
        '''

        # Call Ollama API with timeout
        result = call_ollama_with_timeout(img_path, prompt, schema)
        image_results.append(result)
        if result == "" :
            return
        print(result)

    # S'il n'y a qu'un seul PDF, on ne fait pas le regroupement
    if len(image_paths) == 1:
        logging.info(f"Résultat final : {result}")
        # Validate and save JSON
        result = validate_json(result)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json.loads(result) if isinstance(result, str) else result, f, ensure_ascii=False, indent=2)
        logging.info(f"Résultat sauvegardé dans {output_file}")
        return

    '''
    # S'il confondu le nom du bénéficiaire avec AXA ou qu'il n'a mis qu'un seul mot (inventé), je le corrige et je mets tout en null
    for i, result in enumerate(image_results):
        nom = get_nom_beneficiaire(validate_json(result))
        if nom == "axa":
            image_results[i] = ""
    '''


    # Si un seul des 3 json est non null, on le renvoi directement
    non_null_jsons = [validate_json(result) for result in image_results if (result != "" and is_non_null_json(validate_json(result)))]
    if len(non_null_jsons) == 1:
        logging.info(f"Un seul JSON non-null trouvé : {non_null_jsons[0]}")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json.loads(non_null_jsons[0]) if isinstance(non_null_jsons[0], str) else non_null_jsons[0], f, ensure_ascii=False, indent=2)
        logging.info(f"Résultat sauvegardé dans {output_file}")
        return



    # Final request to combine results
    combined_prompt = '''
        1. **Consigne**
        À partir de ces trois fichiers JSON ''' + '\n'.join(image_results) + ''' \n, chacun représentant les données extraites d'une image analysée. Une seule de ces images contient des informations pertinentes, tandis que les autres contiennent des informations inutiles (par exemple, des données sur une mutuelle) et auront probablement toutes leurs valeurs à `null`. Ta tâche est de regrouper les données pertinentes des trois JSON en un unique JSON structuré, en suivant les instructions ci-dessous.

        2. **Règles de regroupement** :
        - Examine les trois JSON et identifie celui qui contient des données non-`null` pour au moins un champ.
        - Si un champ est `null` dans tous les JSON, attribue-lui la valeur `null` dans le JSON final.

        3. **Format de la réponse** :
        - Retourne un unique fichier JSON structuré avec tous les champs dans l'ordre suivant :
            ```json
            {
            "Prénom du bénéficiaire": "valeur ou null",
            "Nom du bénéficiaire": "valeur ou null",
            "Date de naissance": "DD/MM/YYYY ou null",
            "Référence / Numéro d'adhérent": "valeur ou null, il peut y avoir des lettres",
            "Numéro d'entrée / Numéro de dossier": "valeur ou null",
            "Date d'entrée / Date de prise en charge": "DD/MM/YYYY ou null",
            "Numéro de sécurité sociale"valeur ou null",
            "Numéro Finess": "valeur ou null",
            "Nom du centre hospitalier / clinique / GH / CH / Hôpital": "valeur ou null"
            }
    '''

    # Call final combination with timeout
    # final_result = call_ollama_with_timeout(None, combined_prompt, timeout=30) if image_results else reset_json_to_null()
    
    final_response = ollama.chat(
        model=model_choisi,
        messages=[
            {
                "role": "user",
                "content": combined_prompt
            }
        ],
        format=schema,
        stream=False
    )
    final_result = final_response["message"]["content"]
    
    print("Résultat final \n" + final_result)
    # Validate and save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        final_result = validate_json(final_result)
        json.dump(json.loads(final_result) if isinstance(final_result, str) else final_result, f, ensure_ascii=False, indent=2)
    logging.info(f"Résultat sauvegardé dans {output_file}")
    return

reset_model()
start_time = time.perf_counter()
for j in range(1, 42):
    logging.info(f"Traitement du dossier PDF{j}")
    analyse(j)
end_time = time.perf_counter()

if __name__ == "__main__":
    # Example usage when running the script directly
    print("Ceci est un module, je ne peux pas être invoqué par le nom de mon fichier")
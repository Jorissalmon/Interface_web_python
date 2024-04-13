import logging
import os
import random
import re
import time
import spacy
import sys
import chromedriver_autoinstaller

import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
from openai import OpenAI
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Cela ne sert à rien dans le cas présent mais permet de lire ce qui est dans le fichier .env
#load_dotenv(dotenv_path=".env")

nlp = spacy.load("en_core_web_sm")  # Chargement du modèle spaCy pour le traitement du langage naturel

#Utile pour le dev, et voir d'où provienne les erreurs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
# Définir le port à écouter
port = 5000

#Ce qui va être lancé quand la page HTML est exécuté
@app.route('/', methods=['GET', 'POST'])
def home():
    # Définir les états de progression
    scraping_status = "En attente"

    if request.method == 'POST':#On va tester si c'est une requête POST, et dans ce cas on execute le programme de scraping
        scraping_status = "Récupération des données"
        product_url = request.form['product_url']
        OpenAI.api_key = request.form['api_key']

        scraping_status = "Récupération des avis Amazon"
        reviews_by_product = scrape_amazon_reviews(product_url)

        scraping_status = "Analyse des avis"
        data = convert_dataframe(reviews=reviews_by_product, product_url=product_url)
        data = get_sentiment_and_positivity(df=data)
        data = extract_entities(df=data)

        scraping_status = "Analyse des mots clés"
        reviews = data["body"].tolist()
        report = summarize_reviews(reviews)

        scraping_status = "Synthétisation"
        positifs, negatifs = generate_summary(report,api_key=OpenAI.api_key)
        print("Avis positifs :", positifs)
        print("Avis négatifs :", negatifs)
        return [positifs, negatifs]
    return render_template('index.html')



def wait_for_element(driver, selector, timeout=60):
    """
    Attend que l'élément spécifié soit présent dans la page.

    Args:
        driver: Instance du navigateur WebDriver.
        selector: Sélecteur CSS de l'élément à attendre.
        timeout: Temps maximum d'attente en secondes (par défaut 10).

    Returns:
        WebElement: L'élément trouvé.
    """
    return WebDriverWait(driver=driver, timeout=timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )

#Fonction qui va scraper tous les avis Amazon en fonction du produit en partant de la page produit initiale
def scrape_amazon_reviews(product_url):
    reviews_by_product = {}  # Dictionnaire pour stocker les avis par produit
    reviews = []  # Dictionnaire pour stocker les avis du produit
    options = Options()
    options.headless = True  # Pour exécuter Chrome en mode headless (sans interface graphique)

    chromedriver_autoinstaller.install()

    option.add_argument("--disable-gpu")
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-infobars")
    option.add_argument("--start-maximized")
    option.add_argument("--disable-notifications")
    option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)

    try:
        try:
            # Charger le cookie de session
            driver.get("https://www.amazon.com")
            wait_for_element(driver, 'div[id="gw-card-layout"]')
        except Exception as e:
            logger.error(f"Il y a eu une erreur lors de la résolution du Capchta: {e}")
            sys.exit()
        # On cache l'écran au user
        driver.set_window_position(3000, 0)  # Déplace la fenêtre hors de l'écran
        driver.set_window_size(400, 300)
        try:
            driver.get(product_url)
            html = driver.page_source
            tree = HTMLParser(html)
            bouton = driver.find_element("css selector", 'a[data-hook="see-all-reviews-link-foot"]')
            bouton.click()
        except Exception as e:
            logger.error(f"Couldn't fetch content from {product_url}: {e}")
            sys.exit()
        time.sleep(4)

        i = 0
        while True:  # Tant qu'il y a des pages suivantes d'avis, le script continue
            i += 1
            print("Page " + str(i))
            try:
                html = driver.page_source
                tree = HTMLParser(html)
            except Exception as e:
                logger.error(f"Il est impossible de charger le HTML de page {i}: {e}")

            try:
                # Viens chercher les avis sur la page Amazon
                review_wrappers = tree.css("div[data-hook='review']")
                for review_wrapper in review_wrappers:  # Pour chaque avis, on récupère une variable
                    review = {}
                    # review["title"] = review_wrapper.css_first("a[data-hook='review-title']").text(strip=True)
                    review["body"] = review_wrapper.css_first("span[data-hook='review-body']").text(strip=True)
                    # review["rating"] = float(review_wrapper.css_first("i[data-hook='review-star-rating']").text(strip=True).split(" ")[0])
                    # review["date"] = review_wrapper.css_first("span[data-hook='review-date']").text(strip=True)
                    reviews.append(review)
            except Exception as e:
                logger.error(f"Il y a une erreur lors de la récupération des éléments dans le HTML de {i}: {e}")
                pass
            try:
                # Vérifier si le bouton "Next" est présent
                next_button = driver.find_elements(By.CSS_SELECTOR, ".a-last a")
                if next_button:  # Si il y a une page suivante, le script continue
                    next_button[0].click()
                    random_delay = random.uniform(1, 5)
                    time.sleep(random_delay)
                else:  # sinon il s'arrête
                    logger.info("Tous les avis ont été scrappé !")
                    break  # Sortir de la boucle si le bouton "Next" n'est pas trouvé
            except Exception as e:
                logger.error(f"Il y a eu une erreur lors du changement de page à la page {i}: {e}")
                pass
        reviews_by_product[product_url] = reviews  # Ajouter les avis de ce produit au dictionnaire
        logger.info("Tous les avis ont été listé")
    except Exception as e:
        print(f"Erreur dans la récupération des reviews : {e}")
    return reviews

#Fonction qui converti les avis en Data-Frame pour leur traitement
def convert_dataframe(reviews, product_url):
    invalid_chars = ['/', '?', '*', '[', ']', ':', '.']

    df = pd.DataFrame(columns=["title", "body", "rating", "date"])

    # Vérifier si des avis sont présents
    if reviews:
        # Créer un DataFrame à partir des avis
        df = pd.DataFrame(reviews)
    return df

#Fonction qui extrait le nom du produit à partir de l'URL
def extract_product_name(url):
    # Exemple d'extraction basé sur l'URL donnée, cela peut nécessiter des ajustements
    match = re.search(r"/([a-zA-Z0-9-]+/product-reviews/)", url)
    if match:
        # Remplace les tirets par des espaces et prend les premiers mots pour simplifier
        return " ".join(match.group(1).replace("-", " ").replace("/product-reviews/", "").title().split(" ")[:5])
    return "Unknown Product"

#Fonction qui va récupérer les adj et va leur donner un score positif ou négatif
def get_sentiment_and_positivity(df: pd.DataFrame):
    model = SentimentIntensityAnalyzer()

    def get_sentiment(text):
        scores = model.polarity_scores(text)
        return scores["compound"]

    # Ajouter la colonne "sentiment" au DataFrame
    df["sentiment"] = df["body"].apply(get_sentiment)

    # Déterminer si le sentiment est positif ou non
    df['is_positive'] = df['sentiment'].apply(lambda x: x > 0)

    return df


def extract_entities(df: pd.DataFrame):
    # Boucle sur chaque texte dans la colonne "body" du DataFrame
    for index, row in df.iterrows():
        doc = nlp(row["body"])  # Traitement du texte avec spaCy
        entities = []

        # Boucle sur chaque entité nommée dans le texte
        for ent in doc.ents:
            # Vérification si l'entité est une entité nommée et n'est pas une entité temporelle ou monétaire
            if ent.label_ not in ["TIME", "MONEY", "DATE"]:
                # Nettoyage et formatage de l'entité
                cleaned_entity = re.sub('[^a-zA-Z0-9]', '_', ent.text.lower())
                formatted_entity = '__'.join([cleaned_entity, ent.label_.upper()])
                entities.append(formatted_entity)

        # Concaténation des entités trouvées pour ce texte
        if entities:
            df.at[index, "entities"] = ' '.join(entities)
        else:
            df.at[index, "entities"] = np.nan

    # Duplication des entités dans la colonne "X"
    df['X'] = df['entities']

    # Duplication de la colonne "is_positive" dans la colonne "Y"
    df['Y'] = df['is_positive']

    return df

#Extrait les adj
def extract_adjectives(text):
    """
    Cette fonction extrait les adjectifs d'un texte donné en utilisant spaCy.
    """
    adjectives = []
    doc = nlp(text)
    for token in doc:
        if token.pos_ == "ADJ":  # Vérifie si le token est un adjectif
            adjectives.append(token.lemma_.lower())  # Utilise la forme de base (lemme) de l'adjectif
    return adjectives

#Trie les adj en fonction de leur occurence
def summarize_reviews(reviews):
    """
    Cette fonction prend une liste d'avis et retourne un résumé basé sur les adjectifs les plus fréquents.
    """
    all_adjectives = []
    for review in reviews:
        all_adjectives.extend(extract_adjectives(review))

    # Compte la fréquence de chaque adjectif
    adjective_freq = Counter(all_adjectives)

    # Trie les adjectifs par leur fréquence en ordre décroissant
    most_common_adjectives = adjective_freq.most_common(30)  # Vous pouvez ajuster le nombre selon vos besoins

    # Crée un rapport basé sur les adjectifs les plus fréquents
    report = "Résumé des avis basé sur les adjectifs les plus fréquents:\n"
    for adj, freq in most_common_adjectives:
        report += f"{adj}: {freq} fois\n"

    return report

#Génère un résumé à partir des adj
def generate_summary(report,api_key):
    """
    Génère un résumé des avis en utilisant l'API OpenAI GPT-3.
    """
    client = OpenAI(api_key=api_key)

    # Consigne pour l'API OpenAI
    #prompt_consigne = "Résumez les points clés de ces avis clients en mettant d'un coté en avant les aspects positifs et d'un autre, les aspects négatifs en essayant d'être clair, précis et conçit: "
    prompt_consigne= """
 À partir d'une liste de mots clés d'avis de clients, résumez de manière concise les points positifs et négatifs.
 Rédigez d'une part les points positifs et d'autre part les points négatifs en restant très axé sur les mots clés fournis. 
 Utilisez des expressions telles que 'Principaux points positifs :' et 'Principaux points négatifs :' pour structurer votre analyse. 
 Mettez en évidence les aspects favorables et les critiques de manière précise et évitez d'inventer des éléments
    """
    # Joindre les avis en une seule chaîne de caractères, séparés par des espaces
    reviews_text = " ".join(report[:40])
    # Concaténation de la consigne avec les avis
    full_prompt = prompt_consigne + reviews_text

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': full_prompt}
        ],
        temperature=0
    )
    answer = response.choices[0].message.content.strip()

    # Diviser les aspects positifs et négatifs
    aspects_positifs = []
    aspects_negatifs = []
    in_positif = False
    in_negatif = False
    print(answer)
    # Parcourir chaque ligne du rapport
    for line in answer.split('\n'):
        if line.startswith('Principaux points positifs :'):
            in_positif = True
            in_negatif = False
        elif line.startswith('Principaux points négatifs :'):
            in_positif = False
            in_negatif = True
        elif line.strip() and (in_positif or in_negatif):
            if in_positif:
                aspects_positifs.append(line.strip())
            elif in_negatif:
                aspects_negatifs.append(line.strip())
    aspects_positifs = '<br>'.join(aspects_positifs)
    aspects_negatifs = '<br>'.join(aspects_negatifs)
    return aspects_positifs, aspects_negatifs


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

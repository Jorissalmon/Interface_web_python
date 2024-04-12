# Utiliser une image de base contenant Python 3.8
FROM python:3.8

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir \
Flask==3.0.3 \
numpy==1.26.4 \
openai==1.17.0 \
pandas==2.2.2 \
python-dotenv==1.0.1 \
selectolax==0.3.21 \
selenium==4.19.0 \
spacy==3.7.4 \
vaderSentiment==3.3.2


# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

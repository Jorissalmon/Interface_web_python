# Utiliser une image de base contenant Python 3.8
FROM python:3.9

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

COPY chromedriver.exe .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

EXPOSE 5000

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

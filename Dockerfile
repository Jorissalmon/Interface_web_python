# Utiliser une image de base contenant Python 3.8
FROM python:3.9

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

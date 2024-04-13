# Utiliser une image de base contenant Python 3.8
FROM python:3.10

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

COPY chromedriver.exe .

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

RUN apt-get update&& apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

# Définir le chemin d'accès au chromedriver.exe dans une variable d'environnement
ENV CHROMEDRIVER_PATH /app/chromedriver.exe

EXPOSE 5000

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

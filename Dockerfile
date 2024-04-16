# Utiliser une image de base contenant Python 3.8
FROM python:3.10

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

COPY chromedriver.exe .

# Rendre le chromedriver exécutable
RUN chmod +x chromedriver.exe

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

# Installer les dépendances nécessaires pour X
RUN apt-get update && apt-get install -y \
    xorg \
    xserver-xorg-core \
    xfonts-base \
    xauth \
    libxrender1 \
    libxcomposite1 \
    libasound2 \
    libdbus-glib-1-2 \
    libgtk2.0-0 \
    libgtk-3-0 \
    libx11-xcb-dev \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Installer Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb || apt-get install -f -y
RUN rm google-chrome-stable_current_amd64.deb

# Définir l'environnement d'affichage
ENV DISPLAY=:0

EXPOSE 5000

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

# Utiliser une image de base contenant Python 3.8
FROM python:3.8

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier le contenu du répertoire de votre projet dans le conteneur
COPY . .

# Installer les dépendances Python
RUN pip install --no-cache-dir \
    annotated-types==0.6.0 \
    anyio==4.3.0 \
    attrs==23.2.0 \
    blinker==1.7.0 \
    blis==0.7.11 \
    bzip2==1.0.8 \
    ca-certificates==2024.3.11 \
    catalogue==2.0.10 \
    certifi==2024.2.2 \
    cffi==1.16.0 \
    charset-normalizer==3.3.2 \
    click==8.1.7 \
    cloudpathlib==0.16.0 \
    colorama==0.4.6 \
    confection==0.1.4 \
    cymem==2.0.8 \
    distro==1.9.0 \
    en-core-web-sm==3.7.1 \
    et-xmlfile==1.1.0 \
    flask==3.0.3 \
    h11==0.14.0 \
    httpcore==1.0.5 \
    httpx==0.27.0 \
    idna==3.7 \
    itsdangerous==2.1.2 \
    jinja2==3.1.3 \
    langcodes==3.3.0 \
    libffi==3.4.4 \
    markupsafe==2.1.5 \
    murmurhash==1.0.10 \
    numpy==1.26.4 \
    openai==1.17.0 \
    openpyxl==3.1.2 \
    openssl==3.0.13 \
    outcome==1.3.0 \
    packaging==24.0 \
    pandas==2.2.2 \
    preshed==3.0.9 \
    pycparser==2.22 \
    pydantic==2.6.4 \
    pydantic-core==2.16.3 \
    pysocks==1.7.1 \
    python==3.11.8 \
    python-dateutil==2.9.0.post0 \
    python-dotenv==1.0.1 \
    pytz==2024.1 \
    requests==2.31.0 \
    selectolax==0.3.21 \
    selenium==4.19.0 \
    setuptools==69.2.0 \
    six==1.16.0 \
    smart-open==6.4.0 \
    sniffio==1.3.1 \
    sortedcontainers==2.4.0 \
    spacy==3.7.4 \
    spacy-legacy==3.0.12 \
    spacy-loggers==1.0.5 \
    sqlite==3.41.2 \
    srsly==2.4.8 \
    thinc==8.2.3 \
    tk==8.6.12 \
    tqdm==4.66.2 \
    trio==0.25.0 \
    trio-websocket==0.11.1 \
    typer==0.9.4 \
    typing-extensions==4.11.0 \
    tzdata==2024.1 \
    urllib3==2.2.1 \
    vadersentiment==3.3.2 \
    vc==14.2 \
    vs2015_runtime==14.27.29016 \
    wasabi==1.1.2 \
    weasel==0.3.4 \
    werkzeug==3.0.2 \
    wheel==0.41.2 \
    wsproto==1.2.0 \
    xz==5.4.6 \
    zlib==1.2.13

# Commande par défaut à exécuter lorsque le conteneur démarre
CMD ["python", "app.py"]

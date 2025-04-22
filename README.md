# Verden på norsk

This repo contains the webapp and database (DuckDB) for __Verden på norsk__.

Build with Docker:

```bash
docker build -t verden_pa_norsk .
```

Test run:

```bash
docker run -it --publish 8501:8501 verden_pa_norsk
```

Requires Python 3.12.
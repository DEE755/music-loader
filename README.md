# Music Sheets API
#General informations:
FastAPI service backed by MongoDB that scrapes music sheets as PDF or various formats and serves it via HTTP.
The API helps finding easily music sheets by title, musical genre, or composer.
IMPORTANT TO KNOW: The code is written in a scalable way to allow many new features.
For example as version 1.0 only PDF format from Mutopia Project can be scrapped and added to our database ~ 1700 pieces.
But further will bve implemented MIDI, XML Formats, etc for interactive content (play the piece interactively for learning etc.., allow modification, AI full song production from base sheets etc..)
Those feature will be implemented easily thanks to current architecture: 
SpecificFormatDAO->CorespondingRepository->CorespondingDbTable->GeneralDatabase

The corresponding repository and db table are created automatically when creating a new Format class, by just indicating type and table,
that way the implementation of compatibility to a new format is almost automated for already existing functions


Singleton Usage & FastApi namespace: Most of the object that doesnt need to be recreated when using for different purpose will be created and served via a container via manual Dependency Injection backed by the new lifespan function from FASTAPI providing a namespace with a determined lifespan, allowing full optimization of ressource creation.

1.The project can be build on docker with docker compose (including both mongodb & our app in one deployment)
2.Or can be run locally( need to run first mongodb- community on computer and provide the localhost in the .env environment file or provide an URL for mongodb atlas to connect to cloud version of mongodb)

3.As an alternative the project has been deployed on render and can be used already reaching the adress: https:// render..

IMPORTANT: Read below to know how to run from each source

FAST API Documents exist for all endpoints




## Prerequisites
- Python 3.11+
- Docker & docker-compose (for containerized runs) -> MACOS: "brew install docker-compose" sudo apt install docker-compose
- MongoDB 7+ (if running locally without Docker) -> MACOS: "brew install mongodb-community" in Terminal App // s

## Running with Docker Compose
```bash
docker compose up --build
```
This starts MongoDB and the app. API is at http://localhost:8000. MongoDB is at mongodb://localhost:27017.

## Running locally (app + Mongo in Docker)
1) Start MongoDB in Docker:
```bash
docker run -d --name mongo \
  -p 27017:27017 \
  mongo:7.0
```
2) Set env vars so the app talks to local Mongo:
```bash
export MONGO_URI="mongodb://localhost:27017"
export MONGO_CURRENT_DB="music_sheets_db"
```
3) Create venv and install deps:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
4) Run the API:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Running everything locally (Mongo installed on host)
1) Install MongoDB:
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```
2) Set env vars as above (`MONGO_URI`, `MONGO_CURRENT_DB`).
3) Create venv, install deps, run uvicorn as above.

## Triggering scraping
Call the scrape endpoint once Mongo is up:
```
GET http://localhost:8000/start-scrapping
```
This will fetch metadata and store it in MongoDB.

## Key Endpoints
- `GET /health` – app and DB status
- `GET /pieces/styles/{style}` – list pieces by style
- `GET /pieces/title/{title}` – list pieces matching title substring
- `GET /start-scrapping` – start scraping Mutopia metadata

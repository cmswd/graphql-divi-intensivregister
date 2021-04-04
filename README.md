# graphql-divi-intensivregister

Implementing a GraphQL API for the DIVI Intensivregister's data by using the Hasura GraphQL engine.

The data used come from DIVI-Intensivregister (https://www.intensivregister.de/).

## Installation

### Python requirements

```
virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

### Node.js requirements

```
npm install
```

### Hasura CLI

```
wget -O hasura https://github.com/hasura/graphql-engine/releases/download/v2.0.0-alpha.6/cli-hasura-darwin-amd64
chmod +x hasura
```

## Usage

```
docker-compose up -d
python3 import.py
```

The web interface can be reached under http://localhost:8080.

After the initial import run the following commands to apply the metadata. Also run to apply changes to the metadata.

```
./hasura metadata apply
```

After changes to the metadata via the console or API, they can be exported:

```
./hasura metadata export
```

## User interfaces

* Hasura console: http://localhost:8080
* React.js Application: http://localhost:3000

## Projects

* https://www.intensivregister.de/
* https://github.com/hasura/graphql-engine/

## Data sources

* https://www.divi.de/divi-intensivregister-tagesreport-archiv-csv/
  * Documentation: https://edoc.rki.de/bitstream/handle/176904/7989/Tagesdaten%20CSV%20Erklärung%20Stand%2029.3.pdf?sequence=1&isAllowed=y
* https://de.wikipedia.org/wiki/Liste_der_Landkreise_in_Deutschland
* https://de.wikipedia.org/wiki/Liste_der_kreisfreien_Städte_in_Deutschland
* https://de.wikipedia.org/wiki/Amtlicher_Gemeindeschlüssel

## References

* https://blog.zeit.de/fragen/2021/02/26/was-hinter-dem-corona-dashboard-auf-zeit-online-steckt/

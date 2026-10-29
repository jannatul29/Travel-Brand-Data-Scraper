# Travel Brand Data Scraper
Travel Brand Data Scraper is a Python-based data extraction project designed to collect, process, and organize travel-related data from various sources. It helps automate data collection workflows, reduce manual effort, and prepare structured datasets for downstream processing, analysis, and integration with travel data pipelines.

## Prerequisites

- Python3.12 or above
- PostgresSQL database
- GeoSpatial Libraries ```sudo apt-get install binutils libproj-dev gdal-bin```
- If using the Nginx proxy then set ```client_max_body_size       100m;```
- Amazon Linux ```sudo amazon-linux-extras install postgresql14```
- Docker

## Database setup in Docker

```shell
docker run -p 5432:5432 --name postgres -e POSTGRES_PASSWORD=postgres -d postgres:18
docker exec -it postgres bash
apt update
apt install postgis postgresql-18-postgis-3
su - postgres
```

OR use docker-compose from db/docker-compose.yml.sample

```commandline
docker-compose up -d
```

Create db user and password

```shell
psql
create database travel_brand_db;
create user travel_brand with encrypted password 'postgres';
grant all privileges on database travel_brand_db to travel_brand;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO travel_brand;
exit
psql -d travel_brand_db
CREATE EXTENSION postgis;
GRANT SELECT ON ALL TABLES IN SCHEMA "public" TO travel_brand;
```

## Project Setup

```shell
git clone https://github.com/jannatul29/Travel-Brand-Data-Scraper.git
git checkout development
Copy `app.conf.sample` file from `core/config` directory and create `app.conf` in the same directory
Open file `core/config/app.conf` and put appropriates credentials
make virtualenv
source env/bin/activate
pip3 install uv
uv pip install -r requirements.txt
```

## Migrations

Django can create migrations for you. Make changes to your models - for example, adding a field and/or removing a
model - run
`makemigrations`:

```shell
python manage.py makemigrations
```

Once you have your new migration files, you should apply them to your database to make sure they work as expected:

```shell
python manage.py migrate db --database="default"
```

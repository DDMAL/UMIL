# UMIL
The Universal Musical Instrument Lexicon (UMIL) is a crowd-sourcing website dedicated to collecting names and images of musical instruments from various historical periods and cultures. Inspired by projects like [MIMO (Musical Instruments Museum Online)](https://mimo-international.com/MIMO/accueil-ermes.aspx), UMIL aims to create a platform where users can contribute instrument names in their native languages while exploring a rich display of instrument pictures.

The ambitious initiative will greatly assist in mapping instrument names and facilitating cross-referencing of instruments across diverse sources. To achieve a multilingual search experience, UMIL employs a thesaurus-like concept, assigning each instrument a unique URI that links all its names together. Furthermore, this system ensures that search results are presented in the user's preferred language when utilizing SESEMMI (Search Engine System for Enhancing Music Metadata Interoperability).

![UMIL-1-1](https://github.com/DDMAL/VIM/assets/61984039/cf808948-11be-459b-9060-55220dbbade6)

## Table of Contents
- [Installation for Local Development](#installation-for-local-development)
  - [Debugging](#debugging)
  - [Additional Tools for Python Development](#additional-tools-for-python-development)
- [Installation for Deployment](#installation-for-deployment)
- [Managing Database Migrations](#managing-database-migrations)
- [Loading Data](#loading-data)

## Installation for Local Development

NOTE: These instructions are for local development only. Refer to the "Installation for Deployment" section for installation on a remote server.

### Requirements
- UMIL requires Docker Engine with Compose V2. Verify your version with `docker compose --version` and look for an output such as `Docker Compose version v2.19.1`. If you do not have the correct version, refer to the [Docker Compose Migration Documentation](https://docs.docker.com/compose/migrate/).

### Initial Set-up Instructions
After cloning this repository, you will need a local `.env` file at the root of the directory. Copy the contents or rename the `.env.sample` file to `.env` and update it to include uncommented environment variables for the database credentials `POSTGRES_USER` and `POSTGRES_PASSWORD`, as well as the `DJANGO_SECRET_KEY`. The database credentials can be set to anything while the `DJANGO_SECRET_KEY` will need to be obtained from one of the developers working on the UMIL project. Next you will need to verify the values of the `DEVELOPMENT`, `HOST_NAME`, and `PORT` variables. For local development ONLY, these should be set to "true", "localhost", and "8000" respectively. \
In one terminal run the following commands to build the docker images and run the specified services.
```sh
docker compose build
docker compose up
```
If you are not running docker containers in detatched mode (e.g `docker compose up -d`) open a second terminal and go into the running container shell. Run migrations commands to create/populate tables. The following commands should be executed to complete the aforementioned steps.
```sh
docker compose exec -it app bash
python manage.py makemigrations
python manage.py migrate
python manage.py import_languages
python manage.py import_instruments
```

The Django development server should now be available at `localhost:8000`. Ensure that the database schema is properly set up and the application can display data as expected by navigating to `localhost:8000/instruments/`.

NOTE: that it is recommended to bring the containers down with `docker compose down` after you are done developing, testing, and committing your changes. After executing the previous command, the application will no longer be available `localhost:8000`. To once again view the running application, run `docker compose up -d` and ensure all migrations  made by you or other developers are up-to-date with `docker compose exec -it app bash` and `python manage.py migrate`. For further clarifications on managing migrations refer to this [section](#managing-database-migrations).

### Debugging

When installed with `DEVELOPMENT=true` in the `.env` file, some additional modules are included in the application container that provide debugging tools: `django-extensions` and `django-debug-toolbar`. The debugging toolbar provided by `django-debug-toolbar` is shown when viewing the development server in the browser. The development installation runs the `runserver_plus` (provided by `django-extensions`) command automatically, which provides an in-browser debug console when errors are raised in the application. `django-extensions` also provides additional tools potentitally useful for development. Further information can be found at [module documentation](https://django-extensions.readthedocs.io/en/latest/command_extensions.html).

## Installation for Deployment

UMIL requires Docker Engine with Compose V2. Ensure that the remote server has these installed.

SSH into the server. After cloning the repository, set up a local `.env` file. Copy or rename the `.env.sample` file to `.env` and update it to include uncommented environment variables for database credentials `POSTGRES_USER` and `POSTGRES_PASSWORD`. Ensure that `POSTGRES_PASSWORD` is secure. Additionally, set `DJANGO_SECRET_KEY` with a secure secret key for Django.

Ensure that the `DEVELOPMENT` variable is set to "false", and that `HOST_NAME` is set to the host name where the UMIL instance will be served (for example, "vim.linkedmusic.ca" or "vim.staging.linkedmusic.ca"). Set the `PORT` variable to "80".
Run the following commands:

```bash
docker compose build
docker compose up -d
```

## Managing Database Migrations

Django automates changes to the database schema with migrations.

If your development changes any application models, be sure to make and commit migrations along with those changes. To create and apply migrations open a separate terminal and run the following commands:

```sh
docker compose exec -it app bash
python manage.py makemigrations
python manage.py migrate
```

Commit the resulting migrations files with the model changes.

If changes you make require migrations, or you merge migrations made by others into you development branch, you will need to apply those migrations to your local copy of the database:

```sh
docker compose exec -it app bash
python manage.py migrate
```

## Loading Data

At present, UMIL supports an initial list of 262 instruments curated from Wikidata, and their names in English and French. These instruments can be found in `web-app/django/startup_data/vim_instruments_with_images-15Sept.csv`.

Two django management commands are provided to load these initial instruments. These should be run from within the app Docker container by going into its shell.

```sh
docker compose exec -it app bash
python manage.py import_languages
python manage.py import_instruments
```

## Additional Tools for Python Development

UMIL uses `poetry` to manage python dependencies and a `poetry.lock` file to ensure reproducible builds in development and production. Dependencies can be found in the `pyproject.toml` file and are divided into three groups:

1. `main` - the core dependencies required by the application.
2. `debug` - dependencies that provide tools for debugging and are installed in the application Docker container only during local development.
3. `dev` - optional dependencies (eg. for code formatting, linting, type checking) that can be useful in the development environment, but are never used in the application container.

NOTE: it is not generally necessary to use `poetry` for development, except when adding additional dependencies.
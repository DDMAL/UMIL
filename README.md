# UMIL
The Universal Musical Instrument Lexicon (UMIL) is a crowd-sourcing website dedicated to collecting names and images of musical instruments from various historical periods and cultures. Inspired by projects like [MIMO (Musical Instruments Museum Online)](https://mimo-international.com/MIMO/accueil-ermes.aspx), UMIL aims to create a platform where users can contribute instrument names in their native languages while exploring a rich display of instrument pictures.

The ambitious initiative will greatly assist in mapping instrument names and facilitating cross-referencing of instruments across diverse sources. To achieve a multilingual search experience, UMIL employs a thesaurus-like concept, assigning each instrument a unique URI that links all its names together. Furthermore, this system ensures that search results are presented in the user's preferred language when utilizing SESEMMI (Search Engine System for Enhancing Music Metadata Interoperability).

![UMIL-1-1](https://github.com/DDMAL/VIM/assets/61984039/cf808948-11be-459b-9060-55220dbbade6)

## Installation for Local Development

NOTE: These instructions are for local development only. Refer to the "Installation for Deployment" section for installation on a remote server.

UMIL requires Docker Engine with Compose V2. UMIL's Docker Compose configuration is written according to the Compose Specification. 

After cloning this repository, set up a local `.env` file. Copy or rename the `.env.sample` file to `.env` and update it to include uncommented environment variables for database credentials `POSTGRES_USER` and `POSTGRES_PASSWORD` and the `DJANGO_SECRET_KEY`. Verify the values of the `DEVELOPMENT`, `HOST_NAME`, and `PORT` variables. For local development ONLY, these should be set to "true", "localhost", and "8000" respectively.

```console
> docker compose build
> docker compose up
```

The django development server should now be available at `localhost:8000`.

### Debugging

When installed with `DEVELOPMENT=true` in the `.env` file, some additional modules are included in the application container that provide debugging tools: `django-extensions` and `django-debug-toolbar`. The development installation runs the `runserver_plus` (provided by `django-extensions`) command automatically, which provides an in-browser debug console when errors are raised in the application. `django-extensions` also provides additional tools potentitally useful for development; see the [module documentation](https://django-extensions.readthedocs.io/en/latest/command_extensions.html) for more. The debugging toolbar provided by `django-debug-toolbar` is shown when viewing the development server in the browser.

### Tools for Python Development

UMIL uses `poetry` to manage python dependencies and a `poetry.lock` file to ensure reproducible builds in development and production. Dependencies can be found in the `pyproject.toml` file and are divided into three groups: 

1. `main` - the core dependencies required by the application
2. `debug` - dependencies that provide tools for debugging, and that are installed in the application Docker container only during local development
3. `dev` - optional dependencies (eg. for code formatting, linting, type checking) that can be useful in the development environment, but are never used in the application container

It is not generally necessary to use `poetry` for development, except when adding additional dependencies. 

## Installation for Deployment

UMIL requires Docker Engine with Compose V2. Ensure that the remote server has these installed. 

SSH into the server. After cloning the repository, set up a local `.env` file. Copy or rename the `.env.sample` file to `.env` and update it to include uncommented environment variables for database credentials `POSTGRES_USER` and `POSTGRES_PASSWORD`. Ensure that `POSTGRES_PASSWORD` is secure. Additionally, set `DJANGO_SECRET_KEY` with a secure secret key for Django. 

Ensure that the `DEVELOPMENT` variable is set to "false", and that `HOST_NAME` is set to the host name where the UMIL instance will be served (for example, "vim.linkedmusic.ca" or "vim.staging.linkedmusic.ca"). Set the `PORT` variable to "80".

Then, run

```bash
> docker compose build
> docker compose up -d
```

## Managing Database Migrations

Django automates changes to the database schema with migrations.

If your development changes any application models, be sure to make and commit migrations along with those changes. To create migrations, enter the application container and run the `makemigrations` command:

```console
> user@machine:~/dev-directory$ docker compose exec -it app bash
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py makemigrations
```

Commit the resulting migrations files with the model changes.

If changes you make require migrations, or you merge migrations made by others into you development branch, you will need to apply those migrations to your local copy of the database:

```console
> user@machine:~/dev-directory$ docker compose exec -it app bash
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py migrate
```

## Loading data

At present, UMIL supports an initial list of 262 instruments curated from Wikidata, and their names in English and French. These instruments can be found in `web-app/django/startup_data/vim_instruments_with_images-15Sept.csv`.

Two django management commands are provided to load these initial instruments. These should be run from within the app Docker container.

```bash
> user@machine:~/dev-directory$ docker compose exec -it app bash
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py import_languages
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py import_instruments
```
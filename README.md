# VIM
The Virtual Instrument Museum (VIM) is a crowd-sourcing website dedicated to collecting names and images of musical instruments from various historical periods and cultures. Inspired by projects like [MIMO (Musical Instruments Museum Online)](https://mimo-international.com/MIMO/accueil-ermes.aspx), VIM aims to create a platform where users can contribute instrument names in their native languages while exploring a rich display of instrument pictures.

The ambitious initiative will greatly assist in map
ping instrument names and facilitating cross-referencing of instruments across diverse sources. To achieve a multilingual search experience, VIM employs a thesaurus-like concept, assigning each instrument a unique URI that links all its names together. Furthermore, this system ensures that search results are presented in the user's preferred language when utilizing SESEMMI (Search Engine System for Enhancing Music Metadata Interoperability).

![VIM-1-1](https://github.com/DDMAL/VIM/assets/61984039/cf808948-11be-459b-9060-55220dbbade6)

## Installation for Local Development

NOTE: VIM is not yet ready for deployment to a remote server. Use these steps for local testing and development only.

VIM requires Docker Engine with Compose V2. VIM's Docker Compose configuration is written according to the Compose Specification. 

After cloning this repository, set up a local `.env` file. Copy or rename the `.env.sample` file to `.env` and update it to include uncommented environment variables for database credentials `POSTGRES_USER` and `POSTGRES_PASSWORD`. 

```console
> docker compose build
> docker compose up
```

The django development server should now be available at `localhost:8000`.

## Managing Database Migrations

Django automates changes to the database schema with migrations.

If your development changes any application models, be sure to make and commit migrations along with those changes. To create migrations, enter the application container and run the `makemigrations` command:

```console
> user@machine:~/dev-directory$ docker exec -it vim-app bash
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py makemigrations
```

Commit the resulting migrations files with the model changes.

If changes you make require migrations, or you merge migrations made by others into you development branch, you will need to apply those migrations to your local copy of the database:

```console
> user@machine:~/dev-directory$ docker exec -it vim-app bash
> root@container-id:/virtual-instrument-museum/vim-app$ python manage.py migrate
```
# VIM
The Virtual Instrument Museum (VIM) is a crowd-sourcing website dedicated to collecting names and images of musical instruments from various historical periods and cultures. Inspired by projects like [MIMO (Musical Instruments Museum Online)](https://mimo-international.com/MIMO/accueil-ermes.aspx), VIM aims to create a platform where users can contribute instrument names in their native languages while exploring a rich display of instrument pictures.

The ambitious initiative will greatly assist in map
ping instrument names and facilitating cross-referencing of instruments across diverse sources. To achieve a multilingual search experience, VIM employs a thesaurus-like concept, assigning each instrument a unique URI that links all its names together. Furthermore, this system ensures that search results are presented in the user's preferred language when utilizing SESEMMI (Search Engine System for Enhancing Music Metadata Interoperability).

![VIM-1-1](https://github.com/DDMAL/VIM/assets/61984039/cf808948-11be-459b-9060-55220dbbade6)

## Installation for Local Development

NOTE: VIM is not yet ready for deployment to a remote server. Use these steps for local testing and development only.

VIM requires Docker Engine with Compose V2. VIM's Docker Compose configuration is written according to the Compose Specification. 

To run VIM locally, clone this repository and then build and run the containers as in the following commands:

```bash
> docker compose build
> docker compose up
```

The django development server should now be available at `localhost:8000`.

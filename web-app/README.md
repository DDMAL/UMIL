# UMIL web application

## Dockerfile

- Image build order for `MODE=dev`: builder -> dev
- Image build order for `MODE=prod`: builder, prod-frontend -> prod

### Common base steps (`builder` stage image)

- Install `poetry` using `pip`
- Use `poetry` to insstall dependencies, without `dev` and `debug`
- Copy files web-app and frontend files to the container
- Set environment variable `PYTHONPATH` and `PATH`

### For development (`$MODE=dev`)

- Install `debug` dependencies that was missing from the builder stage
- Serve simultaneously the frontend (`vite dev` server, port 5173) and Django development server

### For production (`$MODE=prod`)

- Build frontend files with vite and sass
- Move the frontend build to Django assets
- Serve the app with Gunicorn

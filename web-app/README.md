# UMIL web application

## Dockerfile

```
builder
├── dev
└── prod-frontend-build
    └── prod
```

### Common base steps (`builder` stage image)

- Install `poetry` and Django dependencies
- Copy files
- Serve simultaneously the frontend (`vite dev` server, port 5173) and Django development server

### For development (`$MODE=dev`)

### For production (`$MODE=prod`)
- Build frontend files with vite and sass
- Move the frontend build to Django assets
- Serve the app with Gunicorn

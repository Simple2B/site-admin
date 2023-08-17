# Site Admin

1. Run

```bash
poetry install
```

2. Need to set up the [site](https://github.com/Simple2B/site) project (need to up db, and back to create migrations)
3. Run in the site project

```bash
docker compose up -d db back
docker compose exec back inv create-superuser
```

4. Start with F5

5. In main folder need install node_modules to work with tailwind, run

```bash
yarn install
```

# Simple Flask App

1. Run

```bash
poetry install
```

2. Need to set up [site](https://github.com/Simple2B/site) project
3. Need to up db, and back (create migrations)
4. Run in the site project

```bash
docker compose exec back inv create-superuser
```

5. Start with F5

6. In main folder need install node_modules to work with tailwind, run

```bash
yarn install
```

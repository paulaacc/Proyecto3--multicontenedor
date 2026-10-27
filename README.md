# Proyecto 03 - Aplicación multicontenedor con Docker Compose

Infraestructura y Seguridad Computacional - Universidad de Ibagué

App de votación "Docker Compose vs Kubernetes" con 6 contenedores:

| Servicio | Tecnología | Función | Puerto |
|---|---|---|---|
| vote | Python (Flask) | Web para votar | 5000 |
| result | Node.js (Express) | Visualiza resultados | 5001 |
| worker | Python | Procesa votos: Redis -> PostgreSQL + MongoDB | - |
| redis | Redis 7 | Cola de votos | interno |
| db | PostgreSQL 17 | Votos definitivos | interno |
| mongo | MongoDB 7 | Auditoría de eventos | interno |

- Volúmenes: redis-data, postgres-data, mongo-data
- Redes: frontend-net (usuarios) y backend-net (bases de datos)

## Ejecución
```
copy .env.example .env      # (editar DOCKERHUB_USER y POSTGRES_PASSWORD)
docker compose up -d --build
```
- Votar: http://localhost:5000
- Resultados: http://localhost:5001

## Publicar en Docker Hub
```
docker login
docker compose build
docker compose push
```
## Detener
```
docker compose down        # conserva los volúmenes
docker compose down -v     # borra también los datos
```
## Autores
Ana Sofia Vergara
Paula Daniela Cubillos
Sebastián González
Carlos Villanueva


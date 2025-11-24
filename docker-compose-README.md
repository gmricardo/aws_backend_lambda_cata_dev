Guía rápida: uso de `docker compose` para el backend

Este archivo explica qué hace el archivo `docker-compose.yml` en `backend/` y los comandos más útiles para trabajar localmente.

Resumen del `docker-compose.yml` del proyecto
- Servicios definidos:
  - `db`: contenedor PostgreSQL (imagen `postgres:13`). Se monta `backend/postgres/init.sql` en `/docker-entrypoint-initdb.d/` para inicializar la BD la primera vez.
  - `products`: microservicio Flask que expone `GET /products` (puerto contenedor 8001).
  - `auth`: microservicio Flask para registro/login (puerto contenedor 8002).
  - `orders`: microservicio Flask para crear y consultar órdenes (puerto contenedor 8003).
- Variables de entorno (cada servicio lee `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) para conectarse a la BD.

Notas sobre puertos y conflictos
- El contenedor de Postgres escucha en su puerto interno `5432`. En tu máquina host lo publicamos en `5433:5432` para evitar interferir con una instancia local de Postgres que ya usa `5432`.
- Servicios expuestos en host:
  - `http://localhost:8001` → products
  - `http://localhost:8002` → auth
  - `http://localhost:8003` → orders

Comandos comunes
- Levantar todos los servicios (build + run, modo foreground):
```bash
cd backend
docker compose up --build
```

- Levantar en background (detached):
```bash
cd backend
docker compose up --build -d
```

- Listar contenedores creados por el compose:
```bash
docker compose ps
```

- Ver logs de un servicio (ej. `auth`):
```bash
docker compose logs -f auth
```

- Reconstruir un servicio específico (ej. `products`) y reiniciarlo:
```bash
docker compose build products
docker compose up -d products
```

- Detener y eliminar recursos (contenedores, red, volúmenes declarados):
```bash
docker compose down --volumes
```

Acceder a la base de datos desde el host
- Con `psql` (instálalo si es necesario). Parámetros según `docker-compose.yml`:
  - host: `localhost`
  - puerto: `5433` (mapeado en host)
  - usuario: `ecom_user`
  - contraseña: `ecom_pass`
  - BD: `ecommerce`

Ejemplo:
```bash
psql -h localhost -p 5433 -U ecom_user -d ecommerce
```

Notas y buenas prácticas
- `version` en `docker-compose.yml` es obsoleto para el plugin moderno (`docker compose`); puedes eliminar la clave `version:` para evitar la advertencia.
- Si ya tienes Postgres corriendo en el host y prefieres usarlo, cambia el mapeo de puertos o ajusta las variables de entorno para que los contenedores apunten al host DB.
- Para pruebas rápidas con datos iniciales usamos `backend/postgres/init.sql`. Si necesitas controlar la evolución del esquema, considera usar migraciones (Alembic) en lugar de editar `init.sql` directamente.
- En producción (AWS Lambda + RDS): no uses contenedores así; empaqueta cada servicio como Lambda (o despliega en ECS/EKS) y usa RDS para la BD. `docker-compose` es sólo para desarrollo local.

Si quieres, puedo añadir scripts `Makefile` o `scripts/*.sh` para automatizar los comandos más comunes (arrancar, parar, logs). ¿Lo agrego? 

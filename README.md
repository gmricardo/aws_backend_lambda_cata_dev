Backend microservices (local + deploy notes)

This folder contains 3 example Python microservices (Flask) and a local `docker-compose.yml` to run them with a PostgreSQL database for development/testing.

Structure:
- `postgres/init.sql` - DB creation + tables + seed data
- `products/` - Products service (port 8001)
- `auth/` - Authentication service (port 8002)
- `orders/` - Orders service (port 8003)

Quick local run:

1. From the project root run:

```bash
cd backend
docker-compose up --build
```

2. Endpoints (local):
- Products: `GET http://localhost:8001/products`
- Auth: `POST http://localhost:8002/register` and `POST http://localhost:8002/login`
- Orders: `POST http://localhost:8003/orders`

Notes for AWS Lambda deployment:
- Each service can be adapted to run on AWS Lambda using an adapter (API Gateway + Lambda + a WSGI/ASGI adapter such as Mangum or awslambdaric). You will need to package dependencies and set environment variables for DB connectivity (or use RDS + IAM/auth patterns).

See individual service folders for more details.


# Como crear lambdas desde linea de comando:

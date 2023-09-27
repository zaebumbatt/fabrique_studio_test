# Mailing management service

Test task from a [Fabrique Studio](https://fabrique.studio/)

- [Swagger](http://localhost/docs/)
- [Prometheus](http://localhost:9090/) and [metrics](http://localhost/metrics)

## Run
To start a project: 
1. Add ```.env``` file to a root with these variables:
```
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=
PROBE_FBRQ_JWT_TOKEN=
```

2. Execute the following command:  
```
docker compose up -d --build
```  

3. Create superuser with the following command:
```
docker compose exec web python manage.py createsuperuser
 ```

4. Login to [admin panel](http://localhost/admin/).

## Run tests
```
docker compose run --rm web python manage.py test
```

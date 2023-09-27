# Mailing Management Service

Test task from [Fabrique Studio](https://fabrique.studio/)

- [Swagger](http://localhost/docs/)
- [Prometheus](http://localhost:9090/) and [Metrics](http://localhost/metrics)

## Run
To start the project:   
1. Add the ```.env``` file to the root directory with these variables:  
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

3. Create a superuser with the following command:
```
docker compose exec web python manage.py createsuperuser
 ```

4. Log in to the [admin panel](http://localhost/admin/).

## Run tests
```
docker compose run --rm web python manage.py test
```

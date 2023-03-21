# TripPlan - Backend API

## Install

### Pip/Python

1. Make sure Python 3.x is installed.
2. Create and activate virtual environment \
```
python3 -m venv .venv
source .venv/bin/activate
```
3. Install all dependencies
```
pip install -r requirements.txt
```
4. Run `makemigrations` and `migrate` \
```
python3 manage.py makemigrations places
python3 manage.py migrate
```
5. Create `superuser` by following the prompt
```
python3 manage.py createsuperuser
```
6. Run Django server and access it via `http://127.0.0.1:8000`
```
python3 manage.py runserver
```

### Docker

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and run it.
2. Build Docker container by using docker-compose
```
docker-compose up -d --build
```
3. Run `makemigrations` and `migrate` 
```
docker-compose exec web python manage.py makemigrations places
docker-compose exec web python manage.py migrate
```
4. Create `superuser` by following the prompt
```
docker-compose exec web python manage.py createsuperuser
```
5. Access Django API via `http://127.0.0.1:8000`
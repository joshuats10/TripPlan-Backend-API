# TripPlan - Backend API

Backend API for [TripPlan](https://github.com/joshuats10/TripPlan) mobile app with Django 4.x

## Install

### Environment File

Create `.env` file on the top directory with the following content
<pre><code>DEBUG=True
SECRET_KEY=<i>SECRET_KEY</i>
MAPS_API_KEY=<i>GOOGLE_MAPS_PLATFORM_API_KEY</i>
DATABASE_URL=<i>DATABASE_URL</i></code></pre>

Note: 
* `DATABASE_URL` is omitted if the API is installed locally and `SQLite3` is used. 
* If Docker is used, please use the following URL for the database 
```postgres://postgres@db/postgres```

### Pip/Python (Local)

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
4. Run `migrate` \
```
python3 manage.py migrate
```
5. Create `superuser` by following the prompt
```
python3 manage.py createsuperuser
```
6. Run Django server and access it via `http://127.0.0.1:8000/api/schema/redoc/`
```
python3 manage.py runserver
```

### Docker

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and run it.
2. Build Docker container by using docker-compose
```
docker-compose up -d --build
```
3. Run `migrate` 
```
docker-compose exec web python manage.py migrate
```
4. Create `superuser` by following the prompt
```
docker-compose exec web python manage.py createsuperuser
```
5. Access Django API via `http://127.0.0.1:8000/api/schema/redoc/`

## API

### Native Documentation / Schema

Can be accessed after running the API app through the following URL \
`http://127.0.0.1.8000/api/schema/redoc/` or `http://127.0.0.1.8000/api/schema/swagger-ui/`

### Optimize Trip Plan

* **Method** \
`POST`

* **URL** \
`http://127.0.0.1:8000/api/optimize_trip/`

* **Data Params** \
```json
{
    "date": "2023-04-01",
    "start_time": "12:15:22Z",
    "end_time": "14:15:22Z",
    "places": [{
        "place_name": "string",
        "place_id": "string",
        "photo_reference": "string"
    }]
}
```

* **Cookie**
<pre><code>device=<i>uuid</i></code></pre>

* **Success Response**
  - **Code**: 201
  - **Content**:
  ```json
  {
    "trip_id": "5fda87db-e6bf-4e34-b494-09479ec8c84a",
    "date": "2023-04-01",
    "start_time": "12:15:22Z",
    "end_time": "14:15:22Z",
    "user": 0
  }
  ```

* **Sample Call**
<pre><code>curl -i --cookie "device=ebfcc6ac-5c6c-4e34-9c2f-5067f130c4ee" -H 'Content-Type: application/json' -d <i>data params</i> http://127.0.0.1:8000/api/optimize_trip/
</code></pre>

### Get Destinations of an Optimized Trip Plan

* **Method** \
`GET`

* **URL** \
`http://127.0.0.1:8000/api/get_trip_destinations/`

* **URL Params** \
**Required** \
id=[uuid]

* **Success Response**
  - **Code**: 200
  - **Content**:
  ```json
  [
    {
    "destination_id": "f73cdd0c-5b5d-4102-9dde-c2ec04ceba9e",
    "name": "string",
    "google_place_id": "string",
    "photo_id": "string",
    "travel_order": 2147483647,
    "arrival_time": "2019-08-24T14:15:22Z",
    "departure_time": "2019-08-24T14:15:22Z",
    "stay_time": "string",
    "next_destination_mode": "string",
    "next_destination_travel_time": "string",
    "trip": "c0c45b0e-e022-45e9-af05-af7fc3a255a5"
    }
  ]
  ```

* **Error Response**
  - **Code**: 404 NOT FOUND
  - **Content**: `{ error : "Bad Request (Trip ID not found)" }`

* **Sample Call**
```
curl -i http://127.0.0.1:8000/api/get_trip_destinations/f6292fe4-5efc-4992-85f4-3329d0754f5b/
```
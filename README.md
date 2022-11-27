# Rates API
A REST API that calculates average prices between origin and destination for a given date range.


## Prerequisites
The `rates-api` and `db` services are containerized using `docker` and orchestrated using `docker-compose`. Please make sure you have the following tools available in your workstation:

1. `docker >= 19.03.13`
2. `docker-compose >=1.25.0`

## Setup Guidelines
1. Clone the `rates-api` repository from [here](https://github.com/saimoncse19/rates-api) and `cd` into it.
2. The development work is in the `dev` branch. Please checkout to it:
    ```shell
    git checkout dev
    ```
3. Create an env file in the root directory such as `.env.dev`:
    ```text=
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=01MyCatLovesYou
    POSTGRES_DB_NAME=postgres
    ```
4. Run the following command to start the services: (Supply `-d` flag to run in detached mode)
    ```shell
    docker-compose --env-file=./.env.dev up
    ```
5. If everything works as expected, you should be able to open `http://0.0.0.0:8000` which will greet you with the following:
    ![](https://i.imgur.com/ImLLQ3V.png)


> Note: If you get `Port already in use` error for postgres then please stop your local postgres with `sudo service postgresql stop`


## The Rates API endpoint
The Rates API endpoint at `/rates` accepts `GET` requests with four required query parameters: 
1. date_from: datetime
2. date_to: datetime
3. origin: string
4. destination: string

To view the Swagger docs, open `http://0.0.0.0:8000/docs`

FastAPI returns `HTTPException` with status code `422 Unprocessable Entity` for any missing or invalid parameters.

#### Request with missing parameters:

```shell
curl -X 'GET' 'http://0.0.0.0:8000/rates?date_from=2016-01-01&date_to=2016-01-10' -H 'accept: application/json'
```
##### Output
```shell
{"detail":[{"loc":["query","origin"],"msg":"field required","type":"value_error.missing"},{"loc":["query","destination"],"msg":"field required","type":"value_error.missing"}]}
```

#### Request with invalid parameters:
```shell
curl -X 'GET' 'http://0.0.0.0:8000/rates?date_from=2016-01-141&date_to=2016-01-10&origin=CNSGH&destination=GBFXT' -H 'accept: application/json'
```
##### Output
```shell
{"detail":[{"loc":["query","date_from"],"msg":"invalid date format","type":"value_error.date"}]}
```

Our API returns HTTPException with status code `400 Bad Request` for invalid date range.

#### Request with invalid date range:
```shell
curl -X 'GET' 'http://0.0.0.0:8000/rates?date_from=2016-01-11&date_to=2016-01-10&origin=CNSGH&destination=GBFXT' -H 'accept: application/json'
```
##### Output
```shell
{"detail":"Invalid date range, start date is greater than end date."}
```

#### Request with port code and region slug:
![](https://i.imgur.com/XnbDej4.png)

#### Request with only port codes:
![](https://i.imgur.com/p0jSZDl.png)

#### API returns `null` for average_prices
The API returns `null` for average_prices where the total number of price is less than 3 on a given day between two geographical regions.

![](https://i.imgur.com/PwHzshp.png)

#### Request with root regions:
![](https://i.imgur.com/5SM9mSn.png)

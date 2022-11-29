class TestHomeRoute:
    def test_home(self, mock_app):
        response = mock_app.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome! from Rates API."}


class TestRatesRoute:
    def test_with_missing_query_parameters(self, mock_app):
        response = mock_app.get("/rates?date_from=2021-01-01&date_to=2021-01-10&origin=china_main")
        assert response.status_code == 422
        assert response.json() == {"detail": [{"loc": ["query", "destination"], "msg": "field required",
                                               "type": "value_error.missing"}]}

    def test_with_invalid_query_parameters(self, mock_app):
        response = mock_app.get("/rates?date_from=2021-01-01&date_to=2021-011-10&origin=china_main&"
                                "destination=northern_europe")
        assert response.status_code == 422
        assert response.json() == {"detail": [{"loc": ["query", "date_to"], "msg": "invalid date format",
                                               "type": "value_error.date"}]}

    def test_with_invalid_date_range(self, mock_app):
        response = mock_app.get("/rates?date_from=2021-01-11&date_to=2021-01-10&origin=china_main&"
                                "destination=northern_europe")
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid date range, start date is greater than end date."}

    def test_with_valid_query_parameters_succeed(self, mock_app):
        response = mock_app.get("/rates?date_from=2021-01-01&date_to=2021-01-10&origin=china_main&"
                                "destination=northern_europe")
        assert response.status_code == 200
        # should return [] as testdb is empty
        assert response.json() == []


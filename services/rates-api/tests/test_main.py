class TestHome:
    def test_home(self, mock_app):
        response = mock_app.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome! from Rates API."}

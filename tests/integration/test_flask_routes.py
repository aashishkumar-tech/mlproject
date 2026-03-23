def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_predict_page_returns_200(client):
    response = client.get("/predictdata")
    assert response.status_code == 200


def test_predict_post_valid_data_returns_200(client):
    form_data = {
        "gender": "female",
        "ethnicity": "group B",
        "parental_level_of_education": "bachelor's degree",
        "lunch": "standard",
        "test_preparation_course": "none",
        "reading_score": "72",
        "writing_score": "74",
    }
    response = client.post("/predictdata", data=form_data)
    assert response.status_code == 200


def test_predict_post_invalid_data_does_not_crash(client):
    form_data = {
        "gender": "female",
        "ethnicity": "group B",
        "parental_level_of_education": "bachelor's degree",
        "lunch": "standard",
        "test_preparation_course": "none",
        "reading_score": "-5",
        "writing_score": "150",
    }
    response = client.post("/predictdata", data=form_data)
    assert response.status_code in [200, 400]

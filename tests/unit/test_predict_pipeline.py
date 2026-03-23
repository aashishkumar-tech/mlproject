import os
import pickle


def test_model_artifact_exists():
    assert os.path.exists("artifacts/model.pkl"), "model.pkl missing"


def test_preprocessor_artifact_exists():
    assert os.path.exists("artifacts/proprocessor.pkl"), "proprocessor.pkl missing"


def test_model_loads_successfully():
    with open("artifacts/model.pkl", "rb") as f:
        model = pickle.load(f)
    assert model is not None


def test_model_has_predict_method():
    with open("artifacts/model.pkl", "rb") as f:
        model = pickle.load(f)
    assert hasattr(model, "predict")


def test_prediction_score_in_valid_range():
    from src.pipeline.predict_pipeline import CustomData, PredictPipeline

    data = CustomData(
        gender="female",
        race_ethnicity="group B",
        parental_level_of_education="bachelor's degree",
        lunch="standard",
        test_preparation_course="none",
        reading_score=72,
        writing_score=74,
    )
    pipeline = PredictPipeline()
    result = pipeline.predict(data.get_data_as_data_frame())
    assert result is not None
    assert 0 <= float(result[0]) <= 100

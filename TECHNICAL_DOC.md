# Technical Documentation - Student Performance Prediction System

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Codebase Structure](#2-codebase-structure)
3. [Data Pipeline](#3-data-pipeline)
4. [Machine Learning Pipeline](#4-machine-learning-pipeline)
5. [Web Application](#5-web-application)
6. [Deployment Pipeline](#6-deployment-pipeline)
7. [Configuration](#7-configuration)
8. [Error Handling & Logging](#8-error-handling--logging)
9. [Performance Optimization](#9-performance-optimization)
10. [Testing Strategy](#10-testing-strategy)

---

## 1. System Architecture

### 1.1 Design Principles

The system follows these core principles:

- **Separation of Concerns**: Clear boundaries between data ingestion, transformation, training, and inference
- **Modularity**: Independent, reusable components
- **Pipeline Architecture**: Sequential processing stages
- **Exception Handling**: Custom exception framework for debugging
- **Logging**: Comprehensive logging at each stage
- **Serialization**: Pickle-based model persistence

### 1.2 Technology Stack

```python
# Core ML Libraries
scikit-learn==1.3.0      # ML algorithms, preprocessing
xgboost==1.7.6           # Gradient boosting
catboost==1.2            # Categorical boosting
pandas==2.0.3            # Data manipulation
numpy==1.24.3            # Numerical operations

# Web Framework
Flask==2.3.3             # Web server
gunicorn==21.2.0         # WSGI server

# Utilities
dill==0.3.7              # Enhanced pickling
python-dotenv==1.0.0     # Environment variables
```

---

## 2. Codebase Structure

### 2.1 Directory Layout

```text
src/
├── __init__.py                    # Package initialization
├── exception.py                   # Custom exception handling
├── logger.py                      # Logging configuration
├── utils.py                       # Common utilities
├── components/
│   ├── __init__.py
│   ├── data_ingestion.py         # Data loading & splitting
│   ├── data_transformation.py    # Feature engineering
│   └── model_trainer.py          # Model training & evaluation
└── pipeline/
    ├── __init__.py
    └── predict_pipeline.py       # Inference pipeline
```

### 2.2 Key Modules

#### 2.2.1 Exception Handler (`exception.py`)

```python
class CustomException(Exception):
    """
    Custom exception class for detailed error tracking
    
    Features:
    - Captures error message
    - Logs file name, line number, and function
    - Formats traceback for debugging
    """
    
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, 
            error_detail=error_detail
        )
    
    def __str__(self):
        return self.error_message
```

**Usage Pattern**:

```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    raise CustomException(e, sys)
```

#### 2.2.2 Logger Configuration (`logger.py`)

```python
"""
Logging Setup:
- Creates logs/ directory if not exists
- Generates timestamped log files (MM_DD_YYYY_HH_MM_SS.log)
- Format: [%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s
- Level: INFO
"""

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
logs_path = os.path.join(os.getcwd(), "logs", LOG_FILE)
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)
```

**Usage**:

```python
import logging
logging.info("Data ingestion started")
logging.error("Failed to load data")
```

#### 2.2.3 Utility Functions (`utils.py`)

```python
def save_object(file_path, obj):
    """
    Save Python object to file using dill
    
    Args:
        file_path (str): Destination path
        obj: Python object to serialize
    
    Features:
    - Creates directories if needed
    - Uses dill for complex object serialization
    - Error handling with CustomException
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)
    except Exception as e:
        raise CustomException(e, sys)


def load_object(file_path):
    """
    Load Python object from file
    
    Args:
        file_path (str): Source file path
    
    Returns:
        Deserialized Python object
    """
    try:
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise CustomException(e, sys)


def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    """
    Train and evaluate multiple models with hyperparameter tuning
    
    Args:
        X_train, y_train: Training data
        X_test, y_test: Test data
        models (dict): {model_name: model_instance}
        param (dict): {model_name: parameter_grid}
    
    Returns:
        dict: {model_name: test_r2_score}
    
    Process:
    1. For each model:
       a. GridSearchCV with parameter grid
       b. Fit on training data
       c. Get best parameters
       d. Evaluate on test set
    2. Return R² scores for all models
    """
    try:
        report = {}
        
        for model_name, model in models.items():
            para = param[model_name]
            
            gs = GridSearchCV(model, para, cv=3)
            gs.fit(X_train, y_train)
            
            model.set_params(**gs.best_params_)
            model.fit(X_train, y_train)
            
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            train_score = r2_score(y_train, y_train_pred)
            test_score = r2_score(y_test, y_test_pred)
            
            report[model_name] = test_score
        
        return report
    except Exception as e:
        raise CustomException(e, sys)
```

---

## 3. Data Pipeline

### 3.1 Data Ingestion (`data_ingestion.py`)

**Purpose**: Load raw data and split into train/test sets

```python
@dataclass
class DataIngestionConfig:
    """Configuration for data ingestion paths"""
    train_data_path: str = os.path.join('artifacts', "train.csv")
    test_data_path: str = os.path.join('artifacts', "test.csv")
    raw_data_path: str = os.path.join('artifacts', "data.csv")


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()
    
    def initiate_data_ingestion(self):
        """
        Process:
        1. Read CSV from notebook/data/stud.csv
        2. Create artifacts/ directory
        3. Save full dataset as data.csv
        4. Split 80/20 train/test
        5. Save train.csv and test.csv
        
        Returns:
            tuple: (train_path, test_path)
        """
        logging.info("Entered the data ingestion method")
        
        try:
            df = pd.read_csv('notebook/data/stud.csv')
            logging.info('Read the dataset as dataframe')
            
            os.makedirs(
                os.path.dirname(self.ingestion_config.train_data_path), 
                exist_ok=True
            )
            
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)
            
            logging.info("Train test split initiated")
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)
            
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path, index=False, header=True)
            
            logging.info("Ingestion of the data is completed")
            
            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path
            )
        except Exception as e:
            raise CustomException(e, sys)
```

### 3.2 Dataset Schema

```python
# Features (7 columns)
features = {
    'gender': ['male', 'female'],
    'race_ethnicity': ['group A', 'group B', 'group C', 'group D', 'group E'],
    'parental_level_of_education': [
        'some high school', 'high school', 'some college',
        "associate's degree", "bachelor's degree", "master's degree"
    ],
    'lunch': ['standard', 'free/reduced'],
    'test_preparation_course': ['none', 'completed'],
    'reading_score': 'int (0-100)',
    'writing_score': 'int (0-100)'
}

# Target
target = 'math_score'  # int (0-100)
```

---

## 4. Machine Learning Pipeline

### 4.1 Data Transformation (`data_transformation.py`)

**Purpose**: Feature engineering and preprocessing

#### 4.1.1 Preprocessing Pipeline

```python
@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path = os.path.join('artifacts', "preprocessor.pkl")


class DataTransformation:
    def get_data_transformer_object(self):
        """
        Creates preprocessing pipeline
        
        Pipeline Structure:
        
        Numerical Features (reading_score, writing_score):
        ┌──────────────────┐
        │ StandardScaler   │  # Z-score normalization
        └──────────────────┘
        
        Categorical Features (5 columns):
        ┌──────────────────────┐
        │ SimpleImputer        │  # Fill missing with 'missing'
        ├──────────────────────┤
        │ Pipeline:            │
        │ 1. OneHotEncoder     │  # For gender, race_ethnicity
        │ 2. OrdinalEncoder    │  # For ordered categories
        │ 3. StandardScaler    │  # Scale encoded features
        └──────────────────────┘
        
        Returns:
            ColumnTransformer with fitted pipelines
        """
        try:
            numerical_columns = ["writing_score", "reading_score"]
            categorical_columns = [
                "gender",
                "race_ethnicity",
                "parental_level_of_education",
                "lunch",
                "test_preparation_course",
            ]
            
            # Numerical pipeline
            num_pipeline = Pipeline(
                steps=[
                    ("scaler", StandardScaler())
                ]
            )
            
            # Categorical pipeline
            cat_pipeline = Pipeline(
                steps=[
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot_encoder", OneHotEncoder()),
                    ("scaler", StandardScaler(with_mean=False))
                ]
            )
            
            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")
            
            # Combine pipelines
            preprocessor = ColumnTransformer(
                [
                    ("num_pipeline", num_pipeline, numerical_columns),
                    ("cat_pipeline", cat_pipeline, categorical_columns)
                ]
            )
            
            return preprocessor
        except Exception as e:
            raise CustomException(e, sys)
```

#### 4.1.2 Transformation Execution

```python
def initiate_data_transformation(self, train_path, test_path):
    """
    Process:
    1. Load train and test CSV files
    2. Separate features (X) and target (y)
    3. Fit preprocessor on training data
    4. Transform both train and test sets
    5. Save preprocessor object
    
    Returns:
        tuple: (train_array, test_array, preprocessor_path)
    """
    try:
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        logging.info("Read train and test data completed")
        
        preprocessing_obj = self.get_data_transformer_object()
        
        target_column_name = "math_score"
        
        input_feature_train_df = train_df.drop(columns=[target_column_name], axis=1)
        target_feature_train_df = train_df[target_column_name]
        
        input_feature_test_df = test_df.drop(columns=[target_column_name], axis=1)
        target_feature_test_df = test_df[target_column_name]
        
        logging.info("Applying preprocessing object on training and testing dataframes")
        
        input_feature_train_arr = preprocessing_obj.fit_transform(input_feature_train_df)
        input_feature_test_arr = preprocessing_obj.transform(input_feature_test_df)
        
        train_arr = np.c_[
            input_feature_train_arr, np.array(target_feature_train_df)
        ]
        test_arr = np.c_[
            input_feature_test_arr, np.array(target_feature_test_df)
        ]
        
        logging.info("Saved preprocessing object")
        
        save_object(
            file_path=self.data_transformation_config.preprocessor_obj_file_path,
            obj=preprocessing_obj
        )
        
        return (
            train_arr,
            test_arr,
            self.data_transformation_config.preprocessor_obj_file_path,
        )
    except Exception as e:
        raise CustomException(e, sys)
```

### 4.2 Model Training (`model_trainer.py`)

**Purpose**: Train multiple models and select the best one

#### 4.2.1 Model Configuration

```python
@dataclass
class ModelTrainerConfig:
    trained_model_file_path = os.path.join("artifacts", "model.pkl")


class ModelTrainer:
    def initiate_model_trainer(self, train_array, test_array):
        """
        Process:
        1. Split arrays into X and y
        2. Define model dictionary
        3. Define hyperparameter grids
        4. Evaluate all models using GridSearchCV
        5. Select best model based on R² score
        6. Check if best score > 0.6 threshold
        7. Save best model
        
        Models Evaluated:
        - Random Forest Regressor
        - Decision Tree Regressor
        - Gradient Boosting Regressor
        - Linear Regression
        - XGBRegressor
        - CatBoosting Regressor
        - AdaBoost Regressor
        
        Returns:
            float: R² score of best model on test set
        """
        try:
            logging.info("Split training and test input data")
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],
                train_array[:, -1],
                test_array[:, :-1],
                test_array[:, -1]
            )
            
            models = {
                "Random Forest": RandomForestRegressor(),
                "Decision Tree": DecisionTreeRegressor(),
                "Gradient Boosting": GradientBoostingRegressor(),
                "Linear Regression": LinearRegression(),
                "XGBRegressor": XGBRegressor(),
                "CatBoosting Regressor": CatBoostRegressor(verbose=False),
                "AdaBoost Regressor": AdaBoostRegressor(),
            }
            
            params = {
                "Decision Tree": {
                    'criterion': ['squared_error', 'friedman_mse', 'absolute_error', 'poisson'],
                },
                "Random Forest": {
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "Gradient Boosting": {
                    'learning_rate': [.1, .01, .05, .001],
                    'subsample': [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "Linear Regression": {},
                "XGBRegressor": {
                    'learning_rate': [.1, .01, .05, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                },
                "CatBoosting Regressor": {
                    'depth': [6, 8, 10],
                    'learning_rate': [0.01, 0.05, 0.1],
                    'iterations': [30, 50, 100]
                },
                "AdaBoost Regressor": {
                    'learning_rate': [.1, .01, 0.5, .001],
                    'n_estimators': [8, 16, 32, 64, 128, 256]
                }
            }
            
            model_report: dict = evaluate_models(
                X_train=X_train, y_train=y_train,
                X_test=X_test, y_test=y_test,
                models=models, param=params
            )
            
            # Get best model score
            best_model_score = max(sorted(model_report.values()))
            
            # Get best model name
            best_model_name = list(model_report.keys())[
                list(model_report.values()).index(best_model_score)
            ]
            best_model = models[best_model_name]
            
            if best_model_score < 0.6:
                raise CustomException("No best model found")
            
            logging.info(f"Best found model on both training and testing dataset")
            
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )
            
            predicted = best_model.predict(X_test)
            r2_square = r2_score(y_test, predicted)
            
            return r2_square
        except Exception as e:
            raise CustomException(e, sys)
```

#### 4.2.2 Model Selection Criteria

```python
# Model evaluation metrics
metrics = {
    'R² Score': 'Coefficient of determination',
    'Threshold': 0.6,
    'Cross-Validation': 3-fold GridSearchCV
}

# Selection process
best_model = argmax(r2_scores) if max(r2_scores) > 0.6 else raise_error
```

### 4.3 Inference Pipeline (`predict_pipeline.py`)

**Purpose**: Handle real-time predictions

#### 4.3.1 Custom Data Class

```python
class CustomData:
    """
    Data model for user input
    
    Attributes match form fields and dataset columns
    Provides method to convert to DataFrame for prediction
    """
    def __init__(self,
                 gender: str,
                 race_ethnicity: str,
                 parental_level_of_education: str,
                 lunch: str,
                 test_preparation_course: str,
                 reading_score: int,
                 writing_score: int):
        self.gender = gender
        self.race_ethnicity = race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch = lunch
        self.test_preparation_course = test_preparation_course
        self.reading_score = reading_score
        self.writing_score = writing_score
    
    def get_data_as_data_frame(self):
        """
        Convert instance to pandas DataFrame
        
        Returns:
            pd.DataFrame: Single row with all features
        """
        try:
            custom_data_input_dict = {
                "gender": [self.gender],
                "race_ethnicity": [self.race_ethnicity],
                "parental_level_of_education": [self.parental_level_of_education],
                "lunch": [self.lunch],
                "test_preparation_course": [self.test_preparation_course],
                "reading_score": [self.reading_score],
                "writing_score": [self.writing_score],
            }
            
            return pd.DataFrame(custom_data_input_dict)
        except Exception as e:
            raise CustomException(e, sys)
```

#### 4.3.2 Prediction Pipeline

```python
class PredictPipeline:
    """
    Handles model loading and prediction
    """
    def __init__(self):
        pass
    
    def predict(self, features):
        """
        Process:
        1. Load preprocessor.pkl
        2. Load model.pkl
        3. Transform features using preprocessor
        4. Make prediction using model
        5. Return predicted value
        
        Args:
            features (pd.DataFrame): Input features
        
        Returns:
            np.array: Predicted math scores
        """
        try:
            model_path = os.path.join("artifacts", "model.pkl")
            preprocessor_path = os.path.join('artifacts', 'preprocessor.pkl')
            
            print("Before Loading")
            model = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)
            print("After Loading")
            
            data_scaled = preprocessor.transform(features)
            preds = model.predict(data_scaled)
            
            return preds
        except Exception as e:
            raise CustomException(e, sys)
```

---

## 5. Web Application

### 5.1 Flask Application (`app.py`)

```python
from flask import Flask, request, render_template
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

application = Flask(__name__)
app = application

@app.route('/')
def index():
    """
    Landing page
    Route: GET /
    Template: index.html
    """
    return render_template('index.html')


@app.route('/predictdata', methods=['GET', 'POST'])
def predict_datapoint():
    """
    Prediction endpoint
    
    GET Request:
        Returns prediction form (home.html)
    
    POST Request:
        1. Extract form data
        2. Create CustomData instance
        3. Convert to DataFrame
        4. Run PredictPipeline
        5. Return results to template
    
    Form Fields:
        - gender
        - ethnicity (race_ethnicity)
        - parental_level_of_education
        - lunch
        - test_preparation_course
        - reading_score
        - writing_score
    """
    if request.method == 'GET':
        return render_template('home.html')
    else:
        data = CustomData(
            gender=request.form.get('gender'),
            race_ethnicity=request.form.get('ethnicity'),
            parental_level_of_education=request.form.get('parental_level_of_education'),
            lunch=request.form.get('lunch'),
            test_preparation_course=request.form.get('test_preparation_course'),
            reading_score=float(request.form.get('reading_score')),
            writing_score=float(request.form.get('writing_score'))
        )
        
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        print("Before Prediction")
        
        predict_pipeline = PredictPipeline()
        print("Mid Prediction")
        results = predict_pipeline.predict(pred_df)
        print("After Prediction")
        
        return render_template('home.html', results=results[0])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### 5.2 Templates

#### 5.2.1 Landing Page (`index.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Student Performance Predictor</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <h1>Student Performance Prediction System</h1>
        <p>Predict student math scores based on demographic and academic factors</p>
        <a href="/predictdata" class="btn">Get Started</a>
    </div>
</body>
</html>
```

#### 5.2.2 Prediction Form (`home.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Predict Math Score</title>
</head>
<body>
    <div class="container">
        <h1>Predict Math Score</h1>
        
        <form method="POST">
            <!-- Gender -->
            <label>Gender:</label>
            <select name="gender" required>
                <option value="male">Male</option>
                <option value="female">Female</option>
            </select>
            
            <!-- Race/Ethnicity -->
            <label>Race/Ethnicity:</label>
            <select name="ethnicity" required>
                <option value="group A">Group A</option>
                <option value="group B">Group B</option>
                <option value="group C">Group C</option>
                <option value="group D">Group D</option>
                <option value="group E">Group E</option>
            </select>
            
            <!-- Parental Education -->
            <label>Parental Level of Education:</label>
            <select name="parental_level_of_education" required>
                <option value="some high school">Some High School</option>
                <option value="high school">High School</option>
                <option value="some college">Some College</option>
                <option value="associate's degree">Associate's Degree</option>
                <option value="bachelor's degree">Bachelor's Degree</option>
                <option value="master's degree">Master's Degree</option>
            </select>
            
            <!-- Lunch Type -->
            <label>Lunch Type:</label>
            <select name="lunch" required>
                <option value="standard">Standard</option>
                <option value="free/reduced">Free/Reduced</option>
            </select>
            
            <!-- Test Prep Course -->
            <label>Test Preparation Course:</label>
            <select name="test_preparation_course" required>
                <option value="none">None</option>
                <option value="completed">Completed</option>
            </select>
            
            <!-- Reading Score -->
            <label>Reading Score (0-100):</label>
            <input type="number" name="reading_score" min="0" max="100" required>
            
            <!-- Writing Score -->
            <label>Writing Score (0-100):</label>
            <input type="number" name="writing_score" min="0" max="100" required>
            
            <button type="submit">Predict</button>
        </form>
        
        {% if results %}
        <div class="result">
            <h2>Predicted Math Score: {{ results }}</h2>
        </div>
        {% endif %}
    </div>
</body>
</html>
```

---

## 6. Deployment Pipeline

### 6.1 GitHub Actions Workflow

**File**: `.github/workflows/ec2-deploy.yml`

#### 6.1.1 Workflow Triggers

```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

#### 6.1.2 Job 1: Continuous Integration

```yaml
ci:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests (placeholder)
      run: |
        echo "Running tests..."
```

#### 6.1.3 Job 2: Build and Push to ECR

```yaml
build-and-push:
  needs: ci
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ secrets.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build, tag, and push image to Amazon ECR
      env:
        ECR_REGISTRY: ${{ secrets.ECR_REGISTRY }}
        ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
```

#### 6.1.4 Job 3: Deploy to EC2

```yaml
deploy:
  needs: build-and-push
  runs-on: ubuntu-latest
  steps:
    - name: Deploy to EC2
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USER }}
        key: ${{ secrets.EC2_SSH_KEY }}
        script: |
          # Install AWS CLI if not present
          if ! command -v aws &> /dev/null; then
            curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
            unzip -q awscliv2.zip
            sudo ./aws/install
          fi
          
          # Login to ECR
          aws ecr get-login-password --region ${{ secrets.AWS_REGION }} | \
            docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          
          # Pull latest image
          docker pull ${{ secrets.ECR_REGISTRY }}/${{ secrets.ECR_REPOSITORY }}:latest
          
          # Stop and remove old container
          docker stop mlproject || true
          docker rm mlproject || true
          
          # Run new container
          docker run -d -p 80:8080 --name mlproject \
            ${{ secrets.ECR_REGISTRY }}/${{ secrets.ECR_REPOSITORY }}:latest
          
          # Health check
          sleep 10
          curl -f http://localhost || exit 1
          
          # Clean up old images
          docker image prune -af
```

### 6.2 Docker Configuration

#### 6.2.1 Dockerfile

```dockerfile
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

EXPOSE 8080

# Run with Gunicorn
CMD ["gunicorn", "-w", "2", "--timeout", "120", "-b", "0.0.0.0:8080", "app:app"]
```

**Key Configuration**:
- **Workers**: 2 (optimized for 1GB RAM)
- **Timeout**: 120s (allows model loading time)
- **Port**: 8080 (mapped to host port 80)

#### 6.2.2 .dockerignore

```text
__pycache__
*.pyc
*.pyo
*.pyd

venv/
.venv/
env/

.vscode/
.idea/

# artifacts/ commented out - needed for predictions
notebook/
logs/
catboost_info/

build/
dist/
*.egg-info/
```

---

## 7. Configuration

### 7.1 Environment Variables

```python
# Required GitHub Secrets
AWS_ACCESS_KEY_ID          # IAM user access key
AWS_SECRET_ACCESS_KEY      # IAM user secret key
AWS_REGION                 # us-east-1
ECR_REGISTRY              # 951897726242.dkr.ecr.us-east-1.amazonaws.com
ECR_REPOSITORY            # mlproject
EC2_HOST                  # 34.228.159.84
EC2_USER                  # ec2-user
EC2_SSH_KEY               # RSA private key content
```

### 7.2 Application Configuration

```python
# Flask settings
HOST = "0.0.0.0"
PORT = 8080
DEBUG = False  # Production mode

# Gunicorn settings
WORKERS = 2
TIMEOUT = 120
BIND = "0.0.0.0:8080"

# Model paths
MODEL_PATH = "artifacts/model.pkl"
PREPROCESSOR_PATH = "artifacts/preprocessor.pkl"

# Data paths
RAW_DATA = "artifacts/data.csv"
TRAIN_DATA = "artifacts/train.csv"
TEST_DATA = "artifacts/test.csv"
```

---

## 8. Error Handling & Logging

### 8.1 Exception Hierarchy

```text
Exception (Python built-in)
    └── CustomException (src/exception.py)
            ├── Data Ingestion Errors
            ├── Transformation Errors
            ├── Model Training Errors
            └── Prediction Errors
```

### 8.2 Logging Strategy

```python
# Log Levels
logging.INFO     # Standard operations
logging.ERROR    # Caught exceptions
logging.WARNING  # Potential issues
logging.DEBUG    # Detailed debugging (disabled in production)

# Log Format
[2026-02-01 15:11:38] 42 src.components.data_ingestion - INFO - Read dataset as dataframe

# Log Locations
logs/MM_DD_YYYY_HH_MM_SS.log  # Timestamped log files
Docker logs: docker logs mlproject
```

---

## 9. Performance Optimization

### 9.1 Model Loading Optimization

**Problem**: Model loading takes 10-15 seconds, causing worker timeouts

**Solution**:
1. Increased Gunicorn timeout to 120s
2. Reduced workers from 4 to 2 (memory constraint)
3. Lazy loading (load model only when needed)

```python
# Before (eager loading)
class PredictPipeline:
    def __init__(self):
        self.model = load_object("artifacts/model.pkl")
        self.preprocessor = load_object("artifacts/preprocessor.pkl")

# After (lazy loading)
class PredictPipeline:
    def __init__(self):
        pass
    
    def predict(self, features):
        model = load_object("artifacts/model.pkl")  # Load on demand
        preprocessor = load_object("artifacts/preprocessor.pkl")
        # ... prediction logic
```

### 9.2 Memory Optimization

**Constraints**: t2.micro has 1GB RAM

**Strategies**:
- Reduced Gunicorn workers (2 instead of 4)
- Disabled verbose logging in CatBoost
- Used `--no-cache-dir` in pip install
- Cleaned up unused Docker images after deployment

---

## 10. Testing Strategy

### 10.1 Manual Testing Checklist

```text
Local Testing:
□ python app.py runs without errors
□ http://localhost:8080 loads landing page
□ Form submission returns prediction
□ Logs are created in logs/ directory
□ Invalid inputs show error messages

Docker Testing:
□ docker build completes successfully
□ Container starts and exposes port 8080
□ http://localhost works (port mapping)
□ Docker logs show Gunicorn startup
□ Prediction endpoint responds correctly

Deployment Testing:
□ GitHub Actions workflow passes all jobs
□ ECR contains new image with latest tag
□ EC2 container is running (docker ps)
□ Public IP serves application
□ Prediction works on production
```

### 10.2 Future Testing Recommendations

```python
# Unit Tests (pytest)
tests/
├── test_data_ingestion.py       # Test CSV loading, splitting
├── test_data_transformation.py  # Test preprocessing pipeline
├── test_model_trainer.py        # Test model training logic
├── test_predict_pipeline.py     # Test inference
└── test_app.py                  # Test Flask routes

# Integration Tests
# - End-to-end prediction flow
# - Database connectivity (future)
# - API contract testing

# Load Tests (locust)
# - Concurrent user simulation
# - Response time benchmarks
# - Memory usage under load
```

---

## 11. Troubleshooting Guide

### 11.1 Common Issues

**Issue**: Worker Timeout

```bash
[CRITICAL] WORKER TIMEOUT (pid:9)
[ERROR] Worker (pid:9) exited with code 1
```

**Solution**: Increase Gunicorn timeout in Dockerfile

```dockerfile
CMD ["gunicorn", "-w", "2", "--timeout", "120", "-b", "0.0.0.0:8080", "app:app"]
```

---

**Issue**: Missing Model Files

```python
FileNotFoundError: [Errno 2] No such file or directory: 'artifacts/model.pkl'
```

**Solution**: Remove `artifacts/` from .dockerignore

---

**Issue**: Memory Issues on EC2

```bash
docker: Error response from daemon: OOM command not allowed when used memory > 'memory+swap'
```

**Solution**: Reduce workers or upgrade to t2.small

---

**Issue**: SSH Authentication Failed

```bash
ssh: unable to authenticate using publickey
```

**Solution**: Update EC2_SSH_KEY secret with full .pem content including BEGIN/END lines

---

This technical documentation provides comprehensive implementation details for developers working on or extending the Student Performance Prediction System.

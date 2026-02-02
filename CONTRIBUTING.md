# Contributing to Student Performance Prediction System

Thank you for considering contributing to this project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing Guidelines](#testing-guidelines)

---

## Code of Conduct

### Our Pledge

We pledge to make participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes**:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes**:

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

- Check existing issues to avoid duplicates
- Verify the bug in the latest version
- Collect relevant information (logs, screenshots, system info)

**Bug Report Template**:

```markdown
## Bug Description
A clear description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Windows 11]
- Python Version: [e.g., 3.10.5]
- Docker Version: [e.g., 24.0.5]

## Logs
```

Paste relevant logs here

```
## Screenshots
If applicable, add screenshots.
```

### Suggesting Enhancements

**Enhancement Request Template**:

```markdown
## Feature Description
A clear description of the feature you'd like.

## Problem It Solves
Explain the problem this feature would solve.

## Proposed Solution
Describe how you envision this feature working.

## Alternatives Considered
What alternative solutions have you considered?

## Additional Context
Add any other context or screenshots about the feature request.
```

### Contributing Code

Areas where contributions are welcome:

- Bug fixes
- Feature implementations
- Documentation improvements
- Test coverage
- Performance optimizations
- Code refactoring

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- Docker (optional, for local testing)
- AWS Account (optional, for deployment testing)

### Local Setup

1. **Fork the repository**

   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Clone your fork**

   ```bash
   git clone https://github.com/aashishkumar-tech/mlproject.git
   cd mlproject
   ```

3. **Add upstream remote**

   ```bash
   git remote add upstream https://github.com/aashishkumar-tech/mlproject.git
   ```

4. **Create virtual environment**

   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # macOS/Linux
   source venv/bin/activate
   ```

5. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

6. **Run the application**

   ```bash
   python app.py
   ```

7. **Test locally**
   - Visit: <http://localhost:8080>
   - Test prediction endpoint

### Docker Setup

```bash
# Build image
docker build -t mlproject:dev .

# Run container
docker run -p 8080:8080 mlproject:dev

# Test
curl http://localhost:8080
```

---

## Coding Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) style guide:

```python
# Good
def calculate_student_score(reading_score, writing_score):
    """Calculate average score from reading and writing scores."""
    return (reading_score + writing_score) / 2

# Bad
def calc(r,w):
    return (r+w)/2
```

### Code Organization

```python
# Import order
import os                           # Standard library
import sys

import pandas as pd                 # Third-party
import numpy as np
from sklearn.ensemble import RandomForestRegressor

from src.exception import CustomException  # Local imports
from src.logger import logging
```

### Documentation Standards

**Module docstrings**:

```python
"""
Module: data_ingestion.py

This module handles data loading and train/test splitting.

Classes:
    DataIngestionConfig: Configuration for data paths
    DataIngestion: Main data ingestion class

Functions:
    initiate_data_ingestion(): Execute data ingestion pipeline
"""
```

**Function docstrings**:

```python
def evaluate_models(X_train, y_train, X_test, y_test, models, param):
    """
    Train and evaluate multiple models with hyperparameter tuning.
    
    Args:
        X_train (np.ndarray): Training features
        y_train (np.ndarray): Training labels
        X_test (np.ndarray): Test features
        y_test (np.ndarray): Test labels
        models (dict): Dictionary of model instances
        param (dict): Dictionary of hyperparameter grids
    
    Returns:
        dict: Model names mapped to R² scores
    
    Raises:
        CustomException: If model evaluation fails
    
    Example:
        >>> models = {"RF": RandomForestRegressor()}
        >>> params = {"RF": {"n_estimators": [10, 50]}}
        >>> scores = evaluate_models(X_train, y_train, X_test, y_test, models, params)
    """
```

### Error Handling

Always use custom exception:

```python
# Good
try:
    df = pd.read_csv(file_path)
except Exception as e:
    raise CustomException(e, sys)

# Bad
try:
    df = pd.read_csv(file_path)
except:
    print("Error reading file")
```

### Logging

Use structured logging:

```python
# Good
logging.info(f"Data ingestion started with file: {file_path}")
logging.error(f"Failed to load model from {model_path}")

# Bad
print("Starting data ingestion")
```

---

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code formatting (no logic change)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Build process, dependencies

**Examples**:

```bash
feat(model): add XGBoost hyperparameter tuning

Implemented GridSearchCV for XGBoost with learning_rate and n_estimators parameters.
Improved R² score from 0.82 to 0.87 on test set.

Closes #42

---

fix(docker): increase gunicorn timeout to prevent worker crashes

Workers were timing out during model loading on t2.micro instances.
Increased timeout from 30s to 120s and reduced workers from 4 to 2.

Fixes #58

---

docs(readme): update deployment instructions

Added section on AWS setup and GitHub Secrets configuration.
Included troubleshooting guide for common deployment issues.
```

### Commit Best Practices

- One logical change per commit
- Write descriptive commit messages
- Reference issues/PRs when relevant
- Keep commits atomic and focused

---

## Pull Request Process

### Before Submitting

1. **Update your fork**

   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes**
   - Write clean, documented code
   - Follow coding standards
   - Add tests if applicable

4. **Test thoroughly**

   ```bash
   # Run application
   python app.py
   
   # Test Docker build
   docker build -t mlproject:test .
   docker run -p 8080:8080 mlproject:test
   
   # Manual testing
   # - Test all routes
   # - Verify predictions
   # - Check logs
   ```

5. **Commit changes**

   ```bash
   git add .
   git commit -m "feat(scope): descriptive message"
   ```

6. **Push to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Fill in the PR template:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran and how to reproduce them.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)

## Related Issues
Closes #<issue_number>
```

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

### After Merge

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Testing Guidelines

### Manual Testing Checklist

**Core Functionality**:

- [ ] Application starts without errors
- [ ] Landing page loads correctly
- [ ] Prediction form displays all fields
- [ ] Form validation works
- [ ] Prediction returns valid result
- [ ] Result is displayed correctly

**Edge Cases**:

- [ ] Invalid input handling
- [ ] Empty form submission
- [ ] Boundary values (0, 100 for scores)
- [ ] Special characters in form fields

**Performance**:

- [ ] Page load time < 2 seconds
- [ ] Prediction response time < 15 seconds
- [ ] No memory leaks during repeated requests

### Automated Testing (Future)

```python
# tests/test_predict_pipeline.py
import pytest
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

def test_custom_data_to_dataframe():
    """Test CustomData converts to DataFrame correctly."""
    data = CustomData(
        gender="male",
        race_ethnicity="group A",
        parental_level_of_education="bachelor's degree",
        lunch="standard",
        test_preparation_course="completed",
        reading_score=72,
        writing_score=74
    )
    df = data.get_data_as_data_frame()
    
    assert df.shape == (1, 7)
    assert df['gender'].iloc[0] == "male"
    assert df['reading_score'].iloc[0] == 72

def test_prediction_pipeline():
    """Test prediction returns valid score."""
    pipeline = PredictPipeline()
    data = CustomData(...)
    df = data.get_data_as_data_frame()
    result = pipeline.predict(df)
    
    assert len(result) == 1
    assert 0 <= result[0] <= 100
```

---

## Project Structure for Contributors

```text
mlproject/
├── src/                    # Core application code
│   ├── components/         # Training pipeline components
│   ├── pipeline/           # Inference pipeline
│   └── utils/              # Helper functions
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── tests/                  # Unit and integration tests
├── .github/                # GitHub Actions workflows
├── artifacts/              # Model artifacts (not in git)
├── logs/                   # Application logs (not in git)
├── notebook/               # Jupyter notebooks for EDA
└── docs/                   # Additional documentation
```

---

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue with bug template
- **Features**: Open an Issue with feature template
- **Security**: Email aashishkumar.tech@gmail.com directly

---

## Recognition

Contributors will be recognized in:

- README.md Contributors section
- Release notes
- GitHub Contributors page

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)

---

Thank you for contributing to the Student Performance Prediction System! 🎉

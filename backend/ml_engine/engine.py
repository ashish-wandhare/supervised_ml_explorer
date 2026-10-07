import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestClassifier, RandomForestRegressor,
    GradientBoostingClassifier, GradientBoostingRegressor
)
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from typing import Optional
import traceback

ALGORITHMS = {
    "classification": {
        "Logistic Regression": {
            "model_class": LogisticRegression,
            "default_params": {"max_iter": 1000, "random_state": 42},
            "description": "Linear model for binary/multiclass classification using sigmoid.",
        },
        "Decision Tree": {
            "model_class": DecisionTreeClassifier,
            "default_params": {"random_state": 42, "max_depth": 10},
            "description": "Tree-based model that splits features to minimise impurity.",
        },
        "Random Forest": {
            "model_class": RandomForestClassifier,
            "default_params": {"n_estimators": 100, "random_state": 42},
            "description": "Ensemble of decision trees that vote for the final class.",
        },
        "SVM": {
            "model_class": SVC,
            "default_params": {"probability": True, "random_state": 42},
            "description": "Finds the optimal hyperplane with maximum margin between classes.",
        },
        "KNN": {
            "model_class": KNeighborsClassifier,
            "default_params": {"n_neighbors": 5},
            "description": "Classifies by majority vote among k nearest neighbours.",
        },
        "Naive Bayes": {
            "model_class": GaussianNB,
            "default_params": {},
            "description": "Probabilistic classifier based on Bayes theorem with feature independence.",
        },
        "Gradient Boosting": {
            "model_class": GradientBoostingClassifier,
            "default_params": {"n_estimators": 100, "random_state": 42},
            "description": "Sequential ensemble that corrects errors of previous trees.",
        },
    },
    "regression": {
        "Linear Regression": {
            "model_class": LinearRegression,
            "default_params": {},
            "description": "Fits a straight line to minimise squared residuals.",
        },
        "Ridge Regression": {
            "model_class": Ridge,
            "default_params": {"alpha": 1.0},
            "description": "Linear regression with L2 regularisation to prevent overfitting.",
        },
        "Lasso Regression": {
            "model_class": Lasso,
            "default_params": {"alpha": 1.0},
            "description": "Linear regression with L1 regularisation that can zero out features.",
        },
        "Decision Tree": {
            "model_class": DecisionTreeRegressor,
            "default_params": {"random_state": 42, "max_depth": 10},
            "description": "Tree-based model for predicting continuous values.",
        },
        "Random Forest": {
            "model_class": RandomForestRegressor,
            "default_params": {"n_estimators": 100, "random_state": 42},
            "description": "Ensemble of trees whose predictions are averaged.",
        },
        "SVR": {
            "model_class": SVR,
            "default_params": {},
            "description": "SVM adapted for regression tasks using epsilon-insensitive loss.",
        },
        "KNN Regressor": {
            "model_class": KNeighborsRegressor,
            "default_params": {"n_neighbors": 5},
            "description": "Predicts by averaging the values of k nearest neighbours.",
        },
        "Gradient Boosting": {
            "model_class": GradientBoostingRegressor,
            "default_params": {"n_estimators": 100, "random_state": 42},
            "description": "Sequential boosting ensemble for regression.",
        },
    },
}


def get_available_algorithms(task_type: str) -> dict:
    return {
        name: {"description": info["description"], "default_params": info["default_params"]}
        for name, info in ALGORITHMS.get(task_type, {}).items()
    }


def run_experiment(
    df: pd.DataFrame,
    target_column: str,
    algorithm_name: str,
    task_type: str,
    test_size: float = 0.2,
    hyperparameters: Optional[dict] = None,
) -> dict:
    try:
        # Prepare features
        X = df.drop(columns=[target_column])
        y = df[target_column]

        # Encode categorical features
        X = pd.get_dummies(X, drop_first=True)
        le = None
        if task_type == "classification" and y.dtype == object:
            le = LabelEncoder()
            y = le.fit_transform(y)

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s = scaler.transform(X_test)

        # Build model
        algo_info = ALGORITHMS[task_type][algorithm_name]
        params = {**algo_info["default_params"], **(hyperparameters or {})}
        model = algo_info["model_class"](**params)

        # Train
        start = time.time()
        model.fit(X_train_s, y_train)
        elapsed_ms = (time.time() - start) * 1000

        y_pred = model.predict(X_test_s)

        # Compute metrics
        if task_type == "classification":
            avg = "weighted"
            metrics = {
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "f1_score": round(float(f1_score(y_test, y_pred, average=avg, zero_division=0)), 4),
                "precision": round(float(precision_score(y_test, y_pred, average=avg, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, y_pred, average=avg, zero_division=0)), 4),
            }
            cm = confusion_matrix(y_test, y_pred).tolist()
            classes = (le.classes_.tolist() if le else sorted(set(y_test.tolist())))
        else:
            metrics = {
                "r2_score": round(float(r2_score(y_test, y_pred)), 4),
                "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
                "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
            }
            cm = None
            classes = None

        # Feature importance
        feat_imp = None
        feature_names = list(X.columns)
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_.tolist()
            feat_imp = dict(sorted(
                zip(feature_names, importances), key=lambda x: x[1], reverse=True
            ))
        elif hasattr(model, "coef_"):
            coef = model.coef_
            if coef.ndim > 1:
                coef = np.abs(coef).mean(axis=0)
            feat_imp = dict(sorted(
                zip(feature_names, np.abs(coef).tolist()), key=lambda x: x[1], reverse=True
            ))

        return {
            "status": "success",
            "metrics": metrics,
            "confusion_matrix": cm,
            "classes": classes,
            "feature_importance": feat_imp,
            "training_time_ms": round(elapsed_ms, 2),
            "hyperparameters": params,
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

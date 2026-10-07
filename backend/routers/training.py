import os, io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Dataset, Experiment
from ml_engine.engine import run_experiment, get_available_algorithms

router = APIRouter()
UPLOAD_DIR = "uploads"


class TrainRequest(BaseModel):
    dataset_id: int
    algorithm: str
    test_size: float = 0.2
    hyperparameters: Optional[dict] = None


@router.get("/algorithms")
def list_algorithms(task_type: str = "classification"):
    return get_available_algorithms(task_type)


@router.post("/run")
def train_model(req: TrainRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == req.dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    path = os.path.join(UPLOAD_DIR, dataset.filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Dataset file not found on disk.")

    df = pd.read_csv(path)

    result = run_experiment(
        df=df,
        target_column=dataset.target_column,
        algorithm_name=req.algorithm,
        task_type=dataset.task_type,
        test_size=req.test_size,
        hyperparameters=req.hyperparameters,
    )

    exp = Experiment(
        dataset_id=dataset.id,
        dataset_name=dataset.name,
        algorithm=req.algorithm,
        task_type=dataset.task_type,
        target_column=dataset.target_column,
        hyperparameters=result.get("hyperparameters"),
        metrics=result.get("metrics"),
        feature_importance=result.get("feature_importance"),
        confusion_matrix=result.get("confusion_matrix"),
        training_time_ms=result.get("training_time_ms"),
        test_size=req.test_size,
        status=result.get("status"),
        error_message=result.get("error"),
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)

    return {
        "experiment_id": exp.id,
        **result,
        "algorithm": req.algorithm,
        "dataset": dataset.name,
        "task_type": dataset.task_type,
    }


@router.post("/run-all")
def train_all_algorithms(dataset_id: int, test_size: float = 0.2, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(404, "Dataset not found.")

    path = os.path.join(UPLOAD_DIR, dataset.filename)
    df = pd.read_csv(path)

    algos = get_available_algorithms(dataset.task_type)
    results = []

    for algo_name in algos:
        result = run_experiment(
            df=df,
            target_column=dataset.target_column,
            algorithm_name=algo_name,
            task_type=dataset.task_type,
            test_size=test_size,
        )
        exp = Experiment(
            dataset_id=dataset.id,
            dataset_name=dataset.name,
            algorithm=algo_name,
            task_type=dataset.task_type,
            target_column=dataset.target_column,
            hyperparameters=result.get("hyperparameters"),
            metrics=result.get("metrics"),
            feature_importance=result.get("feature_importance"),
            confusion_matrix=result.get("confusion_matrix"),
            training_time_ms=result.get("training_time_ms"),
            test_size=test_size,
            status=result.get("status"),
            error_message=result.get("error"),
        )
        db.add(exp)
        db.commit()
        db.refresh(exp)
        results.append({
            "experiment_id": exp.id,
            "algorithm": algo_name,
            "status": result.get("status"),
            "metrics": result.get("metrics"),
            "training_time_ms": result.get("training_time_ms"),
        })

    return {"dataset": dataset.name, "results": results, "total": len(results)}

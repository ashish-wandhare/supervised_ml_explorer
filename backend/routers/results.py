from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Experiment

router = APIRouter()


@router.get("/")
def list_results(
    dataset_id: int = None,
    algorithm: str = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Experiment)
    if dataset_id:
        q = q.filter(Experiment.dataset_id == dataset_id)
    if algorithm:
        q = q.filter(Experiment.algorithm == algorithm)
    experiments = q.order_by(Experiment.created_at.desc()).limit(limit).all()

    return [
        {
            "id": e.id,
            "dataset": e.dataset_name,
            "algorithm": e.algorithm,
            "task_type": e.task_type,
            "metrics": e.metrics,
            "training_time_ms": e.training_time_ms,
            "test_size": e.test_size,
            "status": e.status,
            "created_at": e.created_at,
        }
        for e in experiments
    ]


@router.get("/{experiment_id}")
def get_result(experiment_id: int, db: Session = Depends(get_db)):
    e = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not e:
        raise HTTPException(404, "Experiment not found.")
    return {
        "id": e.id,
        "dataset": e.dataset_name,
        "dataset_id": e.dataset_id,
        "algorithm": e.algorithm,
        "task_type": e.task_type,
        "target_column": e.target_column,
        "metrics": e.metrics,
        "confusion_matrix": e.confusion_matrix,
        "feature_importance": e.feature_importance,
        "hyperparameters": e.hyperparameters,
        "training_time_ms": e.training_time_ms,
        "test_size": e.test_size,
        "status": e.status,
        "error_message": e.error_message,
        "created_at": e.created_at,
    }


@router.delete("/{experiment_id}")
def delete_result(experiment_id: int, db: Session = Depends(get_db)):
    e = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not e:
        raise HTTPException(404, "Experiment not found.")
    db.delete(e)
    db.commit()
    return {"message": "Experiment deleted."}

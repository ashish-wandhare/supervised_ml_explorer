from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Experiment
from collections import defaultdict

router = APIRouter()


@router.get("/compare")
def compare_algorithms(dataset_id: int, db: Session = Depends(get_db)):
    experiments = (
        db.query(Experiment)
        .filter(Experiment.dataset_id == dataset_id, Experiment.status == "success")
        .order_by(Experiment.created_at.desc())
        .all()
    )
    if not experiments:
        raise HTTPException(404, "No successful experiments found for this dataset.")

    # Deduplicate — keep latest run per algorithm
    seen = {}
    for e in experiments:
        if e.algorithm not in seen:
            seen[e.algorithm] = e

    comparison = []
    for algo, e in seen.items():
        comparison.append({
            "algorithm": algo,
            "metrics": e.metrics,
            "training_time_ms": e.training_time_ms,
            "experiment_id": e.id,
        })

    # Determine best algorithm per metric
    if comparison:
        task = experiments[0].task_type
        primary_metric = "accuracy" if task == "classification" else "r2_score"
        best = max(
            comparison,
            key=lambda x: x["metrics"].get(primary_metric, -9999) if x["metrics"] else -9999,
        )
        best_algo = best["algorithm"]
    else:
        best_algo = None

    return {
        "dataset_id": dataset_id,
        "task_type": experiments[0].task_type if experiments else None,
        "comparison": comparison,
        "best_algorithm": best_algo,
        "total_algorithms": len(comparison),
    }


@router.get("/leaderboard")
def global_leaderboard(db: Session = Depends(get_db)):
    experiments = (
        db.query(Experiment)
        .filter(Experiment.status == "success")
        .order_by(Experiment.created_at.desc())
        .all()
    )

    board = defaultdict(list)
    for e in experiments:
        if e.metrics:
            board[e.algorithm].append(e.metrics)

    summary = []
    for algo, metrics_list in board.items():
        avg_metrics = {}
        for key in metrics_list[0]:
            values = [m[key] for m in metrics_list if key in m]
            avg_metrics[key] = round(sum(values) / len(values), 4)
        summary.append({"algorithm": algo, "avg_metrics": avg_metrics, "runs": len(metrics_list)})

    return {"leaderboard": sorted(summary, key=lambda x: x["runs"], reverse=True)}


@router.get("/summary")
def platform_summary(db: Session = Depends(get_db)):
    total = db.query(Experiment).count()
    success = db.query(Experiment).filter(Experiment.status == "success").count()
    failed = db.query(Experiment).filter(Experiment.status == "failed").count()
    algorithms_used = db.query(Experiment.algorithm).distinct().count()

    return {
        "total_experiments": total,
        "successful": success,
        "failed": failed,
        "unique_algorithms": algorithms_used,
    }

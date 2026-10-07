import os, io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db, Dataset
from typing import Optional

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def auto_detect_task_type(df: pd.DataFrame, target_column: str) -> str:
    """
    Auto-detect whether the target column needs classification or regression.

    Rules:
    1. If target is text/string → Classification
    2. If target has <= 10 unique numeric values → Classification
    3. If target has only 0s and 1s → Classification
    4. Otherwise → Regression
    """
    col = df[target_column].dropna()

    # Rule 1: Text labels → Classification
    if col.dtype == object:
        return "classification"

    unique_vals = sorted(col.unique())
    n_unique = len(unique_vals)

    # Rule 2: Binary 0/1 → Classification
    if set(unique_vals).issubset({0, 1}):
        return "classification"

    # Rule 3: Few unique integers → Classification
    if col.dtype in ['int64', 'int32'] and n_unique <= 10:
        return "classification"

    # Rule 4: Floats or many unique values → Regression
    return "regression"


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    target_column: str = Form(...),
    task_type: str = Form(None),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported.")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    if target_column not in df.columns:
        raise HTTPException(400, f"Target column '{target_column}' not found in CSV.")

    # Auto-detect task type if not provided or set to "auto"
    if not task_type or task_type == "auto":
        task_type = auto_detect_task_type(df, target_column)
        auto_detected = True
    else:
        auto_detected = False

    # Save file
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(contents)

    dataset = Dataset(
        name=file.filename.replace(".csv", ""),
        filename=file.filename,
        rows=len(df),
        columns=len(df.columns),
        column_names=list(df.columns),
        task_type=task_type,
        target_column=target_column,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    return {
        "id": dataset.id,
        "name": dataset.name,
        "rows": dataset.rows,
        "columns": dataset.columns,
        "column_names": dataset.column_names,
        "task_type": dataset.task_type,
        "target_column": dataset.target_column,
        "auto_detected": auto_detected,
        "preview": df.head(5).to_dict(orient="records"),
        "stats": df.describe().round(3).to_dict(),
    }


@router.get("/")
def list_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).order_by(Dataset.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "rows": d.rows,
            "columns": d.columns,
            "task_type": d.task_type,
            "target_column": d.target_column,
            "column_names": d.column_names,
            "created_at": d.created_at,
        }
        for d in datasets
    ]


@router.get("/{dataset_id}")
def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(404, "Dataset not found.")
    path = os.path.join(UPLOAD_DIR, d.filename)
    df = pd.read_csv(path)
    return {
        "id": d.id,
        "name": d.name,
        "rows": d.rows,
        "columns": d.columns,
        "task_type": d.task_type,
        "target_column": d.target_column,
        "column_names": d.column_names,
        "preview": df.head(10).to_dict(orient="records"),
        "stats": df.describe().round(3).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    d = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not d:
        raise HTTPException(404, "Dataset not found.")
    db.delete(d)
    db.commit()
    return {"message": "Dataset deleted."}

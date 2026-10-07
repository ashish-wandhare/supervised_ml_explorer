# 🤖 Supervised Learning Explorer

A professional full-stack platform to train, compare, and analyse **all supervised learning algorithms** in one place. Built with FastAPI + React + SQLite + scikit-learn.

---

## 📸 What You'll See

- 🏠 **Overview** — Stats dashboard + algorithm cards
- 📂 **Datasets** — Upload CSV files with drag & drop
- 🧠 **Train Model** — Train single or all algorithms at once
- 📊 **Results** — Browse experiment history with charts
- ⚖️ **Compare** — Side-by-side performance analysis
- 🏆 **Leaderboard** — Global ranking across all experiments
- 📖 **Algorithm Guide** — Deep dive into every algorithm

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Chart.js (no build step needed) |
| Backend | FastAPI + Uvicorn |
| Database | SQLite via SQLAlchemy |
| ML Engine | scikit-learn |
| API Docs | Swagger UI (auto-generated at /docs) |

---

## 📁 Project Structure

```
supervised_ml/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── database.py          ← SQLAlchemy models & DB setup
│   ├── requirements.txt     ← Python dependencies
│   ├── uploads/             ← Uploaded CSV files stored here
│   ├── ml_engine/
│   │   ├── __init__.py
│   │   └── engine.py        ← All ML algorithms + metrics
│   └── routers/
│       ├── __init__.py
│       ├── datasets.py      ← Upload & manage CSV datasets
│       ├── training.py      ← Run experiments
│       ├── results.py       ← Fetch experiment history
│       └── analysis.py      ← Compare & leaderboard
├── frontend/
│   └── index.html           ← Full React dashboard (single file)
├── sample_data/
│   ├── iris.csv             ← Sample classification dataset
│   └── titanic.csv          ← Real-world classification dataset
└── README.md
```

---

## ✅ Requirements

Before starting, make sure you have:

- **Python 3.8 or higher** (Recommended: Python 3.11)
- **pip** (comes with Python)
- **VS Code** or any code editor
- **Web Browser** (Chrome, Firefox, Edge)

Check your Python version:
```bash
python --version
```

Download Python 3.11 from: https://www.python.org/downloads/

> ⚠️ During Python installation, make sure to check **"Add Python to PATH"**

---

## 🚀 How to Run — Step by Step

### Step 1: Open the Project in VS Code

```bash
code .
```

Or open VS Code → File → Open Folder → select `supervised_ml`

---

### Step 2: Open Terminal in VS Code

Press **Ctrl + `** (backtick) to open terminal inside VS Code.

---

### Step 3: Go to Backend Folder

```bash
cd backend
```

---

### Step 4: Create Virtual Environment

```bash
python -m venv venv
```

---

### Step 5: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

After activation you will see **(venv)** at the start of your terminal — this means it is active ✅

---

### Step 6: Install All Dependencies

```bash
pip install -r requirements.txt
```

> ⏳ This takes 1–2 minutes depending on your internet speed.

---

### Step 7: Create Uploads Folder

**Windows:**
```bash
mkdir uploads
```

**Mac / Linux:**
```bash
mkdir -p uploads
```

---

### Step 8: Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

✅ Backend is now running!

---

### Step 9: Open the Frontend

**Do NOT close the terminal running uvicorn.**

Open a new terminal tab (press **+** in VS Code terminal), then open `frontend/index.html` in your browser:

**Windows:**
```bash
start ..\frontend\index.html
```

**Mac:**
```bash
open ../frontend/index.html
```

**Or simply double-click** `frontend/index.html` in File Explorer / Finder.

---

### Step 10: Verify Everything Works

Open browser and check:

| URL | Expected Result |
|-----|----------------|
| http://localhost:8000 | `{"status":"online"}` JSON response |
| http://localhost:8000/docs | Swagger API documentation page |
| frontend/index.html | Dark dashboard UI loads |

---

## 🎯 Quick Demo — Test It Right Away

### Using Iris Dataset (Simple — all 100%)

1. Go to **Datasets** tab → Upload `sample_data/iris.csv`
2. Target column: `species` | Task type: `Classification`
3. Go to **Train Model** → check **Train all algorithms** → click Train
4. Go to **Compare** → see results

### Using Titanic Dataset (Real World — different results!)

1. Go to **Datasets** tab → Upload `sample_data/titanic.csv`
2. Target column: `Survived` | Task type: `Classification`
3. Train all algorithms → Go to **Compare**
4. See how each algorithm gives different accuracy! 🚢

---

## 🤖 Algorithms Included

### Classification (7 algorithms)

| Algorithm | Best For |
|-----------|----------|
| Logistic Regression | Linear boundaries, fast, interpretable |
| Decision Tree | Rule-based, visual, interpretable |
| Random Forest | General purpose, robust, accurate |
| SVM | High-dimensional, complex boundaries |
| KNN | Small datasets, local patterns |
| Naive Bayes | Fast, probabilistic, text data |
| Gradient Boosting | Best accuracy on tabular data |

### Regression (8 algorithms)

| Algorithm | Best For |
|-----------|----------|
| Linear Regression | Simple, interpretable, linear data |
| Ridge Regression | Prevents overfitting with L2 |
| Lasso Regression | Feature selection with L1 |
| Decision Tree | Non-linear regression |
| Random Forest | Robust regression ensemble |
| SVR | Non-linear regression with kernels |
| KNN Regressor | Local pattern regression |
| Gradient Boosting | Highest accuracy regression |

---

## 🔌 API Reference

### Datasets
```
POST   /api/datasets/upload        Upload a CSV dataset
GET    /api/datasets/              List all datasets
GET    /api/datasets/{id}          Get dataset details + preview
DELETE /api/datasets/{id}          Delete a dataset
```

### Training
```
GET    /api/train/algorithms       List available algorithms
POST   /api/train/run              Train a single algorithm
POST   /api/train/run-all          Train ALL algorithms at once
```

### Results
```
GET    /api/results/               List all experiments
GET    /api/results/{id}           Get full experiment details
DELETE /api/results/{id}           Delete an experiment
```

### Analysis
```
GET    /api/analysis/compare       Compare algorithms on a dataset
GET    /api/analysis/leaderboard   Global algorithm leaderboard
GET    /api/analysis/summary       Platform-wide statistics
```

---

## ❌ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `uvicorn: command not found` | venv not activated | Run activate command first |
| `ModuleNotFoundError` | Dependencies missing | Run `pip install -r requirements.txt` |
| CORS error in browser | Backend not running | Start uvicorn on port 8000 |
| `uploads` folder error | Folder missing | Run `mkdir uploads` inside backend/ |
| Port 8000 already in use | Another app using port | Use `--port 8001` instead |
| `python not recognized` | Python not in PATH | Reinstall Python, check "Add to PATH" |
| Target column not found | Wrong column name | Check exact column name in your CSV |

---

## 🔄 How to Restart Next Time

Every time you open the project again:

```bash
# 1. Go to backend folder
cd backend

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Start server
uvicorn main:app --reload --port 8000

# 4. Open frontend/index.html in browser
```

---

## 🎓 Presentation Flow (Suggested)

1. **Overview page** → explain supervised learning concept
2. **Algorithm Guide** → explain each algorithm with pros/cons
3. **Upload Titanic dataset live** → show drag and drop
4. **Train All algorithms** → show real-time training
5. **Compare page** → explain metrics (accuracy, F1, precision, recall)
6. **Leaderboard** → identify best algorithm
7. **Open localhost:8000/docs** → show the professional REST API

---

## 👨‍💻 Built With

- [FastAPI](https://fastapi.tiangolo.com/) — Modern Python web framework
- [scikit-learn](https://scikit-learn.org/) — Machine learning library
- [SQLAlchemy](https://www.sqlalchemy.org/) — Python SQL toolkit
- [React](https://react.dev/) — Frontend UI library
- [Chart.js](https://www.chartjs.org/) — Beautiful charts

---
## Render Deployment

**Live Application:**  
https://supervised-ml-explorer-1.onrender.com/


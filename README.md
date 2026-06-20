# Developer Burnout Analysis

A full-stack web application that predicts developer burnout levels using a **manually implemented CART decision tree** (Gini impurity). The dashboard lets you train a model from CSV data, submit developer profile inputs, inspect the prediction path, and explore the full tree as an interactive graph.

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Algorithm | Manual CART decision tree (no scikit-learn, TensorFlow, PyTorch, XGBoost, etc.) |
| Frontend | React, TypeScript, Vite, plain CSS |
| Visualization | React Flow (`@xyflow/react`) |

## Project Structure

```
backend/
  app/
    main.py              # FastAPI routes and CORS
    models.py            # Pydantic request/response schemas
    decision_tree.py     # Manual CART implementation
    dataset_loader.py    # CSV parsing and validation
    sample_data_schema.md
  requirements.txt

frontend/
  src/
    api/client.ts
    components/
      BurnoutForm.tsx
      PredictionResult.tsx
      TreeVisualizer.tsx
      Dashboard.tsx
    types/tree.ts
    App.tsx
    main.tsx
    styles.css
  package.json
  vite.config.ts
```

## How to Run the Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

Interactive API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## How to Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api/*` to the backend during local development.

For production builds, set `VITE_API_URL` to your deployed backend URL before `npm run build`.

## Dataset Format

Create a UTF-8 CSV file with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `Sleep` | number | Average sleep hours per night |
| `Meetings` | number | Calls or meetings per day |
| `Weekends` | YES/NO | Whether the developer works on weekends |
| `Stress` | number | Subjective stress level (1ÔÇô10) |
| `Target` | text | Burnout class label |

### Allowed `Target` values

- `healthy`
- `risk of burnout`
- `vacation required`
- `critical condition`

### Example CSV rows

```csv
Sleep,Meetings,Weekends,Stress,Target
8,2,NO,3,healthy
7,3,NO,4,healthy
6,6,YES,7,risk of burnout
5,8,YES,9,vacation required
4,9,YES,10,critical condition
```

Upload your CSV via the dashboard **Train Model** section or `POST /train`. If no file is uploaded, the API uses a small built-in fallback dataset for demonstration only.

See [backend/app/sample_data_schema.md](backend/app/sample_data_schema.md) for the schema reference.

## Algorithm: CART Decision Tree with Gini Impurity

### What is CART?

**CART** (Classification and Regression Trees) builds a binary tree by recursively choosing the split that best separates classes. Each internal node asks a yes/no question; each leaf predicts the majority class among training samples that reach that node.

### Gini impurity

For a node with class counts \(n_1, n_2, \ldots, n_k\) and total \(N\):

\[
Gini = 1 - \sum_{i=1}^{k} \left(\frac{n_i}{N}\right)^2
\]

A split is scored by the **weighted average Gini** of its left and right child nodes. The algorithm picks the split with the lowest weighted impurity that still reduces parent impurity.

### Why CART was chosen

- **Interpretable**: Each prediction comes with an explicit decision path.
- **Inspectable**: Numerical thresholds (`Stress <= 6.5`) and categorical checks (`Weekends == YES`) map directly to the dashboard graph.
- **Educational fit**: CART with Gini impurity is straightforward to implement manually without ML libraries.
- **Mixed feature types**: Supports numeric threshold search and binary categorical splits in one framework.

### Stopping rules

Recursion stops when any of the following is true:

1. **Pure node** ÔÇö all samples share one class
2. **`max_depth`** reached (default: 8)
3. **`min_samples_split`** not met (default: 2)
4. **No useful split** ÔÇö no candidate reduces Gini impurity

### Node statistics stored in JSON

Every node includes:

- sample count
- class distribution
- predicted (majority) class
- Gini value

## API Documentation

### `GET /health`

Returns backend status.

**Response**

```json
{ "status": "ok" }
```

### `POST /train`

Trains the decision tree from an uploaded CSV (`multipart/form-data`, field name `file`) or from the built-in fallback dataset when no file is provided.

**Response**

```json
{
  "message": "Model trained successfully from uploaded CSV.",
  "rows": 25,
  "features": ["Sleep", "Meetings", "Weekends", "Stress"],
  "target_classes": ["critical condition", "healthy", "risk of burnout", "vacation required"],
  "tree": { "...": "full tree JSON" }
}
```

**Errors (400)**

- Missing/invalid CSV columns
- Empty dataset
- Invalid `Weekends` value
- Unsupported `Target` value
- Non-numeric feature values

### `POST /predict`

**Request**

```json
{
  "Sleep": 5,
  "Meetings": 8,
  "Weekends": "YES",
  "Stress": 9
}
```

**Response**

```json
{
  "prediction": "vacation required",
  "path": [
    "Stress <= 7.5",
    "Sleep <= 5.5",
    "leaf: vacation required"
  ]
}
```

**Errors (400)**

- Model not trained yet
- Invalid `Weekends` value

### `GET /tree`

Returns the latest trained tree JSON.

**Errors (400)**

- Model not trained yet

## Frontend Features

- **Train Model** panel with CSV upload or fallback training
- **Developer Profile** form with sliders/inputs for Sleep, Meetings, Stress (1ÔÇô10), and Weekends (YES/NO radio buttons)
- **Predict** button with instant burnout level result
- **Decision path** list showing each split taken through the tree
- **Interactive decision tree** (React Flow):
  - Internal nodes display split conditions
  - Leaf nodes display predicted classes with severity colors
  - Hover tooltips show sample count, class distribution, Gini, and predicted class
  - Pan/zoom controls and minimap for readability

## Assignment Requirement Checklist

| Requirement | Implementation |
|-------------|----------------|
| Python + FastAPI backend | `backend/app/main.py`, `requirements.txt` |
| TypeScript + React + Vite frontend | `frontend/` |
| No TailwindCSS | Plain CSS in `frontend/src/styles.css` |
| No ML libraries | Manual tree in `backend/app/decision_tree.py` |
| Manual CART + Gini impurity | `gini_impurity`, weighted split scoring, recursive `_build_tree` |
| Numerical threshold search | Midpoints between sorted unique values |
| Categorical/binary splits | `Weekends == YES/NO` evaluation |
| Stopping rules | Pure node, max depth, min samples, no useful split |
| Node statistics in JSON | samples, class_distribution, predicted_class, gini |
| CSV upload + user-created data | `POST /train` + `dataset_loader.py`; fallback only if no upload |
| `GET /health` | Implemented |
| `POST /train` | Implemented |
| `POST /predict` with path | Implemented |
| `GET /tree` | Implemented |
| Dashboard inputs (Sleep, Meetings, Weekends, Stress) | `BurnoutForm.tsx` |
| Prediction + decision path UI | `PredictionResult.tsx` |
| Interactive tree graph | `TreeVisualizer.tsx` |
| Leaf severity styling | CSS classes per burnout level |
| Hover node statistics | Tooltip on tree nodes |
| CORS for local dev | FastAPI `CORSMiddleware` |
| Error handling | CSV, Weekends, empty data, untrained model, invalid targets |
| Deployment-ready structure | Separate backend/frontend, env-based API URL, proxy in Vite |
| README + AI transparency | This document |

## Deployment Notes (future)

- **Backend (Render)**: run `uvicorn app.main:app --host 0.0.0.0 --port $PORT` from `backend/`
- **Frontend (Vercel)**: set `VITE_API_URL` to the Render backend URL and build `frontend/`
- Update CORS `allow_origins` in `main.py` with production frontend URLs

## AI Collaboration Transparency

AI tools (including Cursor / Claude) were used during development for:

- generating the initial full-stack boilerplate
- structuring the FastAPI routes
- helping design the manual CART recursion
- explaining and documenting the Gini calculation
- improving frontend component structure
- styling the dashboard and graph using plain CSS
- debugging edge cases in tree traversal and prediction path generation

**Important:** No ready-made machine learning libraries (scikit-learn, TensorFlow, PyTorch, XGBoost, LightGBM, etc.) were used. The decision tree classifier is implemented manually in Python.

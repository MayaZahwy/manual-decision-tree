import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.dataset_loader import (
    ALLOWED_WEEKENDS,
    FEATURE_COLUMNS,
    DatasetError,
    get_fallback_dataset,
    parse_csv_content,
)
from app.decision_tree import DecisionTreeClassifier
from app.models import HealthResponse, PredictRequest, PredictResponse, TrainResponse

app = FastAPI(
    title="Developer Burnout Analysis API",
    description="Decision tree based burnout prediction without ML libraries",
    version="1.0.0",
)

_DEFAULT_CORS = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_CORS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = DecisionTreeClassifier(max_depth=8, min_samples_split=2)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/train", response_model=TrainResponse)
async def train(file: UploadFile | None = File(default=None)) -> TrainResponse:
    try:
        if file is not None and file.filename:
            raw = (await file.read()).decode("utf-8-sig")
            rows = parse_csv_content(raw)
            source = "uploaded CSV"
        else:
            rows = get_fallback_dataset()
            source = "built-in fallback dataset"
    except DatasetError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.") from exc

    classifier.fit(rows, FEATURE_COLUMNS)
    tree_json = classifier.to_json()
    target_classes = sorted({str(row["Target"]) for row in rows})

    return TrainResponse(
        message=f"Model trained successfully from {source}.",
        rows=len(rows),
        features=FEATURE_COLUMNS,
        target_classes=target_classes,
        tree=tree_json,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    if classifier.root is None:
        raise HTTPException(
            status_code=400,
            detail="Model has not been trained yet. Call POST /train first.",
        )

    weekends = payload.Weekends.strip().upper()
    if weekends not in ALLOWED_WEEKENDS:
        raise HTTPException(
            status_code=400,
            detail="Weekends must be YES or NO.",
        )

    sample = {
        "Sleep": payload.Sleep,
        "Meetings": payload.Meetings,
        "Weekends": weekends,
        "Stress": payload.Stress,
    }

    try:
        prediction, path = classifier.predict_one(sample)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return PredictResponse(prediction=prediction, path=path)


@app.get("/tree")
def get_tree() -> dict:
    if classifier.root is None:
        raise HTTPException(
            status_code=400,
            detail="Model has not been trained yet. Call POST /train first.",
        )
    return classifier.to_json()

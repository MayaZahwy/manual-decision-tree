from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.dataset_loader import (
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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

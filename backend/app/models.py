from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class PredictRequest(BaseModel):
    Sleep: float = Field(..., ge=0, le=24, description="Average sleep hours per night")
    Meetings: float = Field(..., ge=0, description="Meetings or calls per day")
    Weekends: str = Field(..., description="Whether the developer works on weekends (YES/NO)")
    Stress: float = Field(..., ge=1, le=10, description="Subjective stress level 1-10")


class PredictResponse(BaseModel):
    prediction: str
    path: list[str]


class TrainResponse(BaseModel):
    message: str
    rows: int
    features: list[str]
    target_classes: list[str]
    tree: dict

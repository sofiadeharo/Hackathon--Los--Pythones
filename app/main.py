from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, validator
import math


# -----------------------------
# Data models
# -----------------------------


class Weights(BaseModel):
    crew: float = 1.0
    load: float = 1.0

    @validator("crew", "load")
    def validate_weights_positive(cls, value: float) -> float:
        if value < 0:
            raise ValueError("Weights must be non-negative")
        return value


class OptimalScheduleRequest(BaseModel):
    crew_availability: List[float] = Field(
        ..., min_items=24, max_items=24, description="24-length list of crew counts or availability scores"
    )
    network_load: List[float] = Field(
        ..., min_items=24, max_items=24, description="24-length list of network load values"
    )
    patch_duration_hours: float = Field(
        ..., gt=0, le=24, description="Duration of patch in hours (0 < d ≤ 24)"
    )
    weights: Weights = Field(default_factory=Weights)
    crew_required: Optional[float] = Field(
        default=None, description="If set, only windows where each covered hour meets this crew threshold are considered"
    )
    normalize: bool = Field(
        default=True,
        description=(
            "If true, normalize crew and load series to [0,1] by dividing by their respective max (>0)."
            " Helps balance magnitudes when units differ."
        ),
    )

    @validator("crew_availability", "network_load")
    def validate_non_negative(cls, values: List[float]) -> List[float]:
        for v in values:
            if v < 0:
                raise ValueError("Series values must be non-negative")
        return values


class HourContribution(BaseModel):
    hour: int
    weight: float
    crew: float
    load: float
    crew_norm: float
    load_norm: float
    crew_contribution: float
    load_contribution: float


class OptimalScheduleResponse(BaseModel):
    best_start_hour: int
    score: float
    contributions: List[HourContribution]


# -----------------------------
# Core algorithm
# -----------------------------


def _weighted_hour_segments(start_hour: int, duration_hours: float) -> List[Tuple[int, float]]:
    """
    Split a window starting at `start_hour` with length `duration_hours` into hour-sized segments with weights
    (proportional to fractional overlap). Returns a list of (hour, weight) pairs.
    """
    remaining = duration_hours
    k = 0
    segments: List[Tuple[int, float]] = []
    eps = 1e-9
    while remaining > eps:
        segment = 1.0 if remaining >= 1.0 else remaining
        hour = int((start_hour + k) % 24)
        segments.append((hour, segment))
        remaining -= segment
        k += 1
    return segments


def _normalize_series(series: List[float]) -> List[float]:
    series_max = max(series) if series else 0.0
    if series_max <= 0:
        # All zeros: return the original to avoid division by zero; contributions will be zero anyway
        return series
    return [v / series_max for v in series]


def score_start_hour(
    start_hour: int,
    duration_hours: float,
    crew: List[float],
    load: List[float],
    weights: Weights,
    crew_required: Optional[float],
    normalize: bool,
) -> Tuple[float, List[HourContribution]]:
    segments = _weighted_hour_segments(start_hour, duration_hours)

    # If there is a crew requirement, ensure every covered hour meets it (using the raw crew values)
    if crew_required is not None:
        for hour, _w in segments:
            if crew[hour] < crew_required:
                return float("-inf"), []  # Disqualify this start hour

    crew_series = _normalize_series(crew) if normalize else crew
    load_series = _normalize_series(load) if normalize else load

    contributions: List[HourContribution] = []
    total_score = 0.0

    for hour, weight in segments:
        crew_value = crew[hour]
        load_value = load[hour]
        crew_norm = crew_series[hour]
        load_norm = load_series[hour]

        crew_contribution = weights.crew * crew_norm * weight
        load_contribution = -weights.load * load_norm * weight
        total_score += crew_contribution + load_contribution

        contributions.append(
            HourContribution(
                hour=hour,
                weight=weight,
                crew=crew_value,
                load=load_value,
                crew_norm=crew_norm,
                load_norm=load_norm,
                crew_contribution=crew_contribution,
                load_contribution=load_contribution,
            )
        )

    return total_score, contributions


def find_optimal_start(
    request: OptimalScheduleRequest,
) -> Tuple[int, float, List[HourContribution]]:
    best_hour = 0
    best_score = float("-inf")
    best_contribs: List[HourContribution] = []

    for hour in range(24):
        score, contribs = score_start_hour(
            start_hour=hour,
            duration_hours=request.patch_duration_hours,
            crew=request.crew_availability,
            load=request.network_load,
            weights=request.weights,
            crew_required=request.crew_required,
            normalize=request.normalize,
        )
        if score > best_score:
            best_hour = hour
            best_score = score
            best_contribs = contribs

    if best_score == float("-inf"):
        raise HTTPException(
            status_code=422,
            detail=(
                "No feasible start hour satisfies the crew requirement for the full patch window."
            ),
        )

    return best_hour, best_score, best_contribs


# -----------------------------
# FastAPI app
# -----------------------------


app = FastAPI(title="Optimal Scheduling Service", version="0.1.0")

# Allow local dev UIs to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/optimal-schedule", response_model=OptimalScheduleResponse)
async def optimal_schedule(request: OptimalScheduleRequest) -> OptimalScheduleResponse:
    best_hour, score, contribs = find_optimal_start(request)
    return OptimalScheduleResponse(best_start_hour=best_hour, score=score, contributions=contribs)


@app.get("/api/sample")
async def sample() -> Dict[str, object]:
    """Provide a minimal sample payload for convenience in testing."""
    crew = [8, 8, 7, 6, 6, 5, 5, 6, 7, 8, 10, 12, 12, 12, 11, 10, 9, 9, 9, 10, 10, 9, 9, 8]
    load = [8, 7, 6, 5, 5, 5, 6, 7, 8, 10, 12, 14, 14, 13, 12, 11, 10, 9, 8, 7, 6, 6, 7, 8]
    return {
        "crew_availability": crew,
        "network_load": load,
        "patch_duration_hours": 2.5,
        "weights": {"crew": 1.0, "load": 1.0},
        "crew_required": 6,
        "normalize": True,
    }


# Serve static frontend
_static_dir = Path(__file__).parent / "static"
_static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(_static_dir), html=True), name="frontend")

# Optimal Scheduling Web App

A small FastAPI-based web app that recommends the best start hour to schedule a system patch, using:

- Crew availability per hour (higher is better)
- Network load per hour (lower is better)
- Patch duration in hours (supports fractional hours)

The app evaluates all start hours in a 24-hour day and returns the hour that maximizes a weighted score of high crew availability and low network load. It also supports an optional minimum crew requirement for every hour covered by the patch window.

### Features
- Fractional patch windows (e.g., 2.5 hours) with correct partial-hour weighting
- Independent weights for crew vs. network load
- Optional per-hour crew requirement constraint
- Normalization toggle to balance differing input scales
- Simple web UI and documented API

## Getting started

### Prerequisites
- Python 3.9+

### Install
```bash
pip install -r requirements.txt
```

### Run the server (development)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the UI at `http://localhost:8000/`.

## Usage

### Web UI
1. Click "Fill sample" for example data
2. Adjust crew/network series (24 numbers each), duration, weights, and optional crew requirement
3. Click "Compute optimal hour" to see the recommended start hour and per-hour contributions

### API

#### Health
```http
GET /api/health
```
Response:
```json
{ "status": "ok" }
```

#### Sample payload
```http
GET /api/sample
```
Returns a ready-to-use example JSON payload.

#### Compute optimal schedule
```http
POST /api/optimal-schedule
Content-Type: application/json
```
Body fields:
- `crew_availability` (number[24]): Crew scores or counts per hour (≥ 0)
- `network_load` (number[24]): Network load per hour (≥ 0)
- `patch_duration_hours` (number): > 0 and ≤ 24; fractional supported
- `weights` (object): `{ crew: number ≥ 0, load: number ≥ 0 }`
- `crew_required` (number | null): If set, disqualify windows where any covered hour has crew below this value
- `normalize` (boolean): Normalize the two series to [0,1] before scoring

Example request:
```json
{
  "crew_availability": [8,8,7,6,6,5,5,6,7,8,10,12,12,12,11,10,9,9,9,10,10,9,9,8],
  "network_load": [8,7,6,5,5,5,6,7,8,10,12,14,14,13,12,11,10,9,8,7,6,6,7,8],
  "patch_duration_hours": 2.5,
  "weights": {"crew": 1.0, "load": 1.0},
  "crew_required": 6,
  "normalize": true
}
```

Response:
```json
{
  "best_start_hour": 10,
  "score": 0.123,
  "contributions": [
    {
      "hour": 10,
      "weight": 1.0,
      "crew": 10,
      "load": 12,
      "crew_norm": 0.83,
      "load_norm": 0.86,
      "crew_contribution": 0.83,
      "load_contribution": -0.86
    }
    // ... additional rows for each covered hour
  ]
}
```

### Scoring model
For a given start hour `h` and duration `d` hours, the window is split into whole hours with a final fractional hour when applicable. For each covered hour `i` with weight `w_i` (the fractional overlap):

- Contribution from crew: `weights.crew * crew_norm[i] * w_i`
- Contribution from load: `-weights.load * load_norm[i] * w_i`

The total score is the sum of contributions. The `normalize` flag divides each series by its own max value to scale to [0, 1]. If `crew_required` is set, only start hours where every covered hour meets the raw crew threshold are considered.

## Project structure
```
app/
  main.py          # FastAPI app and scheduling logic
  static/
    index.html     # Minimal UI client
requirements.txt   # Python dependencies
BackENd/tun.py     # Legacy demo script (unused by the app)
```

## Notes
- CORS is open for simplicity in local development
- The UI fetches from the same origin; deploy behind a reverse proxy if needed
- Extend the algorithm by adding more signals or alternative scoring in `app/main.py`

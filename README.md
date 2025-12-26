# Multimodal AI System for Suspect Identification with Deepfake Verification

> ⚠️ **Educational Project Disclaimer**: This project is strictly for educational and research purposes. It must NOT be used for real-world surveillance, law enforcement, or any form of actual suspect identification.

## Overview

A modular AI system combining multiple AI technologies to demonstrate identity analysis workflows:
- 🎤 **Speech-to-Text**: Convert witness audio descriptions to text
- 🧠 **NLP Processing**: Extract facial attributes from text
- 🎨 **Face Sketch Generation**: AI-generated portraits from descriptions
- 🔍 **Deepfake Detection**: Verify image authenticity
- 👤 **Face Matching**: Similarity search using embeddings

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                           │
├─────────────────────────────────────────────────────────────────┤
│  Audio Upload  │  Image Upload  │  Text Input  │  Results View  │
└───────┬────────┴───────┬────────┴──────┬───────┴───────┬────────┘
        │                │               │               │
        ▼                ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                            │
├─────────────────────────────────────────────────────────────────┤
│ Whisper ASR │ spaCy NLP │ Stable Diffusion │ EfficientNet │ FAISS│
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.10+, FastAPI |
| Speech-to-Text | OpenAI Whisper (base) |
| NLP | spaCy |
| Face Generation | Stable Diffusion v1.5 |
| Deepfake Detection | EfficientNet-B0 |
| Face Embeddings | InsightFace (ArcFace) |
| Vector Database | FAISS |
| Frontend | React 18 |

## Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Download sample dataset
python scripts/download_dataset.py

# Start server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/speech-to-text` | POST | Transcribe audio file |
| `/api/v1/process-description` | POST | Extract attributes from text |
| `/api/v1/generate-sketch` | POST | Generate face from description |
| `/api/v1/deepfake/verify` | POST | Detect image manipulation |
| `/api/v1/match-faces` | POST | Find similar faces |
| `/api/v1/analyze` | POST | Full pipeline analysis |

## Project Structure

```
deepfake/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Configuration
│   │   ├── models/           # Pydantic schemas
│   │   ├── routers/          # API routes
│   │   └── services/         # AI services
│   ├── data/                 # Datasets & embeddings
│   ├── scripts/              # Utility scripts
│   └── tests/                # Unit tests
├── frontend/
│   └── src/
│       ├── components/       # React components
│       └── pages/            # Page views
└── docs/                     # Documentation
```

## Ethical Considerations

⚠️ **This system is designed with ethical AI principles:**

1. **No Real Criminal Data**: Uses only synthetic/public datasets (LFW)
2. **Bias Awareness**: AI systems have known biases that can affect results
3. **No Demographic Predictions**: Does not predict race, ethnicity, or religion
4. **Educational Only**: Not intended for real-world law enforcement
5. **Transparency**: All AI decisions include confidence scores and explanations

See [ETHICS.md](docs/ETHICS.md) for detailed ethical guidelines.

## AI Models Used

- **Whisper Base** (74M params): Efficient speech recognition
- **spaCy en_core_web_sm**: Lightweight NLP model
- **Stable Diffusion v1.5**: Text-to-image generation
- **EfficientNet-B0**: Deepfake detection classifier
- **InsightFace/ArcFace**: Face embedding generation
- **FAISS**: Fast similarity search

## Sample Usage

### 1. Audio Description Analysis

```python
import requests

# Upload audio file
with open("witness_description.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/speech-to-text",
        files={"file": f}
    )
print(response.json())
```

### 2. Generate Face Sketch

```python
response = requests.post(
    "http://localhost:8000/api/v1/generate-sketch",
    json={
        "description": "Male, around 30 years old, short black hair, clean shaven, oval face"
    }
)
# Returns base64 encoded image
```

### 3. Deepfake Detection

```python
with open("suspect_photo.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/deepfake/verify",
        files={"file": f}
    )
print(response.json())
# {"is_real": true, "confidence": 0.95, "verdict": "Real Image"}
```

## Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## License

This project is for educational purposes only. See LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for speech recognition
- Stability AI for Stable Diffusion
- InsightFace for face recognition
- University of Massachusetts for LFW dataset

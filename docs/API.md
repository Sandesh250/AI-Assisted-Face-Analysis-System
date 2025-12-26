# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

This educational system does not require authentication.

---

## Endpoints

### Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "device": "cuda",
  "disclaimer": "This system is for EDUCATIONAL purposes only"
}
```

---

### Speech-to-Text

```http
POST /api/v1/speech-to-text
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| file | File | Audio file (WAV, MP3, M4A, FLAC, OGG) |

**Response:**
```json
{
  "text": "The suspect was a male, around 30 years old with short black hair",
  "language": "en",
  "duration_seconds": 5.2,
  "confidence": 1.0
}
```

---

### NLP Processing

```http
POST /api/v1/process-description
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Male, around 30 years old, short black hair, clean shaven, oval face"
}
```

**Response:**
```json
{
  "attributes": {
    "age_range": "27-33",
    "gender": "male",
    "hair_color": "black",
    "hair_style": "short",
    "facial_hair": "clean shaven",
    "face_shape": "oval",
    "glasses": null,
    "distinctive_features": [],
    "raw_description": "male, around 30 years old, short black hair..."
  },
  "entities": [],
  "keywords": ["male", "hair", "black", "shaven", "oval", "face"]
}
```

---

### Face Sketch Generation

```http
POST /api/v1/generate-sketch
Content-Type: application/json
```

**Request Body:**
```json
{
  "description": "Male, around 30 years old with short black hair",
  "style": "portrait"
}
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| description | string | required | Text description of the face |
| style | string | "portrait" | Style: portrait, sketch, realistic |

**Response:**
```json
{
  "image_base64": "iVBORw0KGgo...",
  "prompt_used": "professional portrait photograph of a male aged 27-33...",
  "generation_time_seconds": 3.45
}
```

---

### Deepfake Detection

```http
POST /api/v1/deepfake/verify
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| file | File | Image file (JPG, PNG, WebP) |

**Response:**
```json
{
  "is_real": true,
  "confidence": 0.9234,
  "verdict": "High confidence: Image appears authentic",
  "details": {
    "real_probability": 0.9234,
    "fake_probability": 0.0766,
    "frequency_analysis": {
      "low_freq_energy": 12345.67,
      "suspicious_frequency": false
    },
    "processing_time_seconds": 0.234,
    "model_used": "EfficientNet-B0",
    "threshold": 0.5
  },
  "disclaimer": "AI detection is not 100% accurate..."
}
```

---

### Face Matching

```http
POST /api/v1/match-faces
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| file | File | required | Image file with face |
| top_k | int | 5 | Number of top matches (1-20) |

**Response:**
```json
{
  "matches": [
    {
      "id": "face_0001",
      "name": "John Doe",
      "similarity_score": 0.8765,
      "image_path": "/data/sample_faces/john_doe.jpg",
      "similarity_percentage": 87.65
    }
  ],
  "query_embedding_generated": true,
  "total_database_faces": 100,
  "search_time_seconds": 0.045,
  "disclaimer": "Face matching provides AI suggestions only..."
}
```

---

### Full Analysis (Audio)

```http
POST /api/v1/analyze/audio
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| audio_file | File | required | Audio file with description |
| generate_sketch | bool | true | Generate face sketch |
| top_k | int | 5 | Number of face matches |

**Response:**
```json
{
  "transcription": { ... },
  "attributes": { ... },
  "generated_sketch": { ... },
  "deepfake_verification": null,
  "face_matches": { ... },
  "processing_time_seconds": 12.34,
  "disclaimer": "This system provides AI-assisted analysis..."
}
```

---

### Full Analysis (Image)

```http
POST /api/v1/analyze/image
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| image_file | File | required | Image file to analyze |
| top_k | int | 5 | Number of face matches |

---

### Database Statistics

```http
GET /api/v1/database-stats
```

**Response:**
```json
{
  "total_faces": 100,
  "embedding_dimension": 512,
  "index_type": "FAISS IndexFlatIP",
  "similarity_metric": "Cosine Similarity",
  "disclaimer": "Database contains only synthetic/public dataset faces..."
}
```

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error (processing failed)

---

## Rate Limits

This educational system does not enforce rate limits.

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

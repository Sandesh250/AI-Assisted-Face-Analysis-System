"""
Unit tests for API endpoints.
Uses FastAPI TestClient for HTTP testing.
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


client = TestClient(app)


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self):
        """Test health endpoint returns success."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "disclaimer" in data
    
    def test_root_endpoint(self):
        """Test root endpoint returns info."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "docs" in data


class TestNLPEndpoints:
    """Tests for NLP processing endpoints."""
    
    def test_process_description_success(self):
        """Test successful description processing."""
        response = client.post(
            "/api/v1/process-description",
            json={"text": "Male, 30 years old, short black hair, beard"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "attributes" in data
        assert data["attributes"]["gender"] == "male"
        assert data["attributes"]["hair_color"] == "black"
    
    def test_process_description_empty(self):
        """Test empty description returns error."""
        response = client.post(
            "/api/v1/process-description",
            json={"text": "hi"}
        )
        assert response.status_code == 400
    
    def test_extract_attributes_alias(self):
        """Test extract-attributes endpoint alias."""
        response = client.post(
            "/api/v1/extract-attributes",
            json={"text": "Female with long blonde hair"}
        )
        assert response.status_code == 200


class TestDeepfakeEndpoints:
    """Tests for deepfake detection endpoints."""
    
    def test_deepfake_info(self):
        """Test deepfake info endpoint."""
        response = client.get("/api/v1/deepfake/info")
        assert response.status_code == 200
        
        data = response.json()
        assert "model" in data
        assert "threshold" in data
        assert "limitations" in data


class TestFaceMatchingEndpoints:
    """Tests for face matching endpoints."""
    
    def test_database_stats(self):
        """Test database stats endpoint."""
        response = client.get("/api/v1/database-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_faces" in data
        assert "embedding_dimension" in data
    
    def test_similarity_explained(self):
        """Test similarity explanation endpoint."""
        response = client.get("/api/v1/similarity-explained")
        assert response.status_code == 200
        
        data = response.json()
        assert "title" in data
        assert "steps" in data
        assert "formula" in data


class TestAnalysisEndpoints:
    """Tests for analysis pipeline endpoints."""
    
    def test_analysis_status(self):
        """Test analysis status endpoint."""
        response = client.get("/api/v1/analyze/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "speech_to_text" in data
        assert "face_generator" in data
        assert "deepfake_detector" in data


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_json(self):
        """Test invalid JSON returns error."""
        response = client.post(
            "/api/v1/process-description",
            content="not json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_field(self):
        """Test missing field returns error."""
        response = client.post(
            "/api/v1/process-description",
            json={}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Unit tests for the NLP Processor service.
Tests attribute extraction from text descriptions.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.nlp_processor import NLPProcessorService, nlp_service


class TestNLPProcessor:
    """Tests for NLP processing functionality."""
    
    def test_clean_text(self):
        """Test text cleaning and normalization."""
        text = "  This is   a TEST!!! with extra   spaces  "
        cleaned = nlp_service.clean_text(text)
        assert cleaned == "this is a test with extra spaces"
    
    def test_extract_gender_male(self):
        """Test male gender extraction."""
        texts = [
            "The man was tall",
            "He had blue eyes",
            "A male suspect",
            "The gentleman wore a hat"
        ]
        for text in texts:
            result = nlp_service.extract_gender(text)
            assert result == "male", f"Failed for: {text}"
    
    def test_extract_gender_female(self):
        """Test female gender extraction."""
        texts = [
            "The woman was tall",
            "She had blue eyes",
            "A female suspect",
            "The lady wore a hat"
        ]
        for text in texts:
            result = nlp_service.extract_gender(text)
            assert result == "female", f"Failed for: {text}"
    
    def test_extract_age_specific(self):
        """Test specific age extraction."""
        text = "The person was 35 years old"
        result = nlp_service.extract_age(text)
        assert result == "32-38"  # 35 +/- 3
    
    def test_extract_age_range(self):
        """Test age range extraction."""
        text = "Person aged 25 to 30"
        result = nlp_service.extract_age(text)
        assert result == "25-30"
    
    def test_extract_age_approximate(self):
        """Test approximate age extraction."""
        text = "Around 40 years old"
        result = nlp_service.extract_age(text)
        assert result == "35-45"  # 40 +/- 5
    
    def test_extract_age_descriptor(self):
        """Test age descriptor extraction."""
        test_cases = [
            ("young person", "20-35"),
            ("middle-aged man", "40-55"),
            ("elderly woman", "65-80"),
        ]
        for text, expected in test_cases:
            result = nlp_service.extract_age(text)
            assert result == expected, f"Failed for: {text}"
    
    def test_extract_hair_color(self):
        """Test hair color extraction."""
        test_cases = [
            ("black hair", "black"),
            ("had brown hair", "brown"),
            ("blonde haired woman", "blonde"),
            ("hair was gray", "gray"),
        ]
        for text, expected in test_cases:
            result = nlp_service.extract_hair_color(text)
            assert result == expected, f"Failed for: {text}"
    
    def test_extract_hair_style(self):
        """Test hair style extraction."""
        test_cases = [
            ("short hair", "short"),
            ("was bald", "bald"),
            ("curly black hair", "curly"),
            ("long straight hair", "long"),
        ]
        for text, expected in test_cases:
            result = nlp_service.extract_hair_style(text)
            assert result == expected, f"Failed for: {text}"
    
    def test_extract_facial_hair(self):
        """Test facial hair extraction."""
        test_cases = [
            ("had a beard", "beard"),
            ("with mustache", "mustache"),
            ("clean shaven", "clean shaven"),
            ("stubble on face", "stubble"),
        ]
        for text, expected in test_cases:
            result = nlp_service.extract_facial_hair(text)
            assert result == expected, f"Failed for: {text}"
    
    def test_extract_face_shape(self):
        """Test face shape extraction."""
        test_cases = [
            ("oval face", "oval"),
            ("round faced", "round"),
            ("square face shape", "square"),
        ]
        for text, expected in test_cases:
            result = nlp_service.extract_face_shape(text)
            assert result == expected, f"Failed for: {text}"
    
    def test_extract_glasses(self):
        """Test glasses detection."""
        assert nlp_service.extract_glasses("wearing glasses") == True
        assert nlp_service.extract_glasses("had spectacles") == True
        assert nlp_service.extract_glasses("no glasses") == False
        assert nlp_service.extract_glasses("doesn't wear glasses") == False
        assert nlp_service.extract_glasses("blue eyes") is None
    
    def test_extract_distinctive_features(self):
        """Test distinctive features extraction."""
        text = "had a scar on the left cheek and a mole near the eye"
        features = nlp_service.extract_distinctive_features(text)
        assert "scar" in features
        assert "mole" in features
    
    def test_full_processing(self):
        """Test complete description processing."""
        description = """
        The suspect was a male, approximately 35 years old. 
        He had short black hair and a full beard. 
        His face was oval shaped and he was wearing glasses.
        There was a noticeable scar on his left cheek.
        """
        
        attributes, entities, keywords = nlp_service.process_description(description)
        
        assert attributes.gender == "male"
        assert attributes.hair_color == "black"
        assert attributes.hair_style == "short"
        assert attributes.facial_hair == "beard"
        assert attributes.face_shape == "oval"
        assert attributes.glasses == True
        assert "scar" in attributes.distinctive_features
        assert len(keywords) > 0
    
    def test_empty_description(self):
        """Test handling of minimal description."""
        description = "A person"
        attributes, _, _ = nlp_service.process_description(description)
        
        # Should not crash, but may have None values
        assert attributes.raw_description is not None


class TestNLPServiceSingleton:
    """Test singleton pattern for NLP service."""
    
    def test_singleton(self):
        """Test that service uses singleton pattern."""
        service1 = NLPProcessorService()
        service2 = NLPProcessorService()
        assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

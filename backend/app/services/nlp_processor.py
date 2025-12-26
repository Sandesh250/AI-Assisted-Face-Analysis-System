"""
NLP Processing Service for extracting facial attributes from text.
Uses spaCy for NER and custom rules for attribute extraction.
"""
import re
from typing import List, Dict, Optional, Tuple
import spacy
from loguru import logger

from app.models.schemas import FacialAttributes


class NLPProcessorService:
    """Service for processing text descriptions and extracting facial attributes."""
    
    _instance = None
    _nlp = None
    
    # Attribute patterns for extraction
    AGE_PATTERNS = [
        (r'(\d{1,2})\s*(?:to|-)\s*(\d{1,2})\s*(?:years?\s*old)?', lambda m: f"{m.group(1)}-{m.group(2)}"),
        (r'(?:around|about|approximately)\s*(\d{1,2})\s*(?:years?\s*old)?', lambda m: f"{int(m.group(1))-5}-{int(m.group(1))+5}"),
        (r'(\d{1,2})\s*years?\s*old', lambda m: f"{int(m.group(1))-3}-{int(m.group(1))+3}"),
        (r'(?:early|late|mid)\s*(twenties|thirties|forties|fifties|sixties)', lambda m: _age_word_to_range(m.group(0))),
        (r'(young|middle[- ]aged|elderly|old|teenage|adolescent)', lambda m: _age_descriptor_to_range(m.group(1))),
    ]
    
    GENDER_KEYWORDS = {
        'male': ['male', 'man', 'boy', 'gentleman', 'guy', 'he', 'him', 'his'],
        'female': ['female', 'woman', 'girl', 'lady', 'she', 'her', 'hers']
    }
    
    HAIR_COLORS = ['black', 'brown', 'blonde', 'red', 'gray', 'grey', 'white', 'auburn', 'ginger', 'dark', 'light']
    HAIR_STYLES = ['short', 'long', 'bald', 'balding', 'curly', 'straight', 'wavy', 'braided', 'ponytail', 
                   'buzz cut', 'crew cut', 'mohawk', 'afro', 'dreadlocks', 'shaved', 'receding']
    
    FACIAL_HAIR_KEYWORDS = ['beard', 'mustache', 'moustache', 'goatee', 'stubble', 'clean[- ]shaven', 
                            'sideburns', 'clean shaven', 'bearded', 'full beard', 'no facial hair']
    
    FACE_SHAPES = ['oval', 'round', 'square', 'rectangular', 'heart', 'triangular', 'diamond', 
                   'oblong', 'long', 'wide', 'narrow', 'chubby', 'thin', 'angular']
    
    DISTINCTIVE_FEATURES = ['scar', 'mole', 'birthmark', 'freckles', 'dimples', 'wrinkles', 
                            'tattoo', 'piercing', 'acne', 'blemish', 'beauty mark']
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the NLP processor."""
        if self._nlp is None:
            self._load_model()
    
    def _load_model(self) -> None:
        """Load spaCy model."""
        logger.info("Loading spaCy NLP model...")
        try:
            self._nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found, downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self._nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model downloaded and loaded")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize input text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\-.,]', '', text)
        return text.lower()
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text using spaCy."""
        doc = self._nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        doc = self._nlp(text)
        keywords = []
        for token in doc:
            if token.pos_ in ['NOUN', 'ADJ', 'PROPN'] and not token.is_stop:
                keywords.append(token.lemma_.lower())
        return list(set(keywords))
    
    def extract_age(self, text: str) -> Optional[str]:
        """Extract age or age range from text."""
        for pattern, formatter in self.AGE_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return formatter(match)
        return None
    
    def extract_gender(self, text: str) -> Optional[str]:
        """Extract gender from text."""
        text_lower = text.lower()
        for gender, keywords in self.GENDER_KEYWORDS.items():
            for keyword in keywords:
                if re.search(r'\b' + keyword + r'\b', text_lower):
                    return gender
        return None
    
    def extract_hair_color(self, text: str) -> Optional[str]:
        """Extract hair color from text."""
        for color in self.HAIR_COLORS:
            if re.search(r'\b' + color + r'\s*(?:hair|haired)\b', text, re.IGNORECASE):
                return color
            if re.search(r'\bhair\s*(?:is\s*)?' + color + r'\b', text, re.IGNORECASE):
                return color
        return None
    
    def extract_hair_style(self, text: str) -> Optional[str]:
        """Extract hair style from text."""
        for style in self.HAIR_STYLES:
            if re.search(r'\b' + style + r'\b', text, re.IGNORECASE):
                return style
        return None
    
    def extract_facial_hair(self, text: str) -> Optional[str]:
        """Extract facial hair description from text."""
        for keyword in self.FACIAL_HAIR_KEYWORDS:
            if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE):
                return keyword.replace('[- ]', ' ')
        return None
    
    def extract_face_shape(self, text: str) -> Optional[str]:
        """Extract face shape from text."""
        for shape in self.FACE_SHAPES:
            if re.search(r'\b' + shape + r'\s*(?:face|faced|shape)?\b', text, re.IGNORECASE):
                return shape
        return None
    
    def extract_glasses(self, text: str) -> Optional[bool]:
        """Check if person wears glasses."""
        if re.search(r'\b(?:glasses|spectacles|eyeglasses)\b', text, re.IGNORECASE):
            if re.search(r'\b(?:no|without|doesn\'t|does not)\s+(?:wear\s+)?(?:glasses|spectacles)\b', text, re.IGNORECASE):
                return False
            return True
        return None
    
    def extract_distinctive_features(self, text: str) -> List[str]:
        """Extract distinctive features from text."""
        features = []
        for feature in self.DISTINCTIVE_FEATURES:
            if re.search(r'\b' + feature + r'\b', text, re.IGNORECASE):
                features.append(feature)
        return features
    
    def process_description(self, text: str) -> Tuple[FacialAttributes, List[Dict], List[str]]:
        """
        Process a text description and extract all facial attributes.
        
        Args:
            text: Raw text description of a person
            
        Returns:
            Tuple of (FacialAttributes, entities, keywords)
        """
        cleaned_text = self.clean_text(text)
        logger.info(f"Processing description: {cleaned_text[:100]}...")
        
        # Extract all attributes
        attributes = FacialAttributes(
            age_range=self.extract_age(cleaned_text),
            gender=self.extract_gender(cleaned_text),
            hair_color=self.extract_hair_color(cleaned_text),
            hair_style=self.extract_hair_style(cleaned_text),
            facial_hair=self.extract_facial_hair(cleaned_text),
            face_shape=self.extract_face_shape(cleaned_text),
            glasses=self.extract_glasses(cleaned_text),
            distinctive_features=self.extract_distinctive_features(cleaned_text),
            raw_description=cleaned_text
        )
        
        entities = self.extract_entities(text)
        keywords = self.extract_keywords(text)
        
        logger.info(f"Extracted attributes: {attributes.model_dump(exclude_none=True)}")
        
        return attributes, entities, keywords


def _age_word_to_range(text: str) -> str:
    """Convert age words like 'early thirties' to ranges."""
    text_lower = text.lower()
    ranges = {
        'twenties': (20, 29),
        'thirties': (30, 39),
        'forties': (40, 49),
        'fifties': (50, 59),
        'sixties': (60, 69),
    }
    for word, (low, high) in ranges.items():
        if word in text_lower:
            if 'early' in text_lower:
                return f"{low}-{low+4}"
            elif 'late' in text_lower:
                return f"{high-4}-{high}"
            elif 'mid' in text_lower:
                return f"{low+3}-{high-3}"
            return f"{low}-{high}"
    return None


def _age_descriptor_to_range(descriptor: str) -> str:
    """Convert age descriptors to ranges."""
    mappings = {
        'teenage': '13-19',
        'adolescent': '13-19',
        'young': '20-35',
        'middle-aged': '40-55',
        'middle aged': '40-55',
        'elderly': '65-80',
        'old': '60-75',
    }
    return mappings.get(descriptor.lower().replace('-', ' ').replace('  ', ' '))


# Create singleton instance
nlp_service = NLPProcessorService()

"""
Gemini Vision Language Model (VLM) integration for advanced disaster image analysis.

Uses Google's Gemini Pro Vision to analyze disaster imagery and provide
detailed damage assessments with natural language explanations.
"""

import os
from typing import Dict, Optional
import base64
from PIL import Image
import io


class GeminiAnalyzer:
    """
    Gemini VLM analyzer for disaster image assessment.
    Provides detailed damage analysis using Google's multimodal AI.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini analyzer.
        
        Args:
            api_key: Google AI API key (or set GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini VLM initialized successfully")
            except ImportError:
                print("⚠️  google-generativeai not installed. Run: pip install google-generativeai")
                self.model = None
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
                self.model = None
        else:
            print("⚠️  No Gemini API key found. Set GEMINI_API_KEY environment variable.")
            print("   Get your free API key: https://makersuite.google.com/app/apikey")
    
    def analyze_disaster_image(self, image_path: str) -> Dict:
        """
        Analyze disaster image using Gemini VLM.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with damage assessment from Gemini
        """
        if not self.model:
            return {
                "available": False,
                "error": "Gemini not available - no API key or initialization failed"
            }
        
        try:
            # Load and prepare image
            image = Image.open(image_path)
            
            # Create detailed prompt for damage assessment
            prompt = """You are an expert disaster damage assessment AI. Analyze this image and provide:

1. **Damage Severity** (0-3 scale):
   - 0 = No damage visible
   - 1 = Minor damage (broken windows, minor debris, superficial damage)
   - 2 = Major damage (partial collapse, significant structural damage, heavy debris)
   - 3 = Severe destruction (complete collapse, total destruction, massive debris field)

2. **Confidence Level** (0.0-1.0): How confident are you in this assessment?

3. **Key Indicators**: List specific visual indicators you see (e.g., "collapsed buildings", "overturned vehicles", "debris scattered", "structural cracks")

4. **Description**: Brief description of the damage visible (1-2 sentences)

5. **Recommendations**: Immediate response priorities based on what you see

Respond in this EXACT format:
SEVERITY: [0-3]
CONFIDENCE: [0.0-1.0]
INDICATORS: [comma-separated list]
DESCRIPTION: [brief description]
RECOMMENDATIONS: [priorities]"""

            # Generate response
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def analyze_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Analyze disaster image from bytes.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with damage assessment from Gemini
        """
        if not self.model:
            return {
                "available": False,
                "error": "Gemini not available"
            }
        
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Same prompt as above
            prompt = """You are an expert disaster damage assessment AI. Analyze this image and provide:

1. **Damage Severity** (0-3 scale):
   - 0 = No damage visible
   - 1 = Minor damage (broken windows, minor debris, superficial damage)
   - 2 = Major damage (partial collapse, significant structural damage, heavy debris)
   - 3 = Severe destruction (complete collapse, total destruction, massive debris field)

2. **Confidence Level** (0.0-1.0): How confident are you in this assessment?

3. **Key Indicators**: List specific visual indicators you see

4. **Description**: Brief description of the damage visible (1-2 sentences)

Respond in this EXACT format:
SEVERITY: [0-3]
CONFIDENCE: [0.0-1.0]
INDICATORS: [comma-separated list]
DESCRIPTION: [brief description]
RECOMMENDATIONS: [priorities]"""

            response = self.model.generate_content([prompt, image])
            
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            print(f"❌ Gemini analysis failed: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse structured response from Gemini"""
        try:
            lines = response_text.strip().split('\n')
            result = {
                "available": True,
                "severity": 0,
                "confidence": 0.0,
                "indicators": [],
                "description": "",
                "recommendations": "",
                "raw_response": response_text
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('SEVERITY:'):
                    try:
                        result['severity'] = int(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('CONFIDENCE:'):
                    try:
                        result['confidence'] = float(line.split(':')[1].strip())
                    except:
                        pass
                elif line.startswith('INDICATORS:'):
                    indicators_str = ':'.join(line.split(':')[1:]).strip()
                    result['indicators'] = [i.strip() for i in indicators_str.split(',')]
                elif line.startswith('DESCRIPTION:'):
                    result['description'] = ':'.join(line.split(':')[1:]).strip()
                elif line.startswith('RECOMMENDATIONS:'):
                    result['recommendations'] = ':'.join(line.split(':')[1:]).strip()
            
            return result
            
        except Exception as e:
            print(f"⚠️  Error parsing Gemini response: {e}")
            return {
                "available": True,
                "severity": 0,
                "confidence": 0.0,
                "description": response_text,
                "raw_response": response_text
            }


# Singleton instance
_gemini_instance = None

def get_gemini_analyzer() -> GeminiAnalyzer:
    """Get singleton Gemini analyzer instance"""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiAnalyzer()
    return _gemini_instance

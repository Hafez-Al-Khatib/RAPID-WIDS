"""
Use Roboflow pre-trained disaster detection model.

Roboflow has many disaster detection models available.
Visit: https://universe.roboflow.com/search?q=disaster+damage
"""

# Example: Using Roboflow model
# pip install roboflow

from roboflow import Roboflow

def setup_roboflow_model():
    """
    Setup Roboflow disaster detection model
    
    Steps:
    1. Sign up at https://roboflow.com (free)
    2. Browse models at https://universe.roboflow.com
    3. Search for "disaster damage" or "building damage"
    4. Get your API key
    5. Use the model
    """
    
    # Get API key from Roboflow
    api_key = "YOUR_ROBOFLOW_API_KEY"  # Get from https://app.roboflow.com/settings/api
    
    rf = Roboflow(api_key=api_key)
    
    # Example project (search for your preferred one)
    project = rf.workspace("disaster-detection").project("building-damage")
    model = project.version(1).model
    
    # Use the model
    result = model.predict("image.jpg", confidence=40, overlap=30)
    
    return model

# For integration with your DamageDetector:
# You'll need to adapt the response format to match your schema

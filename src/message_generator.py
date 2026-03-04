"""
Message/Stimuli Generator
Generates advertising messages with specific linguistic attributes.
Messages vary on two dimensions: emotionality and abstraction/concreteness.
"""

import random
from typing import Dict, List, Tuple


class MessageGenerator:
    """Generates advertising stimuli messages with controlled dimensions."""
    
    # Emotionality dimension
    EMOTIONALITY = {
        "emotional": {
            "openings": [
                "Imagine the joy of",
                "Feel the excitement of",
                "Experience the delight of",
                "Discover the happiness that",
                "Embrace the wonderful feeling of"
            ],
            "connectors": ["You'll love how", "It's amazing because", "What makes it wonderful is", "The best part is"],
            "closings": [
                "Your life will be so much better!",
                "You'll be absolutely thrilled!",
                "It's an amazing experience you deserve!",
                "You'll fall in love with it!",
            ],
            "vocabulary": ["beautiful", "wonderful", "amazing", "incredible", "fantastic", "love", "adore"]
        },
        "rational": {
            "openings": [
                "Research shows that",
                "Studies demonstrate that",
                "Evidence indicates that",
                "Data proves that",
                "Analysis reveals that"
            ],
            "connectors": ["Notably,", "Significantly,", "Importantly,", "The facts show"],
            "closings": [
                "This represents a practical advantage.",
                "The benefits are measurable and clear.",
                "This solution provides tangible value.",
                "The results speak for themselves.",
            ],
            "vocabulary": ["effective", "efficient", "proven", "reliable", "superior", "advanced", "optimal"]
        }
    }
    
    # Abstraction/Concreteness dimension
    ABSTRACTION = {
        "concrete": {
            "details": [
                "saves you 3 hours daily",
                "costs just $29.99",
                "comes with a 10-year warranty",
                "has 500+ five-star reviews",
                "weighs only 2.5 pounds"
            ],
            "examples": [
                "like our bestselling Model X",
                "just like Sarah's experience",
                "for instance, the turbo edition",
                "for example, in Seattle last month",
                "think of it like a Swiss Army knife"
            ]
        },
        "abstract": {
            "benefits": [
                "enhances your quality of life",
                "promotes personal growth",
                "elevates your lifestyle",
                "empowers your potential",
                "embodies excellence"
            ],
            "concepts": [
                "represents innovation itself",
                "embodies modern thinking",
                "reflects contemporary values",
                "captures the essence of freedom",
                "symbolizes progress"
            ]
        }
    }
    
    # Advertising products/services (can be extended)
    PRODUCTS = {
        "smartwatch": ["fitness tracker", "health monitoring", "smart wearable", "activity tracker"],
        "coffee_maker": ["brewing caffeine", "morning ritual", "hot beverage", "espresso machine"],
        "headphones": ["audio experience", "sound quality", "wireless listening", "earbuds"],
        "fitness_app": ["workout tracking", "health management", "exercise guidance", "fitness coaching"],
        "cloud_storage": ["file backup", "data protection", "cloud services", "file sharing"]
    }
    
    def __init__(self):
        """Initialize the message generator."""
        self.generated_messages = []
    
    def generate_message(
        self,
        emotionality: str = "emotional",
        abstraction: str = "concrete",
        product: str = "smartwatch"
    ) -> Dict[str, str]:
        """
        Generate an advertising message with specified dimensions.
        
        Args:
            emotionality: "emotional" or "rational"
            abstraction: "concrete" or "abstract"
            product: Product category
            
        Returns:
            Dictionary with message and metadata
        """
        if emotionality not in self.EMOTIONALITY:
            raise ValueError(f"Emotionality must be one of {list(self.EMOTIONALITY.keys())}")
        if abstraction not in self.ABSTRACTION:
            raise ValueError(f"Abstraction must be one of {list(self.ABSTRACTION.keys())}")
        if product not in self.PRODUCTS:
            raise ValueError(f"Product must be one of {list(self.PRODUCTS.keys())}")
        
        emotion_config = self.EMOTIONALITY[emotionality]
        selected_product = random.choice(self.PRODUCTS[product])
        
        # Build message
        opening = f"{random.choice(emotion_config['openings'])} {selected_product}."
        
        # Add detail based on abstraction level
        if abstraction == "concrete":
            detail = f"It {random.choice(self.ABSTRACTION['concrete']['details'])}. {random.choice(self.ABSTRACTION['concrete']['examples'])}."
        else:
            detail = f"It {random.choice(self.ABSTRACTION['abstract']['benefits'])} and {random.choice(self.ABSTRACTION['abstract']['concepts'])}."
        
        connector = random.choice(emotion_config['connectors'])
        closing = random.choice(emotion_config['closings'])
        
        message = f"{opening} {connector} {detail} {closing}"
        
        metadata = {
            "message": message,
            "emotionality": emotionality,
            "abstraction": abstraction,
            "product": product,
            "selected_product": selected_product
        }
        
        self.generated_messages.append(metadata)
        return metadata
    
    def generate_pair(
        self,
        emotionality1: str = "emotional",
        emotionality2: str = "rational",
        abstraction1: str = "concrete",
        abstraction2: str = "abstract",
        product: str = "smartwatch"
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Generate a pair of messages with different dimensions.
        
        Args:
            emotionality1: Emotionality for first message
            emotionality2: Emotionality for second message
            abstraction1: Abstraction level for first message
            abstraction2: Abstraction level for second message
            product: Product category for both messages
            
        Returns:
            Tuple of two message dictionaries
        """
        msg1 = self.generate_message(emotionality=emotionality1, abstraction=abstraction1, product=product)
        msg2 = self.generate_message(emotionality=emotionality2, abstraction=abstraction2, product=product)
        return msg1, msg2
    
    def get_generated_count(self) -> int:
        """Return count of generated messages."""
        return len(self.generated_messages)

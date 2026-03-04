"""
Message/Stimuli Generator
Generates short messages with specific linguistic attributes.
"""

import random
from typing import Dict, List, Tuple


class MessageGenerator:
    """Generates stimuli messages with configurable linguistic attributes."""
    
    # Tone variations
    TONES = {
        "academic": {
            "openings": [
                "According to recent research,",
                "It has been established that",
                "The empirical evidence suggests",
                "Contemporary analysis demonstrates",
                "From a theoretical perspective,"
            ],
            "connectors": ["Furthermore,", "Moreover,", "In addition,", "Consequently,"],
            "closings": [
                "This underscores the importance of further investigation.",
                "Such findings have significant implications.",
                "These results warrant additional examination.",
                "The data supports this conclusion.",
            ],
            "vocabulary": ["utilize", "facilitate", "implement", "optimize", "elucidate"]
        },
        "casual": {
            "openings": [
                "You know,",
                "Here's the thing,",
                "Honestly,",
                "Look,",
                "So basically,"
            ],
            "connectors": ["Plus,", "Also,", "And then,", "Like,"],
            "closings": [
                "Pretty cool, right?",
                "It's pretty straightforward.",
                "Makes sense, doesn't it?",
                "That's basically it.",
            ],
            "vocabulary": ["use", "help", "do", "make", "figure out"]
        }
    }
    
    # Message topics (can be extended)
    TOPICS = {
        "technology": [
            "technology adoption",
            "software development",
            "artificial intelligence",
            "digital transformation"
        ],
        "environment": [
            "sustainability practices",
            "climate action",
            "renewable energy",
            "environmental conservation"
        ],
        "education": [
            "learning methods",
            "educational innovation",
            "student engagement",
            "curriculum development"
        ]
    }
    
    def __init__(self):
        """Initialize the message generator."""
        self.generated_messages = []
    
    def generate_message(
        self,
        tone: str = "academic",
        topic: str = "technology",
        length: str = "short"
    ) -> Dict[str, str]:
        """
        Generate a stimuli message with specified attributes.
        
        Args:
            tone: "academic" or "casual"
            topic: Topic category (technology, environment, education)
            length: "short" or "long" (controls number of sentences)
            
        Returns:
            Dictionary with message and metadata
        """
        if tone not in self.TONES:
            raise ValueError(f"Tone must be one of {list(self.TONES.keys())}")
        if topic not in self.TOPICS:
            raise ValueError(f"Topic must be one of {list(self.TOPICS.keys())}")
        
        tone_config = self.TONES[tone]
        selected_topic = random.choice(self.TOPICS[topic])
        
        # Build message
        sentence1 = f"{random.choice(tone_config['openings'])} {selected_topic} {random.choice(tone_config['vocabulary'])}."
        
        sentence2 = f"{random.choice(tone_config['connectors'])} the approach {random.choice(tone_config['vocabulary'])} multiple benefits."
        
        sentence3 = random.choice(tone_config['closings'])
        
        # Adjust length
        if length == "long":
            extra_sentence = f"{random.choice(tone_config['connectors'])} this consideration has practical implications. {random.choice(tone_config['vocabulary'].upper() if tone == 'academic' else tone_config['vocabulary'])} impact across various domains."
            message = f"{sentence1} {sentence2} {extra_sentence} {sentence3}"
        else:
            message = f"{sentence1} {sentence2} {sentence3}"
        
        metadata = {
            "message": message,
            "tone": tone,
            "topic": topic,
            "length": length,
            "selected_subtopic": selected_topic
        }
        
        self.generated_messages.append(metadata)
        return metadata
    
    def generate_pair(
        self,
        tone1: str = "academic",
        tone2: str = "casual",
        topic: str = "technology"
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Generate a pair of messages with different linguistic attributes.
        
        Args:
            tone1: Tone for first message
            tone2: Tone for second message
            topic: Topic for both messages
            
        Returns:
            Tuple of two message dictionaries
        """
        msg1 = self.generate_message(tone=tone1, topic=topic, length="short")
        msg2 = self.generate_message(tone=tone2, topic=topic, length="short")
        return msg1, msg2
    
    def get_generated_count(self) -> int:
        """Return count of generated messages."""
        return len(self.generated_messages)

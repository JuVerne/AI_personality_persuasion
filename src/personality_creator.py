"""
LLM Personality Creator
Creates system prompts based on Big-5 personality types with dynamic scoring.
"""

from typing import Dict, Tuple


class PersonalityCreator:
    """Manages personality-based system prompts using Big-5 personality model with dynamic scores."""
    
    # Big-5 personality types with score profiles
    # Each profile defines the scores for [openness, conscientiousness, extraversion, agreeableness, neuroticism]
    PERSONALITY_PROFILES = {
        "openness": {
            "name": "High Openness",
            "description": "Creative and intellectually curious",
            "scores": (9, 5, 5, 5, 5)  # (openness, conscientiousness, extraversion, agreeableness, neuroticism)
        },
        "conscientiousness": {
            "name": "High Conscientiousness",
            "description": "Organized, disciplined, and reliable",
            "scores": (5, 9, 5, 5, 5)
        },
        "extraversion": {
            "name": "High Extraversion",
            "description": "Outgoing, energetic, and social",
            "scores": (5, 5, 9, 5, 5)
        },
        "agreeableness": {
            "name": "High Agreeableness",
            "description": "Compassionate, cooperative, and empathetic",
            "scores": (5, 5, 5, 9, 5)
        },
        "neuroticism": {
            "name": "High Neuroticism",
            "description": "Sensitive to emotions, cautious, and anxious",
            "scores": (5, 5, 5, 5, 9)
        }
    }
    
    # System prompt template
    SYSTEM_PROMPT_TEMPLATE = """People with high openness score are imaginative, curious, and creative. Your openness score is {openness} out of {n}. People with high conscientiousness score are disciplined and dependable. Your conscientiousness score is {conscientiousness} out of {n}. People with high extraversion score are outgoing, enthusiastic, and enjoy social interactions. Your extraversion score is {extraversion} out of {n}. People with high agreeableness score prioritize harmony and positive relationships. Your agreeableness score is {agreeableness} out of {n}. People with high neuroticism score are more emotionally reactive and prone to mood swings. Your neuroticism score is {neuroticism} out of {n}. From now on, you are an agent with this personality, and you should respond based on this personality."""
    
    def __init__(self, scale: int = 10):
        """
        Initialize the personality creator.
        
        Args:
            scale: Maximum score for personality dimensions (default: 10)
        """
        self.available_personalities = list(self.PERSONALITY_PROFILES.keys())
        self.scale = scale
    
    def get_system_prompt(self, personality_type: str) -> str:
        """
        Get the system prompt for a specific personality type with its score profile.
        
        Args:
            personality_type: One of the Big-5 personality types
            
        Returns:
            System prompt string for the LLM with personality scores
        """
        if personality_type not in self.PERSONALITY_PROFILES:
            raise ValueError(
                f"Personality type must be one of {self.available_personalities}"
            )
        
        profile = self.PERSONALITY_PROFILES[personality_type]
        openness, conscientiousness, extraversion, agreeableness, neuroticism = profile["scores"]
        
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism,
            n=self.scale
        )
    
    def get_system_prompt_with_scores(
        self,
        openness: int,
        conscientiousness: int,
        extraversion: int,
        agreeableness: int,
        neuroticism: int
    ) -> str:
        """
        Generate a system prompt with custom personality scores.
        
        Args:
            openness: Score for openness dimension
            conscientiousness: Score for conscientiousness dimension
            extraversion: Score for extraversion dimension
            agreeableness: Score for agreeableness dimension
            neuroticism: Score for neuroticism dimension
            
        Returns:
            System prompt string with the specified scores
        """
        # Validate scores
        for score in [openness, conscientiousness, extraversion, agreeableness, neuroticism]:
            if not 0 <= score <= self.scale:
                raise ValueError(f"Scores must be between 0 and {self.scale}")
        
        return self.SYSTEM_PROMPT_TEMPLATE.format(
            openness=openness,
            conscientiousness=conscientiousness,
            extraversion=extraversion,
            agreeableness=agreeableness,
            neuroticism=neuroticism,
            n=self.scale
        )
    
    def get_personality_info(self, personality_type: str) -> Dict:
        """
        Get full personality information including scores.
        
        Args:
            personality_type: One of the Big-5 personality types
            
        Returns:
            Dictionary with personality details and scores
        """
        if personality_type not in self.PERSONALITY_PROFILES:
            raise ValueError(
                f"Personality type must be one of {self.available_personalities}"
            )
        
        profile = self.PERSONALITY_PROFILES[personality_type]
        openness, conscientiousness, extraversion, agreeableness, neuroticism = profile["scores"]
        
        return {
            "name": profile["name"],
            "description": profile["description"],
            "scores": {
                "openness": openness,
                "conscientiousness": conscientiousness,
                "extraversion": extraversion,
                "agreeableness": agreeableness,
                "neuroticism": neuroticism
            },
            "scale": self.scale,
            "system_prompt": self.get_system_prompt(personality_type)
        }
    
    def get_all_personalities(self) -> Dict[str, Dict]:
        """Return all available personality types and their info."""
        return {
            ptype: self.get_personality_info(ptype)
            for ptype in self.available_personalities
        }
    
    def list_personalities(self) -> list:
        """Return list of available personality type identifiers."""
        return self.available_personalities

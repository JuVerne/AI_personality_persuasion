"""
LLM Interface
Handles communication with the LLM API (OpenAI by default).
"""

import os
from typing import Dict, Optional
import json


class LLMInterface:
    """Interface for interacting with LLM APIs."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM interface.
        
        Args:
            api_key: API key for the LLM service (defaults to env variable)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key not provided and OPENAI_API_KEY environment variable not set"
            )
        self.model = model
        self._init_client()
    
    def _init_client(self):
        """Initialize the OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
    
    def compare_messages(
        self,
        message1: str,
        message2: str,
        system_prompt: str,
        temperature: float = 0.7
    ) -> Dict[str, any]:
        """
        Ask the LLM to rate persuasiveness of both messages and choose a preference.
        
        Args:
            message1: First message for comparison
            message2: Second message for comparison
            system_prompt: System prompt defining the personality
            temperature: Temperature for LLM response
            
        Returns:
            Dictionary with ratings, preference and details
        """
        comparison_prompt = f"""You are evaluating two advertising messages for persuasiveness.

MESSAGE 1:
{message1}

MESSAGE 2:
{message2}

Please provide:
1. A persuasiveness rating for Message 1 on a scale of 1-7 (1=not persuasive, 7=very persuasive)
2. A persuasiveness rating for Message 2 on a scale of 1-7 (1=not persuasive, 7=very persuasive)
3. Which message do you find more persuasive (1 or 2)

Format your response exactly as:
Message 1 Rating: [1-7]
Message 2 Rating: [1-7]
Preference: [1 or 2]
Reason: [brief explanation]"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=temperature,
                max_tokens=150
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse response
            rating1, rating2, preferred = self._parse_ratings_and_preference(response_text)
            
            return {
                "message1_rating": rating1,
                "message2_rating": rating2,
                "preferred_message": preferred,
                "explanation": response_text,
                "raw_response": response_text,
                "model": self.model,
                "temperature": temperature
            }
        
        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {str(e)}")
    
    def _parse_ratings_and_preference(self, response_text: str) -> tuple:
        """
        Parse the LLM response to extract ratings and preference.
        
        Args:
            response_text: Raw response from LLM
            
        Returns:
            Tuple of (rating1, rating2, preference)
        """
        rating1 = 4  # default
        rating2 = 4  # default
        preference = 1  # default
        
        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            if 'message 1 rating' in line_lower:
                # Extract number after colon
                try:
                    rating_str = line.split(':')[-1].strip()
                    rating1 = int(rating_str.split()[0])
                    rating1 = max(1, min(7, rating1))  # Clamp to 1-7
                except (ValueError, IndexError):
                    pass
            
            elif 'message 2 rating' in line_lower:
                try:
                    rating_str = line.split(':')[-1].strip()
                    rating2 = int(rating_str.split()[0])
                    rating2 = max(1, min(7, rating2))  # Clamp to 1-7
                except (ValueError, IndexError):
                    pass
            
            elif 'preference' in line_lower:
                try:
                    pref_str = line.split(':')[-1].strip()
                    if '1' in pref_str:
                        preference = 1
                    elif '2' in pref_str:
                        preference = 2
                except (ValueError, IndexError):
                    pass
        
        return rating1, rating2, preference
    
    def test_connection(self) -> bool:
        """
        Test the API connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

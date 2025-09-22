"""
Response cleaning utilities to fix LLM output issues
"""
import re
from typing import List


class ResponseCleaner:
    """Clean and fix common LLM response issues"""
    
    @staticmethod
    def remove_repetition(text: str, min_repeat_length: int = 10) -> str:
        """
        Remove repeated sentences or phrases from text
        
        Args:
            text: Input text to clean
            min_repeat_length: Minimum length of text to consider for repetition
            
        Returns:
            Cleaned text with repetitions removed
        """
        if not text or len(text) < min_repeat_length * 2:
            return text
            
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        removed_count = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                cleaned_lines.append(line)
                continue
                
            # Check for exact repetition
            if line in seen_lines:
                removed_count += 1
                continue
                
            # Check for similar repetition (fuzzy matching)
            is_similar = False
            for seen_line in seen_lines:
                if len(line) > min_repeat_length and len(seen_line) > min_repeat_length:
                    # Calculate similarity
                    similarity = ResponseCleaner._calculate_similarity(line, seen_line)
                    if similarity > 0.8:  # 80% similar
                        is_similar = True
                        removed_count += 1
                        break
            
            if not is_similar:
                cleaned_lines.append(line)
                seen_lines.add(line)
        
        # Log when repetition is detected and cleaned
        if removed_count > 0:
            print(f"🧹 ResponseCleaner: Removed {removed_count} duplicate/similar lines")
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    @staticmethod
    def clean_response(text: str) -> str:
        """
        Apply all cleaning operations to response text
        
        Args:
            text: Raw response text
            
        Returns:
            Cleaned response text
        """
        if not text:
            print("⚠️ ResponseCleaner: Received empty response text")
            return "No response generated."
        
        original_length = len(text)
        
        # Remove repetition
        cleaned = ResponseCleaner.remove_repetition(text)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
        
        # Remove trailing whitespace
        cleaned = cleaned.strip()
        
        # If cleaning removed everything, return a safe message
        if not cleaned or len(cleaned) < 10:
            print("❌ ResponseCleaner: Cleaning removed all content - returning safe message")
            return "No relevant information found in the response."
        
        # Log cleaning stats
        cleaned_length = len(cleaned)
        if cleaned_length < original_length:
            reduction = original_length - cleaned_length
            print(f"✅ ResponseCleaner: Cleaned response (reduced by {reduction} characters)")
        
        return cleaned


def test_response_cleaner():
    """Test the response cleaner"""
    test_text = """This is the only mission in the game where the player can choose to either help John or go back for the money.
This is the only mission in the game where the player can choose to either help John or go back for the money.
This is the only mission in the game where the player can choose to either help John or go back for the money.
This is some unique content.
This is the only mission in the game where the player can choose to either help John or go back for the money."""
    
    cleaned = ResponseCleaner.clean_response(test_text)
    print("Original:")
    print(test_text)
    print("\nCleaned:")
    print(cleaned)


if __name__ == "__main__":
    test_response_cleaner()

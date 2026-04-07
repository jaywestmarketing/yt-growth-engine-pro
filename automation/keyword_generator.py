# -*- coding: utf-8 -*-
"""
RealE Tube - AI Keyword Generator
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from anthropic import Anthropic
from typing import List, Dict
import json

class KeywordGenerator:
    def __init__(self, api_key: str):
        """Initialize keyword generator with Claude API"""
        self.client = Anthropic(api_key=api_key)
    
    def generate_keywords(self, description: str, aggressiveness: str = "Medium") -> List[str]:
        """
        Generate keywords from video description
        
        Args:
            description: Brief video description from user
            aggressiveness: "Low", "Medium", or "High" - determines keyword variety
            
        Returns:
            List of generated keywords
        """
        
        # Adjust keyword count based on aggressiveness
        keyword_counts = {
            "Low": "5-8",
            "Medium": "10-15",
            "High": "15-25"
        }
        count_range = keyword_counts.get(aggressiveness, "10-15")
        
        prompt = f"""You are a YouTube SEO expert. Given this video description, generate strategic keywords that will help the video rank well in YouTube search.

Video Description: "{description}"

Generate {count_range} keywords that include:
1. Primary keywords (main topic)
2. Long-tail variations (more specific phrases)
3. Question-based keywords (how to, what is, etc.)
4. Related semantic keywords

Return ONLY a JSON array of keywords, nothing else. Example format:
["keyword one", "keyword two", "keyword three"]

Keywords:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            keywords = json.loads(response_text)
            return keywords
            
        except Exception as e:
            print(f"Error generating keywords: {e}")
            # Fallback to basic keyword extraction
            return self._fallback_keywords(description)
    
    def _fallback_keywords(self, description: str) -> List[str]:
        """Fallback keyword generation if API fails"""
        # Simple extraction from description
        words = description.lower().split()
        
        # Remove common words
        stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'on', 'in', 'at', 'to', 'for', 'of', 'and', 'or'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Add some variations
        if len(keywords) >= 2:
            keywords.append(" ".join(keywords[:2]))  # Combine first two
        
        return keywords[:10]
    
    def generate_title(self, description: str, competitor_titles: List[str], attempt: int = 1) -> str:
        """
        Generate optimized video title
        
        Args:
            description: Video description
            competitor_titles: List of successful competitor titles
            attempt: Retry attempt number (1-3) - changes strategy
            
        Returns:
            Optimized title
        """
        
        strategy_prompts = {
            1: "Create a title that mimics the style and structure of high-performing videos while being unique.",
            2: "Create a title with a different angle - try question format or listicle style.",
            3: "Create a simple, direct title focusing on the core value proposition."
        }
        
        strategy = strategy_prompts.get(attempt, strategy_prompts[1])
        
        competitor_examples = "\n".join([f"- {title}" for title in competitor_titles[:5]])
        
        prompt = f"""You are a YouTube SEO expert creating viral titles.

Video Description: "{description}"

High-Performing Competitor Titles:
{competitor_examples}

Strategy for Attempt #{attempt}: {strategy}

Requirements:
- 60 characters or less (YouTube optimal)
- Include main keyword
- Engaging and click-worthy
- Capitalize Important Words
- Use numbers or power words where appropriate

Return ONLY the title, nothing else.

Title:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            title = message.content[0].text.strip()
            
            # Remove quotes if present
            title = title.strip('"\'')
            
            # Ensure under 100 characters (YouTube max)
            if len(title) > 100:
                title = title[:97] + "..."
            
            return title
            
        except Exception as e:
            print(f"Error generating title: {e}")
            # Fallback
            return description[:60].strip() + "..."
    
    def generate_description(self, description: str, keywords: List[str], 
                           competitor_descriptions: List[str], attempt: int = 1) -> str:
        """
        Generate optimized video description
        
        Args:
            description: Original video description
            keywords: Generated keywords
            competitor_descriptions: Sample competitor descriptions
            attempt: Retry attempt number
            
        Returns:
            Optimized description
        """
        
        keywords_text = ", ".join(keywords[:10])
        competitor_sample = competitor_descriptions[0] if competitor_descriptions else ""
        
        prompt = f"""You are a YouTube SEO expert creating video descriptions.

Original Description: "{description}"

Target Keywords: {keywords_text}

Sample Competitor Description Structure:
{competitor_sample[:500]}...

Create an engaging YouTube description that:
1. Starts with a hook (first 2-3 lines are crucial)
2. Naturally incorporates keywords
3. Explains what the video covers
4. Includes a call-to-action
5. Is 150-250 words

Return ONLY the description, nothing else.

Description:"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating description: {e}")
            # Fallback
            return f"{description}\n\nKeywords: {keywords_text}"
    
    def generate_tags(self, keywords: List[str], competitor_tags: List[str]) -> List[str]:
        """
        Generate optimized tags combining AI keywords and competitor tags
        
        Args:
            keywords: AI-generated keywords
            competitor_tags: Tags extracted from successful competitors
            
        Returns:
            Combined list of optimized tags
        """
        
        # Combine and deduplicate
        all_tags = list(set(keywords + competitor_tags))
        
        # Sort by length (shorter tags first, they're more general)
        all_tags.sort(key=len)
        
        # Limit to 500 characters total (YouTube limit)
        selected_tags = []
        total_length = 0
        
        for tag in all_tags:
            if total_length + len(tag) + 1 < 500:  # +1 for comma
                selected_tags.append(tag)
                total_length += len(tag) + 1
            else:
                break
        
        return selected_tags[:30]  # Max 30 tags

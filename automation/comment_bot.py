# -*- coding: utf-8 -*-
"""
RealE Tube - YouTube Comment Bot
Copyright © 2024 RealE Technology Solutions. All rights reserved.
"""

from automation.google_auth import GoogleAuthHelper
from automation.keyword_generator import KeywordGenerator
from typing import List, Dict
import random
import time

class CommentBot:
    def __init__(self, youtube_service, ai_generator: KeywordGenerator = None):
        """
        Initialize comment bot
        
        Args:
            youtube_service: Authenticated YouTube API service
            ai_generator: AI keyword generator for creating natural comments (optional)
        """
        self.youtube = youtube_service
        self.ai_generator = ai_generator
        self.commented_videos = set()  # Track videos we've already commented on
    
    def comment_on_competitor(self, video_id: str, comment_style: str = "helpful") -> bool:
        """
        Post a comment on a competitor's video
        
        Args:
            video_id: YouTube video ID to comment on
            comment_style: "helpful", "question", "appreciation", or "engaging"
            
        Returns:
            True if successful
        """
        
        # Skip if already commented
        if video_id in self.commented_videos:
            print(f"Already commented on video: {video_id}")
            return False
        
        try:
            # Get video info first
            video_info = self.youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not video_info['items']:
                return False
            
            video_title = video_info['items'][0]['snippet']['title']
            
            # Generate comment
            if self.ai_generator:
                comment_text = self._generate_ai_comment(video_title, comment_style)
            else:
                comment_text = self._get_template_comment(comment_style)
            
            # Post comment
            request = self.youtube.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": comment_text
                            }
                        }
                    }
                }
            )
            
            response = request.execute()
            
            # Track that we've commented
            self.commented_videos.add(video_id)
            
            print(f"✓ Commented on video: {video_title[:50]}...")
            print(f"  Comment: {comment_text[:80]}...")
            
            return True
            
        except Exception as e:
            print(f"Error commenting on video {video_id}: {e}")
            return False
    
    def _generate_ai_comment(self, video_title: str, comment_style: str) -> str:
        """Generate natural-sounding comment using AI"""
        
        style_prompts = {
            "helpful": "Write a helpful, genuine comment praising the video and adding value. 1-2 sentences, friendly tone.",
            "question": "Write a curious question about the topic that shows genuine interest. 1 sentence.",
            "appreciation": "Write a brief thank you comment expressing how helpful the video was. 1 sentence.",
            "engaging": "Write an engaging comment that might start a discussion. Ask a thought-provoking question. 1-2 sentences."
        }
        
        prompt = f"""You're commenting on a YouTube video titled: "{video_title}"

{style_prompts.get(comment_style, style_prompts['helpful'])}

Rules:
- Sound natural and human
- Don't promote anything
- Don't mention other channels
- Be genuine and positive
- Keep it under 100 characters

Return ONLY the comment text, nothing else.

Comment:"""

        try:
            message = self.ai_generator.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            comment = message.content[0].text.strip()
            
            # Remove quotes if present
            comment = comment.strip('"\'')
            
            return comment
            
        except Exception as e:
            print(f"Error generating AI comment: {e}")
            return self._get_template_comment(comment_style)
    
    def _get_template_comment(self, comment_style: str) -> str:
        """Get pre-written template comment as fallback"""
        
        templates = {
            "helpful": [
                "Great tutorial! This really helped clarify things for me. Thanks for sharing!",
                "Super helpful video! Exactly what I was looking for. Appreciate it!",
                "This is gold! Thanks for breaking it down so clearly.",
                "Fantastic explanation! You made this so easy to understand.",
                "Really appreciate you taking the time to make this. Very helpful!"
            ],
            "question": [
                "Does this work if you're using a different setup?",
                "What would you recommend for beginners just starting out?",
                "Have you tried this with other methods? Curious about alternatives.",
                "How long does this typically take to work?",
                "What's your take on doing it the other way?"
            ],
            "appreciation": [
                "Thank you so much for this! Exactly what I needed.",
                "This saved me so much time. Really appreciate it!",
                "Thanks for sharing your knowledge! Super useful.",
                "This is exactly what I was looking for. Thank you!",
                "Really helpful video. Thanks for putting this together!"
            ],
            "engaging": [
                "Interesting approach! Have you found this works better than the traditional method?",
                "Great content! What's your opinion on the debate around this topic?",
                "Love this! Do you think this will still be relevant in the next few years?",
                "Solid advice! What would you say is the biggest mistake people make with this?",
                "This is great! How do you think this compares to what others are teaching?"
            ]
        }
        
        return random.choice(templates.get(comment_style, templates["helpful"]))
    
    def comment_on_multiple(self, video_ids: List[str], 
                          comment_style: str = "helpful",
                          delay_seconds: int = 30,
                          max_comments: int = 5) -> Dict:
        """
        Comment on multiple competitor videos with delays
        
        Args:
            video_ids: List of YouTube video IDs
            comment_style: Style of comments
            delay_seconds: Seconds to wait between comments (to avoid spam detection)
            max_comments: Maximum number of comments to post in this batch
            
        Returns:
            Dict with success/failure counts
        """
        
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0
        }
        
        # Limit to max_comments
        videos_to_comment = video_ids[:max_comments]
        
        for i, video_id in enumerate(videos_to_comment):
            # Skip if already commented
            if video_id in self.commented_videos:
                results["skipped"] += 1
                continue
            
            # Post comment
            success = self.comment_on_competitor(video_id, comment_style)
            
            if success:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            # Wait between comments (except for last one)
            if i < len(videos_to_comment) - 1:
                print(f"Waiting {delay_seconds} seconds before next comment...")
                time.sleep(delay_seconds)
        
        return results
    
    def reset_commented_videos(self):
        """Clear the commented videos cache"""
        self.commented_videos.clear()

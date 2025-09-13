"""
Sports data processing from Kafka streams.
"""

import logging
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from .database import AsyncSessionLocal
from .models import Football, Tennis

logger = logging.getLogger(__name__)


class SportsDataProcessor:
    """Process sports data from Kafka streams."""
    
    def __init__(self):
        self.team_patterns = {
            # Football teams (you can expand this)
            'liverpool': 'football',
            'arsenal': 'football',
            'chelsea': 'football',
            'manchester': 'football',
            'tottenham': 'football',
            'everton': 'football',
            'barcelona': 'football',
            'realmadrid': 'football',
            'juventus': 'football',
            'milan': 'football',
            'psg': 'football',
            'bayern': 'football',
            'dortmund': 'football',
            
            # NBA teams (add as needed)
            'lakers': 'nba',
            'warriors': 'nba',
            'bulls': 'nba',
            'celtics': 'nba',
            'heat': 'nba',
            'nets': 'nba',
            'knicks': 'nba',
            'spurs': 'nba',
            'rockets': 'nba',
            'clippers': 'nba',
            'sixers': 'nba',
            'nuggets': 'nba',
            'suns': 'nba',
            'bucks': 'nba',
        }
    
    def determine_sport_type(self, topic: str, data: Dict[str, Any]) -> Optional[str]:
        """Determine if this is NBA or football data."""
        topic_lower = topic.lower()
        
        # Map known team topics to sports
        football_teams = [
            'liverpool', 'chelsea', 'arsenal', 'manchesterunited', 'tottenhamhotspur',
            'everton', 'leicestercity', 'afc_bournemouth', 'southampton'
        ]
        
        nba_teams = [
            'lakers', 'warriors', 'bulls', 'celtics', 'heat', 'nets', 'knicks', 
            'spurs', 'rockets', 'clippers', 'sixers', 'nuggets', 'suns', 'bucks'
        ]
        
        if topic_lower in football_teams:
            return 'football'
        elif topic_lower in nba_teams:
            return 'nba'
        
        # Check message content for keywords
        text_lower = data.get('text', '').lower()
        
        football_keywords = [
            'fc', 'football', 'soccer', 'premier league', 'champions league',
            'goal', 'match', 'stadium', 'league', 'cup', 'uefa', 'fifa'
        ]
        
        nba_keywords = [
            'nba', 'basketball', 'dunk', 'three pointer', '3pt', 'playoff',
            'finals', 'court', 'arena', 'points', 'rebounds', 'assists'
        ]
        
        football_count = sum(1 for keyword in football_keywords if keyword in text_lower)
        nba_count = sum(1 for keyword in nba_keywords if keyword in text_lower)
        
        if football_count > nba_count:
            return 'football'
        elif nba_count > football_count:
            return 'nba'
        
        # Default to football for known football team topics
        return 'football'
    
    async def process_sports_message(self, message: Dict[str, Any], topic: str, key: Optional[str], timestamp: int) -> None:
        """Process incoming sports data message."""
        try:
            logger.info(f"=== KAFKA MESSAGE RECEIVED ===")
            logger.info(f"Topic: {topic}")
            logger.info(f"Key: {key}")
            logger.info(f"Timestamp: {timestamp}")
            logger.info(f"Message: {json.dumps(message, indent=2)}")
            logger.info(f"================================")
            
            # Determine sport type
            sport_type = self.determine_sport_type(topic, message)
            
            if sport_type == 'football':
                await self._process_football_data(message, topic, timestamp)
            elif sport_type == 'nba':
                await self._process_nba_data(message, topic, timestamp)
            else:
                logger.warning(f"Unknown sport type for topic {topic}")
                
        except Exception as e:
            logger.error(f"Error processing sports message from {topic}: {str(e)}")
    
    async def _process_football_data(self, data: Dict[str, Any], topic: str, timestamp: int) -> None:
        """Process football-related data."""
        try:
            # Since this is social media data and our database schema is for season statistics,
            # we'll just log the activity for now. In a real system, you might want to:
            # 1. Store social media data in a separate table
            # 2. Aggregate sentiment/engagement metrics
            # 3. Update team popularity metrics
            
            team_name = topic.replace('_', ' ')  # Convert AFC_Bournemouth to AFC Bournemouth
            
            logger.info(f"🏈 FOOTBALL MESSAGE PROCESSED:")
            logger.info(f"   Team: {team_name}")
            logger.info(f"   Platform: {data.get('platform', 'Unknown')}")
            logger.info(f"   User: {data.get('screenname', 'Unknown')}")
            logger.info(f"   Location: {data.get('location', 'Unknown')}")
            logger.info(f"   Search Query: {data.get('search_query', 'N/A')}")
            logger.info(f"   Tweet Text: {data.get('text', '')}")
            logger.info(f"   Clean Text: {data.get('clean_text', '')}")
            logger.info(f"   Timestamp: {timestamp}")
            
            # You could add logic here to:
            # - Calculate sentiment scores
            # - Track trending topics
            # - Update team social media metrics
            # - Store in a separate social_media_posts table
                
        except Exception as e:
            logger.error(f"Error processing football data: {str(e)}")
    
    async def _process_nba_data(self, data: Dict[str, Any], topic: str, timestamp: int) -> None:
        """Process NBA-related data."""
        try:
            # Similar to football, just log NBA social media activity
            team_name = topic.replace('_', ' ')
            
            logger.info(f"🏀 NBA MESSAGE PROCESSED:")
            logger.info(f"   Team: {team_name}")
            logger.info(f"   Platform: {data.get('platform', 'Unknown')}")
            logger.info(f"   User: {data.get('screenname', 'Unknown')}")
            logger.info(f"   Location: {data.get('location', 'Unknown')}")
            logger.info(f"   Search Query: {data.get('search_query', 'N/A')}")
            logger.info(f"   Tweet Text: {data.get('text', '')}")
            logger.info(f"   Clean Text: {data.get('clean_text', '')}")
            logger.info(f"   Timestamp: {timestamp}")
                
        except Exception as e:
            logger.error(f"Error processing NBA data: {str(e)}")


# Global processor instance
sports_processor = SportsDataProcessor()
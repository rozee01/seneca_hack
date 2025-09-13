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
            
            # Tennis players/tournaments (add as needed)
            'wimbledon': 'tennis',
            'usopen': 'tennis',
            'frenchopen': 'tennis',
            'australianopen': 'tennis',
            'federer': 'tennis',
            'nadal': 'tennis',
            'djokovic': 'tennis',
            'serena': 'tennis',
        }
    
    def determine_sport_type(self, topic: str, data: Dict[str, Any]) -> Optional[str]:
        """Determine if this is tennis or football data."""
        topic_lower = topic.lower()
        file_name_lower = data.get('file_name', '').lower()
        search_query_lower = data.get('search_query', '').lower()
        text_lower = data.get('text', '').lower()
        
        # Check topic name first
        for team, sport in self.team_patterns.items():
            if team in topic_lower or team in file_name_lower:
                return sport
        
        # Check search query and text for football keywords
        football_keywords = [
            'fc', 'football', 'soccer', 'premier league', 'champions league',
            'goal', 'match', 'stadium', 'league', 'cup', 'uefa', 'fifa'
        ]
        
        tennis_keywords = [
            'tennis', 'grand slam', 'atp', 'wta', 'set', 'serve', 'ace',
            'court', 'racket', 'tournament', 'open'
        ]
        
        combined_text = f"{search_query_lower} {text_lower}"
        
        football_count = sum(1 for keyword in football_keywords if keyword in combined_text)
        tennis_count = sum(1 for keyword in tennis_keywords if keyword in combined_text)
        
        if football_count > tennis_count:
            return 'football'
        elif tennis_count > football_count:
            return 'tennis'
        
        # Default to football if unclear (since most sports social media is football)
        return 'football'
    
    async def process_sports_message(self, message: Dict[str, Any], topic: str, key: Optional[str], timestamp: int) -> None:
        """Process incoming sports data message."""
        try:
            logger.info(f"Processing sports message from topic: {topic}")
            
            # Determine sport type
            sport_type = self.determine_sport_type(topic, message)
            
            if sport_type == 'football':
                await self._process_football_data(message, topic, timestamp)
            elif sport_type == 'tennis':
                await self._process_tennis_data(message, topic, timestamp)
            else:
                logger.warning(f"Unknown sport type for topic {topic}")
                
        except Exception as e:
            logger.error(f"Error processing sports message from {topic}: {str(e)}")
    
    async def _process_football_data(self, data: Dict[str, Any], topic: str, timestamp: int) -> None:
        """Process football-related data."""
        try:
            async with AsyncSessionLocal() as session:
                # Extract team name from topic (cleaned_<team_name>)
                team_match = re.search(r'cleaned_(.+)', topic)
                team_name = team_match.group(1) if team_match else data.get('file_name', 'Unknown')
                
                # Create a football social media entry
                # Note: This is social media data, not match data, so we'll create a simplified entry
                football_entry = Football(
                    match_id=f"social_{timestamp}_{hash(data.get('text', ''))[:8]}",
                    league="Social Media",
                    season="2025",
                    date=datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc) if timestamp else datetime.now(timezone.utc),
                    home_team=team_name,
                    away_team="Social Media Post",
                    home_score=None,
                    away_score=None,
                    winner=None,
                    final_result=f"Social media activity for {team_name}",
                    # Store additional metadata in unused fields
                    stadium=data.get('location', 'Unknown'),
                    referee=data.get('screenname', 'Unknown'),
                    weather=data.get('search_query', ''),
                    # You could store the social media text in a notes field if you add one
                )
                
                session.add(football_entry)
                await session.commit()
                
                logger.info(f"Stored football social media data for team: {team_name}")
                
        except Exception as e:
            logger.error(f"Error storing football data: {str(e)}")
            await session.rollback()
    
    async def _process_tennis_data(self, data: Dict[str, Any], topic: str, timestamp: int) -> None:
        """Process tennis-related data."""
        try:
            async with AsyncSessionLocal() as session:
                # Extract player/tournament name from topic
                entity_match = re.search(r'cleaned_(.+)', topic)
                entity_name = entity_match.group(1) if entity_match else data.get('file_name', 'Unknown')
                
                # Create a tennis social media entry
                tennis_entry = Tennis(
                    match_id=f"social_{timestamp}_{hash(data.get('text', ''))[:8]}",
                    tournament="Social Media",
                    date=datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc) if timestamp else datetime.now(timezone.utc),
                    round="Social Media Post",
                    surface="Social",
                    player1_name=entity_name,
                    player2_name="Social Media",
                    winner=None,
                    score=f"Social media activity",
                    # Store additional metadata
                    sets=data.get('location', 'Unknown'),
                )
                
                session.add(tennis_entry)
                await session.commit()
                
                logger.info(f"Stored tennis social media data for: {entity_name}")
                
        except Exception as e:
            logger.error(f"Error storing tennis data: {str(e)}")
            await session.rollback()


# Global processor instance
sports_processor = SportsDataProcessor()
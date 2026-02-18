import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class MoodMusicDatabase:
    """Database handler for mood music history"""
    
    def __init__(self, db_path: str = "mood_music.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Create and return a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Create the history tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Mood-based search history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                mood TEXT NOT NULL,
                features TEXT NOT NULL,
                tracks TEXT NOT NULL,
                audio_features_map TEXT,
                evaluation TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Song-based discovery history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS song_discovery_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source_track TEXT NOT NULL,
                source_artist TEXT NOT NULL,
                source_track_id TEXT NOT NULL,
                source_features TEXT,
                similar_tracks TEXT NOT NULL,
                mood_description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_search(self, mood: str, features: dict, tracks: list, 
                   audio_features_map: dict = None, evaluation: dict = None) -> int:
        """
        Add a new search to history
        
        Args:
            mood: User's mood text
            features: Extracted audio features
            tracks: List of recommended tracks
            audio_features_map: Map of track IDs to audio features
            evaluation: AI evaluation of recommendations
        
        Returns:
            ID of inserted record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO search_history 
            (timestamp, mood, features, tracks, audio_features_map, evaluation)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            mood,
            json.dumps(features, ensure_ascii=False),
            json.dumps(tracks, ensure_ascii=False),
            json.dumps(audio_features_map, ensure_ascii=False) if audio_features_map else None,
            json.dumps(evaluation, ensure_ascii=False) if evaluation else None
        ))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def get_all_searches(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all search history, ordered by most recent first
        
        Args:
            limit: Maximum number of records to return (None for all)
        
        Returns:
            List of search history entries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, mood, features, tracks, audio_features_map, evaluation
            FROM search_history
            ORDER BY id DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entry = {
                'id': row['id'],
                'timestamp': datetime.fromisoformat(row['timestamp']),
                'mood': row['mood'],
                'features': json.loads(row['features']),
                'tracks': json.loads(row['tracks']),
                'audio_features_map': json.loads(row['audio_features_map']) if row['audio_features_map'] else {},
                'evaluation': json.loads(row['evaluation']) if row['evaluation'] else None
            }
            results.append(entry)
        
        return results
    
    def get_search_by_id(self, search_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific search by ID
        
        Args:
            search_id: ID of the search
        
        Returns:
            Search entry or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, mood, features, tracks, audio_features_map, evaluation
            FROM search_history
            WHERE id = ?
        """, (search_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'id': row['id'],
            'timestamp': datetime.fromisoformat(row['timestamp']),
            'mood': row['mood'],
            'features': json.loads(row['features']),
            'tracks': json.loads(row['tracks']),
            'audio_features_map': json.loads(row['audio_features_map']) if row['audio_features_map'] else {},
            'evaluation': json.loads(row['evaluation']) if row['evaluation'] else None
        }
    
    def delete_search(self, search_id: int) -> bool:
        """
        Delete a search from history
        
        Args:
            search_id: ID of the search to delete
        
        Returns:
            True if deleted, False if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM search_history WHERE id = ?", (search_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def clear_all_history(self) -> int:
        """
        Delete all search history
        
        Returns:
            Number of records deleted
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM search_history")
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_search_count(self) -> int:
        """
        Get total number of searches in history
        
        Returns:
            Count of searches
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM search_history")
        count = cursor.fetchone()['count']
        
        conn.close()
        return count
    
    def get_recent_moods(self, limit: int = 10) -> List[str]:
        """
        Get recent mood texts
        
        Args:
            limit: Number of moods to return
        
        Returns:
            List of recent mood texts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT mood FROM search_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['mood'] for row in rows]
    
    # Song Discovery Methods
    def add_song_discovery(self, source_track: str, source_artist: str, source_track_id: str,
                          source_features: dict, similar_tracks: list, mood_description: str = None) -> int:
        """
        Add a new song discovery search to history
        
        Args:
            source_track: Source track name
            source_artist: Source artist name
            source_track_id: Spotify track ID
            source_features: Audio features of source track
            similar_tracks: List of similar tracks found
            mood_description: AI-generated mood description
        
        Returns:
            ID of inserted record
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO song_discovery_history 
            (timestamp, source_track, source_artist, source_track_id, source_features, similar_tracks, mood_description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            source_track,
            source_artist,
            source_track_id,
            json.dumps(source_features, ensure_ascii=False) if source_features else None,
            json.dumps(similar_tracks, ensure_ascii=False),
            mood_description
        ))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def get_all_song_discoveries(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all song discovery history, ordered by most recent first
        
        Args:
            limit: Maximum number of records to return (None for all)
        
        Returns:
            List of song discovery history entries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, timestamp, source_track, source_artist, source_track_id, 
                   source_features, similar_tracks, mood_description
            FROM song_discovery_history
            ORDER BY id DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entry = {
                'id': row['id'],
                'timestamp': datetime.fromisoformat(row['timestamp']),
                'source_track': row['source_track'],
                'source_artist': row['source_artist'],
                'source_track_id': row['source_track_id'],
                'source_features': json.loads(row['source_features']) if row['source_features'] else None,
                'similar_tracks': json.loads(row['similar_tracks']),
                'mood_description': row['mood_description']
            }
            results.append(entry)
        
        return results
    
    def clear_song_discovery_history(self) -> int:
        """
        Delete all song discovery history
        
        Returns:
            Number of records deleted
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM song_discovery_history")
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_song_discovery_count(self) -> int:
        """
        Get total number of song discoveries in history
        
        Returns:
            Count of song discoveries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM song_discovery_history")
        count = cursor.fetchone()['count']
        
        conn.close()
        return count
    
    def get_all_history_combined(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get combined history from both mood searches and song discoveries
        
        Returns:
            List of all history entries with type indicator
        """
        mood_searches = self.get_all_searches(limit=limit)
        song_discoveries = self.get_all_song_discoveries(limit=limit)
        
        # Add type indicator
        for entry in mood_searches:
            entry['type'] = 'mood'
        
        for entry in song_discoveries:
            entry['type'] = 'song'
        
        # Combine and sort by timestamp
        combined = mood_searches + song_discoveries
        combined.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if limit:
            combined = combined[:limit]
        
        return combined

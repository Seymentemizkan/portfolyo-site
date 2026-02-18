import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import json
import random
from database import MoodMusicDatabase

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

client = OpenAI(api_key=OPENAI_API_KEY)

# Page config
st.set_page_config(
    page_title="Ruh Haline Göre Müzik",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern Design
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Header with Animation */
    .main-header {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        animation: gradientShift 8s ease infinite;
        background-size: 200% 200%;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: rgba(255, 255, 255, 0.9);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: rgba(255, 255, 255, 0.9);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Text Area Styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e9ecef;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Card Styling */
    .song-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    .song-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.15);
        border-color: rgba(102, 126, 234, 0.3);
    }
    
    /* Feature Badge */
    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.3rem;
        display: inline-block;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        transition: all 0.2s ease;
    }
    
    .feature-badge:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 100%;
        animation: progressShine 2s linear infinite;
    }
    
    @keyframes progressShine {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #495057;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 500;
        color: #6c757d;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3.5rem;
        padding: 0 2rem;
        background-color: #f8f9fa;
        border-radius: 12px 12px 0 0;
        color: #6c757d;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        color: #495057;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 12px;
        font-weight: 600;
        color: #495057;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Link Button Styling */
    .stLinkButton > a {
        background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%);
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(29, 185, 84, 0.3);
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #1ed760 0%, #1DB954 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.4);
    }
    
    /* Info/Warning/Success Box Styling */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
    }
    
    /* Image Styling */
    img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    img:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    
    /* Slider Styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
@st.cache_resource
def get_database():
    return MoodMusicDatabase()

db = get_database()

# Initialize session state for history
if 'history' not in st.session_state:
    # Load mood search history from database
    st.session_state.history = db.get_all_searches()

if 'song_discovery_history' not in st.session_state:
    # Load song discovery history from database
    st.session_state.song_discovery_history = db.get_all_song_discoveries()

if 'combined_history' not in st.session_state:
    # Load combined history
    st.session_state.combined_history = db.get_all_history_combined()

if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = True

# Header with subtitle and Spotify logo
st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; position: relative; z-index: 1;">
        <svg viewBox="0 0 24 24" width="64" height="64" xmlns="http://www.w3.org/2000/svg" style="filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));">
            <path fill="#1DB954" d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
        </svg>
        <h1 style="margin: 0;">Ruh Haline Göre Müzik Önerici</h1>
    </div>
    <p style="color: rgba(255,255,255,0.95); font-size: 1.2rem; margin-top: 1rem; font-weight: 300; position: relative; z-index: 1;">
        Duygularını anlat, mükemmel şarkıları keşfet
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar with enhanced design
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0; margin-bottom: 1rem;">
        <h2 style="color: #ffffff; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">⚙️ Ayarlar</h2>
    </div>
    """, unsafe_allow_html=True)
    
    num_songs = st.slider(
        "🎵 Şarkı Sayısı", 
        min_value=5, 
        max_value=20, 
        value=10, 
        step=1,
        help="Önerilecek şarkı sayısını belirleyin"
    )
    
    # Database stats
    total_searches = len(st.session_state.history)
    if total_searches > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); 
                    padding: 1rem; border-radius: 12px; margin: 1rem 0; text-align: center;
                    box-shadow: 0 4px 15px rgba(29, 185, 84, 0.3);">
            <p style="color: white; margin: 0; font-size: 0.9rem; font-weight: 500;">📊 Toplam Arama</p>
            <p style="color: white; margin: 0; font-size: 2rem; font-weight: 700;">{total_searches}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="background: rgba(255, 255, 255, 0.1); 
                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);">
        <h3 style="color: #ffffff; margin-top: 0; font-size: 1.1rem;">📖 Nasıl Çalışır?</h3>
        <div style="color: rgba(255, 255, 255, 0.9); line-height: 1.8;">
            <p style="margin: 0.5rem 0;"><strong>1️⃣</strong> Ruh halinizi yazın</p>
            <p style="margin: 0.5rem 0;"><strong>2️⃣</strong> AI analiz yapar</p>
            <p style="margin: 0.5rem 0;"><strong>3️⃣</strong> Spotify'dan şarkılar bulur</p>
            <p style="margin: 0.5rem 0;"><strong>4️⃣</strong> AI önerileri değerlendirir</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="background: rgba(255, 215, 0, 0.2); 
                padding: 1rem; border-radius: 12px; text-align: center;
                border: 1px solid rgba(255, 215, 0, 0.3);">
        <p style="margin: 0; color: #FFD700; font-weight: 600;">💡 İpucu</p>
        <p style="margin: 0.5rem 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 0.9rem;">
            Duygularını detaylı anlat, daha iyi sonuçlar al!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div style="text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.85rem; margin-top: 2rem;">
        <p style="margin: 0;">Made with ❤️ using</p>
        <p style="margin: 0.3rem 0 0 0; font-weight: 600; color: rgba(255, 255, 255, 0.8);">OpenAI • Spotify • Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# Function definitions
def get_spotify_token():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        raise RuntimeError("Spotify env vars missing: SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET")
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth}"}
    data = {"grant_type": "client_credentials"}
    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    if not r.ok:
        raise RuntimeError(f"Spotify token error {r.status_code}: {r.text}")

    payload = r.json()
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"Spotify token missing in response: {payload}")

    return token

def mood_to_features(mood):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        temperature=0.7,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return only a valid JSON object with these fields:\n"
                    "- energy, valence, danceability (0-1): energy level, happiness, danceability\n"
                    "- acousticness (0-1): acoustic vs electronic (0=electronic, 1=acoustic)\n"
                    "- instrumentalness (0-1): vocal content (0=lots of vocals, 1=no vocals/instrumental)\n"
                    "- speechiness (0-1): spoken words (0=music, 0.33-0.66=rap, >0.66=podcast/speech)\n"
                    "- loudness (-60 to 0): volume in dB (typical: -60=very quiet, -5=loud)\n"
                    "- mode (0 or 1): minor=0, major=1 (sad=minor, happy=major)\n"
                    "- tempo (60-180): beats per minute\n"
                    "- genres: array of 2-3 music genre strings (electronic, rock, pop, jazz, hip-hop, indie, classical, etc.)\n"
                    "- keywords: array of 3-5 mood/style descriptive words for search\n"
                    "- artist_style: a brief artist style description"
                ),
            },
            {"role": "user", "content": f'Ruh hali: "{mood}"'},
        ],
    )

    return response.choices[0].message.content

def parse_features(raw_json):
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        start = raw_json.find("{")
        end = raw_json.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(raw_json[start : end + 1])

    required = {"energy", "valence", "danceability", "tempo"}
    if not required.issubset(data):
        raise ValueError("Missing required fields in LLM response.")

    features = {
        "energy": float(data["energy"]),
        "valence": float(data["valence"]),
        "danceability": float(data["danceability"]),
        "acousticness": float(data.get("acousticness", 0.5)),
        "instrumentalness": float(data.get("instrumentalness", 0.0)),
        "speechiness": float(data.get("speechiness", 0.0)),
        "loudness": float(data.get("loudness", -10.0)),
        "mode": int(data.get("mode", 1)),
        "tempo": float(data["tempo"]),
        "primary_genre": data.get("primary_genre", "pop"),
        "genres": data.get("genres", ["pop"]),
        "language": data.get("language", "English"),
        "lyrics_theme": data.get("lyrics_theme", ""),
        "lyrics_keywords": data.get("lyrics_keywords", []),
        "keywords": data.get("keywords", []),
        "artist_style": data.get("artist_style", ""),
    }

    # Clamp values to valid ranges
    features["energy"] = max(0.0, min(1.0, features["energy"]))
    features["valence"] = max(0.0, min(1.0, features["valence"]))
    features["danceability"] = max(0.0, min(1.0, features["danceability"]))
    features["acousticness"] = max(0.0, min(1.0, features["acousticness"]))
    features["instrumentalness"] = max(0.0, min(1.0, features["instrumentalness"]))
    features["speechiness"] = max(0.0, min(1.0, features["speechiness"]))
    features["loudness"] = max(-60.0, min(0.0, features["loudness"]))
    features["mode"] = 1 if features["mode"] > 0 else 0
    features["tempo"] = max(60.0, min(180.0, features["tempo"]))

    return features

def get_recommendations_via_search(token, features, limit=10):
    """Search for tracks matching mood features with emphasis on genre and language"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Calculate candidate pool size
    candidate_pool_size = max(50, limit * 5)
    
    # Build search queries with PRIORITY on genre and language
    queries = []
    
    primary_genre = features.get("primary_genre", "")
    language = features.get("language", "")
    genres = features.get("genres", [])
    
    # Determine mood descriptors based on audio features
    mood_descriptors = []
    
    # Energy + Valence combined
    if features["energy"] > 0.6 and features["valence"] > 0.6:
        mood_descriptors.append("upbeat")
        mood_descriptors.append("energetic")
    elif features["energy"] > 0.6 and features["valence"] < 0.4:
        mood_descriptors.append("powerful")
        mood_descriptors.append("intense")
    elif features["energy"] < 0.4 and features["valence"] > 0.6:
        mood_descriptors.append("chill")
        mood_descriptors.append("peaceful")
    elif features["energy"] < 0.4 and features["valence"] < 0.4:
        mood_descriptors.append("emotional")
        mood_descriptors.append("sad")
    
    # Acousticness
    if features.get("acousticness", 0.5) > 0.7:
        mood_descriptors.append("acoustic")
    elif features.get("acousticness", 0.5) < 0.3:
        mood_descriptors.append("electronic")
    
    # Mode
    if features.get("mode", 1) == 0:
        mood_descriptors.append("melancholic")
    
    # PRIORITY 1: Primary genre + language (if Turkish)
    if primary_genre and language:
        if language.lower() in ["turkish", "türkçe", "turkce"]:
            # For Turkish songs, search with Turkish artist/location tags
            queries.append(f"{primary_genre} türkçe")
            queries.append(f"{primary_genre} turkish")
            queries.append(f"türkçe {primary_genre}")
        else:
            # For other languages, combine genre with language
            queries.append(f"{primary_genre} {language}")
    
    # PRIORITY 2: Primary genre + mood descriptors (highly weighted)
    if primary_genre and mood_descriptors:
        queries.append(f"{primary_genre} {mood_descriptors[0]}")
        if len(mood_descriptors) > 1:
            queries.append(f"{primary_genre} {mood_descriptors[1]}")
    
    # PRIORITY 3: Just primary genre (still important)
    if primary_genre:
        queries.append(primary_genre)
    
    # PRIORITY 4: Primary genre + lyrics theme (medium priority - YENI!)
    lyrics_theme = features.get("lyrics_theme", "")
    lyrics_keywords = features.get("lyrics_keywords", [])
    
    if primary_genre and lyrics_theme:
        queries.append(f"{primary_genre} {lyrics_theme}")
    
    if lyrics_keywords and primary_genre:
        # Combine genre with lyrics keywords
        lyrics_query = f"{primary_genre} {' '.join(lyrics_keywords[:2])}"
        queries.append(lyrics_query)
    
    # PRIORITY 5: Lyrics theme alone (if exists)
    if lyrics_theme:
        queries.append(lyrics_theme)
    
    # PRIORITY 6: Secondary genres with mood
    if genres and len(genres) > 1:
        for genre in genres[1:2]:  # Use second genre if exists
            if mood_descriptors:
                queries.append(f"{genre} {mood_descriptors[0]}")
            else:
                queries.append(genre)
    
    # PRIORITY 7: Keywords (lower priority now)
    if features.get("keywords"):
        keywords = " ".join(features["keywords"][:2])
        queries.append(keywords)
    
    # PRIORITY 8: General mood search (lowest priority)
    if mood_descriptors:
        queries.append(" ".join(mood_descriptors[:2]))
    
    # Ensure we have at least one query
    if not queries:
        queries = ["pop music"]
    
    # Use top queries with different weights
    # First 3 queries get more results, rest get fewer
    all_tracks = []
    seen_ids = set()
    
    # Gather candidate tracks from queries with weighted importance
    for idx, query in enumerate(queries[:8]):  # Use up to 8 queries
        # First 3 queries are most important (genre/language based)
        if idx < 3:
            search_limit = 15  # More results from genre-based searches
            offset = random.randint(0, 3)  # Less randomness for better relevance
        elif idx < 5:
            search_limit = 10
            offset = random.randint(0, 5)
        else:
            search_limit = 8
            offset = random.randint(0, 8)
        
        params = {
            "q": query,
            "type": "track",
            "limit": search_limit,
            "offset": offset
        }
        
        try:
            r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params, timeout=10)
            if r.ok:
                tracks = r.json().get("tracks", {}).get("items", [])
                for track in tracks:
                    track_id = track.get("id")
                    if track_id and track_id not in seen_ids:
                        seen_ids.add(track_id)
                        all_tracks.append(track)
                        if len(all_tracks) >= candidate_pool_size:
                            break
        except Exception as e:
            print(f"Search error for '{query}': {str(e)}")
            continue
        
        if len(all_tracks) >= candidate_pool_size:
            break
    
    # Last resort fallback
    if not all_tracks:
        genre_query = primary_genre or (genres[0] if genres else "pop")
        try:
            r = requests.get("https://api.spotify.com/v1/search", 
                            headers=headers, 
                            params={"q": genre_query, "type": "track", "limit": min(limit * 2, 20)},
                            timeout=10)
            if r.ok:
                all_tracks = r.json().get("tracks", {}).get("items", [])
        except:
            pass
    
    # Shuffle for variety and return requested amount
    if all_tracks:
        random.shuffle(all_tracks)
        return all_tracks[:limit]
    
    return []

def get_audio_features(token, track_ids):
    """Get audio features for multiple tracks from Spotify"""
    if not track_ids:
        return {}
    
    headers = {"Authorization": f"Bearer {token}"}
    # API accepts up to 100 IDs but we'll do in batches of 50
    features_map = {}
    
    for i in range(0, len(track_ids), 50):
        batch_ids = track_ids[i:i+50]
        ids_str = ",".join(batch_ids)
        
        try:
            r = requests.get(
                "https://api.spotify.com/v1/audio-features",
                headers=headers,
                params={"ids": ids_str},
                timeout=10
            )
            
            if r.ok:
                audio_features = r.json().get("audio_features", [])
                for af in audio_features:
                    if af:  # Can be None if track not found
                        features_map[af["id"]] = af
            else:
                # Log error but continue
                print(f"Audio features error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"Audio features exception: {str(e)}")
            pass  # Skip on error
    
    return features_map

def audio_features_to_mood_features(track_info, audio_features):
    """Analyze a track's audio features using LLM and generate mood-based recommendations features"""
    artist_names = ', '.join([a['name'] for a in track_info.get('artists', [])])
    track_name = track_info.get('name', '')
    
    # Build detailed feature description
    feature_text = f"""
Şarkı: "{track_name}" - {artist_names}

Audio Özellikleri:
- Energy (Enerji): {audio_features.get('energy', 0.5):.0%} (0=sakin, 1=enerjik)
- Valence (Mutluluk): {audio_features.get('valence', 0.5):.0%} (0=hüzünlü, 1=mutlu)
- Danceability (Dans Edilebilirlik): {audio_features.get('danceability', 0.5):.0%}
- Acousticness (Akustiklik): {audio_features.get('acousticness', 0.5):.0%} (0=elektronik, 1=akustik)
- Instrumentalness (Enstrümantal): {audio_features.get('instrumentalness', 0):.0%}
- Speechiness (Konuşma): {audio_features.get('speechiness', 0):.0%}
- Loudness (Ses Seviyesi): {audio_features.get('loudness', -10):.1f} dB
- Tempo: {audio_features.get('tempo', 120):.0f} BPM
- Mode: {'Majör (Neşeli)' if audio_features.get('mode', 1) == 1 else 'Minör (Melankolik)'}

Şarkının adı ve sanatçısına bakarak ŞARKI SÖZLERİNİN muhtemel temasını ve konusunu tahmin et.
Bu şarkının ruh halini, müzikal karakterini, TÜRÜNÜ, DİLİNİ ve ŞARKI SÖZLERİ TEMASINI analiz et.
Benzer özelliklere sahip şarkılar bulmak için ideal parametreleri belirle.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Sen bir müzik analisti ve öneri uzmanısın. Şarkının adı, sanatçısı ve audio özelliklerine bakarak "
                        "şarkının tüm karakteristiklerini (tür, dil, şarkı sözleri teması) analiz ediyorsun.\n\n"
                        "ÖNEMLİ KURALLAR:\n"
                        "1. Şarkının TÜRÜ (genre) ve DİLİ (language) çok önemli - mutlaka doğru belirle\n"
                        "2. Şarkı adı ve sanatçıya bakarak ŞARKI SÖZLERİ TEMASINI tahmin et (örn: aşk, ayrılık, parti, motivasyon, hüzün, nostalji, vs.)\n"
                        "3. Lyrics theme'i arama için kullanılacak, orta seviye öncelikte olmalı\n\n"
                        "Döndür: JSON object with these fields:\n"
                        "- energy, valence, danceability (0-1): enerji, mutluluk, dans edilebilirlik\n"
                        "- acousticness (0-1): akustik vs elektronik (0=elektronik, 1=akustik)\n"
                        "- instrumentalness (0-1): vokal içeriği (0=çok vokal, 1=enstrümantal)\n"
                        "- speechiness (0-1): konuşma içeriği (0=müzik, 0.33-0.66=rap, >0.66=podcast)\n"
                        "- loudness (-60 to 0): ses seviyesi dB cinsinden\n"
                        "- mode (0 or 1): minör=0, majör=1\n"
                        "- tempo (60-180): dakikadaki vuruş sayısı\n"
                        "- primary_genre: şarkının ANA türü (rap, pop, rock, jazz, hip-hop, indie, classical, electronic, folk, country, r&b, vs.)\n"
                        "- genres: 2-3 müzik türü array - primary_genre mutlaka ilk sırada olmalı\n"
                        "- language: şarkının dili (Turkish, English, Spanish, French, Korean, Japanese, vs.)\n"
                        "- lyrics_theme: şarkı sözlerinin ana teması (love, heartbreak, party, motivation, sadness, nostalgia, social, protest, fun, romance, vs.)\n"
                        "- lyrics_keywords: şarkı sözleri için 2-3 kelime array (arama için)\n"
                        "- keywords: 3-5 genel arama kelimesi (mood/stil tanımlayıcı)\n"
                        "- artist_style: kısa sanatçı stili açıklaması\n"
                        "- explanation: Bu şarkının ruh halini, türünü, dilini, şarkı sözü temasını ve neden bu özellikleri seçtiğini açıkla (2-3 cümle)"
                    ),
                },
                {"role": "user", "content": feature_text},
            ],
        )
        
        features_json = response.choices[0].message.content
        features = parse_features(features_json)
        
        # Add explanation if available
        try:
            data = json.loads(features_json)
            features['explanation'] = data.get('explanation', '')
        except:
            features['explanation'] = ''
        
        return features
        
    except Exception as e:
        print(f"LLM audio analysis error: {e}")
        # Fallback: use similar features with slight variation
        return {
            'energy': max(0, min(1, audio_features.get('energy', 0.5) + random.uniform(-0.1, 0.1))),
            'valence': max(0, min(1, audio_features.get('valence', 0.5) + random.uniform(-0.1, 0.1))),
            'danceability': max(0, min(1, audio_features.get('danceability', 0.5) + random.uniform(-0.1, 0.1))),
            'acousticness': audio_features.get('acousticness', 0.5),
            'instrumentalness': audio_features.get('instrumentalness', 0),
            'speechiness': audio_features.get('speechiness', 0.05),
            'loudness': audio_features.get('loudness', -10),
            'mode': audio_features.get('mode', 1),
            'tempo': audio_features.get('tempo', 120),
            'primary_genre': 'pop',
            'genres': ['pop'],
            'language': 'English',
            'lyrics_theme': '',
            'lyrics_keywords': [],
            'keywords': [],
            'explanation': 'Audio features analizi kullanılıyor.'
        }

def get_similar_tracks_by_seed(token, track_id, audio_features=None, artist_ids=None, limit=10):
    """Get similar tracks using search-based approach (recommendations API is restricted)"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get the original track details
    try:
        r = requests.get(
            f"https://api.spotify.com/v1/tracks/{track_id}",
            headers=headers,
            timeout=10
        )
        if not r.ok:
            print(f"Failed to get track details: {r.status_code}")
            return []
        
        track = r.json()
        artist_names = [a['name'] for a in track.get('artists', [])]
        track_name = track.get('name', '')
        
    except Exception as e:
        print(f"Error getting track details: {str(e)}")
        return []
    
    # Build search queries based on artist and audio features
    queries = []
    all_tracks = []
    seen_ids = set([track_id])  # Exclude the seed track
    
    # Query 1: Search by artist name
    if artist_names:
        for artist in artist_names[:2]:
            queries.append(f"artist:{artist}")
    
    # Query 2: Search by genre/mood based on audio features
    if audio_features:
        energy = audio_features.get('energy', 0.5)
        valence = audio_features.get('valence', 0.5)
        acousticness = audio_features.get('acousticness', 0.5)
        
        # Determine mood keywords
        if energy > 0.6 and valence > 0.6:
            queries.append("upbeat energetic")
        elif energy > 0.6 and valence < 0.4:
            queries.append("intense powerful")
        elif energy < 0.4 and valence > 0.6:
            queries.append("calm peaceful")
        elif energy < 0.4 and valence < 0.4:
            queries.append("sad melancholic")
        
        # Add acoustic/electronic
        if acousticness > 0.7:
            queries.append("acoustic")
        elif acousticness < 0.3:
            queries.append("electronic")
    
    # Search with each query
    for query in queries[:4]:  # Limit to 4 queries
        try:
            params = {
                "q": query,
                "type": "track",
                "limit": min(20, limit * 2),
                "offset": 0
            }
            
            r = requests.get(
                "https://api.spotify.com/v1/search",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if r.ok:
                tracks = r.json().get("tracks", {}).get("items", [])
                for t in tracks:
                    tid = t.get('id')
                    if tid and tid not in seen_ids:
                        seen_ids.add(tid)
                        all_tracks.append(t)
                        if len(all_tracks) >= limit * 3:
                            break
        except Exception as e:
            print(f"Search error: {str(e)}")
            continue
        
        if len(all_tracks) >= limit * 3:
            break
    
    # Shuffle and return
    if all_tracks:
        random.shuffle(all_tracks)
        return all_tracks[:limit]
    
    return []

def generate_similarity_explanation(source_track, source_features, similar_tracks_count):
    """Generate an LLM explanation about why similar tracks were chosen"""
    artist_names = ', '.join([a['name'] for a in source_track.get('artists', [])])
    
    prompt = f"""
Kaynak Şarkı: "{source_track['name']}" - {artist_names}

Audio Features:
- Energy (Enerji): {source_features.get('energy', 0):.0%} (0=sakin, 1=enerjik)
- Valence (Mutluluk): {source_features.get('valence', 0):.0%} (0=hüzünlü, 1=mutlu)
- Danceability (Dans Edilebilirlik): {source_features.get('danceability', 0):.0%}
- Acousticness (Akustiklik): {source_features.get('acousticness', 0):.0%} (0=elektronik, 1=akustik)
- Tempo: {source_features.get('tempo', 0):.0f} BPM
- Mode: {'Majör (Neşeli)' if source_features.get('mode', 1) == 1 else 'Minör (Melankolik)'}

Bu şarkının ruh halini ve müzikal özelliklerini 2-3 cümle ile açıkla. 
Bulunan {similar_tracks_count} benzer şarkının neden bu özelliklere göre seçildiğini belirt.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "Sen bir müzik uzmanısın. Audio features'lara bakarak şarkıların ruh halini ve benzerliklerini açıklıyorsun."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM explanation error: {e}")
        return f'Bu şarkı, {source_features.get("energy", 0):.0%} enerji ve {source_features.get("valence", 0):.0%} mutluluk seviyesiyle karakterize ediliyor. Benzer audio özelliklere sahip {similar_tracks_count} şarkı bulundu.'

def get_recommendations(token, features, limit=10):
    """Get track recommendations - uses search since recommendations API is restricted"""
    # Directly use search-based approach since recommendations API returns 404
    all_tracks = get_recommendations_via_search(token, features, limit=limit)
    return all_tracks

def evaluate_recommendations(mood_text, features, tracks, audio_features_map):
    """LLM evaluates if recommendations match user's mood and provides explanation"""
    
    # Prepare track summary for LLM
    track_summaries = []
    for i, track in enumerate(tracks[:5], 1):  # Analyze first 5 tracks
        track_id = track.get('id')
        artist_names = ', '.join([a['name'] for a in track.get('artists', [])])
        
        summary = {
            'name': track['name'],
            'artist': artist_names,
            'popularity': track.get('popularity', 0)
        }
        
        # Add audio features if available
        if track_id and track_id in audio_features_map:
            af = audio_features_map[track_id]
            summary['features'] = {
                'energy': round(af.get('energy', 0), 2),
                'valence': round(af.get('valence', 0), 2),
                'danceability': round(af.get('danceability', 0), 2),
                'tempo': round(af.get('tempo', 0), 0),
                'acousticness': round(af.get('acousticness', 0), 2),
                'mode': 'major' if af.get('mode', 1) == 1 else 'minor'
            }
        
        track_summaries.append(summary)
    
    # Create evaluation prompt
    prompt = f"""Kullanıcının ruh hali: "{mood_text}"

Hedef müzik özellikleri:
- Enerji: {features['energy']:.0%}
- Mutluluk (Valence): {features['valence']:.0%}
- Dans: {features['danceability']:.0%}
- Tempo: {features['tempo']:.0f} BPM
- Akustik: {features['acousticness']:.0%}
- Ton: {'Majör (mutlu)' if features['mode'] == 1 else 'Minör (üzgün)'}

Önerilen ilk 5 şarkı:
{json.dumps(track_summaries, indent=2, ensure_ascii=False)}

Görevin:
1. Bu şarkılar kullanıcının ruh haline uygun mu? (1-10 puan ver)
2. Neden bu şarkıları önerdik? (2-3 cümle, samimi ve kişisel bir dille)
3. Hangi şarkılar en uygun? (şarkı isimlerini belirt)

JSON formatında cevap ver:
{{
  "score": <1-10 arası puan>,
  "explanation": "<açıklama metni>",
  "best_matches": ["<şarkı adı 1>", "<şarkı adı 2>"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": "Sen bir müzik uzmanısın. Kullanıcıya samimi, arkadaşça ve kişisel bir dille konuş. Türkçe cevap ver."
                },
                {"role": "user", "content": prompt}
            ]
        )
        
        evaluation = json.loads(response.choices[0].message.content)
        return evaluation
    
    except Exception as e:
        # Fallback if LLM fails
        return {
            "score": 7,
            "explanation": f"Bu şarkılar senin '{mood_text}' ruh haline göre seçildi. Her birinin enerji, tempo ve atmosfer özellikleri isteğinle uyumlu!",
            "best_matches": [tracks[0]['name'], tracks[1]['name']] if len(tracks) >= 2 else []
        }

# Initialize active tab in session state
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Custom tab selector using radio buttons
tab_options = ["🎵 Şarkı Öner", "🎧 Şarkıdan Bul", "📜 Geçmiş"]
selected_tab = st.radio("", tab_options, index=st.session_state.active_tab, horizontal=True, label_visibility="collapsed", key="tab_selector")

# Update active tab based on selection
st.session_state.active_tab = tab_options.index(selected_tab)

# Apply custom CSS for tab-like appearance
st.markdown("""
<style>
    /* Tab container styling */
    div[data-testid="stRadio"] {
        background: transparent;
        padding: 0;
        margin-bottom: 1.5rem;
    }
    
    div[data-testid="stRadio"] > div {
        gap: 0.5rem;
        background: transparent;
    }
    
    div[data-testid="stRadio"] > div > label {
        display: none !important;
    }
    
    /* Individual tab buttons */
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        border: 2px solid #34495e !important;
        color: #ecf0f1 !important;
        display: inline-block !important;
        margin-right: 0.5rem !important;
        font-size: 0.9rem !important;
    }
    
    /* Hover effect */
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Active/checked tab */
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Hide radio circles completely */
    div[data-testid="stRadio"] input[type="radio"] {
        opacity: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
    }
    
    div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Render selected tab content
if st.session_state.active_tab == 0:  # Şarkı Öner tab
    # Welcome message
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
        <h3 style="color: #495057; margin-top: 0;">✨ Hoş Geldiniz!</h3>
        <p style="color: #6c757d; margin: 0; line-height: 1.6;">
            Şu an nasıl hissediyorsunuz? Duygularınızı, enerji seviyenizi veya yapmak istediğiniz aktiviteyi anlat. 
            Yapay zeka ruh halinizi analiz edip mükemmel şarkıları bulacak! 🎧
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content with enhanced styling
    st.markdown("### 🎭 Ruh Halinizi Anlatın")
    mood_text = st.text_area(
        "",
        placeholder="Örn: Bugün hava çok güzel, enerji doluyum ve dans edebileceğim neşeli şarkılar istiyorum...",
        height=150,
        label_visibility="collapsed"
    )
    
    st.markdown("")  # Spacing

    if st.button("🎵 Şarkı Öner", use_container_width=True, key="recommend_button", type="primary"):
        if not mood_text:
            st.warning("⚠️ Lütfen bir ruh hali yazın.")
        else:
            if not OPENAI_API_KEY:
                st.error("❌ OPENAI_API_KEY env degiskeni tanimli degil.")
                st.stop()
            if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
                st.error("❌ Spotify API icin SPOTIFY_CLIENT_ID ve SPOTIFY_CLIENT_SECRET tanimli degil.")
                st.stop()

        # Progress steps
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: LLM Analysis
        status_text.text("🤖 AI ruh halini analiz ediyor...")
        progress_bar.progress(25)
        raw_json = mood_to_features(mood_text)

        try:
            features = parse_features(raw_json)
        except Exception:
            st.error("❌ LLM'den beklenen JSON gelmedi.")
            st.write(raw_json)
            st.stop()
        
        progress_bar.progress(50)
        status_text.text("🔍 Spotify'dan şarkılar aranıyor...")

        # Step 2: Get Token
        try:
            token = get_spotify_token()
        except Exception as exc:
            st.error(f"❌ Spotify token hatası: {str(exc)}")
            st.stop()
        
        progress_bar.progress(75)
        
        # Step 3: Get Recommendations
        try:
            tracks = get_recommendations(token, features, limit=num_songs)
            
            # Get audio features for all tracks
            track_ids = [t['id'] for t in tracks if t.get('id')]
            audio_features_map = get_audio_features(token, track_ids)
            
            progress_bar.progress(85)
            status_text.text("🤔 AI önerileri değerlendiriyor...")
            
            # Step 4: LLM evaluates recommendations
            evaluation = evaluate_recommendations(mood_text, features, tracks, audio_features_map)
            
            progress_bar.progress(100)
            status_text.text(f"✅ {len(tracks)} şarkı bulundu ve değerlendirildi!")
        except Exception as exc:
            st.error(f"❌ Şarkı arama hatası: {str(exc)}")
            import traceback
            st.code(traceback.format_exc())
            st.stop()
        
        st.balloons()
        
        # Save to database and update session state
        import datetime
        
        # Save to database
        record_id = db.add_search(
            mood=mood_text,
            features=features,
            tracks=tracks,
            audio_features_map=audio_features_map,
            evaluation=evaluation
        )
        
        # Add to session state history
        new_entry = {
            'id': record_id,
            'timestamp': datetime.datetime.now(),
            'mood': mood_text,
            'features': features,
            'tracks': tracks,
            'audio_features_map': audio_features_map,
            'evaluation': evaluation,
            'type': 'mood'
        }
        st.session_state.history.insert(0, new_entry)
        st.session_state.combined_history.insert(0, new_entry)
        
        # Display evaluation message BEFORE features
        st.markdown("---")
        
        # Show AI evaluation in a nice card
        score = evaluation.get('score', 0)
        explanation = evaluation.get('explanation', '')
        best_matches = evaluation.get('best_matches', [])
        
        # Score color based on rating
        if score >= 8:
            score_color = "#00FF88"  # Bright neon green
            emoji = "🎯"
        elif score >= 6:
            score_color = "#FFD700"  # Gold
            emoji = "👍"
        else:
            score_color = "#FF6B6B"  # Bright red
            emoji = "🤔"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: white; margin: 0 0 1rem 0;">{emoji} AI Değerlendirmesi</h3>
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                <p style="color: white; font-size: 1.1rem; margin: 0; line-height: 1.6;">
                    {explanation}
                </p>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px;">
                    <span style="color: white; font-weight: bold;">Uygunluk Puanı:</span>
                    <span style="color: {score_color}; font-size: 1.5rem; font-weight: bold; margin-left: 0.5rem;">
                        {score}/10
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show best matches if available
        if best_matches:
            st.markdown("**✨ En Uygun Şarkılar:**")
            for match in best_matches:
                st.markdown(f"- 🎵 {match}")
            st.markdown("---")
        
        # Display Audio Features in nice cards
        st.markdown("---")
        st.subheader("📊 Ruh Hali Analizi")
        
        # Primary features
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚡ Enerji", f"{features['energy']:.0%}")
        with col2:
            st.metric("😊 Mutluluk", f"{features['valence']:.0%}")
        with col3:
            st.metric("💃 Dans", f"{features['danceability']:.0%}")
        with col4:
            st.metric("🥁 Tempo", f"{features['tempo']:.0f} BPM")
        
        # Secondary features
        st.markdown("")
        col5, col6, col7, col8 = st.columns(4)
        with col5:
            st.metric("🎸 Akustik", f"{features['acousticness']:.0%}")
        with col6:
            st.metric("🎼 Enstrümantal", f"{features['instrumentalness']:.0%}")
        with col7:
            st.metric("🎤 Konuşma", f"{features['speechiness']:.0%}")
        with col8:
            mode_text = "Majör 🌞" if features['mode'] == 1 else "Minör 🌙"
            st.metric("🎵 Ton", mode_text)
        
        # Display genres and keywords as badges
        if features.get('genres') or features.get('keywords'):
            st.markdown("")
            badge_html = ""
            if features.get('genres'):
                badge_html += "<div style='margin: 1rem 0;'>🎵 <strong>Türler:</strong> "
                for genre in features['genres']:
                    badge_html += f'<span class="feature-badge">{genre}</span> '
                badge_html += "</div>"
            
            if features.get('keywords'):
                badge_html += "<div style='margin: 1rem 0;'>🔑 <strong>Anahtar Kelimeler:</strong> "
                for kw in features['keywords']:
                    badge_html += f'<span class="feature-badge">{kw}</span> '
                badge_html += "</div>"
            
            st.markdown(badge_html, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("🎶 Önerilen Şarkılar")
        
        if not tracks:
            st.warning("⚠️ Şarkı bulunamadı. Farklı bir ruh hali dene.")
        else:
            for i, t in enumerate(tracks, 1):
                album_images = t.get('album', {}).get('images', [])
                album_img = album_images[0].get('url', '') if album_images else ''
                artist_names = ', '.join([a['name'] for a in t.get('artists', [])])
                album_name = t.get('album', {}).get('name', 'Unknown Album')
                duration_ms = t.get('duration_ms', 0)
                duration_min = duration_ms // 60000
                duration_sec = (duration_ms % 60000) // 1000
                popularity = t.get('popularity', 0)
                
                # Create card for each song
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        if album_img:
                            st.image(album_img, use_container_width=True)
                        else:
                            st.write("🎵")
                    
                    with col2:
                        st.markdown(f"### {i}. {t['name']}")
                        st.markdown(f"**🎤 {artist_names}** · 💿 {album_name}")
                        
                        info_col1, info_col2, info_col3 = st.columns([2, 2, 3])
                        with info_col1:
                            st.caption(f"⏱️ {duration_min}:{duration_sec:02d}")
                        with info_col2:
                            st.caption(f"⭐ {popularity}/100")
                        with info_col3:
                            if t.get('external_urls', {}).get('spotify'):
                                st.link_button("▶️ Spotify'da Dinle", t['external_urls']['spotify'], use_container_width=True)
                        
                        # Show actual audio features if available
                        track_id = t.get('id')
                        if track_id and track_id in audio_features_map:
                            af = audio_features_map[track_id]
                            with st.expander("📊 Şarkının Gerçek Özellikleri (Spotify)"):
                                feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
                                with feat_col1:
                                    st.metric("⚡ Enerji", f"{af.get('energy', 0):.0%}", 
                                             delta=f"{(af.get('energy', 0) - features['energy']):.0%}")
                                with feat_col2:
                                    st.metric("😊 Mutluluk", f"{af.get('valence', 0):.0%}", 
                                             delta=f"{(af.get('valence', 0) - features['valence']):.0%}")
                                with feat_col3:
                                    st.metric("💃 Dans", f"{af.get('danceability', 0):.0%}", 
                                             delta=f"{(af.get('danceability', 0) - features['danceability']):.0%}")
                                with feat_col4:
                                    st.metric("🥁 Tempo", f"{af.get('tempo', 0):.0f}", 
                                             delta=f"{(af.get('tempo', 0) - features['tempo']):.0f}")
                                
                                feat_col5, feat_col6, feat_col7, feat_col8 = st.columns(4)
                                with feat_col5:
                                    st.metric("🎸 Akustik", f"{af.get('acousticness', 0):.0%}", 
                                             delta=f"{(af.get('acousticness', 0) - features['acousticness']):.0%}")
                                with feat_col6:
                                    st.metric("🎼 Enstrümantal", f"{af.get('instrumentalness', 0):.0%}", 
                                             delta=f"{(af.get('instrumentalness', 0) - features['instrumentalness']):.0%}")
                                with feat_col7:
                                    st.metric("🎤 Konuşma", f"{af.get('speechiness', 0):.0%}", 
                                             delta=f"{(af.get('speechiness', 0) - features['speechiness']):.0%}")
                                with feat_col8:
                                    mode_text = "Majör" if af.get('mode', 1) == 1 else "Minör"
                                    target_mode = "Majör" if features['mode'] == 1 else "Minör"
                                    match = "✓" if mode_text == target_mode else "✗"
                                    st.metric("🎵 Ton", mode_text, delta=match)
                    
                    st.divider()

elif st.session_state.active_tab == 1:  # Şarkıdan Bul tab
    st.markdown("### 🎧 Şarkıdan Şarkı Bul")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;">
        <h3 style="color: #495057; margin-top: 0;">🎵 Sevdiğin Şarkıya Benzer Şarkılar Bul</h3>
        <p style="color: #6c757d; margin: 0; line-height: 1.6;">
            Bir şarkı adı veya sanatçı yaz, o şarkının ruh haline göre benzer şarkılar bulalım! 
            AI şarkının duygusal özelliklerini analiz edip size benzer şarkılar önerecek. 🎶
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("**🔍 Şarkı Ara**")
        search_query = st.text_input(
            "",
            placeholder="Örn: Bohemian Rhapsody Queen veya Just Dance Lady Gaga",
            label_visibility="collapsed",
            key="song_search"
        )
    
    with col2:
        st.markdown("**🎵 Öneri Sayısı**")
        similar_song_count = st.slider("", min_value=5, max_value=15, value=8, step=1, label_visibility="collapsed", key="similar_count")
    
    if st.button("🔍 Benzer Şarkılar Bul", use_container_width=True, key="find_similar_button", type="primary"):
        if not search_query:
            st.warning("⚠️ Lütfen bir şarkı adı veya sanatçı yazın.")
        else:
            if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
                st.error("❌ Spotify API icin SPOTIFY_CLIENT_ID ve SPOTIFY_CLIENT_SECRET tanimli degil.")
                st.stop()
            
            # Progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Search for the song
            status_text.text("🔍 Şarkı aranıyor...")
            progress_bar.progress(25)
            
            try:
                token = get_spotify_token()
                
                # Search for the track
                headers = {"Authorization": f"Bearer {token}"}
                params = {
                    "q": search_query,
                    "type": "track",
                    "limit": 5
                }
                
                r = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params, timeout=10)
                
                if not r.ok:
                    st.error(f"❌ Spotify arama hatası: {r.status_code}")
                    st.stop()
                
                search_results = r.json().get("tracks", {}).get("items", [])
                
                if not search_results:
                    st.warning("⚠️ Şarkı bulunamadı. Farklı bir şarkı adı deneyin.")
                    st.stop()
                
                # Select track (always use first result for simplicity)
                selected_track = search_results[0]
                
                # Show what we found
                progress_bar.progress(50)
                status_text.text(f"✅ Şarkı bulundu: {selected_track['name']}")
                
                # Show the found track info
                st.markdown("**🎵 Bulunan Şarkı:**")
                col_img, col_info = st.columns([1, 5])
                with col_img:
                    album_images = selected_track.get('album', {}).get('images', [])
                    if album_images:
                        st.image(album_images[-1].get('url', ''), width=80)
                with col_info:
                    artist_names = ', '.join([a['name'] for a in selected_track.get('artists', [])])
                    st.markdown(f"**{selected_track['name']}**")
                    st.caption(f"🎤 {artist_names}")
                
                import time
                time.sleep(0.5)  # Small delay for user to see
                
                progress_bar.progress(60)
                status_text.text("🎵 Şarkı özellikleri alınıyor...")
                
                # Get audio features for the selected track
                track_id = selected_track.get('id')
                
                if not track_id:
                    st.error("❌ Şarkı ID'si bulunamadı.")
                    st.stop()
                
                track_ids = [track_id]
                audio_features_map = get_audio_features(token, track_ids)
                
                has_real_features = track_id in audio_features_map and audio_features_map[track_id] is not None
                
                if not has_real_features:
                    # Use default/estimated features based on general characteristics
                    source_features = {
                        'energy': 0.5,
                        'valence': 0.5,
                        'danceability': 0.5,
                        'acousticness': 0.3,
                        'instrumentalness': 0.0,
                        'speechiness': 0.05,
                        'loudness': -10.0,
                        'mode': 1,
                        'tempo': 120,
                    }
                else:
                    source_features = audio_features_map[track_id]
                
                progress_bar.progress(70)
                status_text.text("🤖 AI ile şarkı özellikleri analiz ediliyor...")
                
                # Use LLM to analyze audio features and generate mood-based recommendations features
                mood_features = audio_features_to_mood_features(selected_track, source_features)
                
                # Display the AI analysis
                if mood_features.get('explanation'):
                    st.info(f"🎵 **AI Analizi:** {mood_features['explanation']}")
                
                # Show genre, language, and lyrics theme
                info_cols = st.columns(3)
                with info_cols[0]:
                    primary_genre = mood_features.get('primary_genre', 'pop')
                    st.markdown(f"**🎸 Tür:** {primary_genre.title()}")
                with info_cols[1]:
                    language = mood_features.get('language', 'English')
                    st.markdown(f"**🌍 Dil:** {language}")
                with info_cols[2]:
                    lyrics_theme = mood_features.get('lyrics_theme', '')
                    if lyrics_theme:
                        st.markdown(f"**📝 Şarkı Sözü Teması:** {lyrics_theme.title()}")
                    else:
                        st.markdown(f"**📝 Şarkı Sözü:** -")
                
                # Show the features as percentages (like in mood search)
                st.markdown("**📊 Hedeflenen Müzikal Özellikler:**")
                feat_cols = st.columns(4)
                with feat_cols[0]:
                    st.metric("Enerji", f"{mood_features.get('energy', 0.5):.0%}")
                with feat_cols[1]:
                    st.metric("Mutluluk", f"{mood_features.get('valence', 0.5):.0%}")
                with feat_cols[2]:
                    st.metric("Dans", f"{mood_features.get('danceability', 0.5):.0%}")
                with feat_cols[3]:
                    st.metric("Tempo", f"{mood_features.get('tempo', 120):.0f} BPM")
                
                progress_bar.progress(80)
                status_text.text("🔍 Bu özelliklere uygun şarkılar aranıyor...")
                
                # Search for similar tracks using the LLM-generated features
                similar_tracks = get_recommendations_via_search(token, mood_features, limit=similar_song_count)
                
                # Remove the seed track if it appears in results
                similar_tracks = [t for t in similar_tracks if t.get('id') != track_id]
                
                # If still need more tracks, get a few extra
                if len(similar_tracks) < similar_song_count:
                    extra_needed = similar_song_count - len(similar_tracks)
                    extra_tracks = get_recommendations_via_search(token, mood_features, limit=extra_needed * 2)
                    for t in extra_tracks:
                        if t.get('id') != track_id and t not in similar_tracks:
                            similar_tracks.append(t)
                            if len(similar_tracks) >= similar_song_count:
                                break
                
                # Final check: if still no results, show error and stop
                if not similar_tracks:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ Hiç benzer şarkı bulunamadı. Lütfen başka bir şarkı deneyin.")
                    st.info("💡 İpucu: Daha popüler şarkılar deneyin veya farklı bir şarkı seçin.")
                    st.stop()
                
                # Trim to requested count
                similar_tracks = similar_tracks[:similar_song_count]
                
                # Get audio features for similar tracks
                similar_track_ids = [t['id'] for t in similar_tracks if t.get('id')]
                similar_audio_features = get_audio_features(token, similar_track_ids)
                
                progress_bar.progress(90)
                status_text.text("✨ Sonuçlar hazırlanıyor...")
                
                # Get artist names for description and database
                artist_names = ', '.join([a['name'] for a in selected_track.get('artists', [])])
                
                # Use the LLM's explanation as mood description
                mood_description = mood_features.get('explanation', f'"{selected_track["name"]}" - {artist_names} şarkısına benzer {len(similar_tracks)} şarkı bulundu.')
                
                progress_bar.progress(100)
                status_text.text(f"✅ {len(similar_tracks)} benzer şarkı bulundu!")
                
                st.balloons()
                
                # Save to database
                import datetime
                
                record_id = db.add_song_discovery(
                    source_track=selected_track['name'],
                    source_artist=artist_names,
                    source_track_id=track_id,
                    source_features=source_features if has_real_features else None,
                    similar_tracks=similar_tracks,
                    mood_description=mood_description
                )
                
                # Update session state
                new_entry = {
                    'id': record_id,
                    'timestamp': datetime.datetime.now(),
                    'source_track': selected_track['name'],
                    'source_artist': artist_names,
                    'source_track_id': track_id,
                    'source_features': source_features if has_real_features else None,
                    'similar_tracks': similar_tracks,
                    'mood_description': mood_description,
                    'type': 'song'
                }
                st.session_state.song_discovery_history.insert(0, new_entry)
                st.session_state.combined_history.insert(0, new_entry)
                
                # Display source song
                st.markdown("---")
                st.markdown("### 🎵 Kaynak Şarkı")
                
                col_img, col_info = st.columns([1, 4])
                
                with col_img:
                    album_images = selected_track.get('album', {}).get('images', [])
                    if album_images:
                        st.image(album_images[0].get('url', ''), use_container_width=True)
                
                with col_info:
                    st.markdown(f"## {selected_track['name']}")
                    st.markdown(f"**🎤 {artist_names}**")
                    st.markdown(f"**💿 {selected_track.get('album', {}).get('name', 'Unknown')}**")
                    
                    if selected_track.get('external_urls', {}).get('spotify'):
                        st.link_button("▶️ Spotify'da Dinle", selected_track['external_urls']['spotify'])
                
                # Show mood description
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
                    <div style="color: white;">
                        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem; margin-right: 0.5rem;">🤖</span>
                            <strong style="font-size: 1.1rem;">Şarkının Ruh Hali</strong>
                        </div>
                        <p style="margin: 0; line-height: 1.7; color: white; font-size: 1rem;">
                            {mood_description}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show source features only if we have real data
                if has_real_features:
                    st.markdown("**📊 Şarkı Özellikleri:**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("⚡ Enerji", f"{source_features.get('energy', 0):.0%}")
                    with col2:
                        st.metric("😊 Mutluluk", f"{source_features.get('valence', 0):.0%}")
                    with col3:
                        st.metric("💃 Dans", f"{source_features.get('danceability', 0):.0%}")
                    with col4:
                        st.metric("🥁 Tempo", f"{source_features.get('tempo', 0):.0f}")
                else:
                    st.info("💡 Bu şarkı için Spotify'ın öneri algoritması kullanıldı - benzer tarz ve duyguya sahip şarkılar listelendi.")
                
                st.markdown("---")
                st.markdown(f"### 🎶 Benzer {len(similar_tracks)} Şarkı")
                
                # Display similar tracks
                for i, t in enumerate(similar_tracks, 1):
                    album_images = t.get('album', {}).get('images', [])
                    album_img = album_images[-1].get('url', '') if album_images else ''
                    artist_names_track = ', '.join([a['name'] for a in t.get('artists', [])])
                    
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        
                        with col1:
                            if album_img:
                                st.image(album_img, use_container_width=True)
                        
                        with col2:
                            st.markdown(f"### {i}. {t['name']}")
                            st.markdown(f"**🎤 {artist_names_track}**")
                            
                            info_col1, info_col2 = st.columns([3, 2])
                            with info_col1:
                                duration_ms = t.get('duration_ms', 0)
                                duration_min = duration_ms // 60000
                                duration_sec = (duration_ms % 60000) // 1000
                                popularity = t.get('popularity', 0)
                                st.caption(f"⏱️ {duration_min}:{duration_sec:02d} • ⭐ {popularity}/100")
                            
                            with info_col2:
                                if t.get('external_urls', {}).get('spotify'):
                                    st.link_button("▶️ Dinle", t['external_urls']['spotify'], use_container_width=True)
                            
                            # Show similarity metrics only if we have real source features
                            track_id = t.get('id')
                            if has_real_features and track_id and track_id in similar_audio_features:
                                af = similar_audio_features[track_id]
                                with st.expander("📊 Audio Features Karşılaştırması"):
                                    feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)
                                    with feat_col1:
                                        delta_energy = af.get('energy', 0) - source_features.get('energy', 0)
                                        st.metric("⚡ Enerji", f"{af.get('energy', 0):.0%}", 
                                                 delta=f"{delta_energy:.0%}")
                                    with feat_col2:
                                        delta_valence = af.get('valence', 0) - source_features.get('valence', 0)
                                        st.metric("😊 Mutluluk", f"{af.get('valence', 0):.0%}", 
                                                 delta=f"{delta_valence:.0%}")
                                    with feat_col3:
                                        delta_dance = af.get('danceability', 0) - source_features.get('danceability', 0)
                                        st.metric("💃 Dans", f"{af.get('danceability', 0):.0%}", 
                                                 delta=f"{delta_dance:.0%}")
                                    with feat_col4:
                                        delta_tempo = af.get('tempo', 0) - source_features.get('tempo', 0)
                                        st.metric("🥁 Tempo", f"{af.get('tempo', 0):.0f}", 
                                                 delta=f"{delta_tempo:.0f}")
                        
                        st.divider()
                
            except Exception as exc:
                st.error(f"❌ Hata: {str(exc)}")
                import traceback
                st.code(traceback.format_exc())

elif st.session_state.active_tab == 2:  # Geçmiş tab
    st.markdown("### 📜 Arama Geçmişi")
    
    if not st.session_state.combined_history:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); 
                    padding: 3rem 2rem; border-radius: 16px; text-align: center; margin: 2rem 0;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">📭</div>
            <h3 style="color: #1976d2; margin: 1rem 0;">Henüz Arama Yapmadınız</h3>
            <p style="color: #42a5f5; font-size: 1.1rem; margin: 0;">
                Ruh halinize göre veya sevdiğiniz şarkılara benzer müzikler keşfedin!
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Statistics section
        total_combined = len(st.session_state.combined_history)
        total_mood = len([e for e in st.session_state.combined_history if e.get('type') == 'mood'])
        total_song = len([e for e in st.session_state.combined_history if e.get('type') == 'song'])
        
        # Average score for mood searches only
        mood_searches_with_scores = [e for e in st.session_state.combined_history 
                                     if e.get('type') == 'mood' and e.get('evaluation')]
        avg_score = sum([e.get('evaluation', {}).get('score', 0) for e in mood_searches_with_scores]) / max(len(mood_searches_with_scores), 1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
                <div style="font-size: 2rem; font-weight: 700;">{total_mood}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Ruh Hali Araması</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); 
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎧</div>
                <div style="font-size: 2rem; font-weight: 700;">{total_song}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Şarkıdan Keşif</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            total_tracks = sum([len(e.get('tracks', e.get('similar_tracks', []))) for e in st.session_state.combined_history])
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        padding: 1.5rem; border-radius: 12px; text-align: center; color: white;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎵</div>
                <div style="font-size: 2rem; font-weight: 700;">{total_tracks}</div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Önerilen Şarkı</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("")  # Spacing
        
        col_left, col_right = st.columns([3, 1])
        with col_left:
            st.markdown(f"**📋 Toplam {total_combined} kayıt** ({total_mood} ruh hali, {total_song} şarkı keşfi)")
        with col_right:
            if st.button("🗑️ Tümünü Sil", use_container_width=True, key="clear_history_button", type="secondary"):
                # Clear both databases
                deleted_mood = db.clear_all_history()
                deleted_song = db.clear_song_discovery_history()
                # Clear session state
                st.session_state.history = []
                st.session_state.song_discovery_history = []
                st.session_state.combined_history = []
                st.success(f"✅ {deleted_mood + deleted_song} kayıt silindi!")
                st.rerun()
        
        st.markdown("---")
        
        # Display each search in combined history
        for idx, entry in enumerate(st.session_state.combined_history, 1):
            entry_type = entry.get('type', 'mood')
            timestamp_str = entry['timestamp'].strftime('%d %B %Y, %H:%M')
            
            # Different styling based on type
            if entry_type == 'mood':
                score = entry.get('evaluation', {}).get('score', 0)
                score_emoji = "🎯" if score >= 8 else "👍" if score >= 6 else "🤔"
                
                with st.expander(
                    f"{score_emoji} **Ruh Hali #{idx}** - {timestamp_str} 🎭", 
                    expanded=(idx == 1)
                ):
                    # Mood display with nice styling
                    mood_text = entry.get('mood', 'Ruh hali bilgisi yok')
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <strong style="color: #495057;">🎭 Ruh Hali:</strong><br>
                        <p style="color: #6c757d; margin: 0.5rem 0 0 0; font-size: 1.05rem; line-height: 1.6;">
                            "{mood_text}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show evaluation if available
                    if entry.get('evaluation'):
                        eval_data = entry['evaluation']
                        score = eval_data.get('score', 0)
                        explanation = eval_data.get('explanation', '')
                        
                        # Score color
                        if score >= 8:
                            score_color = "#00ff88"
                        elif score >= 6:
                            score_color = "#ffd700"
                        else:
                            score_color = "#ff6b6b"
                        
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
                            <div style="color: white;">
                                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🤖</span>
                                    <strong style="font-size: 1.1rem;">AI Değerlendirmesi</strong>
                                </div>
                                <p style="margin: 0 0 1rem 0; line-height: 1.7; color: white; font-size: 1rem;">
                                    {explanation}
                                </p>
                                <div style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; 
                                            display: inline-block;">
                                    <strong>Uygunluk Puanı:</strong> 
                                    <span style="font-size: 1.5rem; color: {score_color}; font-weight: bold; margin-left: 0.5rem;">
                                        {score}/10
                                    </span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show features summary
                    features = entry['features']
                    st.markdown("**📊 Müzik Özellikleri:**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("⚡ Enerji", f"{features['energy']:.0%}")
                    with col2:
                        st.metric("😊 Mutluluk", f"{features['valence']:.0%}")
                    with col3:
                        st.metric("💃 Dans", f"{features['danceability']:.0%}")
                    with col4:
                        st.metric("🥁 Tempo", f"{features['tempo']:.0f}")
                    
                    # Show genre badges
                    if features.get('genres'):
                        st.markdown("")
                        badge_html = "<div style='margin: 0.5rem 0;'><strong style='color: #495057;'>🎵 Türler:</strong> "
                        for genre in features['genres']:
                            badge_html += f'<span class="feature-badge">{genre}</span> '
                        badge_html += "</div>"
                        st.markdown(badge_html, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.markdown(f"**🎶 Önerilen Şarkılar** ({len(entry['tracks'])} adet)")
                    
                    # Display tracks
                    for i, t in enumerate(entry['tracks'][:5], 1):  # Show first 5
                        artist_names_track = ', '.join([a['name'] for a in t.get('artists', [])])
                        track_url = t.get('external_urls', {}).get('spotify', '')
                        
                        if track_url:
                            st.markdown(f"**{i}.** [{t['name']}]({track_url}) - {artist_names_track}")
                        else:
                            st.markdown(f"**{i}.** {t['name']} - {artist_names_track}")
                    
                    if len(entry['tracks']) > 5:
                        st.caption(f"... ve {len(entry['tracks']) - 5} şarkı daha")
            
            else:  # song type
                
                with st.expander(
                    f"🎧 **Şarkı Keşfi #{idx}** - {timestamp_str} 🎵", 
                    expanded=(idx == 1)
                ):
                    # Source song display
                    source_track = entry.get('source_track', 'Unknown')
                    source_artist = entry.get('source_artist', 'Unknown')
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); 
                                padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                        <div style="color: white;">
                            <strong style="font-size: 1.1rem;">🎵 Kaynak Şarkı:</strong><br>
                            <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; font-weight: 600;">
                                {source_track}
                            </p>
                            <p style="margin: 0.3rem 0 0 0; font-size: 0.95rem; opacity: 0.95;">
                                🎤 {source_artist}
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show mood description if available
                    if entry.get('mood_description'):
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
                            <div style="color: white;">
                                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                                    <span style="font-size: 1.5rem; margin-right: 0.5rem;">🤖</span>
                                    <strong style="font-size: 1.1rem;">AI Analizi</strong>
                                </div>
                                <p style="margin: 0; line-height: 1.7; color: white; font-size: 1rem;">
                                    {entry['mood_description']}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show features if available
                    if entry.get('source_features'):
                        features = entry['source_features']
                        st.markdown("**📊 Şarkı Özellikleri:**")
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("⚡ Enerji", f"{features.get('energy', 0):.0%}")
                        with col2:
                            st.metric("😊 Mutluluk", f"{features.get('valence', 0):.0%}")
                        with col3:
                            st.metric("💃 Dans", f"{features.get('danceability', 0):.0%}")
                        with col4:
                            st.metric("🥁 Tempo", f"{features.get('tempo', 0):.0f}")
                    
                    st.markdown("---")
                    
                    # Display similar tracks if available
                    similar_tracks = entry.get('similar_tracks', [])
                    if similar_tracks:
                        st.markdown(f"**🎶 Benzer Şarkılar** ({len(similar_tracks)} adet)")
                        
                        # Display similar tracks
                        for i, t in enumerate(similar_tracks[:5], 1):  # Show first 5
                            artist_names_track = ', '.join([a['name'] for a in t.get('artists', [])])
                            track_url = t.get('external_urls', {}).get('spotify', '')
                            
                            if track_url:
                                st.markdown(f"**{i}.** [{t['name']}]({track_url}) - {artist_names_track}")
                            else:
                                st.markdown(f"**{i}.** {t['name']} - {artist_names_track}")
                    
                    if len(similar_tracks) > 5:
                        st.caption(f"... ve {len(similar_tracks) - 5} şarkı daha")
                
                # Show evaluation if available
                if 'evaluation' in entry and entry['evaluation']:
                    eval_data = entry['evaluation']
                    score = eval_data.get('score', 0)
                    explanation = eval_data.get('explanation', '')
                    
                    # Score color
                    if score >= 8:
                        score_color = "#00ff88"
                    elif score >= 6:
                        score_color = "#ffd700"
                    else:
                        score_color = "#ff6b6b"
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 1.5rem; border-radius: 12px; margin: 1rem 0;
                                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);">
                        <div style="color: white;">
                            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                                <span style="font-size: 1.5rem; margin-right: 0.5rem;">🤖</span>
                                <strong style="font-size: 1.1rem;">AI Değerlendirmesi</strong>
                            </div>
                            <p style="margin: 0 0 1rem 0; line-height: 1.7; color: white; font-size: 1rem;">
                                {explanation}
                            </p>
                            <div style="background: rgba(255,255,255,0.15); padding: 0.75rem; border-radius: 8px; 
                                        display: inline-block;">
                                <strong>Uygunluk Puanı:</strong> 
                                <span style="font-size: 1.5rem; color: {score_color}; font-weight: bold; margin-left: 0.5rem;">
                                    {score}/10
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Show features summary
                features = entry.get('features')
                if features:
                    st.markdown("**📊 Müzik Özellikleri:**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("⚡ Enerji", f"{features.get('energy', 0):.0%}")
                    with col2:
                        st.metric("😊 Mutluluk", f"{features.get('valence', 0):.0%}")
                    with col3:
                        st.metric("💃 Dans", f"{features.get('danceability', 0):.0%}")
                    with col4:
                        st.metric("🥁 Tempo", f"{features.get('tempo', 0):.0f}")
                    
                    # Show genre badges
                    if features.get('genres'):
                        st.markdown("")
                        badge_html = "<div style='margin: 0.5rem 0;'><strong style='color: #495057;'>🎵 Türler:</strong> "
                        for genre in features['genres']:
                            badge_html += f'<span class="feature-badge">{genre}</span> '
                        badge_html += "</div>"
                        st.markdown(badge_html, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Display tracks if available
                tracks = entry.get('tracks', [])
                if tracks:
                    st.markdown(f"**🎶 Önerilen Şarkılar** ({len(tracks)} adet)")
                    
                    # Display tracks in a nice grid format
                    for i, t in enumerate(tracks, 1):
                        artist_names = ', '.join([a['name'] for a in t.get('artists', [])])
                        track_url = t.get('external_urls', {}).get('spotify', '')
                        album_images = t.get('album', {}).get('images', [])
                        album_img = album_images[-1].get('url', '') if album_images else ''  # Smallest image
                        
                        # Create a mini card for each track
                        img_html = f'<img src="{album_img}" style="width: 40px; height: 40px; border-radius: 6px; margin-right: 0.75rem;">' if album_img else ''
                        
                        if track_url:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; 
                                        display: flex; align-items: center; transition: all 0.2s ease;">
                                {img_html}
                                <div style="flex: 1;">
                                    <strong style="color: #495057;">{i}. {t['name']}</strong><br>
                                    <span style="color: #6c757d; font-size: 0.9rem;">🎤 {artist_names}</span>
                                </div>
                                <a href="{track_url}" target="_blank" 
                                   style="background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); 
                                          color: white; padding: 0.5rem 1rem; border-radius: 8px; 
                                          text-decoration: none; font-weight: 600; font-size: 0.9rem;">
                                    ▶️ Dinle
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div style="background: #f8f9fa; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0; 
                                        display: flex; align-items: center;">
                                {img_html}
                                <div>
                                    <strong style="color: #495057;">{i}. {t['name']}</strong><br>
                                    <span style="color: #6c757d; font-size: 0.9rem;">🎤 {artist_names}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
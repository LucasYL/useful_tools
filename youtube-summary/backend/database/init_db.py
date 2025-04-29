#!/usr/bin/env python3
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import argparse
from dotenv import load_dotenv
import hashlib
import uuid

# Load environment variables from .env file
load_dotenv()

def get_connection_string():
    """Get the database connection string from environment variables or use default"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Warning: DATABASE_URL not found in environment variables. Using default connection string.")
        db_url = "postgresql://youtube_summary:password@localhost:5432/youtube_summary"
    return db_url

def connect_to_database(connection_string):
    """Connect to the database using the provided connection string"""
    try:
        conn = psycopg2.connect(connection_string)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

def create_tables(cursor):
    """Create the necessary tables for the application"""
    print("Creating tables...")
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        api_key VARCHAR(64) UNIQUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Videos table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        youtube_id VARCHAR(20) UNIQUE NOT NULL,
        title TEXT NOT NULL,
        channel VARCHAR(100),
        duration INTEGER,
        view_count BIGINT,
        like_count BIGINT,
        thumbnail_url TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Summaries table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS summaries (
        id SERIAL PRIMARY KEY,
        video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        summary_text TEXT NOT NULL,
        transcript_text TEXT,
        is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
        summary_type VARCHAR(50) NOT NULL DEFAULT 'short',
        language VARCHAR(10) NOT NULL DEFAULT 'en',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(video_id, user_id)
    )
    ''')
    
    # Tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    )
    ''')
    
    # Video-Tags mapping table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS video_tags (
        video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
        tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (video_id, tag_id)
    )
    ''')
    
    print("Tables created successfully.")

def hash_password(password):
    """Create a SHA-256 hash of the password"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def generate_api_key():
    """Generate a unique API key"""
    return str(uuid.uuid4())

def insert_test_data(cursor):
    """Insert test data into the database"""
    print("Inserting test data...")
    
    # Insert test user
    test_user_password = hash_password("password")
    test_api_key = generate_api_key()
    cursor.execute('''
    INSERT INTO users (username, email, password_hash, api_key)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username) DO NOTHING
    RETURNING id
    ''', ("testuser", "test@example.com", test_user_password, test_api_key))
    user_id = cursor.fetchone()
    
    if user_id:
        user_id = user_id[0]
        print(f"Test user created with ID: {user_id}")
        
        # Insert test videos
        sample_videos = [
            ("dQw4w9WgXcQ", "Rick Astley - Never Gonna Give You Up", "Rick Astley", 213, 1234567, 98765, "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"),
            ("9bZkp7q19f0", "PSY - GANGNAM STYLE", "officialpsy", 253, 4567890, 87654, "https://img.youtube.com/vi/9bZkp7q19f0/maxresdefault.jpg"),
            ("kJQP7kiw5Fk", "Luis Fonsi - Despacito ft. Daddy Yankee", "LuisFonsiVEVO", 282, 7890123, 76543, "https://img.youtube.com/vi/kJQP7kiw5Fk/maxresdefault.jpg")
        ]
        
        video_ids = []
        for video in sample_videos:
            cursor.execute('''
            INSERT INTO videos (youtube_id, title, channel, duration, view_count, like_count, thumbnail_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (youtube_id) DO UPDATE 
            SET title = EXCLUDED.title,
                channel = EXCLUDED.channel,
                duration = EXCLUDED.duration,
                view_count = EXCLUDED.view_count,
                like_count = EXCLUDED.like_count,
                thumbnail_url = EXCLUDED.thumbnail_url
            RETURNING id
            ''', video)
            video_id = cursor.fetchone()[0]
            video_ids.append(video_id)
        
        # Insert test summaries
        sample_summaries = [
            (video_ids[0], user_id, "This is a classic 80s music video where Rick Astley promises never to give you up, let you down, run around, or desert you. The video has become an internet meme known as 'Rickrolling'.", "Full transcript would go here..."),
            (video_ids[1], user_id, "PSY's viral hit featuring the iconic horse dance and satirical lyrics about the Gangnam district in Seoul. It was the first YouTube video to reach 1 billion views.", "Full transcript would go here..."),
            (video_ids[2], user_id, "A Spanish-language pop song that became a global hit. The song's title means 'slowly' in English, and it features a blend of Latin and urban rhythms.", "Full transcript would go here...")
        ]
        
        for summary in sample_summaries:
            cursor.execute('''
            INSERT INTO summaries (video_id, user_id, summary_text, transcript_text)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (video_id, user_id) DO UPDATE 
            SET summary_text = EXCLUDED.summary_text,
                transcript_text = EXCLUDED.transcript_text
            ''', summary)
        
        # Insert test tags
        sample_tags = ["music", "viral", "pop", "classic", "spanish", "english", "dance"]
        tag_ids = []
        
        for tag in sample_tags:
            cursor.execute('''
            INSERT INTO tags (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            RETURNING id
            ''', (tag,))
            result = cursor.fetchone()
            if result:
                tag_ids.append(result[0])
            else:
                cursor.execute('SELECT id FROM tags WHERE name = %s', (tag,))
                tag_ids.append(cursor.fetchone()[0])
        
        # Connect videos with tags
        video_tags = [
            (video_ids[0], tag_ids[0]), (video_ids[0], tag_ids[3]), (video_ids[0], tag_ids[5]),
            (video_ids[1], tag_ids[0]), (video_ids[1], tag_ids[1]), (video_ids[1], tag_ids[6]),
            (video_ids[2], tag_ids[0]), (video_ids[2], tag_ids[2]), (video_ids[2], tag_ids[4])
        ]
        
        for vt in video_tags:
            cursor.execute('''
            INSERT INTO video_tags (video_id, tag_id)
            VALUES (%s, %s)
            ON CONFLICT (video_id, tag_id) DO NOTHING
            ''', vt)
        
        print("Test data inserted successfully.")
    else:
        print("Test user already exists.")

def main():
    parser = argparse.ArgumentParser(description='Initialize the YouTube Summary database')
    parser.add_argument('--reset', action='store_true', help='Reset the database by dropping all tables')
    args = parser.parse_args()
    
    # Get database connection
    connection_string = get_connection_string()
    conn = connect_to_database(connection_string)
    cursor = conn.cursor()
    
    try:
        if args.reset:
            print("Resetting database...")
            cursor.execute('''
            DROP TABLE IF EXISTS video_tags CASCADE;
            DROP TABLE IF EXISTS tags CASCADE;
            DROP TABLE IF EXISTS summaries CASCADE;
            DROP TABLE IF EXISTS videos CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            ''')
            print("All tables dropped.")
        
        create_tables(cursor)
        insert_test_data(cursor)
        
        print("\nDatabase initialization completed successfully!")
        print("\nTest user credentials:")
        print("Username: testuser")
        print("Password: password")
        
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main() 
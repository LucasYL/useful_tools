#!/usr/bin/env python3
"""
Database Connection Test Script
This script tests the connection to the YouTube Summary database
and displays basic information about the tables.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_connection_string():
    """Get the database connection string from environment variables or use default"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Warning: DATABASE_URL not found in environment variables. Using default connection string.")
        db_url = "postgresql://youtube_summary:password@localhost:5432/youtube_summary"
    return db_url

def get_db_connection():
    """Establish a connection to the database"""
    connection_string = get_connection_string()
    try:
        print(f"Attempting to connect to database...")
        conn = psycopg2.connect(connection_string)
        print("Connection successful!")
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def display_table_info(cursor, table_name):
    """Display information about a table"""
    print(f"\nTable: {table_name}")
    
    # Get column information
    cursor.execute(f"""
    SELECT column_name, data_type, character_maximum_length 
    FROM information_schema.columns 
    WHERE table_name = '{table_name}'
    """)
    columns = cursor.fetchall()
    
    print("Columns:")
    for col in columns:
        col_name, data_type, max_length = col
        if max_length:
            print(f"  - {col_name} ({data_type}({max_length}))")
        else:
            print(f"  - {col_name} ({data_type})")
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"Total rows: {row_count}")
    
    # Display sample data if table has rows
    if row_count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        
        # Get column names for pretty printing
        column_names = [desc[0] for desc in cursor.description]
        
        print("Sample data:")
        for row in rows:
            print("  Row:")
            for i, value in enumerate(row):
                # Truncate long text values for display
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                print(f"    {column_names[i]}: {value}")

def main():
    """Main function to test database connection and display schema information"""
    conn = get_db_connection()
    if not conn:
        sys.exit(1)
    
    cursor = conn.cursor()
    
    try:
        # Get list of tables
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        """)
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
        
        print(f"\nFound {len(tables)} tables in the database:")
        for table in tables:
            table_name = table[0]
            display_table_info(cursor, table_name)
            
        print("\nDatabase connection test completed successfully!")
            
    except psycopg2.Error as e:
        print(f"Error querying database: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main() 
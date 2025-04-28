# Setting Up a Local Database for YouTube Summary App

This guide will help you set up a local PostgreSQL database for the YouTube Summary application.

## Prerequisites

- PostgreSQL (12 or higher recommended)
- Python 3.8 or higher
- Basic familiarity with terminal/command line

## Setup Steps

### 1. Install PostgreSQL (if not already installed)

#### macOS (using Homebrew)
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Set Up the Database

You can either use the automated script or set up manually:

#### Option 1: Using the Setup Script

1. Make the script executable:
   ```bash
   chmod +x setup_postgres.sh
   ```

2. Run the script:
   ```bash
   ./setup_postgres.sh
   ```

3. Follow the prompts and note the connection string.

#### Option 2: Manual Setup

1. Connect to PostgreSQL as a superuser:
   ```bash
   sudo -u postgres psql
   ```

2. Create a database user:
   ```sql
   CREATE USER youtube_summary WITH PASSWORD 'your_password';
   ```

3. Create a database:
   ```sql
   CREATE DATABASE youtube_summary OWNER youtube_summary;
   ```

4. Grant privileges:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE youtube_summary TO youtube_summary;
   ```

5. Exit PostgreSQL:
   ```sql
   \q
   ```

### 3. Update Environment Variables

1. Create a `.env` file or copy from the example:
   ```bash
   cp .env.sample .env
   ```

2. Update the `DATABASE_URL` in the `.env` file:
   ```
   DATABASE_URL=postgresql://youtube_summary:your_password@localhost:5432/youtube_summary
   ```

### 4. Install Required Python Packages

```bash
pip install psycopg2-binary python-dotenv
```

### 5. Initialize the Database Schema and Test Data

1. Run the database initialization script:
   ```bash
   python init_db.py
   ```

   The script will:
   - Create all necessary tables (users, videos, summaries, tags, video_tags)
   - Insert a test user and sample data
   - Output the test user credentials

   Options:
   - To reset the database (drop all tables and recreate them):
     ```bash
     python init_db.py --reset
     ```

2. Verify the database connection:
   ```bash
   python test_db_connection.py
   ```
   
   This script will:
   - Test the connection to your database
   - Display all tables in the database
   - Show table structure (columns and data types)
   - Display sample data from each table

### 6. Start the Application

```bash
python -m uvicorn main:app --reload
```

## Database Structure

The database includes the following tables:

1. **users** - Store user information
   - id, username, email, password_hash, api_key, created_at, updated_at

2. **videos** - YouTube video metadata
   - id, youtube_id, title, channel, duration, view_count, like_count, thumbnail_url, created_at

3. **summaries** - Generated summaries for videos
   - id, video_id, user_id, summary_text, transcript_text, created_at

4. **tags** - Video categorization tags
   - id, name

5. **video_tags** - Many-to-many relationship between videos and tags
   - video_id, tag_id

## Test User Credentials

The initialization script creates a test user with the following credentials:

- Username: `testuser`
- Password: `password`

## Environment Variables

The application uses environment variables for configuration. Here are the important database-related variables:

```
# Database Configuration
DATABASE_URL=postgresql://youtube_summary:password@localhost:5432/youtube_summary
```

See `.env.sample` for all available configuration options.

## Troubleshooting

### Connection Issues

If you see errors like "connection refused":

1. Check if PostgreSQL is running:
   ```bash
   pg_isready
   ```

2. Verify your connection information:
   ```bash
   psql -U youtube_summary -d youtube_summary -h localhost
   ```

### Database Reset

If you need to reset the database:

1. Option 1: Use the reset parameter with init_db.py:
   ```bash
   python init_db.py --reset
   ```

2. Option 2: Connect to PostgreSQL and manually reset:
   ```bash
   psql postgres
   ```
   ```sql
   DROP DATABASE youtube_summary;
   CREATE DATABASE youtube_summary OWNER youtube_summary;
   ```
   Then run the initialization script again:
   ```bash
   python init_db.py
   ``` 
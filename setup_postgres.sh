#!/bin/bash

# PostgreSQL Setup Script for YouTube Summary App
# This script creates a PostgreSQL user and database for the application

# Configuration
DB_NAME="youtube_summary"
DB_USER="youtube_summary"
DB_PASSWORD="your_password"  # Change this to a secure password

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first."
    echo "On macOS, use: brew install postgresql"
    exit 1
fi

# Check if PostgreSQL server is running
if ! pg_isready &> /dev/null; then
    echo "PostgreSQL server is not running. Starting it now..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew services start postgresql
        sleep 3  # Wait for PostgreSQL to start
    else
        # Linux (assumes systemd)
        sudo systemctl start postgresql
        sleep 3  # Wait for PostgreSQL to start
    fi
fi

# Create user and database
echo "Creating PostgreSQL user and database..."

# Create user if it doesn't exist
psql postgres -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
psql postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

# Create database if it doesn't exist
psql postgres -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
psql postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# Grant privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "PostgreSQL setup completed."
echo ""
echo "Database connection string for .env file:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
echo ""
echo "Next steps:"
echo "1. Copy the DATABASE_URL to your .env file"
echo "2. Run the database initialization script: python init_db.py" 
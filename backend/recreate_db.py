"""
Script to recreate the database with updated schema.
This will DELETE all existing data and create fresh tables.
"""
import os
from app import create_app
from models import db

def recreate_database():
    app = create_app()
    
    with app.app_context():
        # Get the database path
        db_path = 'ai_tutor.db'
        
        # Delete the existing database file if it exists
        if os.path.exists(db_path):
            print(f"🗑️  Deleting existing database: {db_path}")
            os.remove(db_path)
        
        # Create all tables with the new schema
        print("📦 Creating new database with updated schema...")
        db.create_all()
        
        print("✅ Database recreated successfully!")
        print("   All tables created with the latest schema.")
        print("   Note: All previous data has been deleted.")

if __name__ == '__main__':
    recreate_database()

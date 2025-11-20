"""
Reset database to new schema without weeks
"""

from app import create_app
from models import db
import os

def reset_database():
    app = create_app()
    
    with app.app_context():
        print("Resetting database...")
        
        # Get database path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        
        # Close all connections
        db.session.remove()
        db.engine.dispose()
        
        # Delete the database file
        if os.path.exists(db_path):
            print(f"Deleting old database: {db_path}")
            os.remove(db_path)
            print("✓ Database deleted")
        
        # Create new database with updated schema
        print("Creating new database with updated schema...")
        db.create_all()
        print("✓ New database created")
        
        print("\n✅ Database reset complete!")
        print("The database now has the new schema without weeks.")
        print("All existing data has been cleared.")

if __name__ == '__main__':
    reset_database()

"""
Script to recreate the database with the new schema (without weeks)
WARNING: This will DELETE all existing data!
"""

import os
from app import create_app
from models import db

def recreate_database():
    app = create_app()
    
    with app.app_context():
        print("⚠️  WARNING: This will delete all existing data!")
        print("This includes all modules, lessons, users, and progress.")
        
        response = input("Are you sure you want to continue? (yes/no): ")
        
        if response.lower() != 'yes':
            print("Aborted.")
            return
        
        # Get the database path
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI', '').replace('sqlite:///', '')
        
        print(f"\n1. Backing up old database...")
        if os.path.exists(db_path):
            backup_path = db_path + '.backup'
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"   ✓ Backup created at: {backup_path}")
        
        print("\n2. Dropping all tables...")
        db.drop_all()
        print("   ✓ All tables dropped")
        
        print("\n3. Creating new tables with updated schema...")
        db.create_all()
        print("   ✓ New tables created")
        
        print("\n✅ Database recreated successfully!")
        print("   You can now create modules without the weekly structure.")
        print("   Note: All previous data has been deleted.")

if __name__ == '__main__':
    recreate_database()

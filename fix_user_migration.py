#!/usr/bin/env python
"""
Script to fix User model migration issue on server.
Run this script before running migrations.
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    sys.exit(1)

from django.db import connection as db_connection
from django.utils import timezone

def fix_user_migration():
    """Fix migration by creating User table directly"""
    try:
        with db_connection.cursor() as cursor:
            # Check if User table exists
            if db_connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='website_user'
                """)
            else:  # PostgreSQL
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'website_user'
                """)
            
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                print("Creating User table...")
                # Use Django's schema editor to create the table
                from apps.website.models import User
                
                schema_editor = db_connection.schema_editor()
                schema_editor.create_model(User)
                print("User table created successfully")
            else:
                print("User table already exists")
            
            # Check if migration is already marked as applied
            cursor.execute("""
                SELECT * FROM django_migrations 
                WHERE app = 'website' AND name = '0009_create_user_model'
            """)
            if cursor.fetchone():
                print("Migration 0009_create_user_model is already marked as applied")
            else:
                # Mark migration as applied
                now = timezone.now()
                if db_connection.vendor == 'sqlite':
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES ('website', '0009_create_user_model', ?)
                    """, [now])
                else:  # PostgreSQL
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES ('website', '0009_create_user_model', %s)
                    """, [now])
                print("Migration 0009_create_user_model marked as applied")
            
            print("\nNow you can run: python3 manage.py migrate")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    fix_user_migration()

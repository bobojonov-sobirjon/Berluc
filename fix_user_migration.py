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
                # Create User table directly using SQL
                if db_connection.vendor == 'sqlite':
                    cursor.execute("""
                        CREATE TABLE website_user (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            password VARCHAR(128) NOT NULL,
                            last_login DATETIME NULL,
                            is_superuser BOOLEAN NOT NULL DEFAULT 0,
                            username VARCHAR(150) NOT NULL UNIQUE,
                            first_name VARCHAR(150) NOT NULL DEFAULT '',
                            last_name VARCHAR(150) NOT NULL DEFAULT '',
                            email VARCHAR(254) NOT NULL DEFAULT '',
                            is_staff BOOLEAN NOT NULL DEFAULT 0,
                            is_active BOOLEAN NOT NULL DEFAULT 1,
                            date_joined DATETIME NOT NULL,
                            is_manager BOOLEAN NOT NULL DEFAULT 0
                        )
                    """)
                    # Create indexes
                    cursor.execute("CREATE INDEX IF NOT EXISTS website_user_username ON website_user(username)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS website_user_email ON website_user(email)")
                else:  # PostgreSQL
                    cursor.execute("""
                        CREATE TABLE website_user (
                            id SERIAL PRIMARY KEY,
                            password VARCHAR(128) NOT NULL,
                            last_login TIMESTAMP NULL,
                            is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                            username VARCHAR(150) NOT NULL UNIQUE,
                            first_name VARCHAR(150) NOT NULL DEFAULT '',
                            last_name VARCHAR(150) NOT NULL DEFAULT '',
                            email VARCHAR(254) NOT NULL DEFAULT '',
                            is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                            is_active BOOLEAN NOT NULL DEFAULT TRUE,
                            date_joined TIMESTAMP NOT NULL,
                            is_manager BOOLEAN NOT NULL DEFAULT FALSE
                        )
                    """)
                    cursor.execute("CREATE INDEX IF NOT EXISTS website_user_username ON website_user(username)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS website_user_email ON website_user(email)")
                
                print("User table created successfully")
            else:
                print("User table already exists")
            
            # Create many-to-many tables (always check, even if User table exists)
            if db_connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='website_user_groups'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_groups table...")
                    cursor.execute("""
                        CREATE TABLE website_user_groups (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            group_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
                            UNIQUE(user_id, group_id)
                        )
                    """)
                    print("website_user_groups table created")
                else:
                    print("website_user_groups table already exists")
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='website_user_user_permissions'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_user_permissions table...")
                    cursor.execute("""
                        CREATE TABLE website_user_user_permissions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            permission_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
                            UNIQUE(user_id, permission_id)
                        )
                    """)
                    print("website_user_user_permissions table created")
                else:
                    print("website_user_user_permissions table already exists")
            else:  # PostgreSQL
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'website_user_groups'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_groups table...")
                    cursor.execute("""
                        CREATE TABLE website_user_groups (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            group_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
                            UNIQUE(user_id, group_id)
                        )
                    """)
                    print("website_user_groups table created")
                else:
                    print("website_user_groups table already exists")
                
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'website_user_user_permissions'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_user_permissions table...")
                    cursor.execute("""
                        CREATE TABLE website_user_user_permissions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            permission_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
                            UNIQUE(user_id, permission_id)
                        )
                    """)
                    print("website_user_user_permissions table created")
                else:
                    print("website_user_user_permissions table already exists")
            
            # Check and create many-to-many tables if they don't exist
            if db_connection.vendor == 'sqlite':
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='website_user_groups'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_groups table...")
                    cursor.execute("""
                        CREATE TABLE website_user_groups (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            group_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
                            UNIQUE(user_id, group_id)
                        )
                    """)
                    print("website_user_groups table created")
                
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='website_user_user_permissions'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_user_permissions table...")
                    cursor.execute("""
                        CREATE TABLE website_user_user_permissions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            permission_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
                            UNIQUE(user_id, permission_id)
                        )
                    """)
                    print("website_user_user_permissions table created")
            else:  # PostgreSQL
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'website_user_groups'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_groups table...")
                    cursor.execute("""
                        CREATE TABLE website_user_groups (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            group_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
                            UNIQUE(user_id, group_id)
                        )
                    """)
                    print("website_user_groups table created")
                
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'website_user_user_permissions'
                """)
                if not cursor.fetchone():
                    print("Creating website_user_user_permissions table...")
                    cursor.execute("""
                        CREATE TABLE website_user_user_permissions (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER NOT NULL,
                            permission_id INTEGER NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES website_user(id) ON DELETE CASCADE,
                            FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
                            UNIQUE(user_id, permission_id)
                        )
                    """)
                    print("website_user_user_permissions table created")
            
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
                        VALUES (?, ?, ?)
                    """, ['website', '0009_create_user_model', now])
                else:  # PostgreSQL
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied)
                        VALUES (%s, %s, %s)
                    """, ['website', '0009_create_user_model', now])
                print("Migration 0009_create_user_model marked as applied")
            
            print("\nNow you can run: python3 manage.py migrate")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    fix_user_migration()

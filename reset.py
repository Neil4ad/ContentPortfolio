"""
Database Reset Script
This script resets the database by dropping all tables and recreating them.
It then creates a default admin user.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from datetime import datetime

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the app and database
from app import app, db
from models import User, SiteSettings

def reset_database():
    with app.app_context():
        # Confirm reset
        if input("Are you sure you want to reset the database? This will delete all data. (y/n): ").lower() != 'y':
            print("Database reset cancelled.")
            return
        
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Create default admin user
        print("Creating default admin user...")
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin'),
            is_admin=True,
            created_at=datetime.utcnow()
        )
        db.session.add(admin_user)
        
        # Create default site settings
        print("Creating default site settings...")
        default_settings = SiteSettings(
            site_title="Content Designer & Strategist",
            site_subtitle="Crafting clear, compelling digital experiences that engage audiences and drive results",
            about_short="I help brands communicate more effectively through strategic content design, UX writing, and messaging that connects with audiences.",
            brand_name="Your Name",
            contact_email="contact@example.com",
            banner_gradient_start="#4F46E5",
            banner_gradient_end="#3B82F6",
            primary_color="#4F46E5",
            accent_color="#3B82F6",
            primary_text_color="#1f2937",
            secondary_text_color="#6b7280",
            hero_text_color="#ffffff",
            link_hover_color="#4F46E5",
            button_hover_color="#3B82F6"
        )
        db.session.add(default_settings)
        
        # Commit changes
        db.session.commit()
        
        print("Database reset successful!")
        print("\nDefault admin credentials:")
        print("Username: admin")
        print("Password: admin")
        print("\nIMPORTANT: Please change these credentials immediately after logging in.")

if __name__ == "__main__":
    reset_database()
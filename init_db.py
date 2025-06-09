#!/usr/bin/env python3
"""
Database initialization script for ContentPortfolio
Creates all tables and sets up initial data
"""

import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Category, BusinessGoal, Project, Message, SiteSettings

def init_database():
    """Initialize the database with all tables and default data"""
    
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        print("Setting up initial data...")
        
        # Create default admin user
        admin_user = User(
            username='admin',
            email='admin@example.com'
        )
        admin_user.set_password('changeme123')  # Change this password!
        db.session.add(admin_user)
        
        # Create default categories
        categories = [
            Category(name='Web Development', is_active=True),
            Category(name='Content Strategy', is_active=True),
            Category(name='UX Writing', is_active=True),
            Category(name='Digital Marketing', is_active=True),
            Category(name='Brand Strategy', is_active=True)
        ]
        
        for category in categories:
            db.session.add(category)
        
        # Create default business goals
        business_goals = [
            BusinessGoal(name='Increase Conversions', color='#10B981', is_active=True),
            BusinessGoal(name='Improve User Experience', color='#3B82F6', is_active=True),
            BusinessGoal(name='Build Brand Awareness', color='#8B5CF6', is_active=True),
            BusinessGoal(name='Drive Engagement', color='#F59E0B', is_active=True),
            BusinessGoal(name='Generate Leads', color='#EF4444', is_active=True)
        ]
        
        for goal in business_goals:
            db.session.add(goal)
        
        # Create default site settings
        site_settings = SiteSettings(
            site_title="Content Designer & Strategist",
            site_subtitle="Crafting clear, compelling digital experiences that engage audiences and drive results",
            about_short="I help brands communicate more effectively through strategic content design, UX writing, and messaging that connects with audiences.",
            brand_name="Your Name",
            contact_email="contact@example.com",
            banner_gradient_start="#4F46E5",
            banner_gradient_end="#3B82F6",
            hero_text_color="#ffffff",
            link_hover_color="#4F46E5",
            button_hover_color="#3B82F6"
        )
        db.session.add(site_settings)
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print("📋 Summary:")
        print(f"   - Created {User.query.count()} user(s)")
        print(f"   - Created {Category.query.count()} categories")
        print(f"   - Created {BusinessGoal.query.count()} business goals")
        print(f"   - Created site settings")
        print("\n🔐 Default admin login:")
        print("   Username: admin")
        print("   Password: changeme123")
        print("   ⚠️  IMPORTANT: Change this password after first login!")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
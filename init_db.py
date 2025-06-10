#!/usr/bin/env python3
"""
Database initialization script for ContentPortfolio
Creates all tables and sets up initial data
Works in any environment (local, PythonAnywhere, etc.)
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
        # Password hash will be generated in current environment for compatibility
        admin_user = User(
            username='admin',
            email='admin@example.com'
        )
        
        print("Setting admin password (generating hash in current environment)...")
        admin_user.set_password('changeme123')  # Hash generated here will be compatible
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
        print("Committing changes to database...")
        db.session.commit()
        
        # Verify admin user was created properly
        admin_check = User.query.filter_by(username='admin').first()
        if admin_check:
            print("✅ Admin user created and verified successfully!")
        else:
            print("⚠️  Warning: Admin user creation could not be verified")
        
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
        print("\n💡 Note: Password hash generated in current environment for compatibility")

def reset_admin_password_only():
    """Reset only the admin password without reinitializing the entire database"""
    
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        
        if not admin_user:
            print("❌ Admin user not found! Run full initialization first.")
            return False
        
        print("Resetting admin password (generating new hash in current environment)...")
        admin_user.set_password('changeme123')
        db.session.commit()
        
        print("✅ Admin password reset successfully!")
        print("🔐 Login credentials:")
        print("   Username: admin")
        print("   Password: changeme123")
        print("   ⚠️  Change this password after logging in!")
        
        return True

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize ContentPortfolio database')
    parser.add_argument('--reset-password-only', action='store_true', 
                       help='Only reset admin password without reinitializing database')
    
    args = parser.parse_args()
    
    try:
        if args.reset_password_only:
            reset_admin_password_only()
        else:
            init_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   - Ensure you're in the correct directory")
        print("   - Check that all required files (app.py, models.py) exist")
        print("   - Verify database permissions")
        print("   - If password issues persist, try: python3 init_db.py --reset-password-only")
        sys.exit(1)
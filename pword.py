#!/usr/bin/env python3
"""
Password Reset Script for Portfolio CMS
Run this script to reset your admin password
"""

import os
import sys
from werkzeug.security import generate_password_hash
from app import app, db, User

def reset_admin_password():
    """Reset the admin user password"""
    
    with app.app_context():
        # Get the admin user (assuming there's only one user)
        admin = User.query.first()
        
        if not admin:
            print("❌ No admin user found in database!")
            print("You may need to create a new admin user.")
            return False
        
        print(f"📝 Found admin user: {admin.username}")
        print(f"📧 Email: {admin.email}")
        print()
        
        # Get new password
        new_password = input("🔑 Enter new password: ").strip()
        
        if len(new_password) < 6:
            print("❌ Password must be at least 6 characters long!")
            return False
        
        # Confirm password
        confirm_password = input("🔑 Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return False
        
        # Update password
        admin.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            print(f"✅ Password successfully updated for user: {admin.username}")
            print(f"🔗 You can now login at: http://localhost:5000/admin/login")
            return True
            
        except Exception as e:
            print(f"❌ Error updating password: {e}")
            db.session.rollback()
            return False

def create_new_admin():
    """Create a new admin user if none exists"""
    
    with app.app_context():
        print("🆕 Creating new admin user...")
        print()
        
        username = input("👤 Enter username: ").strip()
        email = input("📧 Enter email: ").strip()
        password = input("🔑 Enter password: ").strip()
        
        if len(password) < 6:
            print("❌ Password must be at least 6 characters long!")
            return False
        
        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            print(f"❌ User with username '{username}' or email '{email}' already exists!")
            return False
        
        # Create new user
        new_admin = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        try:
            db.session.add(new_admin)
            db.session.commit()
            print(f"✅ New admin user created successfully!")
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"🔗 Login at: http://localhost:5000/admin/login")
            return True
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            db.session.rollback()
            return False

def main():
    print("🔧 Portfolio CMS - Password Reset Tool")
    print("=" * 40)
    
    with app.app_context():
        # Check if database exists and has users
        try:
            user_count = User.query.count()
            print(f"📊 Found {user_count} user(s) in database")
            print()
            
            if user_count == 0:
                print("No users found. Let's create a new admin user.")
                create_new_admin()
            else:
                print("Choose an option:")
                print("1. Reset existing admin password")
                print("2. Create new admin user")
                print("3. Exit")
                
                choice = input("\nEnter choice (1-3): ").strip()
                
                if choice == "1":
                    reset_admin_password()
                elif choice == "2":
                    create_new_admin()
                elif choice == "3":
                    print("👋 Goodbye!")
                else:
                    print("❌ Invalid choice!")
                    
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("\n💡 Make sure your database file exists and is accessible.")

if __name__ == "__main__":
    main()
# Content Portfolio Website

A Flask-based portfolio website for content creators, strategists, and UX writers. Features project showcases, business goal tracking, and a clean, professional design.

## 🚀 Quick Start Guide

**Time needed:** About 30 minutes  
**Experience needed:** None - we'll walk you through everything

### What You Need
- Free [GitHub](https://github.com) account (for storing your website code)
- Free [PythonAnywhere](https://www.pythonanywhere.com) account (for hosting your website)

## Step-by-Step Setup

### 1. Copy the Website Code
1. **Log into GitHub** and go to this repository
2. **Click the green "Fork" button** at the top right
3. Wait for it to finish - you now have your own copy!

### 2. Create Your Hosting Account
1. **Sign up** for a free PythonAnywhere account
2. **Go to the "Web" tab** and click "Add a new web app"
3. **Choose "Manual Configuration"** and select **Python 3.10**

### 3. Upload Your Code 
1. **Go to the "Files" tab** in PythonAnywhere
2. **Click "Open Bash console here"** (black terminal window)
3. **Copy and paste this command** (replace `YOUR-USERNAME` with your GitHub username):
   ```bash
   git clone https://github.com/YOUR-USERNAME/ContentPortfolio.git
   ```
4. **Press Enter** and wait for it to finish
5. **Type:** `cd ContentPortfolio` and press Enter

### 4. Install Requirements
**Copy and paste this command:**
```bash
pip3.10 install --user -r requirements.txt
```
Wait 2-3 minutes for it to complete.

### 5. Set Up Your Database
**Type this command:**
```bash
python3 init_db.py
```

You should see:
```
✅ Database initialized successfully!
🔐 Default admin login:
   Username: admin
   Password: changeme123
```

### 6. Configure Your Website
1. **Go back to the "Web" tab**
2. **In the "Code" section, set these paths:**
   - **Source code:** `/home/yourusername/ContentPortfolio`
   - **Working directory:** `/home/yourusername/ContentPortfolio`
   
   *(Replace `yourusername` with your PythonAnywhere username)*

3. **Click on your WSGI configuration file**
4. **Delete all existing text** and paste this:
   ```python
   import sys
   import os

   # Add your project directory to the sys.path
   project_home = '/home/yourusername/ContentPortfolio'  # Replace 'yourusername'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path

   from app import app as application

   if __name__ == '__main__':
       application.run()
   ```
5. **Replace `yourusername`** with your actual PythonAnywhere username
6. **Click "Save"**

### 7. Launch Your Website! 🚀
1. **Click the big green "Reload" button**
2. **Click your website URL** (looks like `yourusername.pythonanywhere.com`)

**Success!** Your portfolio website is now live on the internet.

## 🔑 First Login

1. **Find the "Login" link** on your website
2. **Login with:**
   - Username: `admin`
   - Password: `changeme123`
3. **⚠️ IMPORTANT:** Change this password immediately in the admin panel!

## 🎨 Customizing Your Site

Once logged in, you can:
- **Add your projects** with images and descriptions
- **Update site colors and branding** in Settings
- **Write your About page** content
- **Set up social media links**
- **Organize projects by categories and goals**

## 🆘 Troubleshooting

### "Something went wrong" when logging in
**Fix:**
1. Go to your PythonAnywhere terminal
2. Type: `cd ContentPortfolio`
3. Type: `python3 init_db.py --reset-password-only`
4. Go to Web tab, click "Reload"
5. Try logging in again

### Website won't load
**Check these:**
1. **WSGI file:** Make sure you replaced `yourusername` with your actual username
2. **File paths:** Both source code and working directory should be `/home/YOURUSERNAME/ContentPortfolio`
3. **Reload:** Click the green "Reload" button and wait 30 seconds

### Still having issues?
1. **Copy any error messages**
2. **Create a new issue** on this GitHub repository
3. **Include what step you're on** and what error you're seeing

## 🔧 Advanced Options

### Utility Scripts
Your website includes helpful utility scripts for maintenance:

**`init_db.py`** - Database setup and reset
- Sets up your database with default data
- Use `python3 init_db.py --reset-password-only` to reset just your admin password
- Safe way to reinstall the database if needed

**`pword.py`** - Password recovery tool  
- Interactive script to reset your admin password if you're locked out
- Run with `python3 pword.py` and follow the prompts
- Useful when you forget your login credentials

### Custom Domain
Upgrade to a PythonAnywhere paid plan to use your own domain name.

### Backup Your Data
Regularly download your database file from the Files tab to keep your content safe.

## 📄 License
Open source and available under the MIT License.

---

**Questions?** Create an issue on GitHub and we'll help you get set up!
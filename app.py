from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
import markdown
from datetime import datetime
import json
import logging
from flask_mail import Mail, Message as MailMessage

# Import database model classes
from models import db, User, Project, Message, SiteSettings, Category, BusinessGoal
from forms import LoginForm, ContactForm, ProjectForm, ChangePasswordForm, UpdateProfileForm, SiteSettingsForm, CategoryForm, BusinessGoalForm

# Import configuration
from config import config

# Initialize app
app = Flask(__name__)
app.config.from_object(config['development'])

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize mail
mail = Mail(app)

# Custom Jinja filters
@app.template_filter('markdown')
def render_markdown(text):
    if text is None:
        return ""
    return markdown.markdown(text)

@app.template_filter('truncate_text')
def truncate_text(text, length=100):
    if text is None:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + '...'

# Add this to your app.py file to create custom template filters for description control

@app.template_filter('truncate_smart')
def truncate_smart(text, length=150, suffix='...'):
    """
    Smart truncation that breaks at word boundaries
    """
    if text is None:
        return ""
    if len(text) <= length:
        return text
    
    # Try to break at word boundary
    truncated = text[:length]
    last_space = truncated.rfind(' ')
    
    if last_space > length * 0.8:  # If we found a space reasonably close
        return truncated[:last_space] + suffix
    else:
        return truncated + suffix

@app.template_filter('truncate_sentences')
def truncate_sentences(text, sentences=2):
    """
    Truncate at sentence boundaries
    """
    if text is None:
        return ""
    
    import re
    # Split on sentence endings
    sentence_endings = re.split(r'[.!?]+', text)
    
    if len(sentence_endings) <= sentences:
        return text
    
    # Take the first N sentences and add back the punctuation
    result = '. '.join(sentence_endings[:sentences]).strip()
    if result and not result.endswith(('.', '!', '?')):
        result += '.'
    
    return result

@app.template_filter('word_count')
def word_count(text):
    """
    Count words in text
    """
    if text is None:
        return 0
    return len(text.split())

@app.template_filter('reading_time')
def reading_time(text, wpm=200):
    """
    Estimate reading time in minutes
    """
    if text is None:
        return 0
    words = len(text.split())
    minutes = max(1, round(words / wpm))
    return f"{minutes} min read"

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and admin user - Flask 3.x compatible
def initialize_db():
    """Initialize database with default data if needed"""
    db.create_all()
    
    # Initialize site settings if they don't exist
    if SiteSettings.query.count() == 0:
        default_settings = SiteSettings()
        db.session.add(default_settings)
        db.session.commit()
    
    # Create admin user if it doesn't exist
    if User.query.count() == 0:
        admin = User(
            username=app.config['DEFAULT_ADMIN_USERNAME'],
            email=app.config['DEFAULT_ADMIN_EMAIL']
        )
        admin.set_password(app.config['DEFAULT_ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
    
    # Create default categories if they don't exist
    if Category.query.count() == 0:
        default_categories = ['Articles', 'Blog Posts', 'Case Studies', 'Websites', 'Branding', 'UX Design']
        for cat_name in default_categories:
            category = Category(name=cat_name, is_active=True)
            db.session.add(category)
        db.session.commit()

    # Create default business goals if they don't exist
    if BusinessGoal.query.count() == 0:
        default_business_goals = [
            ('User Engagement', '#3B82F6'),      # Blue
            ('Education', '#10B981'),            # Green
            ('Brand Awareness', '#8B5CF6'),      # Purple
            ('Lead Generation', '#F59E0B'),      # Orange
            ('Strategy & Planning', '#6366F1'),   # Indigo
        ]
        for goal_name, goal_color in default_business_goals:
            business_goal = BusinessGoal(name=goal_name, color=goal_color, is_active=True)
            db.session.add(business_goal)
        db.session.commit()

# Flask 3.x compatible - call initialize_db when needed
with app.app_context():
    initialize_db()

# Global context processor to include site settings in templates
@app.context_processor
def inject_site_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    # Count unread messages for admin panel
    unread_count = 0
    if current_user.is_authenticated:
        unread_count = Message.query.filter_by(is_read=False).count()
    
    # Add current year for copyright
    current_year = datetime.now().year
    
    return {
        'settings': settings,
        'unread_messages': unread_count,
        'current_year': current_year
    }

# Routes
@app.route('/')
def home():
    # UPDATED: Only show featured projects that are also visible, ordered by order_index then date
    featured_projects = Project.query.filter_by(featured=True, is_visible=True).order_by(Project.order_index, Project.date_added.desc()).all()
    return render_template('home.html', projects=featured_projects)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Save message to database
        message = Message(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(message)
        db.session.commit()
        
        # Send email notification if properly configured
        try:
            # Use contact email from site settings, fall back to config
            settings = SiteSettings.query.first()
            contact_email = settings.contact_email if settings else app.config.get('CONTACT_EMAIL')
            
            email_subject = f"New contact form message from {form.name.data}"
            email_body = f"""
            Name: {form.name.data}
            Email: {form.email.data}
            
            Message:
            {form.message.data}
            """
            
            mail_message = MailMessage(
                subject=email_subject,
                recipients=[contact_email],
                body=email_body,
                sender=app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(mail_message)
            app.logger.info(f"Email notification sent to {contact_email}")
            flash('Your message has been sent. I will get back to you soon!', 'success')
        except Exception as e:
            app.logger.error(f"Error sending email notification: {str(e)}")
            flash('Your message was received, but there was an issue sending the email notification.', 'warning')
        
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/projects')
def projects():
    # UPDATED: Only show visible projects, ordered by order_index then date
    all_projects = Project.query.filter_by(is_visible=True).order_by(Project.order_index, Project.date_added.desc()).all()
    
    # Get unique categories - UPDATED: Use relationship
    categories = list(set(project.category.name for project in all_projects if project.category))
    
   # Get unique business goals for projects that have them (with color info)
    business_goal_objects = {}
    for project in all_projects:
        if project.business_goal:
            business_goal_objects[project.business_goal.name] = project.business_goal
    business_goals = list(business_goal_objects.values())
    
    return render_template('projects.html', projects=all_projects, categories=categories, business_goals=business_goals)

@app.route('/project/<int:id>')
def view_project(id):
    # UPDATED: Only show visible projects, or 404 if hidden
    project = Project.query.filter_by(id=id, is_visible=True).first_or_404()
    return render_template('project.html', project=project)

# Admin routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/contentadmin')
@login_required
def dashboard():
    # UPDATED: Order projects by order_index for consistent admin display
    projects = Project.query.order_by(Project.order_index, Project.date_added.desc()).all()
    projects_count = Project.query.count()
    
    # UPDATED: Count visible and featured projects separately
    visible_count = Project.query.filter_by(is_visible=True).count()
    hidden_count = Project.query.filter_by(is_visible=False).count()
    featured_count = Project.query.filter_by(featured=True, is_visible=True).count()
    
    # Categories count
    categories_count = Category.query.filter_by(is_active=True).count()
    
    # Business Goals count
    business_goals_count = BusinessGoal.query.filter_by(is_active=True).count()
    
    # Convert set to list for JSON serialization - Updated to use relationship
    categories = [project.category.name for project in projects if project.category]
    categories = list(set(categories))
    
    return render_template(
        'admin/dashboard.html', 
        projects=projects, 
        projects_count=projects_count,
        visible_count=visible_count,
        hidden_count=hidden_count,
        featured_count=featured_count,
        categories_count=categories_count,
        business_goals_count=business_goals_count,
        categories=categories,
        active_tab='dashboard'
    )

# Category Management Routes
@app.route('/contentadmin/categories')
@login_required
def categories():
    categories = Category.query.order_by(Category.name).all()
    
    # Get project counts for each category
    category_stats = {}
    for category in categories:
        category_stats[category.id] = {
            'total_projects': len(category.projects),
            'visible_projects': len([p for p in category.projects if p.is_visible])
        }
    
    return render_template('admin/categories.html', 
                         categories=categories, 
                         category_stats=category_stats,
                         active_tab='categories')

@app.route('/contentadmin/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            category = Category(
                name=form.name.data.strip(),
                is_active=form.is_active.data
            )
            db.session.add(category)
            db.session.commit()
            
            flash(f'Category "{category.name}" added successfully!', 'success')
            return redirect(url_for('categories'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating category: {str(e)}")
            flash(f'Error creating category: {str(e)}', 'error')
    
    return render_template('admin/category_form.html', 
                         form=form, 
                         title="Add New Category",
                         active_tab='categories')

@app.route('/contentadmin/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category, original_name=category.name)
    
    if form.validate_on_submit():
        try:
            category.name = form.name.data.strip()
            category.is_active = form.is_active.data
            db.session.commit()
            
            flash(f'Category "{category.name}" updated successfully!', 'success')
            return redirect(url_for('categories'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating category: {str(e)}")
            flash(f'Error updating category: {str(e)}', 'error')
    
    return render_template('admin/category_form.html', 
                         form=form, 
                         category=category,
                         title="Edit Category",
                         active_tab='categories')

@app.route('/contentadmin/categories/delete/<int:id>', methods=['POST'])
@login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has projects
    if category.projects:
        flash(f'Cannot delete category "{category.name}" - it has {len(category.projects)} project(s). Move projects to another category first.', 'error')
        return redirect(url_for('categories'))
    
    try:
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        flash(f'Category "{category_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting category: {str(e)}")
        flash(f'Error deleting category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))

@app.route('/contentadmin/categories/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_category(id):
    category = Category.query.get_or_404(id)
    
    try:
        category.is_active = not category.is_active
        db.session.commit()
        
        status = "activated" if category.is_active else "deactivated"
        flash(f'Category "{category.name}" {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error toggling category: {str(e)}")
        flash(f'Error updating category: {str(e)}', 'error')
    
    return redirect(url_for('categories'))


# Business Goals Management Routes
@app.route('/contentadmin/business-goals')
@login_required
def business_goals():
    business_goals = BusinessGoal.query.order_by(BusinessGoal.name).all()
    
    # Get project counts for each business goal
    goal_stats = {}
    for goal in business_goals:
        goal_stats[goal.id] = {
            'total_projects': len(goal.projects),
            'visible_projects': len([p for p in goal.projects if p.is_visible])
        }
    
    return render_template('admin/business_goals.html', 
                         business_goals=business_goals, 
                         goal_stats=goal_stats,
                         active_tab='business_goals')

@app.route('/contentadmin/business-goals/add', methods=['GET', 'POST'])
@login_required
def add_business_goal():
    form = BusinessGoalForm()
    
    if form.validate_on_submit():
        try:
            business_goal = BusinessGoal(
                name=form.name.data.strip(),
                color=form.color.data,
                is_active=form.is_active.data
            )
            db.session.add(business_goal)
            db.session.commit()
            
            flash(f'Business goal "{business_goal.name}" added successfully!', 'success')
            return redirect(url_for('business_goals'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating business goal: {str(e)}")
            flash(f'Error creating business goal: {str(e)}', 'error')
    
    return render_template('admin/business_goal_form.html', 
                         form=form, 
                         title="Add New Business Goal",
                         active_tab='business_goals')

@app.route('/contentadmin/business-goals/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_business_goal(id):
    business_goal = BusinessGoal.query.get_or_404(id)
    form = BusinessGoalForm(obj=business_goal, original_name=business_goal.name)
    
    if form.validate_on_submit():
        try:
            business_goal.name = form.name.data.strip()
            business_goal.color = form.color.data
            business_goal.is_active = form.is_active.data
            db.session.commit()
            
            flash(f'Business goal "{business_goal.name}" updated successfully!', 'success')
            return redirect(url_for('business_goals'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating business goal: {str(e)}")
            flash(f'Error updating business goal: {str(e)}', 'error')
    
    return render_template('admin/business_goal_form.html', 
                         form=form, 
                         business_goal=business_goal,
                         title="Edit Business Goal",
                         active_tab='business_goals')

@app.route('/contentadmin/business-goals/delete/<int:id>', methods=['POST'])
@login_required
def delete_business_goal(id):
    business_goal = BusinessGoal.query.get_or_404(id)
    
    # Check if business goal has projects
    if business_goal.projects:
        flash(f'Cannot delete business goal "{business_goal.name}" - it has {len(business_goal.projects)} project(s). Remove this goal from projects first.', 'error')
        return redirect(url_for('business_goals'))
    
    try:
        goal_name = business_goal.name
        db.session.delete(business_goal)
        db.session.commit()
        
        flash(f'Business goal "{goal_name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting business goal: {str(e)}")
        flash(f'Error deleting business goal: {str(e)}', 'error')
    
    return redirect(url_for('business_goals'))

@app.route('/contentadmin/business-goals/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_business_goal(id):
    business_goal = BusinessGoal.query.get_or_404(id)
    
    try:
        business_goal.is_active = not business_goal.is_active
        db.session.commit()
        
        status = "activated" if business_goal.is_active else "deactivated"
        flash(f'Business goal "{business_goal.name}" {status} successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error toggling business goal: {str(e)}")
        flash(f'Error updating business goal: {str(e)}', 'error')
    
    return redirect(url_for('business_goals'))


@app.route('/contentadmin/add-project', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    
    if form.validate_on_submit():
        try:
            # Handle file upload if any
            thumbnail_url = form.thumbnail_url.data
            
            if form.thumbnail_upload.data and hasattr(form.thumbnail_upload.data, 'filename') and form.thumbnail_upload.data.filename:
                filename = secure_filename(form.thumbnail_upload.data.filename)
                upload_folder = os.path.join('static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                form.thumbnail_upload.data.save(file_path)
                thumbnail_url = url_for('static', filename=f'uploads/{filename}')
                app.logger.debug(f"Thumbnail saved to {file_path}, URL set to {thumbnail_url}")
            
            project = Project(
                title=form.title.data,
                description=form.description.data,
                is_external=form.is_external.data,
                external_url=form.external_url.data if form.is_external.data else None,
                internal_content=form.internal_content.data if not form.is_external.data else None,
                thumbnail_url=thumbnail_url,
                category_id=form.category_id.data,  # UPDATED: Use category_id
                business_goal_id=form.business_goal_id.data if form.business_goal_id.data != 0 else None,  # NEW: Business goal assignment
                is_visible=form.is_visible.data,
                featured=form.featured.data,
                order_index=form.order_index.data or 0,
                results=form.results.data,
                # Additional fields
                company=form.company.data,
                tools_used=form.tools_used.data,
                # Resource URL and text for PDFs/documents
                resource_url=form.resource_url.data if form.resource_url.data else None,
                resource_text=form.resource_text.data if form.resource_text.data else "View Resource"
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project added successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating project: {str(e)}")
            flash(f'Error creating project: {str(e)}', 'error')
    
    return render_template('admin/project_form.html', form=form, title="Add New Project", active_tab='works')

@app.route('/contentadmin/edit-project/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        try:
            # Update project data
            project.title = form.title.data
            project.description = form.description.data
            project.is_external = form.is_external.data
            project.external_url = form.external_url.data if form.is_external.data else None
            project.internal_content = form.internal_content.data if not form.is_external.data else None
            project.category_id = form.category_id.data  # UPDATED: Use category_id
            project.business_goal_id = form.business_goal_id.data if form.business_goal_id.data != 0 else None  # NEW: Business goal assignment
            project.is_visible = form.is_visible.data
            project.featured = form.featured.data
            project.order_index = form.order_index.data or 0
            project.results = form.results.data
            project.company = form.company.data
            project.tools_used = form.tools_used.data
            project.resource_url = form.resource_url.data
            project.resource_text = form.resource_text.data
            
            # Handle file upload if any
            if form.thumbnail_url.data:
                project.thumbnail_url = form.thumbnail_url.data
            
            if form.thumbnail_upload.data and hasattr(form.thumbnail_upload.data, 'filename') and form.thumbnail_upload.data.filename:
                filename = secure_filename(form.thumbnail_upload.data.filename)
                upload_folder = os.path.join('static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                form.thumbnail_upload.data.save(file_path)
                project.thumbnail_url = url_for('static', filename=f'uploads/{filename}')
                app.logger.debug(f"Thumbnail saved to {file_path}, URL set to {project.thumbnail_url}")
            
            db.session.commit()
            
            flash('Project updated successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating project: {str(e)}")
            flash(f'Error updating project: {str(e)}', 'error')
    
    return render_template('admin/project_form.html', form=form, project=project, title="Edit Project", active_tab='works')

@app.route('/contentadmin/delete-project/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/contentadmin/messages')
@login_required
def view_messages():
    messages = Message.query.order_by(Message.date_sent.desc()).all()
    
    # Mark all messages as read
    for message in messages:
        message.is_read = True
    
    db.session.commit()
    
    return render_template('admin/messages.html', messages=messages, active_tab='messages')

@app.route('/contentadmin/delete-message/<int:id>', methods=['POST'])
@login_required
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    
    flash('Message deleted successfully', 'success')
    return redirect(url_for('view_messages'))

@app.route('/contentadmin/profile', methods=['GET', 'POST'])
@login_required
def profile():
    update_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()
    
    # Handle profile update
    if 'update_profile' in request.form and update_form.validate_on_submit():
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Handle password change
    if 'change_password' in request.form and password_form.validate_on_submit():
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Password changed successfully', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Current password is incorrect', 'error')
    
    return render_template(
        'admin/profile.html', 
        update_form=update_form, 
        password_form=password_form,
        active_tab='profile'
    )

@app.route('/contentadmin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    form = SiteSettingsForm(obj=settings)
    
    if form.validate_on_submit():
        try:
            # Handle file uploads first before populating object
            profile_image = form.profile_image.data
            if profile_image and hasattr(profile_image, 'filename') and profile_image.filename:
                # Save the profile image
                filename = secure_filename(profile_image.filename)
                upload_folder = os.path.join('static', 'uploads', 'profile')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                profile_image.save(file_path)
                
                # Store the URL (not the file object)
                form.profile_image.data = url_for('static', filename=f'uploads/profile/{filename}')
                app.logger.debug(f"Profile image saved to {file_path}, URL set to {form.profile_image.data}")
            else:
                # Keep the existing value if no new file was uploaded
                form.profile_image.data = settings.profile_image
                
            # Handle default project thumbnail similarly
            default_thumbnail = form.default_project_thumbnail.data
            if default_thumbnail and hasattr(default_thumbnail, 'filename') and default_thumbnail.filename:
                # Save the thumbnail
                filename = secure_filename(default_thumbnail.filename)
                upload_folder = os.path.join('static', 'uploads', 'defaults')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, filename)
                default_thumbnail.save(file_path)
                
                # Store the URL
                form.default_project_thumbnail.data = url_for('static', filename=f'uploads/defaults/{filename}')
                app.logger.debug(f"Default thumbnail saved to {file_path}, URL set to {form.default_project_thumbnail.data}")
            else:
                # Keep existing value
                form.default_project_thumbnail.data = settings.default_project_thumbnail
            
            # Now populate the object with the form data (including URLs for file fields)
            form.populate_obj(settings)
            db.session.commit()
            
            flash('Settings updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating settings: {str(e)}")
            flash(f'Error updating settings: {str(e)}', 'error')
        
        return redirect(url_for('admin_settings'))
    
    return render_template('admin/settings.html', form=form, settings=settings, active_tab='settings')

@app.route('/contentadmin/export-settings', methods=['POST'])
@login_required
def export_settings():
    settings = SiteSettings.query.first()
    if not settings:
        flash('No settings to export', 'error')
        return redirect(url_for('admin_settings'))
    
    # Convert settings to dictionary
    settings_dict = {
        'site_title': settings.site_title,
        'site_subtitle': settings.site_subtitle,
        'about_short': settings.about_short,
        'about_me': settings.about_me,
        'profile_image': settings.profile_image,
        'brand_name': settings.brand_name,
        'logo_url': settings.logo_url,
        'contact_email': settings.contact_email,
        'banner_image': settings.banner_image,
        'banner_gradient_start': settings.banner_gradient_start,
        'banner_gradient_end': settings.banner_gradient_end,
        'hero_text_color': settings.hero_text_color,
        'link_hover_color': settings.link_hover_color,
        'button_hover_color': settings.button_hover_color,
        'linkedin_url': settings.linkedin_url,
        'linkedin_active': settings.linkedin_active,
    }
    
    # Return as downloadable JSON file
    return jsonify(settings_dict)

@app.route('/contentadmin/import-settings', methods=['GET', 'POST'])
@login_required
def import_settings():
    if request.method == 'POST':
        if 'settings_file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        file = request.files['settings_file']
        
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        if file:
            try:
                settings_data = json.loads(file.read().decode('utf-8'))
                settings = SiteSettings.query.first()
                
                if not settings:
                    settings = SiteSettings()
                    db.session.add(settings)
                
                # Update settings from imported data
                settings.update_from_form(settings_data)
                db.session.commit()
                
                flash('Settings imported successfully!', 'success')
                return redirect(url_for('admin_settings'))
            
            except Exception as e:
                flash(f'Error importing settings: {str(e)}', 'error')
                return redirect(request.url)
    
    return render_template('admin/import_settings.html', active_tab='settings')

# Helper route to check file upload directories
@app.route('/check-uploads')
def check_uploads():
    # Check if static and uploads directories exist
    static_dir = os.path.join(app.root_path, 'static')
    uploads_dir = os.path.join(static_dir, 'uploads')
    profile_dir = os.path.join(uploads_dir, 'profile')
    defaults_dir = os.path.join(uploads_dir, 'defaults')
    
    # Create directories if they don't exist
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(defaults_dir, exist_ok=True)
    
    # Check if directories are writable
    results = {
        'static_exists': os.path.exists(static_dir),
        'static_writable': os.access(static_dir, os.W_OK),
        'uploads_exists': os.path.exists(uploads_dir),
        'uploads_writable': os.access(uploads_dir, os.W_OK),
        'profile_exists': os.path.exists(profile_dir),
        'profile_writable': os.access(profile_dir, os.W_OK),
        'defaults_exists': os.path.exists(defaults_dir),
        'defaults_writable': os.access(defaults_dir, os.W_OK),
        'app_root': app.root_path,
        'static_path': static_dir
    }
    
    # Format results as HTML
    html = '<h1>Upload Directory Check</h1>'
    for key, value in results.items():
        html += f'<p><strong>{key}:</strong> {value}</p>'
    
    return html

if __name__ == '__main__':
    app.run(debug=True)
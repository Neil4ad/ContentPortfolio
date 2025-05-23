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
from models import db, User, Project, Message, SiteSettings
from forms import LoginForm, ContactForm, ProjectForm, ChangePasswordForm, UpdateProfileForm, SiteSettingsForm

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

# Usage examples in templates:
# {{ project.description|truncate_smart(120) }}
# {{ project.description|truncate_sentences(1) }}
# {{ project.description|word_count }} words
# {{ project.description|reading_time }}

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and admin user
@app.before_first_request
def initialize_db():
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
    featured_projects = Project.query.filter_by(featured=True).order_by(Project.date_added.desc()).all()
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
    all_projects = Project.query.order_by(Project.date_added.desc()).all()
    
    # Get unique categories - FIXED: convert set to list for JSON serialization
    categories = list(set(project.category for project in all_projects if project.category))
    
    return render_template('projects.html', projects=all_projects, categories=categories)

@app.route('/project/<int:id>')
def view_project(id):
    project = Project.query.get_or_404(id)
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
    projects = Project.query.order_by(Project.date_added.desc()).all()
    projects_count = Project.query.count()
    featured_count = Project.query.filter_by(featured=True).count()
    
    # Convert set to list for JSON serialization
    categories = list(set(project.category for project in projects if project.category))
    
    return render_template(
        'admin/dashboard.html', 
        projects=projects, 
        projects_count=projects_count,
        featured_count=featured_count,
        categories=categories,
        active_tab='dashboard'
    )

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
                category=form.category.data,
                featured=form.featured.data,
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
    
    # If GET request or form validation fails
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
            project.category = form.category.data
            project.featured = form.featured.data
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
        'primary_text_color': settings.primary_text_color,
        'secondary_text_color': settings.secondary_text_color,
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
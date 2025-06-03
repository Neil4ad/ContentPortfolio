from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to projects
    projects = db.relationship('Project', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_external = db.Column(db.Boolean, default=False)
    external_url = db.Column(db.String(255), nullable=True)
    internal_content = db.Column(db.Text, nullable=True)
    thumbnail_url = db.Column(db.String(255), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Updated category relationship
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    featured = db.Column(db.Boolean, default=False)
    is_visible = db.Column(db.Boolean, default=True, nullable=False)
    order_index = db.Column(db.Integer, default=0, nullable=False)
    results = db.Column(db.Text, nullable=True)
    
    # Additional metadata fields
    company = db.Column(db.String(255), nullable=True)
    tools_used = db.Column(db.String(255), nullable=True)
    
    # Resource link fields (e.g., PDF downloads)
    resource_url = db.Column(db.String(255), nullable=True)
    resource_text = db.Column(db.String(100), nullable=True, default="View Resource")
    
    def set_default_thumbnail(self):
        """Set default thumbnail if none provided and default exists in settings"""
        if not self.thumbnail_url:
            try:
                settings = SiteSettings.query.first()
                if settings and settings.default_project_thumbnail:
                    self.thumbnail_url = settings.default_project_thumbnail
            except Exception:
                # Silently continue if unable to get default thumbnail
                # This prevents app startup issues
                pass
    
    def __repr__(self):
        return f'<Project {self.title}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Message from {self.name}>'


class SiteSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic site information
    site_title = db.Column(db.String(100), default="Content Designer & Strategist")
    site_subtitle = db.Column(db.String(255), default="Crafting clear, compelling digital experiences that engage audiences and drive results")
    about_short = db.Column(db.Text, default="I help brands communicate more effectively through strategic content design, UX writing, and messaging that connects with audiences.")
    
    # About page content
    about_me = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    
    # Default project settings
    default_project_thumbnail = db.Column(db.String(255), nullable=True)
    
    # Brand settings
    brand_name = db.Column(db.String(100), default="Jane Smith")
    logo_url = db.Column(db.String(255), nullable=True)
    contact_email = db.Column(db.String(120), default="contact@example.com")
    
    # Banner settings
    banner_image = db.Column(db.String(255), nullable=True)
    banner_gradient_start = db.Column(db.String(20), default="#4F46E5")
    banner_gradient_end = db.Column(db.String(20), default="#3B82F6")
    
    # Color settings (accent colors only - text colors handled by CSS dark/light mode)
    hero_text_color = db.Column(db.String(20), default="#ffffff")
    link_hover_color = db.Column(db.String(20), default="#4F46E5")
    button_hover_color = db.Column(db.String(20), default="#3B82F6")
    
    # Social media settings
    linkedin_url = db.Column(db.String(255), nullable=True)
    linkedin_active = db.Column(db.Boolean, default=False)
    
    def update_from_form(self, form_data):
        """Update settings from form data dictionary"""
        # Mapping of form fields to model attributes
        field_mapping = {
            'site_title': 'site_title',
            'site_subtitle': 'site_subtitle', 
            'about_short': 'about_short',
            'about_me': 'about_me',
            'brand_name': 'brand_name',
            'logo_url': 'logo_url',
            'contact_email': 'contact_email',
            'banner_image': 'banner_image',
            'banner_gradient_start': 'banner_gradient_start',
            'banner_gradient_end': 'banner_gradient_end',
            'hero_text_color': 'hero_text_color',
            'link_hover_color': 'link_hover_color',
            'button_hover_color': 'button_hover_color',
            'linkedin_url': 'linkedin_url',
        }
        
        # Update string/text fields
        for form_field, model_attr in field_mapping.items():
            if form_field in form_data:
                setattr(self, model_attr, form_data[form_field])
        
        # Handle boolean fields separately
        self.linkedin_active = form_data.get('linkedin_active', False)
    
    def __repr__(self):
        return f'<SiteSettings: {self.site_title}>'
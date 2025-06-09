from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, URLField, SelectField, HiddenField, ColorField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, Optional, ValidationError, NumberRange
from flask_wtf.file import FileField, FileAllowed
from models import Category, BusinessGoal


# Custom validator for thumbnail URLs that accepts both full URLs and local paths
def flexible_url_validator(form, field):
    """
    Custom validator that accepts:
    1. Full URLs (http:// or https://)
    2. Relative paths starting with static/uploads/
    3. Flask url_for() generated paths starting with /static/
    4. Empty/None values
    """
    if not field.data:
        return  # Optional field, empty is OK
    
    url = field.data.strip()
    
    # Check if it's a full URL
    if url.startswith(('http://', 'https://')):
        # Use the built-in URL validator for full URLs
        try:
            URL()(form, field)
        except ValidationError:
            raise ValidationError('Please enter a valid URL.')
    
    # Check if it's a local upload path
    elif url.startswith(('static/uploads/', '/static/uploads/', '/static/')):
        # Valid local path
        return
    
    # If it doesn't match any valid pattern
    else:
        raise ValidationError('Please provide a valid image URL or upload an image.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Send Message')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(), 
        Length(min=2, max=50, message='Category name must be between 2 and 50 characters')
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Category')
    
    def __init__(self, original_name=None, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
    
    def validate_name(self, name):
        # Check for duplicate category names (case-insensitive)
        existing_category = Category.query.filter(
            Category.name.ilike(name.data.strip())
        ).first()
        
        if existing_category and existing_category.name.lower() != (self.original_name or '').lower():
            raise ValidationError('A category with this name already exists.')


class BusinessGoalForm(FlaskForm):
    name = StringField('Business Goal Name', validators=[
        DataRequired(), 
        Length(min=2, max=50, message='Business goal name must be between 2 and 50 characters')
    ])
    color = ColorField('Button Color', default="#3B82F6", validators=[DataRequired()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Business Goal')
    
    def __init__(self, original_name=None, *args, **kwargs):
        super(BusinessGoalForm, self).__init__(*args, **kwargs)
        self.original_name = original_name
    
    def validate_name(self, name):
        # Check for duplicate business goal names (case-insensitive)
        existing_goal = BusinessGoal.query.filter(
            BusinessGoal.name.ilike(name.data.strip())
        ).first()
        
        if existing_goal and existing_goal.name.lower() != (self.original_name or '').lower():
            raise ValidationError('A business goal with this name already exists.')


class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    is_external = BooleanField('External Link')
    external_url = URLField('External URL', validators=[Optional(), URL()])
    internal_content = TextAreaField('Internal Content (HTML or Markdown)')
    thumbnail_upload = FileField('Upload Thumbnail', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    # FIXED: Use custom validator instead of strict URL validator
    thumbnail_url = StringField('Or Thumbnail URL', validators=[Optional(), flexible_url_validator])
    
    # Updated: Category dropdown instead of text field
    category_id = SelectField('Category', coerce=int, validators=[DataRequired(message='Please select a category')])
    
    # NEW: Business Goal dropdown (optional)
    business_goal_id = SelectField('Business Goal', coerce=int, validators=[Optional()])
    
    is_visible = BooleanField('Visible on Site', default=True)
    featured = BooleanField('Featured Project')
    order_index = IntegerField('Display Order', validators=[Optional(), NumberRange(min=0, max=9999)], default=0)
    results = TextAreaField('Results', validators=[Optional()])
    
    # Fields for additional metadata
    company = StringField('Client/Company', validators=[Optional(), Length(max=255)])
    tools_used = StringField('Tools Used', validators=[Optional(), Length(max=255)])
    
    # Fields for resource links (e.g., PDF) - also fixed with custom validator
    resource_url = StringField('Resource URL', validators=[Optional(), flexible_url_validator])
    resource_text = StringField('Resource Button Text', validators=[Optional(), Length(max=100)],
                              default="View Resource")
    
    submit = SubmitField('Save Project')
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        
        # Populate category choices with active categories
        self.category_id.choices = [
            (category.id, category.name) 
            for category in Category.query.filter_by(is_active=True).order_by(Category.name).all()
        ]
        # Add empty option if no category selected
        if not self.category_id.data:
            self.category_id.choices.insert(0, (0, 'Select a category...'))
        
        # Populate business goal choices with active business goals
        business_goal_choices = [
            (goal.id, goal.name) 
            for goal in BusinessGoal.query.filter_by(is_active=True).order_by(BusinessGoal.name).all()
        ]
        # Add empty option (since business goals are optional)
        business_goal_choices.insert(0, (0, 'Select a business goal (optional)...'))
        self.business_goal_id.choices = business_goal_choices


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')


class SiteSettingsForm(FlaskForm):
    # General site information
    site_title = StringField('Site Title', validators=[DataRequired()])
    site_subtitle = StringField('Site Subtitle')
    about_short = TextAreaField('Short About Text')
    
    # About page content
    about_me = TextAreaField('About Me Content', validators=[Optional()], render_kw={"rows": 10})
    profile_image = FileField('Profile Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    
    # Default project settings
    default_project_thumbnail = FileField('Default Project Thumbnail', validators=[
        Optional(),
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    
    # Branding
    brand_name = StringField('Brand Name')
    logo_url = StringField('Logo URL')
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    
    # Banner settings
    banner_image = StringField('Banner Image URL')
    banner_gradient_start = ColorField('Gradient Start Color', default="#4F46E5")
    banner_gradient_end = ColorField('Gradient End Color', default="#3B82F6")
    
    # Color settings (only accent colors - text colors handled by CSS dark/light mode)
    hero_text_color = ColorField('Hero Text Color', default="#ffffff")
    link_hover_color = ColorField('Link Hover Color', default="#4F46E5")
    button_hover_color = ColorField('Button Hover Color', default="#3B82F6")
    
    # Social Media
    linkedin_url = StringField('LinkedIn URL')
    linkedin_active = BooleanField('Show LinkedIn')
    
    submit = SubmitField('Save Settings')
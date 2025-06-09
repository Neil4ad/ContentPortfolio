/**
 * Main JavaScript file for portfolio website
 * Contains navigation, business goal colors, and utility functions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize core components
    initMobileMenu();
    
    // Initialize dynamic styling
    applyBusinessGoalColors();
    
    // Initialize utility functions
    initializeUtilityFunctions();
});

/**
 * Initialize mobile menu functionality
 */
function initMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navbarLinks = document.querySelector('.navbar-links');
    
    if (!mobileToggle || !navbarLinks) {
        return;
    }
    
    mobileToggle.addEventListener('click', function() {
        navbarLinks.classList.toggle('open');
        mobileToggle.setAttribute('aria-expanded', 
            navbarLinks.classList.contains('open') ? 'true' : 'false');
    });
}

/**
 * Apply business goal colors to all elements with data-goal-color
 */
function applyBusinessGoalColors() {
    const elementsWithColors = document.querySelectorAll('[data-goal-color]');
    
    elementsWithColors.forEach(function(element) {
        const color = element.getAttribute('data-goal-color');
        if (!color) return;
        
        if (element.classList.contains('business-goal-filter-btn')) {
            // Filter buttons: colored border, colored background when active
            element.style.borderColor = color;
            if (element.classList.contains('nd-active') || element.classList.contains('active')) {
                element.style.backgroundColor = color;
                element.style.color = 'white';
            }
        } else {
            // Everything else: colored background
            element.style.backgroundColor = color;
            element.style.color = 'white';
        }
    });
    
    // Handle "All" button for business goals on page load
    const allBusinessGoalButton = document.querySelector('.business-goal-filter-btn.nd-active:not([data-goal-color])');
    if (allBusinessGoalButton) {
        allBusinessGoalButton.style.backgroundColor = 'var(--primary-color)';
        allBusinessGoalButton.style.color = 'white';
        allBusinessGoalButton.style.borderColor = 'var(--primary-color)';
    }
}

/**
 * Initialize additional utility functions for better user experience
 */
function initializeUtilityFunctions() {
    // Smooth scroll for anchor links
    initSmoothScroll();
    
    // Enhanced form interactions
    enhanceFormExperience();
}

/**
 * Smooth scroll behavior for anchor links
 */
function initSmoothScroll() {
    const anchors = document.querySelectorAll('a[href^="#"]');
    anchors.forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Enhance form user experience
 */
function enhanceFormExperience() {
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        // Add loading state to submit buttons
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.style.opacity = '0.7';
                submitBtn.style.cursor = 'not-allowed';
                
                // Restore after a timeout in case submission fails
                setTimeout(function() {
                    submitBtn.style.opacity = '';
                    submitBtn.style.cursor = '';
                }, 5000);
            }
        });
    });
    
    // Enhanced focus states for better accessibility
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(function(input) {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}
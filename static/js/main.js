/**
 * Main JavaScript file for portfolio website
 * Contains navigation and utility functions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize components that exist in the current page
    initMobileMenu();
    initThemeToggle();
});

/**
 * Initialize mobile menu functionality
 */
function initMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navbarLinks = document.querySelector('.navbar-links');
    
    if (!mobileToggle || !navbarLinks) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    mobileToggle.addEventListener('click', function() {
        navbarLinks.classList.toggle('open');
        mobileToggle.setAttribute('aria-expanded', 
            navbarLinks.classList.contains('open') ? 'true' : 'false');
    });
}

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
    const themeToggleButton = document.querySelector('.theme-toggle');
    const sunIcon = document.querySelector('.sun-icon');
    const moonIcon = document.querySelector('.moon-icon');
    const htmlElement = document.documentElement;
    
    if (!themeToggleButton || !sunIcon || !moonIcon) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    // Apply theme based on localStorage or system preference
    applyTheme(getThemePreference());
    
    // Toggle theme when button is clicked
    themeToggleButton.addEventListener('click', toggleTheme);
}

/**
 * Get theme preference from localStorage or system
 * @returns {string} 'dark' or 'light'
 */
function getThemePreference() {
    // First check localStorage
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme) {
        return savedTheme;
    }
    
    // If no saved preference, check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

/**
 * Apply theme to the document
 * @param {string} theme 'dark' or 'light'
 */
function applyTheme(theme) {
    const sunIcon = document.querySelector('.sun-icon');
    const moonIcon = document.querySelector('.moon-icon');
    const htmlElement = document.documentElement;

    if (!sunIcon || !moonIcon) {
        // Missing elements, apply theme anyway but skip icon changes
        htmlElement.setAttribute('data-theme', theme);
        return;
    }
    
    if (theme === 'dark') {
        htmlElement.setAttribute('data-theme', 'dark');
        sunIcon.style.display = 'block';
        moonIcon.style.display = 'none';
    } else {
        htmlElement.setAttribute('data-theme', 'light');
        sunIcon.style.display = 'none';
        moonIcon.style.display = 'block';
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    applyTheme(newTheme);
    saveThemePreference(newTheme);
}

/**
 * Save theme preference to localStorage
 * @param {string} theme 'dark' or 'light'
 */
function saveThemePreference(theme) {
    localStorage.setItem('theme', theme);
}
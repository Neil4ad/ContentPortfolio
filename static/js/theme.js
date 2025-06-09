/**
 * Theme toggle functionality
 * This script handles light/dark mode toggling
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const themeToggle = document.querySelector('.theme-toggle');
    const sunIcon = document.querySelector('.sun-icon');
    const moonIcon = document.querySelector('.moon-icon');
    const htmlElement = document.documentElement;
    
    // Function to set theme
    function setTheme(theme) {
        if (theme === 'dark') {
            htmlElement.setAttribute('data-theme', 'dark');
            try {
                localStorage.setItem('portfolio-theme', 'dark');
            } catch (e) {
                console.log('LocalStorage not available');
            }
        } else {
            htmlElement.setAttribute('data-theme', 'light');
            try {
                localStorage.setItem('portfolio-theme', 'light');
            } catch (e) {
                console.log('LocalStorage not available');
            }
        }
    }
    
    // Check for saved theme preference or user preference
    function getPreferredTheme() {
        let storedTheme;
        try {
            storedTheme = localStorage.getItem('portfolio-theme');
        } catch (e) {
            console.log('LocalStorage not available');
        }
        
        // If we have a stored preference, use it
        if (storedTheme) {
            return storedTheme;
        }
        
        // Otherwise, check for OS preference
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches 
            ? 'dark' 
            : 'light';
    }
    
    // Set initial theme
    const preferredTheme = getPreferredTheme();
    setTheme(preferredTheme);
    
    // Toggle theme on click
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }
    
    // Listen for OS theme changes
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
            // Only change theme if the user hasn't manually set a preference
            let userSetTheme;
            try {
                userSetTheme = localStorage.getItem('portfolio-theme');
            } catch (e) {
                console.log('LocalStorage not available');
            }
            
            if (!userSetTheme) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
});

// Apply dynamic CSS variables from data attributes
document.addEventListener('DOMContentLoaded', function() {
    const body = document.body;
    if (body.classList.contains('dynamic-theme-vars')) {
        const bannerStart = body.getAttribute('data-banner-start') || '#4F46E5';
        const bannerEnd = body.getAttribute('data-banner-end') || '#3B82F6';
        const heroText = body.getAttribute('data-hero-text') || '#ffffff';
        const linkHover = body.getAttribute('data-link-hover') || '#4f46e5';
        const buttonHover = body.getAttribute('data-button-hover') || '#3b82f6';
        
        document.documentElement.style.setProperty('--banner-gradient-start', bannerStart);
        document.documentElement.style.setProperty('--banner-gradient-end', bannerEnd);
        document.documentElement.style.setProperty('--hero-text-color', heroText);
        document.documentElement.style.setProperty('--link-hover-color', linkHover);
        document.documentElement.style.setProperty('--button-hover-color', buttonHover);
    }
});
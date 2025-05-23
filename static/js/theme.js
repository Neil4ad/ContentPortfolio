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
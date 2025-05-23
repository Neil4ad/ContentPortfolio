/**
 * Mobile menu toggle functionality
 * This script handles the mobile menu open/close actions
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navbarLinks = document.querySelector('.navbar-links');
    
    // If mobile toggle button exists in the DOM
    if (mobileToggle && navbarLinks) {
        // Set up click event for mobile menu toggle
        mobileToggle.addEventListener('click', function(e) {
            // Prevent default behavior
            e.preventDefault();
            
            // Get current state
            const isExpanded = this.getAttribute('aria-expanded') === 'true';
            
            // Toggle aria-expanded attribute
            this.setAttribute('aria-expanded', !isExpanded);
            
            // Toggle active class on navbar links
            navbarLinks.classList.toggle('active');
            
            // Announce state to screen readers
            this.setAttribute('aria-label', 
                isExpanded ? 'Open navigation menu' : 'Close navigation menu'
            );
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            // Only if the menu is open
            if (navbarLinks.classList.contains('active')) {
                // Check if click is outside mobile menu and not on the toggle button
                if (!navbarLinks.contains(e.target) && !mobileToggle.contains(e.target)) {
                    // Close the menu
                    navbarLinks.classList.remove('active');
                    mobileToggle.setAttribute('aria-expanded', 'false');
                    mobileToggle.setAttribute('aria-label', 'Open navigation menu');
                }
            }
        });
    }
});
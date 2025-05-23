/**
 * Category filter functionality for projects page
 * This script provides the filtering functionality for project categories
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize category filtering if filter container exists
    const filterContainer = document.getElementById('nd-filter-container');
    if (filterContainer) {
        initCategoryFilters();
    }
});

/**
 * Initialize the category filters
 */
function initCategoryFilters() {
    const allButtons = document.querySelectorAll('.category-filter-btn');
    
    // Add click event to each filter button
    allButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the category from data attribute or custom attribute
            const category = this.getAttribute('data-category') || 
                             this.getAttribute('onclick').match(/'([^']+)'/)[1];
            
            // Filter the projects
            filterProjectsByCategory(this, category);
        });
    });
    
    // Check URL hash to see if we should filter on page load
    const hash = window.location.hash.substring(1);
    if (hash && hash.startsWith('category-')) {
        const category = hash.replace('category-', '');
        const button = document.querySelector(`[data-category="${category}"]`) || 
                       document.getElementById(`nd-filter-${category.toLowerCase().replace(/\s+/g, '-')}`);
        
        if (button) {
            filterProjectsByCategory(button, category);
        }
    }
}

/**
 * Filter projects by category
 * @param {HTMLElement} clickedButton - The button that was clicked
 * @param {string} category - The category to filter by
 */
function filterProjectsByCategory(clickedButton, category) {
    // Update all button styles
    const allButtons = document.querySelectorAll('.category-filter-btn');
    allButtons.forEach(button => {
        button.classList.remove('nd-active');
    });
    
    // Set active style for clicked button only
    clickedButton.classList.add('nd-active');
    
    // Update URL hash for bookmarkability
    window.location.hash = `category-${category.toLowerCase().replace(/\s+/g, '-')}`;
    
    // Filter projects
    const projects = document.querySelectorAll('.project-card');
    let visibleCount = 0;
    
    projects.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (category === 'all' || cardCategory === category) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show "no projects" message if no projects are visible
    const noProjectsMessage = document.querySelector('.no-projects-message');
    if (noProjectsMessage) {
        if (visibleCount === 0) {
            noProjectsMessage.style.display = 'block';
        } else {
            noProjectsMessage.style.display = 'none';
        }
    }
}

// Make the function available globally for inline onclick handlers
window.ndFilterProjects = function(clickedButton, category) {
    filterProjectsByCategory(clickedButton, category);
};
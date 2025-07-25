/**
 * Category and Business Goal filter functionality for projects page
 * UPDATED: Independent filtering - clicking one resets the other
 */

// Global state to track active filters
let activeFilters = {
    category: 'all',
    business_goal: 'all'
};

document.addEventListener('DOMContentLoaded', function() {
    // Initialize filtering if filter container exists
    const filterContainer = document.getElementById('nd-filter-container');
    if (filterContainer) {
        initFilters();
    }
});

/**
 * Initialize the filters
 */
function initFilters() {
    const allButtons = document.querySelectorAll('.category-filter-btn, .business-goal-filter-btn');
    
    // Add click event to each filter button
    allButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Get the filter type and value from the onclick attribute
            const onclickAttr = this.getAttribute('onclick');
            if (onclickAttr) {
                // Parse the onclick to extract parameters
                const matches = onclickAttr.match(/ndFilterProjects\(this,\s*'([^']+)',\s*'([^']+)'\)/);
                if (matches) {
                    const filterValue = matches[1];
                    const filterType = matches[2];
                    filterProjects(this, filterValue, filterType);
                }
            }
        });
    });
    
    // Check URL hash to see if we should filter on page load
    const hash = window.location.hash.substring(1);
    if (hash) {
        if (hash.startsWith('category-')) {
            const category = hash.replace('category-', '').replace(/-/g, ' ');
            const button = document.querySelector(`[onclick*="'${category}', 'category'"]`);
            if (button) {
                filterProjects(button, category, 'category');
            }
        } else if (hash.startsWith('goal-')) {
            const goal = hash.replace('goal-', '').replace(/-/g, ' ');
            const button = document.querySelector(`[onclick*="'${goal}', 'business_goal'"]`);
            if (button) {
                filterProjects(button, goal, 'business_goal');
            }
        }
    }
}

/**
 * Filter projects by category or business goal
 * UPDATED: Independent filtering - reset other filter when one is clicked
 * @param {HTMLElement} clickedButton - The button that was clicked
 * @param {string} filterValue - The value to filter by ('all' or specific category/goal)
 * @param {string} filterType - Either 'category' or 'business_goal'
 */
function filterProjects(clickedButton, filterValue, filterType) {
    // UPDATED: Reset the other filter to 'all' when this one is clicked
    if (filterType === 'category') {
        activeFilters.category = filterValue;
        activeFilters.business_goal = 'all'; // Reset business goal filter
        
        // Reset business goal buttons
        resetFilterButtons('.business-goal-filter-btn');
        setActiveButton('nd-filter-all-goals');
    } else if (filterType === 'business_goal') {
        activeFilters.business_goal = filterValue;
        activeFilters.category = 'all'; // Reset category filter
        
        // Reset category buttons
        resetFilterButtons('.category-filter-btn');
        setActiveButton('nd-filter-all-categories');
    }
    
    // Update the active filter state for the clicked type
    activeFilters[filterType] = filterValue;
    
    // Update button styles for the specific filter type
    const filterClass = filterType === 'category' ? '.category-filter-btn' : '.business-goal-filter-btn';
    const allFilterButtons = document.querySelectorAll(filterClass);
    
    allFilterButtons.forEach(button => {
        button.classList.remove('nd-active');
        // Reset any custom colors for business goal buttons
        if (filterType === 'business_goal') {
            const color = button.getAttribute('data-goal-color');
            if (color) {
                button.style.backgroundColor = '';
                button.style.color = '';
                button.style.borderColor = color;
            } else {
                // Reset "All" button styles
                button.style.backgroundColor = '';
                button.style.color = '';
                button.style.borderColor = '';
            }
        }
    });
    
    // Set active style for clicked button only
    clickedButton.classList.add('nd-active');
    
    // Apply custom color for business goal buttons when active
    if (filterType === 'business_goal') {
        const color = clickedButton.getAttribute('data-goal-color');
        if (color && filterValue !== 'all') {
            clickedButton.style.backgroundColor = color;
            clickedButton.style.color = 'white';
            clickedButton.style.borderColor = color;
        } else if (filterValue === 'all') {
            // Use default active styling for "All" button
            clickedButton.style.backgroundColor = 'var(--primary-color)';
            clickedButton.style.color = 'white';
            clickedButton.style.borderColor = 'var(--primary-color)';
        }
    }
    
    // Update URL hash for bookmarkability
    if (filterValue !== 'all') {
        const hashPrefix = filterType === 'category' ? 'category-' : 'goal-';
        window.location.hash = `${hashPrefix}${filterValue.toLowerCase().replace(/\s+/g, '-')}`;
    } else {
        // Clear the hash since we're showing all
        window.location.hash = '';
    }
    
    // Apply the filter (now effectively single filter since other is reset to 'all')
    applyFilters();
}

/**
 * Helper function to reset filter buttons
 */
function resetFilterButtons(selector) {
    const buttons = document.querySelectorAll(selector);
    buttons.forEach(button => {
        button.classList.remove('nd-active');
        // Reset business goal button colors
        if (selector.includes('business-goal')) {
            const color = button.getAttribute('data-goal-color');
            if (color) {
                button.style.backgroundColor = '';
                button.style.color = '';
                button.style.borderColor = color;
            } else {
                button.style.backgroundColor = '';
                button.style.color = '';
                button.style.borderColor = '';
            }
        }
    });
}

/**
 * Helper function to set active button by ID
 */
function setActiveButton(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.classList.add('nd-active');
        // Special handling for business goal "All" button
        if (buttonId === 'nd-filter-all-goals') {
            button.style.backgroundColor = 'var(--primary-color)';
            button.style.color = 'white';
            button.style.borderColor = 'var(--primary-color)';
        }
    }
}

/**
 * Apply both category and business goal filters
 * UPDATED: Since one is always 'all', this effectively does single filtering
 */
function applyFilters() {
    const projects = document.querySelectorAll('.project-card');
    let visibleCount = 0;
    
    projects.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        const cardBusinessGoal = card.getAttribute('data-business-goal');
        
        // Check if project matches category filter
        const categoryMatch = activeFilters.category === 'all' || 
                            cardCategory === activeFilters.category;
        
        // Check if project matches business goal filter
        const goalMatch = activeFilters.business_goal === 'all' || 
                         cardBusinessGoal === activeFilters.business_goal;
        
        // Show project only if it matches both filters (but one is always 'all' now)
        if (categoryMatch && goalMatch) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show "no projects" message if no projects are visible
    const noProjectsMessage = document.querySelector('.no-projects');
    if (noProjectsMessage) {
        if (visibleCount === 0) {
            noProjectsMessage.style.display = 'block';
            // Update the message to reflect active filters
            const filterText = getActiveFilterText();
            noProjectsMessage.innerHTML = `<p>No projects found${filterText}. Try adjusting your filters.</p>`;
        } else {
            noProjectsMessage.style.display = 'none';
        }
    }
}

/**
 * Get text description of active filters
 */
function getActiveFilterText() {
    const parts = [];
    
    if (activeFilters.category !== 'all') {
        parts.push(`in category "${activeFilters.category}"`);
    }
    
    if (activeFilters.business_goal !== 'all') {
        parts.push(`with business goal "${activeFilters.business_goal}"`);
    }
    
    if (parts.length === 0) {
        return '';
    }
    
    return ' ' + parts.join(' and ');
}

// Make the function available globally for inline onclick handlers (legacy support)
window.ndFilterProjects = function(clickedButton, filterValue, filterType = 'category') {
    filterProjects(clickedButton, filterValue, filterType);
};
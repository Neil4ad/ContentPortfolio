/**
 * Admin JavaScript file for portfolio website
 * Contains admin-specific functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Only initialize components that exist in the current page
    initProjectForm();
    initImagePreview();
    initSettingsTabs();
    initGuidelines();
    initConfirmDeletes();
});

/**
 * Initialize project form functionality
 */
function initProjectForm() {
    const isExternalCheckbox = document.getElementById('is_external');
    const externalUrlField = document.getElementById('external-url-field');
    const internalContentField = document.getElementById('internal-content-field');
    
    if (!isExternalCheckbox || !externalUrlField || !internalContentField) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    // Set initial state
    if (isExternalCheckbox.checked) {
        externalUrlField.style.display = 'block';
        internalContentField.style.display = 'none';
    } else {
        externalUrlField.style.display = 'none';
        internalContentField.style.display = 'block';
    }
    
    // Add change event listener
    isExternalCheckbox.addEventListener('change', function() {
        if (this.checked) {
            externalUrlField.style.display = 'block';
            internalContentField.style.display = 'none';
        } else {
            externalUrlField.style.display = 'none';
            internalContentField.style.display = 'block';
        }
    });
    
    // Handle results field toggling if present
    const showResultsCheckbox = document.getElementById('show_results');
    const resultsField = document.getElementById('results-field');
    
    if (showResultsCheckbox && resultsField) {
        // Set initial state
        resultsField.style.display = showResultsCheckbox.checked ? 'block' : 'none';
        
        // Add change event listener
        showResultsCheckbox.addEventListener('change', function() {
            resultsField.style.display = this.checked ? 'block' : 'none';
        });
    }
}

/**
 * Initialize image preview functionality
 */
function initImagePreview() {
    const thumbnailUrl = document.getElementById('thumbnail_url');
    const thumbnailUpload = document.getElementById('thumbnail_upload');
    const imagePreview = document.getElementById('image-preview');
    const previewContainer = document.getElementById('image-preview-container');
    
    if (!thumbnailUrl || !imagePreview || !previewContainer) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    // URL input change handler
    thumbnailUrl.addEventListener('input', function() {
        if (this.value) {
            imagePreview.src = this.value;
            previewContainer.style.display = 'block';
        } else if (!thumbnailUpload || !thumbnailUpload.files || thumbnailUpload.files.length === 0) {
            previewContainer.style.display = 'none';
        }
    });
    
    // File input change handler
    if (thumbnailUpload) {
        thumbnailUpload.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    previewContainer.style.display = 'block';
                };
                reader.readAsDataURL(this.files[0]);
            } else if (!thumbnailUrl.value) {
                previewContainer.style.display = 'none';
            }
        });
    }
}

/**
 * Initialize settings tabs functionality
 */
function initSettingsTabs() {
    const tabLinks = document.querySelectorAll('.settings-tab-link');
    const tabContents = document.querySelectorAll('.settings-tab-content');
    
    if (!tabLinks.length || !tabContents.length) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function() {
            // Remove active class from all tabs
            tabLinks.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Show corresponding tab content
            const tabId = this.dataset.tab;
            const contentElement = document.getElementById(tabId + '-tab') || 
                                   document.getElementById(tabId + '-content');
            
            if (contentElement) {
                contentElement.classList.add('active');
            }
        });
    });
}

/**
 * Initialize guidelines box functionality
 */
function initGuidelines() {
    const guidelinesHeader = document.querySelector('.guidelines-header');
    const guidelinesToggle = document.querySelector('.guidelines-toggle');
    const guidelinesContent = document.querySelector('.guidelines-content');
    
    if (!guidelinesHeader || !guidelinesToggle || !guidelinesContent) {
        // Elements don't exist on this page, skip initialization
        return;
    }
    
    // Check if guidelines state is saved in localStorage
    const guidelinesOpen = localStorage.getItem('guidelinesOpen') !== 'false';
    
    // Set initial state
    if (!guidelinesOpen) {
        guidelinesContent.style.display = 'none';
        guidelinesToggle.classList.remove('active');
    } else {
        guidelinesToggle.classList.add('active');
    }
    
    // Add click event listener
    guidelinesHeader.addEventListener('click', function() {
        guidelinesToggle.classList.toggle('active');
        
        if (guidelinesContent.style.display === 'none') {
            guidelinesContent.style.display = 'block';
            localStorage.setItem('guidelinesOpen', 'true');
        } else {
            guidelinesContent.style.display = 'none';
            localStorage.setItem('guidelinesOpen', 'false');
        }
    });
}

/**
 * Initialize confirmation dialogs for delete actions
 */
function initConfirmDeletes() {
    const deleteButtons = document.querySelectorAll('button[data-confirm], .delete');
    
    if (!deleteButtons.length) {
        // No delete buttons on this page
        return;
    }
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}
/**
 * Mobile enhancements for Portfolio site
 * Add this to your static/js directory and include in your base.html template
 */

document.addEventListener('DOMContentLoaded', function() {
    // Detect overflow in tables and add scrollable class
    function checkTableOverflow() {
        const tableWrappers = document.querySelectorAll('.data-table-wrapper');
        
        tableWrappers.forEach(wrapper => {
            const table = wrapper.querySelector('table');
            if (table && table.offsetWidth > wrapper.offsetWidth) {
                wrapper.classList.add('scrollable');
            } else {
                wrapper.classList.remove('scrollable');
            }
        });
    }
    
    // Make sure mobile nav is properly closed when clicking a link
    function setupMobileNavigation() {
        const mobileMenuButton = document.querySelector('.mobile-toggle');
        const navbarLinks = document.querySelector('.navbar-links');
        const navLinks = document.querySelectorAll('.navbar-links a');
        
        if (mobileMenuButton && navbarLinks) {
            // Close mobile menu when a link is clicked
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    if (window.innerWidth <= 768) {
                        navbarLinks.classList.remove('open');
                        mobileMenuButton.setAttribute('aria-expanded', 'false');
                    }
                });
            });
            
            // Close mobile menu when clicking outside
            document.addEventListener('click', function(event) {
                const isMenuOpen = navbarLinks.classList.contains('open');
                const isMenuButton = event.target === mobileMenuButton || mobileMenuButton.contains(event.target);
                const isInsideMenu = navbarLinks.contains(event.target);
                
                if (isMenuOpen && !isMenuButton && !isInsideMenu) {
                    navbarLinks.classList.remove('open');
                    mobileMenuButton.setAttribute('aria-expanded', 'false');
                }
            });
        }
    }
    
    // Custom handling for image gallery on project pages
    function enhanceProjectImages() {
        const projectImages = document.querySelectorAll('.project-detail-image');
        
        projectImages.forEach(img => {
            // Add tap-to-zoom functionality for mobile
            img.addEventListener('click', function() {
                this.classList.toggle('zoomed');
                
                // If zoomed, allow panning
                if (this.classList.contains('zoomed')) {
                    let isDragging = false;
                    let startX, startY, currentX, currentY;
                    
                    img.addEventListener('touchstart', function(e) {
                        isDragging = true;
                        startX = e.touches[0].clientX;
                        startY = e.touches[0].clientY;
                        currentX = startX;
                        currentY = startY;
                        e.preventDefault();
                    });
                    
                    img.addEventListener('touchmove', function(e) {
                        if (isDragging) {
                            currentX = e.touches[0].clientX;
                            currentY = e.touches[0].clientY;
                            
                            const deltaX = currentX - startX;
                            const deltaY = currentY - startY;
                            
                            const currentTransform = window.getComputedStyle(img).getPropertyValue('transform');
                            
                            img.style.transform = `scale(1.5) translate(${deltaX}px, ${deltaY}px)`;
                            e.preventDefault();
                        }
                    });
                    
                    img.addEventListener('touchend', function() {
                        isDragging = false;
                    });
                } else {
                    // Reset transform when un-zoomed
                    img.style.transform = '';
                }
            });
        });
    }
    
    // Add "back to top" button for long pages
    function addBackToTopButton() {
        const footer = document.querySelector('footer');
        
        if (footer) {
            const backToTopBtn = document.createElement('button');
            backToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
            backToTopBtn.className = 'back-to-top-btn';
            backToTopBtn.setAttribute('aria-label', 'Back to top');
            
            backToTopBtn.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
            
            document.body.appendChild(backToTopBtn);
            
            // Show button only when scrolled down
            window.addEventListener('scroll', function() {
                if (window.scrollY > 300) {
                    backToTopBtn.classList.add('visible');
                } else {
                    backToTopBtn.classList.remove('visible');
                }
            });
        }
    }
    
    // Improve form field focus for better mobile experience
    function enhanceFormFields() {
        const formControls = document.querySelectorAll('.form-control');
        
        formControls.forEach(control => {
            // Add active class to parent when field is focused
            control.addEventListener('focus', function() {
                const formGroup = this.closest('.form-group');
                if (formGroup) {
                    formGroup.classList.add('focused');
                }
            });
            
            control.addEventListener('blur', function() {
                const formGroup = this.closest('.form-group');
                if (formGroup) {
                    formGroup.classList.remove('focused');
                }
            });
        });
    }
    
    // Run all enhancements
    checkTableOverflow();
    setupMobileNavigation();
    enhanceProjectImages();
    addBackToTopButton();
    enhanceFormFields();
    
    // Re-check on resize
    window.addEventListener('resize', function() {
        checkTableOverflow();
    });
});

// Additional CSS to be injected
document.addEventListener('DOMContentLoaded', function() {
    const styleElement = document.createElement('style');
    styleElement.textContent = `
        /* Back to top button */
        .back-to-top-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background-color: var(--primary-color);
            color: white;
            border: none;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            z-index: 99;
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.3s, transform 0.3s;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .back-to-top-btn.visible {
            opacity: 0.8;
            transform: translateY(0);
        }
        
        .back-to-top-btn:hover {
            opacity: 1;
        }
        
        /* Zoomed project image */
        .project-detail-image.zoomed {
            transform: scale(1.5);
            cursor: zoom-out;
            transition: transform 0.3s ease;
        }
        
        /* Form focus enhancement */
        .form-group.focused {
            position: relative;
        }
        
        .form-group.focused::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 100%;
            height: 2px;
            background: var(--primary-color);
            transform: scaleX(1);
            transition: transform 0.3s;
        }
        
        @media (max-width: 768px) {
            /* Ensure modals are usable on mobile */
            .modal-container {
                width: 95%;
                max-height: 80vh;
            }
            
            .modal-body {
                max-height: 40vh;
            }
        }
    `;
    
    document.head.appendChild(styleElement);
});

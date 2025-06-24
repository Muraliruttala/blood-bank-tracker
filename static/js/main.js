/**
 * Blood Bank Management System - Main JavaScript File
 * Handles client-side functionality and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components when DOM is loaded
    initializeComponents();
    initializeFormValidation();
    initializeInteractiveElements();
    initializeTooltips();
    initializeAlerts();
});

/**
 * Initialize Bootstrap components and other UI elements
 */
function initializeComponents() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap modals
    var modalList = [].slice.call(document.querySelectorAll('.modal'));
    modalList.forEach(function(modalEl) {
        new bootstrap.Modal(modalEl);
    });

    // Initialize Bootstrap dropdowns
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function(dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
}

/**
 * Initialize form validation and enhancements
 */
function initializeFormValidation() {
    // Get all forms that need validation
    var forms = document.querySelectorAll('.needs-validation, form');
    
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                var firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                    showFieldError(firstInvalidField, 'Please fill out this field correctly.');
                }
            }
            
            form.classList.add('was-validated');
        }, false);
    });

    // Real-time validation for specific fields
    initializePasswordValidation();
    initializeMobileValidation();
    initializeEmailValidation();
    initializeBloodGroupValidation();
}

/**
 * Password field validation and confirmation
 */
function initializePasswordValidation() {
    var passwordField = document.getElementById('password');
    var confirmPasswordField = document.getElementById('confirm_password');
    
    if (passwordField && confirmPasswordField) {
        function validatePasswords() {
            var password = passwordField.value;
            var confirmPassword = confirmPasswordField.value;
            
            // Check password length
            if (password.length > 0 && password.length < 6) {
                showFieldError(passwordField, 'Password must be at least 6 characters long.');
                return false;
            } else {
                clearFieldError(passwordField);
            }
            
            // Check password match
            if (confirmPassword.length > 0 && password !== confirmPassword) {
                showFieldError(confirmPasswordField, 'Passwords do not match.');
                return false;
            } else {
                clearFieldError(confirmPasswordField);
            }
            
            return true;
        }
        
        passwordField.addEventListener('input', validatePasswords);
        confirmPasswordField.addEventListener('input', validatePasswords);
    }
}

/**
 * Mobile number validation
 */
function initializeMobileValidation() {
    var mobileFields = document.querySelectorAll('input[type="tel"], input[name="mobile"]');
    
    mobileFields.forEach(function(field) {
        field.addEventListener('input', function() {
            var mobile = field.value.replace(/\D/g, ''); // Remove non-digits
            
            if (mobile.length > 0 && (mobile.length < 10 || mobile.length > 15)) {
                showFieldError(field, 'Please enter a valid mobile number (10-15 digits).');
            } else {
                clearFieldError(field);
            }
        });
        
        // Format mobile number as user types
        field.addEventListener('keyup', function() {
            var value = field.value.replace(/\D/g, '');
            var formattedValue = value;
            
            if (value.length >= 10) {
                formattedValue = value.substring(0, 3) + '-' + value.substring(3, 6) + '-' + value.substring(6, 10);
                if (value.length > 10) {
                    formattedValue += value.substring(10);
                }
            }
            
            if (formattedValue !== field.value) {
                field.value = formattedValue;
            }
        });
    });
}

/**
 * Email validation
 */
function initializeEmailValidation() {
    var emailFields = document.querySelectorAll('input[type="email"]');
    
    emailFields.forEach(function(field) {
        field.addEventListener('blur', function() {
            var email = field.value;
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email.length > 0 && !emailRegex.test(email)) {
                showFieldError(field, 'Please enter a valid email address.');
            } else {
                clearFieldError(field);
            }
        });
    });
}

/**
 * Blood group validation and compatibility info
 */
function initializeBloodGroupValidation() {
    var bloodGroupFields = document.querySelectorAll('select[name="blood_group"]');
    
    bloodGroupFields.forEach(function(field) {
        field.addEventListener('change', function() {
            var selectedGroup = field.value;
            if (selectedGroup) {
                showBloodGroupCompatibility(selectedGroup);
            }
        });
    });
}

/**
 * Show blood group compatibility information
 */
function showBloodGroupCompatibility(bloodGroup) {
    var compatibilityInfo = {
        'A+': { canDonateTo: 'A+, AB+', canReceiveFrom: 'A+, A-, O+, O-' },
        'A-': { canDonateTo: 'A+, A-, AB+, AB-', canReceiveFrom: 'A-, O-' },
        'B+': { canDonateTo: 'B+, AB+', canReceiveFrom: 'B+, B-, O+, O-' },
        'B-': { canDonateTo: 'B+, B-, AB+, AB-', canReceiveFrom: 'B-, O-' },
        'AB+': { canDonateTo: 'AB+', canReceiveFrom: 'All blood groups' },
        'AB-': { canDonateTo: 'AB+, AB-', canReceiveFrom: 'A-, B-, AB-, O-' },
        'O+': { canDonateTo: 'A+, B+, AB+, O+', canReceiveFrom: 'O+, O-' },
        'O-': { canDonateTo: 'All blood groups', canReceiveFrom: 'O-' }
    };
    
    var info = compatibilityInfo[bloodGroup];
    if (info) {
        // Create or update compatibility tooltip
        var tooltipContent = `
            <strong>Can donate to:</strong> ${info.canDonateTo}<br>
            <strong>Can receive from:</strong> ${info.canReceiveFrom}
        `;
        
        // Add tooltip to blood group field
        var field = document.querySelector('select[name="blood_group"]');
        if (field) {
            field.setAttribute('data-bs-toggle', 'tooltip');
            field.setAttribute('data-bs-html', 'true');
            field.setAttribute('title', tooltipContent);
            
            // Reinitialize tooltip
            var tooltip = bootstrap.Tooltip.getInstance(field);
            if (tooltip) {
                tooltip.dispose();
            }
            new bootstrap.Tooltip(field);
        }
    }
}

/**
 * Initialize interactive elements and animations
 */
function initializeInteractiveElements() {
    // Smooth scrolling for anchor links
    var anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            var targetId = link.getAttribute('href').substring(1);
            var targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to form submissions
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            var submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && form.checkValidity()) {
                addLoadingState(submitButton);
            }
        });
    });

    // Initialize search functionality
    initializeSearch();
    
    // Initialize table sorting (if needed)
    initializeTableFeatures();
    
    // Initialize dashboard widgets
    initializeDashboardWidgets();
}

/**
 * Initialize search functionality
 */
function initializeSearch() {
    var searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(function(input) {
        var searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                // Add visual feedback for search
                if (input.value.length > 0) {
                    input.classList.add('is-valid');
                } else {
                    input.classList.remove('is-valid');
                }
            }, 300);
        });
    });
}

/**
 * Initialize table features like sorting and filtering
 */
function initializeTableFeatures() {
    var tables = document.querySelectorAll('table');
    
    tables.forEach(function(table) {
        // Add hover effects
        var rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            row.addEventListener('mouseenter', function() {
                row.style.backgroundColor = 'rgba(220, 53, 69, 0.05)';
            });
            
            row.addEventListener('mouseleave', function() {
                row.style.backgroundColor = '';
            });
        });
        
        // Add click-to-select functionality for admin tables
        if (table.closest('.admin-dashboard, #admin-dashboard')) {
            rows.forEach(function(row) {
                row.style.cursor = 'pointer';
                row.addEventListener('click', function() {
                    // Toggle row selection
                    if (row.classList.contains('table-active')) {
                        row.classList.remove('table-active');
                    } else {
                        // Remove previous selections
                        table.querySelectorAll('tbody tr.table-active').forEach(function(activeRow) {
                            activeRow.classList.remove('table-active');
                        });
                        row.classList.add('table-active');
                    }
                });
            });
        }
    });
}

/**
 * Initialize dashboard widgets and animations
 */
function initializeDashboardWidgets() {
    // Animate statistics cards on load
    var statCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-warning, .card.bg-info');
    
    statCards.forEach(function(card, index) {
        var numberElement = card.querySelector('h3');
        if (numberElement) {
            var finalNumber = parseInt(numberElement.textContent) || 0;
            
            // Animate number counting
            setTimeout(function() {
                animateNumber(numberElement, 0, finalNumber, 1000);
            }, index * 200);
        }
    });
    
    // Add refresh functionality to dashboard
    initializeDashboardRefresh();
}

/**
 * Animate number counting effect
 */
function animateNumber(element, start, end, duration) {
    var startTime = null;
    
    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        var timeElapsed = currentTime - startTime;
        var progress = Math.min(timeElapsed / duration, 1);
        
        var currentNumber = Math.floor(progress * (end - start) + start);
        element.textContent = currentNumber;
        
        if (progress < 1) {
            requestAnimationFrame(animation);
        }
    }
    
    requestAnimationFrame(animation);
}

/**
 * Initialize dashboard refresh functionality
 */
function initializeDashboardRefresh() {
    // Add refresh buttons to dashboard sections
    var dashboardSections = document.querySelectorAll('.card[id*="dashboard"], .tab-pane');
    
    dashboardSections.forEach(function(section) {
        var header = section.querySelector('.card-header');
        if (header && !header.querySelector('.refresh-btn')) {
            var refreshBtn = document.createElement('button');
            refreshBtn.className = 'btn btn-sm btn-outline-light refresh-btn ms-2';
            refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
            refreshBtn.title = 'Refresh';
            
            refreshBtn.addEventListener('click', function() {
                refreshDashboardSection(section);
            });
            
            header.appendChild(refreshBtn);
        }
    });
}

/**
 * Refresh dashboard section
 */
function refreshDashboardSection(section) {
    var refreshBtn = section.querySelector('.refresh-btn');
    if (refreshBtn) {
        var icon = refreshBtn.querySelector('i');
        icon.classList.add('fa-spin');
        
        // Simulate refresh (in a real app, this would make an AJAX call)
        setTimeout(function() {
            icon.classList.remove('fa-spin');
            showNotification('Dashboard updated successfully!', 'success');
        }, 1000);
    }
}

/**
 * Initialize tooltips for better UX
 */
function initializeTooltips() {
    // Add tooltips to buttons and icons
    var elementsWithTooltips = [
        { selector: '.btn-sm', title: 'Click to perform action' },
        { selector: '.badge', title: 'Status indicator' },
        { selector: '.fas.fa-info-circle', title: 'Information' },
        { selector: '.fas.fa-exclamation-triangle', title: 'Warning' },
        { selector: '.fas.fa-check-circle', title: 'Success' }
    ];
    
    elementsWithTooltips.forEach(function(item) {
        var elements = document.querySelectorAll(item.selector);
        elements.forEach(function(element) {
            if (!element.hasAttribute('title') && !element.hasAttribute('data-bs-original-title')) {
                element.setAttribute('data-bs-toggle', 'tooltip');
                element.setAttribute('title', item.title);
            }
        });
    });
}

/**
 * Initialize alert enhancements
 */
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.parentNode) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
    
    // Add slide-in animation to alerts
    alerts.forEach(function(alert) {
        alert.style.transform = 'translateY(-20px)';
        alert.style.opacity = '0';
        alert.style.transition = 'all 0.3s ease';
        
        setTimeout(function() {
            alert.style.transform = 'translateY(0)';
            alert.style.opacity = '1';
        }, 100);
    });
}

/**
 * Utility function to show field errors
 */
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    
    var errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    field.parentNode.appendChild(errorDiv);
}

/**
 * Utility function to clear field errors
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    
    var existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

/**
 * Utility function to add loading state to buttons
 */
function addLoadingState(button) {
    var originalText = button.innerHTML;
    var loadingText = '<span class="loading me-2"></span>Processing...';
    
    button.innerHTML = loadingText;
    button.disabled = true;
    
    // Remove loading state after form submission (handled by page redirect)
    setTimeout(function() {
        if (button.parentNode) {
            button.innerHTML = originalText;
            button.disabled = false;
        }
    }, 3000);
}

/**
 * Utility function to show notifications
 */
function showNotification(message, type = 'info') {
    var notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1060; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove notification
    setTimeout(function() {
        if (notification.parentNode) {
            var bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }
    }, 4000);
}

/**
 * Utility function for debouncing
 */
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        
        var later = function() {
            timeout = null;
            func.apply(context, args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Handle navigation state and breadcrumbs
 */
function initializeNavigation() {
    // Highlight current page in navigation
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link, .dropdown-item');
    
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Add breadcrumb functionality
    var breadcrumbContainer = document.querySelector('.breadcrumb');
    if (breadcrumbContainer) {
        updateBreadcrumbs(currentPath);
    }
}

/**
 * Update breadcrumbs based on current path
 */
function updateBreadcrumbs(path) {
    var breadcrumbs = [
        { url: '/', text: 'Home' }
    ];
    
    if (path.includes('/user/')) {
        breadcrumbs.push({ url: '/user/dashboard', text: 'Dashboard' });
        if (path.includes('/blood-request')) {
            breadcrumbs.push({ url: '/user/blood-request', text: 'Blood Request' });
        } else if (path.includes('/donation-schedule')) {
            breadcrumbs.push({ url: '/user/donation-schedule', text: 'Schedule Donation' });
        }
    } else if (path.includes('/admin/')) {
        breadcrumbs.push({ url: '/admin/dashboard', text: 'Admin Dashboard' });
        if (path.includes('/requests')) {
            breadcrumbs.push({ url: '/admin/requests', text: 'Blood Requests' });
        } else if (path.includes('/donations')) {
            breadcrumbs.push({ url: '/admin/donations', text: 'Donations' });
        } else if (path.includes('/inventory')) {
            breadcrumbs.push({ url: '/admin/inventory', text: 'Inventory' });
        }
    } else if (path.includes('/login')) {
        breadcrumbs.push({ url: '/login', text: 'Login' });
    } else if (path.includes('/register')) {
        breadcrumbs.push({ url: '/register', text: 'Register' });
    }
    
    // Update breadcrumb display (if container exists)
    var breadcrumbContainer = document.querySelector('.breadcrumb');
    if (breadcrumbContainer) {
        breadcrumbContainer.innerHTML = '';
        breadcrumbs.forEach(function(crumb, index) {
            var li = document.createElement('li');
            li.className = 'breadcrumb-item';
            
            if (index === breadcrumbs.length - 1) {
                li.className += ' active';
                li.textContent = crumb.text;
            } else {
                var a = document.createElement('a');
                a.href = crumb.url;
                a.textContent = crumb.text;
                li.appendChild(a);
            }
            
            breadcrumbContainer.appendChild(li);
        });
    }
}

// Initialize navigation when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
});

// Global error handler
window.addEventListener('error', function(event) {
    console.error('JavaScript Error:', event.error);
    showNotification('An error occurred. Please refresh the page and try again.', 'danger');
});

// Handle form submission errors
document.addEventListener('submit', function(event) {
    var form = event.target;
    if (form.tagName === 'FORM') {
        // Add global form submission handling if needed
        setTimeout(function() {
            // Re-enable form if still on the same page (error occurred)
            var submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && submitButton.disabled) {
                submitButton.disabled = false;
                submitButton.innerHTML = submitButton.innerHTML.replace('<span class="loading me-2"></span>Processing...', submitButton.dataset.originalText || 'Submit');
            }
        }, 2000);
    }
});

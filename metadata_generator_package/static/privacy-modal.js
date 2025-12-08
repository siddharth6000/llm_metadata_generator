/**
 * Privacy Modal JavaScript
 * Add this script at the end of your index.html, before the closing </body> tag
 * File: privacy-modal.js
 */

(function() {
    'use strict';

    // Privacy Modal Functions
    function checkAndShowPrivacyModal() {
        // Always show the modal on every page load
        showPrivacyModal();
    }

    function showPrivacyModal() {
        const modal = document.getElementById('privacyModal');
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
        }
    }

    function hidePrivacyModal() {
        const modal = document.getElementById('privacyModal');
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = ''; // Restore scrolling
        }
    }

    window.togglePrivacyAcceptance = function() {
        const checkbox = document.getElementById('privacyAcceptTerms');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;
            updatePrivacyAcceptButton();
        }
    }

    window.updatePrivacyAcceptButton = function() {
        const checkbox = document.getElementById('privacyAcceptTerms');
        const acceptBtn = document.getElementById('privacyAcceptBtn');
        if (checkbox && acceptBtn) {
            acceptBtn.disabled = !checkbox.checked;
        }
    }

    window.acceptPrivacyTerms = function() {
        hidePrivacyModal();
        // Continue with normal application flow
        console.log('Privacy terms accepted');
    }

    window.declinePrivacyTerms = function() {
        alert('You must accept the terms to use this application. The application uses external LLM services that process your data.');
        // Redirect away from the application
        window.location.href = 'about:blank';
    }

    // Show modal immediately on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkAndShowPrivacyModal);
    } else {
        checkAndShowPrivacyModal();
    }
})();

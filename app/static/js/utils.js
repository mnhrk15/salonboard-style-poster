/**
 * Utility functions for SALON BOARD application
 */

/**
 * Show flash message
 * @param {string} message - Message text
 * @param {string} type - Message type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds (0 = no auto-hide)
 */
function showFlash(message, type = 'info', duration = 5000) {
    const container = document.getElementById('flash-messages');
    if (!container) return;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    container.appendChild(alert);

    if (duration > 0) {
        setTimeout(() => {
            alert.remove();
        }, duration);
    }
}

/**
 * Format date to Japanese format
 * @param {string|Date} date - Date string or Date object
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    return `${year}/${month}/${day} ${hours}:${minutes}`;
}

/**
 * Get status badge HTML
 * @param {string} status - Task status
 * @returns {string} Badge HTML
 */
function getStatusBadge(status) {
    const statusMap = {
        'PENDING': { class: 'badge-pending', text: '待機中' },
        'PROCESSING': { class: 'badge-processing', text: '実行中' },
        'SUCCESS': { class: 'badge-success', text: '完了' },
        'FAILURE': { class: 'badge-failure', text: 'エラー' },
        'INTERRUPTED': { class: 'badge-interrupted', text: '中断' }
    };

    const badge = statusMap[status] || { class: 'badge-pending', text: status };
    return `<span class="badge ${badge.class}">${badge.text}</span>`;
}

/**
 * Show loading spinner on button
 * @param {HTMLButtonElement} button - Button element
 * @param {boolean} loading - Loading state
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner"></span> 処理中...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

/**
 * Confirm dialog
 * @param {string} message - Confirmation message
 * @returns {boolean} User confirmation
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} Valid email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Format file size
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

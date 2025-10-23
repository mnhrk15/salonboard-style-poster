/**
 * Authentication utilities
 */

/**
 * Check if user is authenticated
 * @returns {boolean} True if authenticated
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Logout user
 */
async function logout() {
    if (confirm('サインアウトしますか？')) {
        await API.auth.logout();
    }
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/';
    }
}

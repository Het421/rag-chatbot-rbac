// ─────────────────────────────────
// SESSION MANAGEMENT
// Stores and retrieves user session
// from browser's localStorage
// ─────────────────────────────────

const Session = {

    /**
     * Save user data after successful login.
     * localStorage stores strings only — objects need JSON.stringify
     */
    login(token, role, fullName, employeeId) {
        localStorage.setItem('token', token);
        localStorage.setItem('role', role);
        localStorage.setItem('fullName', fullName);
        localStorage.setItem('employeeId', employeeId);
    },

    /**
     * Clear everything on logout.
     */
    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('role');
        localStorage.removeItem('fullName');
        localStorage.removeItem('employeeId');
        window.location.href = '/';
    },

    /**
     * Check if user is currently logged in.
     * Returns true if token exists in localStorage.
     */
    isLoggedIn() {
        return !!localStorage.getItem('token');
    },

    /**
     * Get the stored JWT token.
     */
    getToken() {
        return localStorage.getItem('token');
    },

    /**
     * Get the user's role — 'admin' or 'employee'
     */
    getRole() {
        return localStorage.getItem('role');
    },

    /**
     * Get the user's full name.
     */
    getFullName() {
        return localStorage.getItem('fullName');
    },

    /**
     * Get the employee ID.
     */
    getEmployeeId() {
        return localStorage.getItem('employeeId');
    },

    /**
     * Build the Authorization header for API calls.
     * Every protected API call needs this header.
     */
    getAuthHeaders() {
        return {
            'Authorization': `Bearer ${this.getToken()}`,
            'Content-Type': 'application/json'
        };
    },

    /**
     * Redirect to login if not authenticated.
     * Call this at the top of every protected page.
     */
    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = '/';
        }
    },

    /**
     * Redirect to chat if already logged in.
     * Call this on the login page so logged-in
     * users don't see the login form again.
     */
    requireGuest() {
        if (this.isLoggedIn()) {
            window.location.href = '/chat';
        }
    }
};
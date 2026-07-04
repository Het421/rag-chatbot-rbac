// ─────────────────────────────────
// API CLIENT
// All fetch calls to FastAPI backend
// Equivalent of api_client.py
// ─────────────────────────────────

const API_BASE = '';  // Empty because FastAPI serves both API and frontend
                      // so we use relative URLs: /auth/login not http://localhost:8000/auth/login

const Api = {

    // ─────────────────────────────────
    // CORE FETCH HELPER
    // ─────────────────────────────────

    /**
     * Base fetch function used by all other methods.
     * Handles errors consistently so we don't repeat
     * error handling in every single API call.
     */
    async request(method, url, body = null, isFormData = false) {
        const headers = Session.getAuthHeaders();

        // For file uploads we don't set Content-Type
        // — browser sets it automatically with boundary
        if (isFormData) {
            delete headers['Content-Type'];
        }

        const options = {
            method,
            headers,
        };

        if (body) {
            options.body = isFormData ? body : JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE}${url}`, options);

        // If unauthorized — token expired, redirect to login
        if (response.status === 401) {
            Session.logout();
            return;
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Something went wrong');
        }

        return data;
    },

    // ─────────────────────────────────
    // AUTH
    // ─────────────────────────────────

    async login(employeeId, password) {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                employee_id: employeeId,
                password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Invalid credentials');
        }

        return data;
    },

    // ─────────────────────────────────
    // CONVERSATIONS
    // ─────────────────────────────────

    async createConversation(title = 'New Conversation') {
        return this.request('POST', '/chat/conversations', { title });
    },

    async listConversations() {
        return this.request('GET', '/chat/conversations');
    },

    async renameConversation(conversationId, title) {
        return this.request(
            'PATCH',
            `/chat/conversations/${conversationId}`,
            { title }
        );
    },

    async deleteConversation(conversationId) {
        return this.request(
            'DELETE',
            `/chat/conversations/${conversationId}`
        );
    },

    async getMessages(conversationId) {
        return this.request(
            'GET',
            `/chat/conversations/${conversationId}/messages`
        );
    },

    // ─────────────────────────────────
    // RAG CHAT
    // ─────────────────────────────────

    async sendMessage(conversationId, message) {
        return this.request('POST', '/rag/chat', {
            conversation_id: conversationId,
            message: message
        });
    },

    // ─────────────────────────────────
    // DOCUMENTS
    // ─────────────────────────────────

    async uploadDocument(file, accessLevel) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('access_level', accessLevel);

        return this.request('POST', '/documents/upload', formData, true);
    },

    async listDocuments() {
        return this.request('GET', '/documents/list');
    }
};
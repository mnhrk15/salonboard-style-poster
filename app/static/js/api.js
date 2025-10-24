/**
 * API Client for SALON BOARD application
 */

const API_BASE_URL = '/api/v1';

/**
 * Get authorization header
 * @returns {Object} Headers with authorization
 */
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

/**
 * Handle API errors
 * @param {Response} response - Fetch response
 * @returns {Promise} Response JSON or throws error
 */
async function handleResponse(response) {
    if (!response.ok) {
        if (response.status === 401) {
            // Unauthorized - redirect to login
            localStorage.removeItem('access_token');
            window.location.href = '/';
            throw new Error('Unauthorized');
        }

        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP Error ${response.status}`);
    }

    return response.json();
}

/**
 * API Client
 */
const API = {
    // Authentication
    auth: {
        async login(email, password) {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const response = await fetch(`${API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });

            const data = await handleResponse(response);
            if (data.access_token) {
                localStorage.setItem('access_token', data.access_token);
            }
            return data;
        },

        async logout() {
            try {
                await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: getAuthHeaders()
                });
            } finally {
                localStorage.removeItem('access_token');
                window.location.href = '/';
            }
        }
    },

    // Tasks
    tasks: {
        async list(skip = 0, limit = 50) {
            const response = await fetch(
                `${API_BASE_URL}/tasks/?skip=${skip}&limit=${limit}`,
                {
                    headers: getAuthHeaders()
                }
            );
            return handleResponse(response);
        },

        async get(taskId) {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        },

        async create(sbSettingId, dataFile, images) {
            const formData = new FormData();
            formData.append('sb_setting_id', sbSettingId);
            formData.append('data_file', dataFile);

            for (const image of images) {
                formData.append('images', image);
            }

            const token = localStorage.getItem('access_token');
            const response = await fetch(`${API_BASE_URL}/tasks/style-post`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            return handleResponse(response);
        },

        async interrupt(taskId) {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/interrupt`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        },

        async resume(taskId) {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/resume`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        },

        async downloadLogs(taskId) {
            const token = localStorage.getItem('access_token');
            window.location.href = `${API_BASE_URL}/tasks/${taskId}/logs?token=${token}`;
        },

        async downloadScreenshot(taskId) {
            const token = localStorage.getItem('access_token');
            window.location.href = `${API_BASE_URL}/tasks/${taskId}/screenshots?token=${token}`;
        },

        async getItems(taskId) {
            const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/items`, {
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        }
    },

    // SALON BOARD Settings
    settings: {
        async list() {
            const response = await fetch(`${API_BASE_URL}/sb-settings/`, {
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        },

        async get(settingId) {
            const response = await fetch(`${API_BASE_URL}/sb-settings/${settingId}`, {
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        },

        async create(data) {
            const response = await fetch(`${API_BASE_URL}/sb-settings/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
            return handleResponse(response);
        },

        async update(settingId, data) {
            const response = await fetch(`${API_BASE_URL}/sb-settings/${settingId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
            return handleResponse(response);
        },

        async delete(settingId) {
            const response = await fetch(`${API_BASE_URL}/sb-settings/${settingId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        }
    },

    // Users (Admin only)
    users: {
        async list(skip = 0, limit = 100) {
            const response = await fetch(
                `${API_BASE_URL}/users/?skip=${skip}&limit=${limit}`,
                {
                    headers: getAuthHeaders()
                }
            );
            return handleResponse(response);
        },

        async create(data) {
            const response = await fetch(`${API_BASE_URL}/users/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
            return handleResponse(response);
        },

        async update(userId, data) {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify(data)
            });
            return handleResponse(response);
        },

        async delete(userId) {
            const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            return handleResponse(response);
        }
    }
};

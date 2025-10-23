/**
 * WebSocket utilities for real-time task updates
 */

class TaskWebSocket {
    constructor(taskId, onUpdate) {
        this.taskId = taskId;
        this.onUpdate = onUpdate;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
    }

    /**
     * Connect to WebSocket
     */
    connect() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            console.error('No access token found');
            return;
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        const wsUrl = `${protocol}//${host}/ws/tasks/${this.taskId}?token=${token}`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log(`WebSocket connected for task ${this.taskId}`);
                this.reconnectAttempts = 0;
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.onUpdate(data);
                } catch (error) {
                    console.error('Failed to parse WebSocket message:', error);
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            this.ws.onclose = (event) => {
                console.log(`WebSocket closed for task ${this.taskId}`, event.code, event.reason);

                // Attempt to reconnect if not a normal closure
                if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
                    setTimeout(() => this.connect(), this.reconnectDelay);
                }
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }

    /**
     * Disconnect WebSocket
     */
    disconnect() {
        if (this.ws) {
            this.ws.close(1000, 'Normal closure');
            this.ws = null;
        }
    }

    /**
     * Check if WebSocket is connected
     */
    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

/**
 * Manager for multiple task WebSocket connections
 */
class TaskWebSocketManager {
    constructor() {
        this.connections = new Map();
    }

    /**
     * Subscribe to task updates
     * @param {string} taskId - Task ID
     * @param {function} onUpdate - Callback function for updates
     */
    subscribe(taskId, onUpdate) {
        if (this.connections.has(taskId)) {
            console.warn(`Already subscribed to task ${taskId}`);
            return;
        }

        const taskWs = new TaskWebSocket(taskId, onUpdate);
        taskWs.connect();
        this.connections.set(taskId, taskWs);
    }

    /**
     * Unsubscribe from task updates
     * @param {string} taskId - Task ID
     */
    unsubscribe(taskId) {
        const taskWs = this.connections.get(taskId);
        if (taskWs) {
            taskWs.disconnect();
            this.connections.delete(taskId);
        }
    }

    /**
     * Unsubscribe from all tasks
     */
    unsubscribeAll() {
        for (const [taskId, taskWs] of this.connections) {
            taskWs.disconnect();
        }
        this.connections.clear();
    }

    /**
     * Get connection status for a task
     * @param {string} taskId - Task ID
     * @returns {boolean} True if connected
     */
    isConnected(taskId) {
        const taskWs = this.connections.get(taskId);
        return taskWs ? taskWs.isConnected() : false;
    }
}

// Global WebSocket manager instance
const wsManager = new TaskWebSocketManager();

// Clean up connections when page is unloaded
window.addEventListener('beforeunload', () => {
    wsManager.unsubscribeAll();
});

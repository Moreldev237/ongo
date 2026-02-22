// API Base URL
const API_BASE = 'http://127.0.0.1:8000/api';

// API Service
const API = {
    // Orders
    async getOrders(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = queryString ? `${API_BASE}/commande/orders/?${queryString}` : `${API_BASE}/commande/orders/`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch orders');
            return await response.json();
        } catch (error) {
            console.error('Error fetching orders:', error);
            return { results: [] };
        }
    },

    async createOrder(data) {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/commande/orders/create_order/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response || !response.ok) {
                const error = await response?.json?.();
                throw new Error(error?.detail || 'Failed to create order');
            }
            return await response.json();
        } catch (error) {
            console.error('Error creating order:', error);
            throw error;
        }
    },

    async getOrderDetails(id) {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/commande/orders/${id}/`);
            if (!response || !response.ok) throw new Error('Failed to fetch order details');
            return await response.json();
        } catch (error) {
            console.error('Error fetching order details:', error);
            return null;
        }
    },

    async updateOrderStatus(id, status, notes = '') {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/commande/orders/${id}/update_status/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status, notes })
            });
            if (!response || !response.ok) throw new Error('Failed to update order status');
            return await response.json();
        } catch (error) {
            console.error('Error updating order status:', error);
            throw error;
        }
    },

    async rateOrder(id, clientRating, clientComment = '') {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/commande/orders/${id}/rate/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ client_rating: clientRating, client_comment: clientComment })
            });
            if (!response || !response.ok) throw new Error('Failed to rate order');
            return await response.json();
        } catch (error) {
            console.error('Error rating order:', error);
            throw error;
        }
    },

    async getOrderStats() {
        try {
            const response = await fetch(`${API_BASE}/commande/orders/stats/`);
            if (!response.ok) throw new Error('Failed to fetch order stats');
            return await response.json();
        } catch (error) {
            console.error('Error fetching order stats:', error);
            return {
                total_orders: 0,
                active_orders: 0,
                completed_orders: 0,
                total_movecoins: 0
            };
        }
    },

    // Promotions
    async getPromotions(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const url = queryString ? `${API_BASE}/promotions/?${queryString}` : `${API_BASE}/promotions/`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch promotions');
            return await response.json();
        } catch (error) {
            console.error('Error fetching promotions:', error);
            return { results: [] };
        }
    },

    async getActivePromotions() {
        try {
            const response = await fetch(`${API_BASE}/promotions/active/`);
            if (!response.ok) throw new Error('Failed to fetch active promotions');
            return await response.json();
        } catch (error) {
            console.error('Error fetching active promotions:', error);
            return { results: [] };
        }
    },

    async applyPromotion(code) {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/promotions/apply/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code })
            });
            if (!response || !response.ok) {
                const error = await response?.json?.();
                throw new Error(error?.detail || 'Failed to apply promotion');
            }
            return await response.json();
        } catch (error) {
            console.error('Error applying promotion:', error);
            throw error;
        }
    },

    async getPromotionDetails(id) {
        try {
            const response = await fetch(`${API_BASE}/promotions/${id}/`);
            if (!response.ok) throw new Error('Failed to fetch promotion details');
            return await response.json();
        } catch (error) {
            console.error('Error fetching promotion details:', error);
            return null;
        }
    },

    // Locations
    async createLocation(data) {
        try {
            const response = await AUTH.protectedFetch(`${API_BASE}/commande/locations/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error('Failed to create location');
            return await response.json();
        } catch (error) {
            console.error('Error creating location:', error);
            throw error;
        }
    },

    // Helper methods
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    formatPrice(price) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'XOF'
        }).format(price);
    },

    getStatusBadgeColor(status) {
        const colors = {
            pending: 'bg-yellow-100 text-yellow-800',
            accepted: 'bg-blue-100 text-blue-800',
            in_progress: 'bg-purple-100 text-purple-800',
            completed: 'bg-green-100 text-green-800',
            cancelled: 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    },

    getStatusLabel(status) {
        const labels = {
            pending: 'En Attente',
            accepted: 'Acceptée',
            in_progress: 'En Cours',
            completed: 'Complétée',
            cancelled: 'Annulée'
        };
        return labels[status] || status;
    },

    getVehicleLabel(type) {
        const labels = {
            scooter: 'Scooter',
            bike: 'Vélo',
            car: 'Voiture',
            truck: 'Camion'
        };
        return labels[type] || type;
    }
};

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-6 py-4 rounded-lg shadow-lg text-white z-50 ${
        type === 'success' ? 'bg-green-600' : type === 'error' ? 'bg-red-600' : 'bg-blue-600'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Show error
function showError(message) {
    showNotification(message, 'error');
}

// Show success
function showSuccess(message) {
    showNotification(message, 'success');
}

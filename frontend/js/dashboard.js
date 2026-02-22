// Dashboard functionality
// Check authentication
requireAuth();

document.addEventListener('DOMContentLoaded', async () => {
    await loadDashboard();
});

async function loadDashboard() {
    try {
        // Load stats
        const stats = await API.getOrderStats();
        updateStats(stats);

        // Load recent orders
        const orders = await API.getOrders({ limit: 5 });
        displayRecentOrders(orders.results || []);

        // Load active promotions
        const promos = await API.getActivePromotions();
        displayPromotions(promos.results || []);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Erreur lors du chargement du tableau de bord');
    }
}

function updateStats(stats) {
    document.getElementById('stat-total-orders').textContent = stats.total_orders || 0;
    document.getElementById('stat-active-orders').textContent = stats.active_orders || 0;
    document.getElementById('stat-completed-orders').textContent = stats.completed_orders || 0;
    document.getElementById('stat-movecoins').textContent = Math.round(stats.total_movecoins || 0);
}

function displayRecentOrders(orders) {
    const container = document.getElementById('recent-orders-list');
    
    if (orders.length === 0) {
        container.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500">Aucune commande pour le moment</td></tr>';
        return;
    }

    container.innerHTML = orders.map(order => `
        <tr class="border-b border-gray-200 hover:bg-gray-50">
            <td class="px-6 py-4 text-sm font-medium text-gray-900">#${order.id}</td>
            <td class="px-6 py-4 text-sm text-gray-700">${order.pickup_location?.address || 'N/A'}</td>
            <td class="px-6 py-4 text-sm text-gray-700">${order.destination_location?.address || 'N/A'}</td>
            <td class="px-6 py-4 text-sm">
                <span class="px-3 py-1 rounded-full text-xs font-medium ${API.getStatusBadgeColor(order.status)}">
                    ${API.getStatusLabel(order.status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">${API.formatPrice(order.total_price)}</td>
            <td class="px-6 py-4 text-sm text-gray-700">${API.formatDate(order.created_at)}</td>
            <td class="px-6 py-4 text-sm">
                <a href="orders.html" class="text-blue-600 hover:text-blue-800 font-medium">Voir</a>
            </td>
        </tr>
    `).join('');
}

function displayPromotions(promos) {
    const container = document.getElementById('promotions-grid');
    
    if (promos.length === 0) {
        container.innerHTML = '<div class="col-span-3 bg-white rounded-lg shadow p-8 text-center"><p class="text-gray-500">Aucune promotion active pour le moment</p></div>';
        return;
    }

    container.innerHTML = promos.slice(0, 3).map(promo => `
        <div class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 p-4 text-white">
                <h3 class="text-lg font-bold">${promo.code}</h3>
                <p class="text-sm opacity-90">${promo.description}</p>
            </div>
            <div class="p-4">
                <div class="mb-4">
                    <p class="text-gray-600 text-sm">Réduction</p>
                    <p class="text-2xl font-bold text-blue-600">
                        ${promo.promotion_type === 'percentage' ? promo.value + '%' : API.formatPrice(promo.value)}
                    </p>
                </div>
                <div class="text-xs text-gray-500 space-y-1 mb-4">
                    <p>Expire: ${API.formatDate(promo.end_date)}</p>
                    <p>Utilisations: ${promo.max_uses_per_user || 'Illimitée'}</p>
                </div>
                <button class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium text-sm">
                    Utiliser le code
                </button>
            </div>
        </div>
    `).join('');
}

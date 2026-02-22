// Orders page functionality
// Check authentication
requireAuth();

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadOrders();
});

function setupEventListeners() {
    document.getElementById('filter-btn').addEventListener('click', loadOrders);
}

async function loadOrders() {
    const status = document.getElementById('filter-status')?.value || '';
    const vehicle = document.getElementById('filter-vehicle')?.value || '';
    const sort = document.getElementById('filter-sort')?.value || '';

    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (vehicle) params.append('vehicle_type', vehicle);
    if (sort) params.append('ordering', sort === 'recent' ? '-created_at' : sort === 'oldest' ? 'created_at' : sort);

    try {
        const orders = await API.getOrders(Object.fromEntries(params));
        displayOrders(orders.results || []);
    } catch (error) {
        console.error('Error loading orders:', error);
        showError('Erreur lors du chargement des commandes');
    }
}

function displayOrders(orders) {
    const container = document.getElementById('orders-container');

    if (orders.length === 0) {
        container.innerHTML = '<div class="bg-white rounded-lg shadow p-8 text-center"><p class="text-gray-500 text-lg">Aucune commande trouvée</p><a href="create-order.html" class="text-blue-600 hover:text-blue-800 font-medium">Créer une commande</a></div>';
        return;
    }

    container.innerHTML = orders.map(order => `
        <div class="bg-white rounded-lg shadow p-6 hover:shadow-lg transition">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                <!-- Order Info -->
                <div>
                    <p class="text-gray-600 text-sm font-medium">Commande</p>
                    <p class="text-2xl font-bold text-gray-900">#${order.id}</p>
                    <p class="text-gray-500 text-sm mt-1">${API.formatDate(order.created_at)}</p>
                </div>

                <!-- Route Info -->
                <div>
                    <p class="text-gray-600 text-sm font-medium">Itinéraire</p>
                    <div class="mt-2">
                        <p class="text-gray-900 font-medium text-sm">${order.pickup_location?.address || 'N/A'}</p>
                        <p class="text-gray-500 text-xs mt-1">↓</p>
                        <p class="text-gray-900 font-medium text-sm">${order.destination_location?.address || 'N/A'}</p>
                    </div>
                </div>

                <!-- Details -->
                <div>
                    <p class="text-gray-600 text-sm font-medium">Détails</p>
                    <div class="mt-2 space-y-1 text-sm">
                        <p>Type: <span class="font-medium">${API.getVehicleLabel(order.vehicle_type)}</span></p>
                        <p>
                            Statut: 
                            <span class="px-2 py-1 rounded text-xs font-medium ${API.getStatusBadgeColor(order.status)}">
                                ${API.getStatusLabel(order.status)}
                            </span>
                        </p>
                        <p>Paiement: <span class="font-medium">${order.payment_method === 'card' ? 'Carte' : order.payment_method === 'wallet' ? 'MOVECoin' : 'Espèces'}</span></p>
                    </div>
                </div>

                <!-- Price & Action -->
                <div class="flex flex-col justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Montant</p>
                        <p class="text-2xl font-bold text-blue-600">${API.formatPrice(order.total_price)}</p>
                        ${order.promotion_discount > 0 ? `<p class="text-green-600 text-sm">-${API.formatPrice(order.promotion_discount)}</p>` : ''}
                    </div>
                    <button onclick="viewOrderDetails(${order.id})" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 font-medium">
                        Détails
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function viewOrderDetails(orderId) {
    try {
        const order = await API.getOrderDetails(orderId);
        if (!order) {
            showError('Impossible de charger les détails');
            return;
        }
        displayOrderModal(order);
    } catch (error) {
        console.error('Error viewing order details:', error);
        showError('Erreur lors du chargement des détails');
    }
}

function displayOrderModal(order) {
    const modal = document.getElementById('order-modal');
    const content = document.getElementById('modal-content');

    const statusHistory = order.status_history || [];

    content.innerHTML = `
        <div class="space-y-6">
            <!-- Header Info -->
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-gray-600 text-sm">Commande #</p>
                    <p class="text-2xl font-bold text-gray-900">${order.id}</p>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Statut</p>
                    <div class="mt-1">
                        <span class="px-3 py-1 rounded-full text-sm font-medium ${API.getStatusBadgeColor(order.status)}">
                            ${API.getStatusLabel(order.status)}
                        </span>
                    </div>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Créée le</p>
                    <p class="text-gray-900 font-medium">${API.formatDate(order.created_at)}</p>
                </div>
                <div>
                    <p class="text-gray-600 text-sm">Véhicule</p>
                    <p class="text-gray-900 font-medium">${API.getVehicleLabel(order.vehicle_type)}</p>
                </div>
            </div>

            <div class="border-t pt-4">
                <h3 class="font-bold text-gray-900 mb-3">Itinéraire</h3>
                <div class="bg-gray-50 p-4 rounded-lg space-y-3">
                    <div>
                        <p class="text-gray-600 text-sm">Départ</p>
                        <p class="text-gray-900 font-medium">${order.pickup_location?.address || 'N/A'}</p>
                        ${order.pickup_location?.landmark ? `<p class="text-gray-600 text-sm">Repère: ${order.pickup_location.landmark}</p>` : ''}
                    </div>
                    <div class="text-center text-gray-400">↓</div>
                    <div>
                        <p class="text-gray-600 text-sm">Destination</p>
                        <p class="text-gray-900 font-medium">${order.destination_location?.address || 'N/A'}</p>
                        ${order.destination_location?.landmark ? `<p class="text-gray-600 text-sm">Repère: ${order.destination_location.landmark}</p>` : ''}
                    </div>
                </div>
            </div>

            <div class="border-t pt-4">
                <h3 class="font-bold text-gray-900 mb-3">Prix</h3>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between">
                        <span>Prix de base:</span>
                        <span class="font-medium">${API.formatPrice(order.base_price)}</span>
                    </div>
                    ${order.promotion_discount > 0 ? `
                    <div class="flex justify-between text-green-600">
                        <span>Réduction:</span>
                        <span class="font-medium">-${API.formatPrice(order.promotion_discount)}</span>
                    </div>
                    ` : ''}
                    <div class="flex justify-between pt-2 border-t font-bold text-base">
                        <span>Total:</span>
                        <span class="text-blue-600">${API.formatPrice(order.total_price)}</span>
                    </div>
                </div>
            </div>

            ${statusHistory.length > 0 ? `
            <div class="border-t pt-4">
                <h3 class="font-bold text-gray-900 mb-3">Historique</h3>
                <div class="space-y-3 max-h-48 overflow-y-auto">
                    ${statusHistory.map(history => `
                        <div class="flex gap-3">
                            <div class="flex-shrink-0">
                                <div class="flex-shrink-0 h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-xs font-bold">
                                    ${history.status === 'pending' ? '📋' : history.status === 'accepted' ? '✓' : history.status === 'in_progress' ? '🚗' : history.status === 'completed' ? '✓✓' : '✕'}
                                </div>
                            </div>
                            <div class="flex-1">
                                <p class="text-sm font-medium text-gray-900">${API.getStatusLabel(history.status)}</p>
                                <p class="text-xs text-gray-600">${API.formatDate(history.created_at)}</p>
                                ${history.notes ? `<p class="text-xs text-gray-700 mt-1">${history.notes}</p>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    modal.classList.remove('hidden');
}

function closeOrderModal() {
    document.getElementById('order-modal').classList.add('hidden');
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('order-modal');
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeOrderModal();
    });
});

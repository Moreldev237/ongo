// Promotions page functionality
// Check authentication
requireAuth();

document.addEventListener('DOMContentLoaded', async () => {
    setupEventListeners();
    await loadPromotions();
    await loadMyPromotions();
});

function setupEventListeners() {
    document.getElementById('filter-btn').addEventListener('click', loadPromotions);
}

async function loadPromotions() {
    const type = document.getElementById('filter-type')?.value || '';
    const status = document.getElementById('filter-status')?.value || 'active';
    const category = document.getElementById('filter-category')?.value || '';

    const params = new URLSearchParams();
    if (type) params.append('promotion_type', type);
    if (status === 'active') params.append('status', 'active');

    try {
        const promos = await API.getPromotions(Object.fromEntries(params));
        displayPromotions(promos.results || []);
    } catch (error) {
        console.error('Error loading promotions:', error);
        showError('Erreur lors du chargement des promotions');
    }
}

function displayPromotions(promotions) {
    const container = document.getElementById('promotions-grid');

    if (promotions.length === 0) {
        container.innerHTML = '<div class="col-span-3 bg-white rounded-lg shadow p-8 text-center"><p class="text-gray-500 text-lg">Aucune promotion trouvée</p></div>';
        return;
    }

    container.innerHTML = promotions.map(promo => {
        const icon = getPromoIcon(promo.promotion_type);
        const isSoon = isEndingSoon(promo.end_date);
        const value = promo.promotion_type === 'percentage' ? `${promo.value}%` : API.formatPrice(promo.value);
        
        return `
            <div class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition transform hover:scale-105">
                <div class="bg-gradient-to-r ${getPromoGradient(promo.promotion_type)} p-4 text-white">
                    <div class="flex items-start justify-between mb-3">
                        <div>
                            <h3 class="text-lg font-bold">${promo.code}</h3>
                            <p class="text-sm opacity-90 line-clamp-2">${promo.description}</p>
                        </div>
                        <span class="text-3xl">${icon}</span>
                    </div>
                </div>
                <div class="p-4">
                    <div class="mb-4 p-3 bg-blue-50 rounded-lg">
                        <p class="text-gray-600 text-xs font-medium">Réduction</p>
                        <p class="text-3xl font-bold text-blue-600">${value}</p>
                    </div>
                    
                    <div class="space-y-2 mb-4 text-xs text-gray-600">
                        <div class="flex justify-between">
                            <span>Type:</span>
                            <span class="font-medium">${getPromoTypeLabel(promo.promotion_type)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Status:</span>
                            <span class="font-medium ${promo.status === 'active' ? 'text-green-600' : 'text-gray-600'}">
                                ${promo.status === 'active' ? 'Actif' : 'Inactif'}
                            </span>
                        </div>
                        <div class="flex justify-between">
                            <span>Expire:</span>
                            <span class="font-medium ${isSoon ? 'text-red-600' : ''}">${API.formatDate(promo.end_date).split(',')[0]}</span>
                        </div>
                        <div class="flex justify-between">
                            <span>Utilisations:</span>
                            <span class="font-medium">${promo.max_uses_per_user || '∞'}</span>
                        </div>
                    </div>

                    ${isSoon ? `<div class="bg-red-50 p-2 rounded mb-3 text-xs text-red-700 font-medium text-center">⏰ Expire bientôt</div>` : ''}

                    <button onclick="copyPromoCode('${promo.code}')" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 font-medium text-sm transition">
                        Copier le code
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function loadMyPromotions() {
    try {
        const promos = await API.getPromotions({ status: 'used' });
        displayMyPromotions(promos.results || []);
        
        // Calculate stats
        const allPromos = await API.getPromotions();
        calculateStats(allPromos.results || []);
    } catch (error) {
        console.error('Error loading my promotions:', error);
    }
}

function displayMyPromotions(promotions) {
    const container = document.getElementById('my-promos-list');

    if (promotions.length === 0) {
        container.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-500">Vous n\'avez pas utilisé de code promo pour le moment</td></tr>';
        return;
    }

    container.innerHTML = promotions.map(promo => `
        <tr class="border-b border-gray-200 hover:bg-gray-50">
            <td class="px-6 py-4 text-sm font-medium text-gray-900">${promo.code}</td>
            <td class="px-6 py-4 text-sm text-gray-700">${getPromoTypeLabel(promo.promotion_type)}</td>
            <td class="px-6 py-4 text-sm font-medium text-blue-600">
                ${promo.promotion_type === 'percentage' ? `${promo.value}%` : API.formatPrice(promo.value)}
            </td>
            <td class="px-6 py-4 text-sm text-gray-700">${API.formatDate(promo.end_date).split(',')[0]}</td>
            <td class="px-6 py-4 text-sm text-gray-700">0 / ${promo.max_uses_per_user || '∞'}</td>
            <td class="px-6 py-4 text-sm">
                <span class="px-2 py-1 rounded-full text-xs font-medium ${promo.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                    ${promo.status === 'active' ? 'Valide' : 'Expiré'}
                </span>
            </td>
        </tr>
    `).join('');
}

function calculateStats(promotions) {
    let totalSavings = 0;
    let totalMovecoins = 0;
    let usedCodes = 0;

    promotions.forEach(promo => {
        if (promo.usage_records && promo.usage_records.length > 0) {
            usedCodes += promo.usage_records.length;
            if (promo.promotion_type === 'percentage') {
                totalSavings += promo.value * promo.usage_records.length;
            } else {
                totalSavings += promo.value * promo.usage_records.length;
            }
            if (promo.promotion_type === 'cashback') {
                totalMovecoins += promo.value * promo.usage_records.length;
            }
        }
    });

    document.getElementById('stat-total-savings').textContent = API.formatPrice(totalSavings);
    document.getElementById('stat-total-movecoins').textContent = Math.round(totalMovecoins);
    document.getElementById('stat-used-codes').textContent = usedCodes;
}

function copyPromoCode(code) {
    navigator.clipboard.writeText(code);
    showSuccess(`Code "${code}" copié!`);
}

function getPromoTypeLabel(type) {
    const labels = {
        'percentage': 'Pourcentage',
        'fixed': 'Montant Fixe',
        'cashback': 'Cashback',
        'free_delivery': 'Livraison Gratuite'
    };
    return labels[type] || type;
}

function getPromoIcon(type) {
    const icons = {
        'percentage': '📉',
        'fixed': '💵',
        'cashback': '💰',
        'free_delivery': '🚚'
    };
    return icons[type] || '🎁';
}

function getPromoGradient(type) {
    const gradients = {
        'percentage': 'from-blue-600 to-blue-800',
        'fixed': 'from-green-600 to-green-800',
        'cashback': 'from-purple-600 to-purple-800',
        'free_delivery': 'from-orange-600 to-orange-800'
    };
    return gradients[type] || 'from-gray-600 to-gray-800';
}

function isEndingSoon(endDate) {
    const end = new Date(endDate);
    const now = new Date();
    const daysLeft = Math.floor((end - now) / (1000 * 60 * 60 * 24));
    return daysLeft <= 3;
}

function closePromoModal() {
    document.getElementById('promo-modal').classList.add('hidden');
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('promo-modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closePromoModal();
        });
    }
});

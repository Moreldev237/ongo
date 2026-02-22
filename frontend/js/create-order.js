// Create Order functionality
// Check authentication
requireAuth();

let currentPickupLocation = null;
let currentDestinationLocation = null;
let appliedPromotion = null;

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    setupFormValidation();
});

function setupEventListeners() {
    const form = document.getElementById('create-order-form');
    
    form.addEventListener('submit', handleSubmit);
    form.addEventListener('change', updatePriceSummary);
    form.addEventListener('input', updatePriceSummary);

    document.getElementById('apply-promo-btn').addEventListener('click', applyPromoCode);
    document.getElementById('vehicle-type').addEventListener('change', updateVehicleSummary);
}

function setupFormValidation() {
    const inputs = document.querySelectorAll('input[type="text"], select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', validateInput);
    });
}

function validateInput(e) {
    const input = e.target;
    if (input.hasAttribute('required') && !input.value.trim()) {
        input.classList.add('border-red-500');
    } else {
        input.classList.remove('border-red-500');
    }
}

function updateVehicleSummary() {
    const vehicleType = document.getElementById('vehicle-type').value;
    const vehicleLabel = {
        scooter: '🛵 Scooter',
        bike: '🚲 Vélo',
        car: '🚗 Voiture',
        truck: '🚚 Camion'
    };
    document.getElementById('summary-vehicle').textContent = vehicleLabel[vehicleType] || 'Non sélectionné';
}

function updatePriceSummary() {
    const vehicleType = document.getElementById('vehicle-type').value;
    
    if (!vehicleType) {
        document.getElementById('base-price').textContent = '--';
        document.getElementById('total-price').textContent = '--';
        document.getElementById('summary-price').textContent = '--';
        return;
    }

    // Base prices (example)
    const basePrices = {
        scooter: 2000,
        bike: 1500,
        car: 4000,
        truck: 8000
    };

    let basePrice = basePrices[vehicleType] || 0;
    const weight = parseFloat(document.getElementById('estimated-weight').value) || 0;
    
    // Add weight surcharge
    if (weight > 0) {
        basePrice += weight * 500; // 500 FCFA per kg
    }

    let totalPrice = basePrice;
    let discount = 0;

    // Apply promotion if any
    if (appliedPromotion) {
        if (appliedPromotion.promotion_type === 'percentage') {
            discount = (basePrice * appliedPromotion.value) / 100;
        } else {
            discount = appliedPromotion.value;
        }
        totalPrice = basePrice - discount;
    }

    // Calculate MOVECoin reward (10% of total)
    const movecoins = Math.round(totalPrice * 0.1);

    document.getElementById('base-price').textContent = API.formatPrice(basePrice);
    document.getElementById('total-price').textContent = API.formatPrice(totalPrice);
    document.getElementById('summary-price').textContent = API.formatPrice(totalPrice);

    if (discount > 0) {
        document.getElementById('discount-row').style.display = 'flex';
        document.getElementById('discount-amount').textContent = `-${API.formatPrice(discount)}`;
    } else {
        document.getElementById('discount-row').style.display = 'none';
    }

    document.getElementById('movecoin-reward').textContent = `Vous gagnerez ${movecoins} MOVECoins`;
}

async function applyPromoCode(e) {
    e.preventDefault();
    const code = document.getElementById('promo-code').value.trim();

    if (!code) {
        showError('Veuillez entrer un code promo');
        return;
    }

    try {
        const response = await API.applyPromotion(code);
        appliedPromotion = response;
        
        document.getElementById('promo-info').innerHTML = `
            <div class="bg-green-50 p-3 rounded-lg border border-green-200">
                <p class="text-green-800 text-sm font-medium">✓ Code appliqué: ${response.code}</p>
                <p class="text-green-700 text-xs">${response.description}</p>
            </div>
        `;
        
        updatePriceSummary();
        showSuccess('Code promo appliqué!');
    } catch (error) {
        appliedPromotion = null;
        document.getElementById('promo-info').innerHTML = `
            <div class="bg-red-50 p-3 rounded-lg border border-red-200">
                <p class="text-red-800 text-sm">✕ Code invalide ou expiré</p>
            </div>
        `;
        showError(error.message);
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    
    // Validate required fields
    const requiredFields = ['pickup-address', 'destination-address', 'vehicle-type', 'payment-method'];
    for (const field of requiredFields) {
        const input = document.getElementById(field);
        if (!input.value.trim()) {
            showError(`${input.previousElementSibling.textContent} est requise`);
            return;
        }
    }

    try {
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Création en cours...';

        // Create pickup location
        const pickupData = {
            address: document.getElementById('pickup-address').value,
            latitude: parseFloat(document.getElementById('pickup-lat').value) || 0,
            longitude: parseFloat(document.getElementById('pickup-lng').value) || 0,
            landmark: document.getElementById('pickup-landmark').value || ''
        };
        currentPickupLocation = await API.createLocation(pickupData);

        // Create destination location
        const destData = {
            address: document.getElementById('destination-address').value,
            latitude: parseFloat(document.getElementById('destination-lat').value) || 0,
            longitude: parseFloat(document.getElementById('destination-lng').value) || 0,
            landmark: document.getElementById('destination-landmark').value || ''
        };
        currentDestinationLocation = await API.createLocation(destData);

        // Calculate price
        const vehicleType = document.getElementById('vehicle-type').value;
        const basePrices = {
            scooter: 2000,
            bike: 1500,
            car: 4000,
            truck: 8000
        };
        let basePrice = basePrices[vehicleType] || 0;
        const weight = parseFloat(document.getElementById('estimated-weight').value) || 0;
        if (weight > 0) {
            basePrice += weight * 500;
        }

        let totalPrice = basePrice;
        let promotionDiscount = 0;
        if (appliedPromotion) {
            if (appliedPromotion.promotion_type === 'percentage') {
                promotionDiscount = (basePrice * appliedPromotion.value) / 100;
            } else {
                promotionDiscount = appliedPromotion.value;
            }
            totalPrice = basePrice - promotionDiscount;
        }

        // Create order
        const orderData = {
            pickup_location: currentPickupLocation.id,
            destination_location: currentDestinationLocation.id,
            vehicle_type: vehicleType,
            description: document.getElementById('description').value || 'Pas de description',
            estimated_weight: weight || 0,
            base_price: basePrice,
            promotion_discount: promotionDiscount,
            total_price: totalPrice,
            payment_method: document.getElementById('payment-method').value,
            promotion_code: appliedPromotion ? appliedPromotion.code : null
        };

        const result = await API.createOrder(orderData);
        
        showSuccess(`Commande créée avec succès! N° ${result.id}`);
        
        setTimeout(() => {
            window.location.href = 'orders.html';
        }, 2000);

    } catch (error) {
        console.error('Error creating order:', error);
        showError(error.message || 'Erreur lors de la création de la commande');
        
        const submitBtn = document.getElementById('submit-btn');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Créer la Commande';
    }
}

// Initialize price summary on load
document.addEventListener('DOMContentLoaded', () => {
    updatePriceSummary();
});

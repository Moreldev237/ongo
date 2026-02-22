// Authentication Service
const AUTH = {
    API_URL: 'http://127.0.0.1:8000/api/utilisateurs',

    // Check if user is logged in
    isLoggedIn() {
        return !!this.getAccessToken();
    },

    // Get access token from localStorage
    getAccessToken() {
        return localStorage.getItem('access_token');
    },

    // Get refresh token from localStorage
    getRefreshToken() {
        return localStorage.getItem('refresh_token');
    },

    // Store tokens in localStorage
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('access_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    },

    // Clear tokens
    clearTokens() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },

    // Get current user from storage
    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    // Store user info
    setCurrentUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    // Register new user
    async register(credentials) {
        try {
            const errorEl = document.getElementById('errorMessage');
            const successEl = document.getElementById('successMessage');

            const response = await fetch(`${this.API_URL}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(credentials)
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMsg = Object.values(data).flat().join(', ');
                if (errorEl) {
                    errorEl.textContent = errorMsg;
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            // Store tokens and user info
            this.setTokens(data.access, data.refresh);
            this.setCurrentUser(data.user);

            if (successEl) {
                successEl.textContent = 'Inscription réussie! Redirection...';
                successEl.classList.remove('hidden');
            }

            // Redirect to dashboard after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);

        } catch (error) {
            console.error('Registration error:', error);
            const errorEl = document.getElementById('errorMessage');
            if (errorEl) {
                errorEl.textContent = 'Erreur lors de l\'inscription';
                errorEl.classList.remove('hidden');
            }
        }
    },

    // Login user
    async login(credentials) {
        try {
            const errorEl = document.getElementById('errorMessage');
            const successEl = document.getElementById('successMessage');

            const response = await fetch(`${this.API_URL}/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: credentials.email,
                    password: credentials.password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                const errorMsg = data.detail || 'Identifiants invalides';
                if (errorEl) {
                    errorEl.textContent = errorMsg;
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            // Store tokens
            this.setTokens(data.access, data.refresh);

            // Fetch user info
            await this.fetchCurrentUser();

            if (successEl) {
                successEl.textContent = 'Connexion réussie! Redirection...';
                successEl.classList.remove('hidden');
            }

            // Redirect to dashboard after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);

        } catch (error) {
            console.error('Login error:', error);
            const errorEl = document.getElementById('errorMessage');
            if (errorEl) {
                errorEl.textContent = 'Erreur lors de la connexion';
                errorEl.classList.remove('hidden');
            }
        }
    },

    // Fetch current user info
    async fetchCurrentUser() {
        try {
            const token = this.getAccessToken();
            if (!token) return null;

            const response = await fetch(`${this.API_URL}/me/`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const user = await response.json();
                this.setCurrentUser(user);
                return user;
            }
        } catch (error) {
            console.error('Error fetching current user:', error);
        }
        return null;
    },

    // Logout user
    async logout() {
        try {
            const token = this.getAccessToken();
            if (token) {
                await fetch(`${this.API_URL}/logout/`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        }

        // Clear local storage
        this.clearTokens();
        window.location.href = '/login.html';
    },

    // Request password reset
    async requestPasswordReset(email) {
        try {
            const errorEl = document.getElementById('errorMessage');
            const successEl = document.getElementById('successMessage');

            const response = await fetch(`${this.API_URL}/password-reset/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (!response.ok) {
                if (errorEl) {
                    errorEl.textContent = data.error || 'Erreur lors de la demande';
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            if (successEl) {
                successEl.textContent = 'Email de réinitialisation envoyé! Vérifiez votre boîte mail.';
                successEl.classList.remove('hidden');
            }

            document.getElementById('requestResetForm').reset();

        } catch (error) {
            console.error('Password reset error:', error);
            const errorEl = document.getElementById('errorMessage');
            if (errorEl) {
                errorEl.textContent = 'Erreur lors de l\'envoi du mail';
                errorEl.classList.remove('hidden');
            }
        }
    },

    // Confirm password reset with token
    async confirmPasswordReset(uid, token, password) {
        try {
            const errorEl = document.getElementById('errorMessage');
            const successEl = document.getElementById('successMessage');

            const response = await fetch(`${this.API_URL}/password-reset-confirm/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    uid,
                    token,
                    password,
                    password_confirm: password
                })
            });

            const data = await response.json();

            if (!response.ok) {
                if (errorEl) {
                    errorEl.textContent = data.error || 'Erreur lors de la réinitialisation';
                    errorEl.classList.remove('hidden');
                }
                return;
            }

            if (successEl) {
                successEl.textContent = 'Mot de passe réinitialisé avec succès! Redirection...';
                successEl.classList.remove('hidden');
            }

            // Redirect to login after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 1500);

        } catch (error) {
            console.error('Confirm reset error:', error);
            const errorEl = document.getElementById('errorMessage');
            if (errorEl) {
                errorEl.textContent = 'Erreur lors de la réinitialisation';
                errorEl.classList.remove('hidden');
            }
        }
    },

    // Refresh token
    async refreshAccessToken() {
        try {
            const refreshToken = this.getRefreshToken();
            if (!refreshToken) return false;

            const response = await fetch(`${this.API_URL}/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('access_token', data.access);
                return true;
            } else {
                this.clearTokens();
                window.location.href = '/login.html';
                return false;
            }

        } catch (error) {
            console.error('Token refresh error:', error);
            this.clearTokens();
            return false;
        }
    },

    // Protected fetch with auto token refresh
    async protectedFetch(url, options = {}) {
        let token = this.getAccessToken();

        if (!token) {
            window.location.href = '/login.html';
            return null;
        }

        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        let response = await fetch(url, { ...options, headers });

        // If unauthorized, try to refresh token
        if (response.status === 401) {
            const refreshed = await this.refreshAccessToken();
            if (refreshed) {
                token = this.getAccessToken();
                headers['Authorization'] = `Bearer ${token}`;
                response = await fetch(url, { ...options, headers });
            }
        }

        return response;
    },

    // Check authentication on page load
    async checkAuth() {
        if (this.isLoggedIn()) {
            const user = await this.fetchCurrentUser();
            return user;
        }
        return null;
    }
};

// Redirect unauthenticated users from protected pages
function requireAuth() {
    if (!AUTH.isLoggedIn()) {
        window.location.href = '/login.html';
    }
}

// Add logout button to navbar if logged in
document.addEventListener('DOMContentLoaded', () => {
    if (AUTH.isLoggedIn()) {
        const user = AUTH.getCurrentUser();
        
        // Add user info and logout button to page if navbar exists
        const nav = document.querySelector('nav');
        if (nav) {
            const ul = nav.querySelector('ul');
            if (ul) {
                // Add user info
                const userLi = document.createElement('li');
                userLi.className = 'text-gray-700 font-medium';
                userLi.innerHTML = `<span>${user?.email || 'Utilisateur'}</span>`;
                
                // Add logout button
                const logoutLi = document.createElement('li');
                logoutLi.innerHTML = `
                    <button onclick="AUTH.logout()" class="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 font-medium">
                        Déconnexion
                    </button>
                `;
                
                ul.appendChild(userLi);
                ul.appendChild(logoutLi);
            }
        }
    }
});

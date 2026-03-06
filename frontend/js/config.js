// API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:8001/api/v1',
    timeout: 30000
};

// Auth token (localStorage)
const AUTH_STORAGE_KEY = 'promo_engine_token';
const AUTH_REFRESH_KEY = 'promo_engine_refresh';

function getAccessToken() {
    return localStorage.getItem(AUTH_STORAGE_KEY);
}
function setAccessToken(token) {
    if (token) localStorage.setItem(AUTH_STORAGE_KEY, token);
    else localStorage.removeItem(AUTH_STORAGE_KEY);
}
function getRefreshToken() {
    return localStorage.getItem(AUTH_REFRESH_KEY);
}
function setRefreshToken(token) {
    if (token) localStorage.setItem(AUTH_REFRESH_KEY, token);
    else localStorage.removeItem(AUTH_REFRESH_KEY);
}
function clearAuth() {
    setAccessToken(null);
    setRefreshToken(null);
}

// Application State
const AppState = {
    currentUser: null,
    currentOperator: null,
    currentPage: 'dashboard'
};


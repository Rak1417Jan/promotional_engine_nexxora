// API Client
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        const token = typeof getAccessToken === 'function' ? getAccessToken() : null;
        if (token) headers['Authorization'] = `Bearer ${token}`;

        const config = { headers, ...options };
        if (options.body) config.body = JSON.stringify(options.body);

        try {
            const response = await fetch(url, config);
            let data;
            try { data = await response.json(); } catch (_) { data = { detail: 'Request failed' }; }
            if (response.status === 401 && typeof onAuthRequired === 'function') {
                onAuthRequired();
            }
            if (!response.ok) {
                throw new Error(Array.isArray(data.detail) ? data.detail.map(d => d.msg || d).join(', ') : (data.detail || 'Request failed'));
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    async requestFormData(endpoint, formData, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {};
        const token = typeof getAccessToken === 'function' ? getAccessToken() : null;
        if (token) headers['Authorization'] = `Bearer ${token}`;
        const config = { method: options.method || 'POST', headers, body: formData };
        const response = await fetch(url, config);
        const data = response.headers.get('content-type')?.includes('json') ? await response.json() : { detail: 'Request failed' };
        if (response.status === 401 && typeof onAuthRequired === 'function') onAuthRequired();
        if (!response.ok) throw new Error(data.detail || 'Request failed');
        return data;
    }

    // Operators
    async getOperators() {
        return this.request('/operators/');
    }

    async getOperator(id) {
        return this.request(`/operators/${id}`);
    }

    async createOperator(data) {
        return this.request('/operators/', { method: 'POST', body: data });
    }

    // Players
    async getPlayers(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/players/${queryString ? '?' + queryString : ''}`);
    }

    async getPlayer(id) {
        return this.request(`/players/${id}`);
    }

    async createPlayer(data) {
        return this.request('/players/', { method: 'POST', body: data });
    }

    async seedSamplePlayers(count = 1000) {
        return this.request(`/players/seed-sample?count=${count}`, { method: 'POST' });
    }

    // Segments
    async getSegments() {
        return this.request('/segments/');
    }
    async createSegment(data) {
        return this.request('/segments/', { method: 'POST', body: data });
    }
    async aiGenerateSegments() {
        return this.request('/segments/ai-generate', { method: 'POST' });
    }

    // Events
    async createEvent(data) {
        return this.request('/events/', { method: 'POST', body: data });
    }

    async getPlayerEvents(playerId) {
        return this.request(`/events/player/${playerId}`);
    }

    // Campaigns
    async getCampaigns(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        return this.request(`/campaigns/?${queryString}`);
    }

    async getCampaign(id) {
        return this.request(`/campaigns/${id}`);
    }

    async createCampaign(data) {
        return this.request('/campaigns/', { method: 'POST', body: data });
    }

    async createAICampaign(objective) {
        return this.request(`/campaigns/ai-generate?objective=${encodeURIComponent(objective)}`, {
            method: 'POST'
        });
    }

    async executeCampaign(id) {
        return this.request(`/campaigns/${id}/execute`, { method: 'POST' });
    }

    async getCampaignAnalytics(id) {
        return this.request(`/campaigns/${id}/analytics`);
    }

    async getCampaignDetails(id) {
        return this.request(`/campaigns/${id}/details`);
    }

    // Auth
    async login(email, password) {
        return this.request('/auth/login', { method: 'POST', body: { email, password } });
    }
    async registerOperator(data) {
        return this.request('/auth/register-operator', { method: 'POST', body: data });
    }
    async getMe() {
        return this.request('/auth/me');
    }
    async logout() {
        return this.request('/auth/logout', { method: 'POST' });
    }

    // Imports
    async createImport(file, entityType = 'player', fileFormat = null) {
        const form = new FormData();
        form.append('file', file);
        if (fileFormat) form.append('file_format', fileFormat);
        return this.requestFormData(`/imports/?entity_type=${encodeURIComponent(entityType)}`, form);
    }
    async getImport(jobId) {
        return this.request(`/imports/${jobId}`);
    }
    async listImports(params = {}) {
        const q = new URLSearchParams(params).toString();
        return this.request(`/imports/${q ? '?' + q : ''}`);
    }

    // Exports
    async createExport(entityType, exportFormat = 'csv', filters = {}) {
        return this.request('/exports/', { method: 'POST', body: { entity_type: entityType, export_format: exportFormat, filters } });
    }
    async getExport(jobId) {
        return this.request(`/exports/${jobId}`);
    }
    async listExports(params = {}) {
        const q = new URLSearchParams(params).toString();
        return this.request(`/exports/${q ? '?' + q : ''}`);
    }
    async downloadExport(jobId, filename) {
        const token = typeof getAccessToken === 'function' ? getAccessToken() : null;
        const res = await fetch(`${this.baseURL}/exports/${jobId}/download`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        if (!res.ok) throw new Error('Download failed');
        const blob = await res.blob();
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = filename || `export_${jobId}.csv`;
        a.click();
        URL.revokeObjectURL(a.href);
    }

    // Insights
    async getPlayerInsights(playerId) {
        return this.request(`/insights/players/${encodeURIComponent(playerId)}`);
    }
    async getCampaignRecommendations() {
        return this.request('/insights/campaigns/recommendations');
    }
    async getBusinessInsights() {
        return this.request('/insights/business');
    }
}

// Initialize API client
const api = new APIClient(API_CONFIG.baseURL);


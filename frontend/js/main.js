// Main Application Logic - Phase 1
function showAuthScreen() {
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('app-container').classList.add('hidden');
}
function showApp() {
    document.getElementById('auth-screen').classList.add('hidden');
    document.getElementById('app-container').classList.remove('hidden');
}
function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg || '';
    el.classList.toggle('hidden', !msg);
}

function onAuthRequired() {
    clearAuth();
    showAuthScreen();
}

document.addEventListener('DOMContentLoaded', () => {
    const authScreen = document.getElementById('auth-screen');
    const appContainer = document.getElementById('app-container');

    // Auth tabs
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const which = tab.getAttribute('data-tab');
            document.getElementById('login-form').classList.toggle('hidden', which !== 'login');
            document.getElementById('register-form').classList.toggle('hidden', which !== 'register');
            showAuthError('');
        });
    });

    // Login form
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        showAuthError('');
        const form = e.target;
        const email = form.querySelector('[name="email"]').value;
        const password = form.querySelector('[name="password"]').value;
        try {
            const res = await api.login(email, password);
            setAccessToken(res.access_token);
            setRefreshToken(res.refresh_token);
            AppState.currentUser = await api.getMe();
            showApp();
            loadPageData('dashboard');
        } catch (err) {
            showAuthError(err.message || 'Login failed');
        }
    });

    // Register form
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        showAuthError('');
        const form = e.target;
        const data = {
            name: form.querySelector('[name="name"]').value,
            domain_url: form.querySelector('[name="domain_url"]').value,
            contact_email: form.querySelector('[name="contact_email"]').value,
            password: form.querySelector('[name="password"]').value
        };
        try {
            await api.registerOperator(data);
            showAuthError('');
            form.querySelector('[name="name"]').value = '';
            form.querySelector('[name="domain_url"]').value = '';
            form.querySelector('[name="contact_email"]').value = '';
            form.querySelector('[name="password"]').value = '';
            document.querySelector('.auth-tab[data-tab="login"]').click();
            alert('Account created. Please sign in.');
        } catch (err) {
            showAuthError(err.message || 'Registration failed');
        }
    });

    // Logout
    document.getElementById('logout-btn').addEventListener('click', (e) => {
        e.preventDefault();
        clearAuth();
        AppState.currentUser = null;
        showAuthScreen();
    });

    // Navigation (skip logout)
    const navItems = document.querySelectorAll('.nav-item[data-page]');
    const pages = document.querySelectorAll('.page');
    const pageTitle = document.getElementById('page-title');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            pages.forEach(p => p.classList.remove('active'));
            const pageEl = document.getElementById(`${page}-page`);
            if (pageEl) {
                pageEl.classList.add('active');
                pageTitle.textContent = item.textContent.trim();
                loadPageData(page);
            }
        });
    });

    // Modal
    const modal = document.getElementById('campaign-modal');
    const createButtons = document.querySelectorAll('#create-campaign-btn, #create-campaign-btn-2');
    const closeBtn = modal.querySelector('.close');
    createButtons.forEach(btn => btn.addEventListener('click', async () => {
        modal.classList.add('active');
        const segSelect = document.getElementById('campaign-target-segment');
        if (segSelect && segSelect.options.length <= 1) {
            try {
                const segments = await api.getSegments();
                segSelect.innerHTML = '<option value="">No segment (target all)</option>' +
                    (segments || []).map(s => `<option value="${s.id}">${s.name} (${s.player_count ?? 0} players)</option>`).join('');
            } catch (_) { segSelect.innerHTML = '<option value="">No segment (target all)</option>'; }
        }
    }));
    closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    window.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });

    const campaignDetailsModal = document.getElementById('campaign-details-modal');
    const campaignDetailsClose = document.querySelector('.campaign-details-close');
    if (campaignDetailsClose) campaignDetailsClose.addEventListener('click', () => campaignDetailsModal.classList.remove('active'));
    if (campaignDetailsModal) campaignDetailsModal.addEventListener('click', (e) => { if (e.target === campaignDetailsModal) campaignDetailsModal.classList.remove('active'); });

    // Campaign form (operator_id from token)
    document.getElementById('campaign-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const aiObjective = formData.get('ai_objective');
        try {
            if (aiObjective) {
                await api.createAICampaign(aiObjective);
                alert('AI Campaign created successfully!');
            } else {
                const segId = formData.get('target_segment_id');
                await api.createCampaign({
                    name: formData.get('name'),
                    campaign_type: formData.get('campaign_type'),
                    description: formData.get('description'),
                    trigger_type: 'manual',
                    target_segment_id: segId ? parseInt(segId, 10) : null
                });
                alert('Campaign created successfully!');
            }
            modal.classList.remove('active');
            e.target.reset();
            loadPageData('campaigns');
        } catch (err) {
            alert('Error: ' + err.message);
        }
    });

    // Import form
    document.getElementById('import-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const file = form.querySelector('[name="file"]').files[0];
        const entityType = form.querySelector('[name="entity_type"]').value;
        if (!file) { alert('Select a file'); return; }
        try {
            await api.createImport(file, entityType);
            alert('Import started.');
            form.querySelector('[name="file"]').value = '';
            loadPageData('import-export');
        } catch (err) {
            alert('Import failed: ' + err.message);
        }
    });

    // Export form
    document.getElementById('export-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const entityType = form.querySelector('[name="entity_type"]').value;
        const exportFormat = form.querySelector('[name="export_format"]').value;
        try {
            await api.createExport(entityType, exportFormat, {});
            alert('Export job created.');
            loadPageData('import-export');
        } catch (err) {
            alert('Export failed: ' + err.message);
        }
    });

    // Seed sample players
    document.getElementById('seed-sample-players-btn').addEventListener('click', async () => {
        if (!confirm('Create 1000 sample players for your operator? This may take a few seconds.')) return;
        const btn = document.getElementById('seed-sample-players-btn');
        btn.disabled = true;
        btn.textContent = 'Importing...';
        try {
            const res = await api.seedSamplePlayers(1000);
            alert(res.message || `Created ${res.count} sample players.`);
            loadPageData('players');
            loadPageData('dashboard');
        } catch (err) {
            alert('Error: ' + err.message);
        }
        btn.disabled = false;
        btn.textContent = 'Import 1000 sample players';
    });

    // Add player modal
    const playerModal = document.getElementById('player-modal');
    document.getElementById('add-player-btn').addEventListener('click', () => {
        playerModal.classList.add('active');
    });
    playerModal.querySelector('.player-modal-close').addEventListener('click', () => {
        playerModal.classList.remove('active');
    });
    window.addEventListener('click', (e) => {
        if (e.target === playerModal) playerModal.classList.remove('active');
    });

    // Player form submit
    document.getElementById('player-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const data = {
            email: form.querySelector('[name="email"]').value.trim() || null,
            first_name: form.querySelector('[name="first_name"]').value.trim() || null,
            last_name: form.querySelector('[name="last_name"]').value.trim() || null,
            phone: form.querySelector('[name="phone"]').value.trim() || null,
            external_player_id: form.querySelector('[name="external_player_id"]').value.trim() || null
        };
        if (!data.email && !data.external_player_id) {
            alert('Please provide at least Email or External ID.');
            return;
        }
        try {
            const player = await api.createPlayer(data);
            const idDisplay = player.id != null ? String(player.id) : (player.external_player_id || '');
            document.getElementById('insight-player-id').value = idDisplay;
            form.reset();
            loadPageData('players');
            loadPageData('dashboard');
            playerModal.classList.remove('active');
            if (idDisplay) {
                const goInsights = confirm('Player created (ID: ' + idDisplay + '). Open Insights and load their insights now?');
                if (goInsights) {
                    document.querySelector('.nav-item[data-page="insights"]').click();
                    document.getElementById('load-player-insights-btn').click();
                } else {
                    alert('Player created. Use Insights and enter ID ' + idDisplay + ' to view their insights.');
                }
            } else {
                alert('Player created.');
            }
        } catch (err) {
            alert('Error: ' + err.message);
        }
    });

    // Player insights button
    let playerInsightChart = null;
    document.getElementById('load-player-insights-btn').addEventListener('click', async () => {
        const playerId = document.getElementById('insight-player-id').value.trim();
        const resultEl = document.getElementById('player-insights-result');
        const chartWrap = document.getElementById('player-insights-chart-wrap');
        if (!playerId) { resultEl.innerHTML = '<p class="text-muted">Enter a player ID.</p>'; chartWrap.style.display = 'none'; return; }
        resultEl.innerHTML = '<p>Loading...</p>';
        chartWrap.style.display = 'none';
        if (playerInsightChart) { playerInsightChart.destroy(); playerInsightChart = null; }
        try {
            const data = await api.getPlayerInsights(playerId);
            const churn = data.churn_risk || {};
            const ltv = (data.ltv_prediction || {}).value || 0;
            const recs = data.recommendations || [];
            chartWrap.style.display = 'block';
            const ctx = document.getElementById('insight-chart-player').getContext('2d');
            playerInsightChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Churn risk 7d', 'Churn risk 30d'],
                    datasets: [{
                        label: 'Risk %',
                        data: [(churn['7_day'] || 0) * 100, (churn['30_day'] || 0) * 100],
                        backgroundColor: ['rgba(239, 68, 68, 0.6)', 'rgba(245, 158, 11, 0.6)']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false, scales: { y: { max: 100, beginAtZero: true } } }
            });
            resultEl.innerHTML = `
                <p><strong>Predicted LTV:</strong> $${Number(ltv).toFixed(2)}</p>
                ${recs.length ? '<p><strong>Recommendations:</strong> ' + recs.map(r => r.action).join('; ') + '</p>' : ''}
            `;
        } catch (err) {
            resultEl.innerHTML = '<p class="auth-error">' + err.message + '</p>';
        }
    });

    // Initial: check auth
    if (!getAccessToken()) {
        showAuthScreen();
        return;
    }
    api.getMe()
        .then(user => {
            AppState.currentUser = user;
            showApp();
            loadPageData('dashboard');
        })
        .catch(() => {
            clearAuth();
            showAuthScreen();
        });
});

function loadPageData(page) {
    switch (page) {
        case 'dashboard': loadDashboard(); break;
        case 'campaigns': loadCampaigns(); break;
        case 'players': loadPlayers(); break;
        case 'segments': loadSegments(); break;
        case 'import-export': loadImportExport(); break;
        case 'insights': loadInsights(); break;
    }
}

async function loadDashboard() {
    try {
        const playerRes = await api.getPlayers({ limit: 1, offset: 0 });
        const total = (playerRes && playerRes.total) != null ? playerRes.total : (playerRes.items ? playerRes.items.length : 0);
        document.getElementById('stat-total-players').textContent = total;
        const campaigns = await api.getCampaigns({ status: 'active' });
        document.getElementById('stat-active-campaigns').textContent = Array.isArray(campaigns) ? campaigns.length : 0;
        document.getElementById('stat-open-rate').textContent = '—';
        document.getElementById('stat-conversion-rate').textContent = '—';
    } catch (err) {
        console.error('Dashboard load error:', err);
    }
}

async function loadCampaigns() {
    const listEl = document.getElementById('campaigns-list');
    listEl.innerHTML = '<p>Loading campaigns...</p>';
    try {
        const campaigns = await api.getCampaigns();
        if (campaigns.length === 0) {
            listEl.innerHTML = '<p>No campaigns found. Create your first campaign!</p>';
            return;
        }
        listEl.innerHTML = campaigns.map(c => `
            <div class="campaign-card" data-campaign-id="${c.id}">
                <div class="campaign-card-info">
                    <h3>${c.name}</h3>
                    <p>${c.description || 'No description'}</p>
                    <small>Type: ${c.campaign_type} | Status: ${c.status}${c.target_segment_id ? ' | Has segment' : ''}</small>
                </div>
                <div class="campaign-actions">
                    <span class="campaign-status ${c.status}">${c.status}</span>
                    ${c.status !== 'completed' ? `<button class="btn btn-primary btn-sm execute-campaign" data-id="${c.id}">Execute</button>` : ''}
                    <button class="btn btn-secondary btn-sm view-campaign-details" data-id="${c.id}">View details</button>
                </div>
            </div>
        `).join('');
        listEl.querySelectorAll('.execute-campaign').forEach(btn => {
            btn.addEventListener('click', async () => {
                try {
                    const res = await api.executeCampaign(btn.getAttribute('data-id'));
                    alert('Execution started. ' + (res.executions_created || 0) + ' executions created.');
                    loadCampaigns();
                } catch (e) { alert('Error: ' + e.message); }
            });
        });
        listEl.querySelectorAll('.view-campaign-details').forEach(btn => {
            btn.addEventListener('click', async () => {
                const modal = document.getElementById('campaign-details-modal');
                const title = document.getElementById('campaign-details-title');
                const body = document.getElementById('campaign-details-body');
                modal.classList.add('active');
                body.innerHTML = '<p class="text-muted">Loading...</p>';
                try {
                    const d = await api.getCampaignDetails(btn.getAttribute('data-id'));
                    const camp = d.campaign || {};
                    const seg = d.segment || {};
                    const players = d.target_players || [];
                    const an = d.analytics || {};
                    const metrics = an.metrics || {};
                    const rates = an.rates || {};
                    title.textContent = camp.name || 'Campaign details';
                    body.innerHTML = `
                        <div class="campaign-details-section">
                            <h3>Target segment</h3>
                            ${seg.name ? `
                                <p><strong>${seg.name}</strong> ${seg.description || ''}</p>
                                <p class="text-muted">Criteria: ${JSON.stringify(seg.criteria || {})} &middot; ${d.target_count || 0} players targeted</p>
                            ` : '<p class="text-muted">No segment assigned (targets all players).</p>'}
                        </div>
                        <div class="campaign-details-section">
                            <h3>Targeted players (${d.target_count || 0})</h3>
                            ${players.length ? `
                                <div class="table-wrap"><table class="data-table">
                                    <thead><tr><th>ID</th><th>Email</th><th>Name</th><th>Status</th><th>LTV</th></tr></thead>
                                    <tbody>
                                        ${players.slice(0, 50).map(p => { const name = [p.first_name, p.last_name].filter(Boolean).join(' ') || '—'; return '<tr><td>' + p.id + '</td><td>' + (p.email || '—') + '</td><td>' + name + '</td><td>' + (p.status || '—') + '</td><td>$' + (p.lifetime_value || 0).toFixed(2) + '</td></tr>'; }).join('')}
                                    </tbody>
                                </table></div>
                                ${(d.target_count || 0) > 50 ? '<p class="text-muted">Showing first 50 of ' + d.target_count + ' players.</p>' : ''}
                            ` : '<p class="text-muted">No players in this segment yet.</p>'}
                        </div>
                        <div class="campaign-details-section">
                            <h3>Performance</h3>
                            <div class="metrics-grid">
                                <div class="metric-box"><span class="metric-value">${metrics.sent ?? 0}</span><span class="metric-label">Sent</span></div>
                                <div class="metric-box"><span class="metric-value">${metrics.delivered ?? 0}</span><span class="metric-label">Delivered</span></div>
                                <div class="metric-box"><span class="metric-value">${metrics.opened ?? 0}</span><span class="metric-label">Opened</span></div>
                                <div class="metric-box"><span class="metric-value">${(rates.delivery_rate != null ? (rates.delivery_rate * 100).toFixed(1) : 0)}%</span><span class="metric-label">Delivery rate</span></div>
                                <div class="metric-box"><span class="metric-value">${(rates.open_rate != null ? (rates.open_rate * 100).toFixed(1) : 0)}%</span><span class="metric-label">Open rate</span></div>
                            </div>
                        </div>
                    `;
                } catch (e) {
                    body.innerHTML = '<p class="auth-error">' + e.message + '</p>';
                }
            });
        });
    } catch (err) {
        listEl.innerHTML = '<p>Error: ' + err.message + '</p>';
    }
}

const PLAYERS_PAGE_SIZE = 50;
let playersPage = 0;
let playersTotal = 0;

async function loadPlayers(offset) {
    if (offset !== undefined) playersPage = offset;
    const tableBody = document.getElementById('players-table-body');
    const infoEl = document.getElementById('players-pagination-info');
    const pageNumEl = document.getElementById('players-page-num');
    tableBody.innerHTML = '<tr><td colspan="6">Loading players...</td></tr>';
    try {
        const res = await api.getPlayers({ limit: PLAYERS_PAGE_SIZE, offset: playersPage * PLAYERS_PAGE_SIZE });
        const items = res.items || [];
        const total = res.total != null ? res.total : items.length;
        playersTotal = total;
        if (items.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="6">No players found</td></tr>';
            infoEl.textContent = '0 players';
            pageNumEl.textContent = 'Page 0';
            return;
        }
        const start = (res.offset || 0) + 1;
        const end = (res.offset || 0) + items.length;
        infoEl.textContent = `Showing ${start}–${end} of ${total} players`;
        const totalPages = Math.max(1, Math.ceil(total / PLAYERS_PAGE_SIZE));
        pageNumEl.textContent = `Page ${playersPage + 1} of ${totalPages}`;
        document.getElementById('players-prev').disabled = playersPage <= 0;
        document.getElementById('players-next').disabled = playersPage >= totalPages - 1;

        tableBody.innerHTML = items.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.email || 'N/A'}</td>
                <td><span class="campaign-status ${p.status}">${p.status}</span></td>
                <td>$${parseFloat(p.lifetime_value || 0).toFixed(2)}</td>
                <td><a href="#" class="view-insights-link" data-player-id="${p.id}">View insights</a></td>
                <td><button class="btn btn-secondary btn-sm">View</button></td>
            </tr>
        `).join('');
        tableBody.querySelectorAll('.view-insights-link').forEach(a => {
            a.addEventListener('click', (e) => {
                e.preventDefault();
                document.getElementById('insight-player-id').value = a.getAttribute('data-player-id');
                document.querySelector('.nav-item[data-page="insights"]').click();
            });
        });
    } catch (err) {
        tableBody.innerHTML = '<tr><td colspan="6">Error: ' + err.message + '</td></tr>';
    }
}

(function initPlayersPagination() {
    const prev = document.getElementById('players-prev');
    const next = document.getElementById('players-next');
    if (prev) prev.addEventListener('click', () => { playersPage--; loadPlayers(); });
    if (next) next.addEventListener('click', () => { playersPage++; loadPlayers(); });
})();

async function loadSegments() {
    const grid = document.getElementById('segments-grid');
    grid.innerHTML = '<p>Loading segments...</p>';
    try {
        const list = await api.getSegments();
        if (list.length === 0) {
            grid.innerHTML = '<p>No segments yet. Click "Create AI segments from player data" to generate segments based on your players.</p>';
            return;
        }
        grid.innerHTML = list.map(s => `
            <div class="segment-card">
                <h3>${s.name}</h3>
                <p>${s.description || '—'}</p>
                <small>Type: ${s.segment_type} | Players: ${s.player_count || 0}</small>
            </div>
        `).join('');
    } catch (err) {
        grid.innerHTML = '<p>Error: ' + err.message + '</p>';
    }
}

(function initAiSegmentsBtn() {
    const btn = document.getElementById('ai-generate-segments-btn');
    if (btn) btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = 'Creating segments...';
        try {
            const res = await api.aiGenerateSegments();
            alert(res.message || 'Segments created.');
            loadSegments();
        } catch (e) {
            alert('Error: ' + e.message);
        }
        btn.disabled = false;
        btn.textContent = 'Create AI segments from player data';
    });
})();

async function loadImportExport() {
    const importList = document.getElementById('import-jobs-list');
    const exportList = document.getElementById('export-jobs-list');
    importList.innerHTML = 'Loading...';
    exportList.innerHTML = 'Loading...';
    try {
        const imports = await api.listImports();
        importList.innerHTML = imports.length === 0 ? '<p>No import jobs yet.</p>' : imports.slice(0, 10).map(j => `
            <div class="job-item">#${j.id} ${j.file_name} – ${j.status}</div>
        `).join('');
    } catch (e) {
        importList.innerHTML = '<p>Error loading imports</p>';
    }
    try {
        const exports = await api.listExports();
        exportList.innerHTML = exports.length === 0 ? '<p>No export jobs yet.</p>' : exports.slice(0, 10).map(j => `
            <div class="job-item">
                #${j.id} ${j.entity_type} (${j.export_format}) – ${j.status}
                ${j.status === 'completed' ? `<button class="btn btn-secondary btn-sm" data-export-id="${j.id}">Download</button>` : ''}
            </div>
        `).join('');
        exportList.querySelectorAll('[data-export-id]').forEach(btn => {
            btn.addEventListener('click', () => {
                api.downloadExport(parseInt(btn.getAttribute('data-export-id'), 10));
            });
            btn.style.marginLeft = '8px';
        });
    } catch (e) {
        exportList.innerHTML = '<p>Error loading exports</p>';
    }
}

let insightCharts = [];

function destroyInsightCharts() {
    insightCharts.forEach(c => { try { c.destroy(); } catch (_) {} });
    insightCharts = [];
}

async function loadInsights() {
    destroyInsightCharts();
    try {
        const business = await api.getBusinessInsights();
        const rev = business.revenue_forecast || {};
        const revCtx = document.getElementById('insight-chart-revenue').getContext('2d');
        insightCharts.push(new Chart(revCtx, {
            type: 'bar',
            data: {
                labels: ['Next 30 days', 'Next 90 days'],
                datasets: [{
                    label: 'Revenue forecast ($)',
                    data: [rev.next_30_days || 0, rev.next_90_days || 0],
                    backgroundColor: ['rgba(99, 102, 241, 0.7)', 'rgba(139, 92, 246, 0.7)']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
        }));

        const ret = business.retention_rate || {};
        const retCtx = document.getElementById('insight-chart-retention').getContext('2d');
        insightCharts.push(new Chart(retCtx, {
            type: 'doughnut',
            data: {
                labels: ['7-day retention', '30-day retention', 'Other'],
                datasets: [{
                    data: [(ret['7_day'] || 0) * 100, (ret['30_day'] || 0) * 100, Math.max(0, 100 - (ret['7_day'] || 0) * 100 - (ret['30_day'] || 0) * 100)],
                    backgroundColor: ['#10b981', '#6366f1', '#e5e7eb']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        }));

        const pac = business.player_acquisition_cost || {};
        const byChannel = pac.by_channel || {};
        const acqCtx = document.getElementById('insight-chart-acquisition').getContext('2d');
        const chLabels = Object.keys(byChannel);
        const chData = chLabels.map(k => byChannel[k]);
        insightCharts.push(new Chart(acqCtx, {
            type: 'bar',
            data: {
                labels: chLabels.length ? chLabels : ['Google', 'Facebook', 'Organic'],
                datasets: [{
                    label: 'Cost ($)',
                    data: chData.length ? chData : [25, 30, 5],
                    backgroundColor: 'rgba(99, 102, 241, 0.6)'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', scales: { x: { beginAtZero: true } } }
        }));

        const rec = await api.getCampaignRecommendations();
        const recs = rec.recommendations || [];
        const recCtx = document.getElementById('insight-chart-recommendations').getContext('2d');
        insightCharts.push(new Chart(recCtx, {
            type: 'bar',
            data: {
                labels: recs.map(r => (r.target_segment || r.campaign_type || 'Campaign')),
                datasets: [{
                    label: 'Expected engagement',
                    data: recs.map(r => (r.expected_engagement || 0) * 100),
                    backgroundColor: 'rgba(16, 185, 129, 0.6)'
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { max: 100, beginAtZero: true } } }
        }));
    } catch (e) {
        console.error('Insights load error:', e);
    }
}

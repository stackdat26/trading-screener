let currentCategory = 'all';
let pollingInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    loadResults();

    document.getElementById('min-strength').addEventListener('input', function() {
        document.getElementById('min-strength-val').textContent = this.value + '%';
        loadResults();
    });

    document.getElementById('sweep-type-filter').addEventListener('change', loadResults);
    document.getElementById('sort-by').addEventListener('change', loadResults);

    document.querySelectorAll('.cat-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentCategory = this.dataset.category;
            loadResults();
        });
    });
});

async function loadStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('total-assets-count').textContent = data.total_assets + '+';
        document.getElementById('sweeps-count').textContent = data.total_results;
        if (data.last_updated) {
            document.getElementById('last-updated').textContent = data.last_updated;
        }
        if (data.is_scanning) {
            showScanning(true);
        } else {
            showScanning(false);
        }
    } catch (e) {
        console.error('Status error:', e);
    }
}

async function startScan() {
    const btn = document.getElementById('scan-btn');
    const checkedBoxes = document.querySelectorAll('.scan-cat-cb:checked');
    const categories = Array.from(checkedBoxes).map(cb => cb.value);

    if (categories.length === 0) {
        showError('Please select at least one category to scan.');
        return;
    }

    btn.disabled = true;
    document.getElementById('error-banner').classList.add('hidden');

    try {
        const res = await fetch('/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ categories })
        });
        const data = await res.json();

        if (data.status === 'started' || data.status === 'already_scanning') {
            showScanning(true);
            startPolling();
        }
    } catch (e) {
        showError('Failed to start scan: ' + e.message);
        btn.disabled = false;
    }
}

function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(async () => {
        const res = await fetch('/api/status');
        const data = await res.json();
        if (!data.is_scanning) {
            clearInterval(pollingInterval);
            pollingInterval = null;
            showScanning(false);
            document.getElementById('scan-btn').disabled = false;
            loadResults();
            loadStatus();
            if (data.error) {
                showError('Scan error: ' + data.error);
            }
        }
    }, 3000);
}

function showScanning(active) {
    const banner = document.getElementById('scanning-banner');
    const btn = document.getElementById('scan-btn');
    const icon = document.getElementById('scan-btn-icon');
    const text = document.getElementById('scan-btn-text');
    if (active) {
        banner.classList.remove('hidden');
        btn.disabled = true;
        icon.textContent = '⏳';
        text.textContent = 'Scanning...';
        if (!pollingInterval) startPolling();
    } else {
        banner.classList.add('hidden');
        btn.disabled = false;
        icon.textContent = '▶';
        text.textContent = 'Run Scan';
    }
}

function showError(msg) {
    const el = document.getElementById('error-banner');
    el.textContent = msg;
    el.classList.remove('hidden');
}

async function loadResults() {
    const category = currentCategory;
    const sweepType = document.getElementById('sweep-type-filter').value;
    const minStrength = document.getElementById('min-strength').value;
    const sortBy = document.getElementById('sort-by').value;

    const params = new URLSearchParams({ category, type: sweepType, min_strength: minStrength, sort_by: sortBy });
    try {
        const res = await fetch('/api/results?' + params);
        const data = await res.json();
        renderResults(data.results);
        document.getElementById('results-count').textContent = data.total_found;
        document.getElementById('sweeps-count').textContent = data.total_found;
        if (data.last_updated) {
            document.getElementById('last-updated').textContent = data.last_updated;
        }
    } catch (e) {
        console.error('Results error:', e);
    }
}

function renderResults(results) {
    const grid = document.getElementById('results-grid');
    const empty = document.getElementById('empty-state');

    if (!results || results.length === 0) {
        grid.innerHTML = '';
        empty.classList.remove('hidden');
        return;
    }

    empty.classList.add('hidden');
    grid.innerHTML = results.map(r => createCard(r)).join('');
}

function createCard(r) {
    const isBullish = r.sweep_type === 'Bullish Sweep';
    const dirClass = isBullish ? 'bullish' : 'bearish';
    const dirIcon = isBullish ? '▲' : '▼';
    const strength = r.strength || 0;

    let changeHtml = '-';
    if (r.change_1d !== null && r.change_1d !== undefined) {
        const positive = r.change_1d >= 0;
        changeHtml = `<span class="${positive ? 'change-positive' : 'change-negative'}">${positive ? '+' : ''}${r.change_1d}%</span>`;
    }

    let rsiColor = '';
    if (r.rsi !== null && r.rsi !== undefined) {
        if (r.rsi > 70) rsiColor = 'color: var(--bearish)';
        else if (r.rsi < 30) rsiColor = 'color: var(--bullish)';
    }

    return `
        <div class="result-card ${dirClass}">
            <div class="card-header">
                <div>
                    <div class="card-ticker">${escapeHtml(r.ticker)}</div>
                    <div class="card-category">${escapeHtml(r.category)}</div>
                </div>
                <div class="sweep-badge ${dirClass}">
                    ${dirIcon} ${isBullish ? 'Bullish' : 'Bearish'}
                </div>
            </div>

            <div class="strength-bar-wrap">
                <div class="strength-label">
                    <span>Sweep Strength</span>
                    <span>${strength}%</span>
                </div>
                <div class="strength-bar">
                    <div class="strength-fill ${dirClass}" style="width: ${strength}%"></div>
                </div>
            </div>

            <div class="card-metrics">
                <div class="metric">
                    <div class="metric-label">Price</div>
                    <div class="metric-value">${formatPrice(r.price)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Sweep Level</div>
                    <div class="metric-value">${formatPrice(r.sweep_level)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Vol Surge</div>
                    <div class="metric-value">${r.volume_surge ? r.volume_surge + 'x' : 'N/A'}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">RSI</div>
                    <div class="metric-value" style="${rsiColor}">${r.rsi !== null && r.rsi !== undefined ? r.rsi : 'N/A'}</div>
                </div>
            </div>

            <div class="card-footer">
                <span>1D Change: ${changeHtml}</span>
                <span>${r.sweep_date || ''}</span>
            </div>
        </div>
    `;
}

function formatPrice(price) {
    if (price === null || price === undefined) return 'N/A';
    if (price >= 1000) return price.toLocaleString(undefined, {maximumFractionDigits: 2});
    if (price >= 1) return price.toFixed(2);
    return price.toFixed(5);
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

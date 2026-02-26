// ═══════════════════════════════════════════════════════
//  LogLens — Dashboard JavaScript
// ═══════════════════════════════════════════════════════

// ── Chart Instance ─────────────────────────────────────
let chartInstance = null;

// ── Theme Toggle ───────────────────────────────────────
function toggleTheme() {
  const html = document.documentElement;
  const label = document.getElementById('themeLabel');
  if (html.getAttribute('data-theme') === 'light') {
    html.removeAttribute('data-theme');
    label.textContent = 'Light';
  } else {
    html.setAttribute('data-theme', 'light');
    label.textContent = 'Dark';
  }
  // Re-render chart with new theme colors
  fetchChart();
}

function getThemeChartColors() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  return {
    grid: isLight ? 'rgba(0,0,0,0.06)' : 'rgba(30, 45, 69, 0.5)',
    tick: isLight ? '#8892a4' : '#4a5a74',
    tooltipBg: isLight ? '#ffffff' : '#1a2234',
    tooltipTitle: isLight ? '#1a1f2e' : '#e8edf5',
    tooltipBody: isLight ? '#5a6478' : '#7a8ba8',
    tooltipBorder: isLight ? '#e0e4ea' : '#1e2d45',
    pointBorder: isLight ? '#ffffff' : '#1a2234',
    line: isLight ? '#dc2626' : '#f87171',
    gradientTop: isLight ? 'rgba(220, 38, 38, 0.2)' : 'rgba(248, 113, 113, 0.3)',
    gradientBottom: isLight ? 'rgba(220, 38, 38, 0.0)' : 'rgba(248, 113, 113, 0.0)',
  };
}

// ── Clock ──────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent = now.toLocaleTimeString('en-US', { hour12: false });
}
setInterval(updateClock, 1000);
updateClock();

// ── Loading Bar ────────────────────────────────────────
function showLoading() {
  const bar = document.getElementById('loadingBar');
  bar.style.width = '70%';
}

function hideLoading() {
  const bar = document.getElementById('loadingBar');
  bar.style.width = '100%';
  setTimeout(() => { bar.style.width = '0%'; }, 300);
}

// ── Build query params from filters ───────────────────
function getFilterParams() {
  const params = new URLSearchParams();
  const level = document.getElementById('filterLevel').value;
  const service = document.getElementById('filterService').value;
  const from = document.getElementById('filterFrom').value;
  const to = document.getElementById('filterTo').value;
  const keyword = document.getElementById('filterKeyword').value;

  if (level && level !== 'ALL') params.append('level', level);
  if (service && service !== 'ALL') params.append('service', service);
  if (from) params.append('from_time', from.replace('T', ' '));
  if (to) params.append('to_time', to.replace('T', ' '));
  if (keyword) params.append('keyword', keyword);

  return params.toString();
}

// ── Escape HTML ────────────────────────────────────────
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ── Animate Counter ────────────────────────────────────
function animateCounter(id, target) {
  const el = document.getElementById(id);
  const start = parseInt(el.textContent.replace(/,/g, '')) || 0;
  const duration = 600;
  const startTime = performance.now();

  function tick(now) {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(start + (target - start) * eased).toLocaleString();
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// ═══════════════════════════════════════════════════════
//  FETCH LOGS
// ═══════════════════════════════════════════════════════
async function fetchLogs() {
  showLoading();
  try {
    const query = getFilterParams();
    const url = '/logs' + (query ? '?' + query : '');
    const res = await fetch(url);
    const data = await res.json();
    renderLogs(data);
    updateStats(data);
  } catch (err) {
    console.error('Failed to fetch logs:', err);
  }
  hideLoading();
}

// ── Render Logs Table ──────────────────────────────────
function renderLogs(logs) {
  const tbody = document.getElementById('logsTableBody');
  document.getElementById('logCount').textContent = logs.length.toLocaleString();

  if (logs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:40px; color:var(--text-muted);">No logs match your filters</td></tr>';
    return;
  }

  tbody.innerHTML = logs.map(log => `
    <tr class="row-${log.level}">
      <td class="td-timestamp">${log.timestamp}</td>
      <td><span class="level-badge level-${log.level}">${log.level}</span></td>
      <td class="td-service">${log.service}</td>
      <td class="td-message">${escapeHtml(log.message)}</td>
    </tr>
  `).join('');
}

// ── Update Stats Cards ─────────────────────────────────
function updateStats(logs) {
  const total = logs.length;
  const errors = logs.filter(l => l.level === 'ERROR').length;
  const warns = logs.filter(l => l.level === 'WARN').length;

  animateCounter('statTotal', total);
  animateCounter('statErrors', errors);
  animateCounter('statWarnings', warns);
}

// ═══════════════════════════════════════════════════════
//  FETCH ALERTS
// ═══════════════════════════════════════════════════════
async function fetchAlerts() {
  try {
    const res = await fetch('/alerts');
    const data = await res.json();
    renderAlerts(data);
    animateCounter('statAlerts', data.length);
  } catch (err) {
    console.error('Failed to fetch alerts:', err);
  }
}

// ── Render Alerts ──────────────────────────────────────
function renderAlerts(alerts) {
  const container = document.getElementById('alertsContainer');

  if (!alerts || alerts.length === 0) {
    container.innerHTML = `
      <div class="no-alerts">
        <div class="no-alerts-icon">✓</div>
        <div class="no-alerts-text">No active alerts — all clear</div>
      </div>`;
    return;
  }

  container.innerHTML = alerts.map(a => {
    const sev = a.severity.toLowerCase();
    return `
      <div class="alert-card ${sev}">
        <div class="alert-top">
          <div class="alert-name">${escapeHtml(a.name)}</div>
          <span class="severity-badge ${sev}">${a.severity}</span>
        </div>
        <div class="alert-reason">${escapeHtml(a.reason)}</div>
        <div class="alert-meta">
          <span>Count: ${a.count}</span>
          <span>Window: ${a.window}</span>
        </div>
      </div>`;
  }).join('');
}

// ═══════════════════════════════════════════════════════
//  FETCH CHART DATA
// ═══════════════════════════════════════════════════════
async function fetchChart() {
  try {
    const query = getFilterParams();
    const url = '/chart' + (query ? '?' + query : '');
    const res = await fetch(url);
    const data = await res.json();
    renderChart(data);
  } catch (err) {
    console.error('Failed to fetch chart:', err);
  }
}

// ── Render Chart ───────────────────────────────────────
function renderChart(data) {
  const ctx = document.getElementById('errorChart').getContext('2d');

  if (chartInstance) chartInstance.destroy();

  const labels = data.map(d => d.time);
  const counts = data.map(d => d.count);
  const theme = getThemeChartColors();

  // Gradient fill
  const gradient = ctx.createLinearGradient(0, 0, 0, 280);
  gradient.addColorStop(0, theme.gradientTop);
  gradient.addColorStop(1, theme.gradientBottom);

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Errors',
        data: counts,
        borderColor: theme.line,
        backgroundColor: gradient,
        borderWidth: 2.5,
        pointBackgroundColor: theme.line,
        pointBorderColor: theme.pointBorder,
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        tension: 0.35,
        fill: true,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: 'index',
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: theme.tooltipBg,
          titleColor: theme.tooltipTitle,
          bodyColor: theme.tooltipBody,
          borderColor: theme.tooltipBorder,
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          titleFont: { family: 'JetBrains Mono', size: 12 },
          bodyFont: { family: 'JetBrains Mono', size: 12 },
          displayColors: false,
          callbacks: {
            label: ctx => `${ctx.parsed.y} errors`
          }
        }
      },
      scales: {
        x: {
          grid: { color: theme.grid, drawBorder: false },
          ticks: {
            color: theme.tick,
            font: { family: 'JetBrains Mono', size: 11 },
            maxRotation: 0,
            maxTicksLimit: 15
          }
        },
        y: {
          beginAtZero: true,
          grid: { color: theme.grid, drawBorder: false },
          ticks: {
            color: theme.tick,
            font: { family: 'JetBrains Mono', size: 11 },
            stepSize: 5
          }
        }
      }
    }
  });
}

// ═══════════════════════════════════════════════════════
//  EXPORT CSV
// ═══════════════════════════════════════════════════════
function exportCSV() {
  const query = getFilterParams();
  const url = '/export' + (query ? '?' + query : '');
  window.location.href = url;
}

// ═══════════════════════════════════════════════════════
//  FETCH RISK SCORES
// ═══════════════════════════════════════════════════════
async function fetchRisk() {
  try {
    const res = await fetch('/risk');
    const data = await res.json();
    renderRisk(data);
  } catch (err) {
    console.error('Failed to fetch risk scores:', err);
  }
}

// ── Render Risk Cards ──────────────────────────────────
function renderRisk(scores) {
  const container = document.getElementById('riskContainer');

  if (!scores || scores.length === 0) {
    container.innerHTML = '<div style="color:var(--text-muted); padding:20px; text-align:center;">No data yet</div>';
    return;
  }

  container.innerHTML = scores.map(s => {
    const level = s.risk_level.toLowerCase();

    // Ring color based on risk level
    let ringColor;
    if (level === 'critical') ringColor = '#f87171';
    else if (level === 'moderate') ringColor = '#fbbf24';
    else ringColor = '#34d399';

    // SVG circle math (radius=27, circumference=169.6)
    const circumference = 2 * Math.PI * 27;
    const offset = circumference - (s.risk_score / 100) * circumference;

    return `
      <div class="risk-card">
        <div class="risk-score-ring">
          <svg viewBox="0 0 64 64">
            <circle class="ring-bg" cx="32" cy="32" r="27"/>
            <circle class="ring-fill" cx="32" cy="32" r="27"
              stroke="${ringColor}"
              stroke-dasharray="${circumference}"
              stroke-dashoffset="${offset}"/>
          </svg>
          <div class="risk-score-number" style="color:${ringColor}">${s.risk_score}</div>
        </div>
        <div class="risk-info">
          <div class="risk-service">${escapeHtml(s.service)}</div>
          <span class="risk-level-badge ${level}">${s.risk_level}</span>
          <div class="risk-stats">
            <span>Err: ${s.errors}</span>
            <span>Warn: ${s.warnings}</span>
            <span>Failed: ${s.failed_keywords}</span>
          </div>
        </div>
      </div>`;
  }).join('');
}

// ═══════════════════════════════════════════════════════
//  EVENT LISTENERS & INIT
// ═══════════════════════════════════════════════════════

// Enter key triggers search
document.getElementById('filterKeyword').addEventListener('keydown', e => {
  if (e.key === 'Enter') fetchLogs();
});

// Initial load
fetchLogs();
fetchAlerts();
fetchChart();
fetchRisk();

// Auto-refresh everything every 2 seconds for real-time feel
setInterval(() => {
  fetchLogs();
  fetchAlerts();
  fetchChart();
  fetchRisk();
}, 2000);
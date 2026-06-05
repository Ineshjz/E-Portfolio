let portfolios = [];

/* ── INIT ─────────────────────────────────── */
async function init() {
    await loadUserInfo();
    await loadPortfolios();
}

/* ── USER INFO ───────────────────────────── */
async function loadUserInfo() {
    try {
        const res = await fetch('/api/me');
        if (!res.ok) return;
        const user = await res.json();
        document.getElementById('headerEmail').textContent = user.email;
        document.getElementById('headerAvatar').textContent =
            user.email.slice(0, 2).toUpperCase();
    } catch (_) { }
}

/* ── LOAD PORTFOLIOS ─────────────────────── */
async function loadPortfolios() {
    try {
        const res = await fetch('/api/my-portfolios');
        if (!res.ok) throw new Error();
        portfolios = await res.json();
        render();
    } catch (_) {
        document.getElementById('skeletonLoader').style.display = 'none';
        showToast('⚠ Impossible de charger les portfolios');
    }
}

/* ── RENDER ──────────────────────────────── */
function render() {
    document.getElementById('skeletonLoader').style.display = 'none';

    if (portfolios.length === 0) {
        document.getElementById('emptyState').style.display = 'flex';
        return;
    }

    const list = document.getElementById('portfolioList');
    list.style.display = '';
    list.innerHTML = portfolios.map(buildRow).join('');
}

function buildRow(p) {
    const initials = `${p.firstname?.[0] || ''}${p.lastname?.[0] || ''}`.toUpperCase();

    const skills = (p.main_skills || '')
        .split(',')
        .map(s => s.trim())
        .filter(Boolean)
        .slice(0, 3)
        .map(s => `<span class="skill-chip">${s}</span>`)
        .join('');

    return `
    <a class="port-row" href="/portfolio/${p.slug}">
      <div class="row-avatar">${initials}</div>
      <div class="row-info">
        <div class="row-name">${p.firstname} ${p.lastname}</div>
        ${p.fields ? `<div class="row-fields">${p.fields}</div>` : ''}
      </div>
      ${skills ? `<div class="row-skills">${skills}</div>` : ''}
      <span class="row-arrow">→</span>
    </a>`;
}

/* ── TOAST ───────────────────────────────── */
function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 3000);
}

init();
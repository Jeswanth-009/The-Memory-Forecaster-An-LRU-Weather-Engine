const API_BASE = "http://127.0.0.1:8000";
const SESSION_KEY = 'mf_session';

// ─── Auth Guard ──────────────────────────────────────────────────
const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null');
if (!session) window.location.href = 'login.html';
else {
  document.getElementById('user-name').textContent   = session.username;
  document.getElementById('user-role').textContent   = session.role || 'USER';
  document.getElementById('user-avatar').textContent = session.avatar || session.username[0].toUpperCase();
}

function signOut() {
  localStorage.removeItem(SESSION_KEY);
  window.location.href = 'login.html';
}

// ─── State ───────────────────────────────────────────────────────
const stats = { total: 0, hits: 0, misses: 0, evictions: 0 };
let prevCacheKeys = [];
let cachedData = {};

// ─── Condition Emoji ─────────────────────────────────────────────
const EMOJI = { sunny:'☀️', cloudy:'☁️', rainy:'🌧️', humid:'💧', haze:'🌫️', hot:'🔥', dry:'🏜️', clear:'✨', windy:'🌬️' };
const getEmoji = c => EMOJI[c?.toLowerCase()] || '🌡️';

// ─── Helpers ─────────────────────────────────────────────────────
function showGlobalError(msg) {
  const el = document.getElementById('global-error');
  el.textContent = msg; el.style.display = 'block';
  clearTimeout(el._t);
  el._t = setTimeout(() => el.style.display = 'none', 4000);
}
function hideGlobalError() { document.getElementById('global-error').style.display = 'none'; }

function setResponse(id, text, cls = '') {
  const el = document.getElementById(id);
  el.textContent = text; el.className = `response-box ${cls}`;
}

// ─── Main Search ─────────────────────────────────────────────────
async function mainSearch() {
  const city = document.getElementById('main-search').value.trim();
  if (!city) return;
  await fetchWeatherAndShow(city);
}

async function quickSearch(city) {
  document.getElementById('main-search').value = city;
  await fetchWeatherAndShow(city);
}

async function fetchWeatherAndShow(city) {
  hideGlobalError();
  document.getElementById('btn-search').disabled = true;
  try {
    const res = await fetch(`${API_BASE}/weather/${encodeURIComponent(city.toLowerCase())}`);
    if (res.status === 404) { showGlobalError(`⚠ City "${city}" not found in the weather store.`); return; }
    if (res.status === 422) { showGlobalError('⚠ Invalid city name.'); return; }
    if (!res.ok) { showGlobalError(`⚠ Server error (${res.status}).`); return; }
    const data = await res.json();
    cachedData[data.city] = data;
    updateStats(data.source);
    showWeatherResult(data);
    await refreshCache();
  } catch (_) {
    showGlobalError('⚠ Cannot reach the API. Is the backend running on port 8000?');
  } finally {
    document.getElementById('btn-search').disabled = false;
  }
}

// ─── Modal ───────────────────────────────────────────────────────
function showWeatherResult(data) {
  const isHit = data.source === 'cache';
  const cityTitle = data.city.charAt(0).toUpperCase() + data.city.slice(1);
  document.getElementById('result-badge').textContent   = isHit ? '⚡ CACHE HIT' : '☁ CACHE MISS';
  document.getElementById('result-badge').className     = `result-badge ${isHit ? 'hit' : 'miss'}`;
  document.getElementById('result-city').textContent    = cityTitle;
  document.getElementById('result-country').textContent = 'India';
  document.getElementById('result-icon').textContent    = getEmoji(data.condition);
  document.getElementById('result-condition').textContent = data.condition;
  document.getElementById('result-feels').textContent   = `Feels like ${data.temperature}°C`;
  document.getElementById('result-temp').textContent    = `${data.temperature}°C`;
  document.getElementById('result-footer').textContent  = isHit
    ? '⚡ Served instantly from LRU cache'
    : '☁ Fetched from store · added to cache';
  document.getElementById('weather-result-panel').style.display = 'block';
}

function closeWeatherResult() {
  document.getElementById('weather-result-panel').style.display = 'none';
}

// ─── Panel: GET ──────────────────────────────────────────────────
async function doGet() {
  const city = document.getElementById('get-city').value.trim().toLowerCase();
  if (!city) { setResponse('get-response', '⚠ Enter a city name.', 'error'); return; }
  setResponse('get-response', 'Fetching…', '');
  try {
    const res = await fetch(`${API_BASE}/weather/${encodeURIComponent(city)}`);
    if (res.status === 404) { setResponse('get-response', `404 — "${city}" not found.`, 'error'); return; }
    if (!res.ok) { setResponse('get-response', `Error ${res.status}`, 'error'); return; }
    const d = await res.json();
    const isHit = d.source === 'cache';
    cachedData[d.city] = d;
    updateStats(d.source);
    setResponse('get-response',
      `${isHit ? '⚡ CACHE HIT' : '☁ CACHE MISS'}\nCity: ${d.city}  |  Temp: ${d.temperature}°C  |  ${d.condition}`,
      isHit ? 'hit' : 'success'
    );
    await refreshCache();
  } catch (_) { setResponse('get-response', '⚠ API unreachable.', 'error'); }
}

// ─── Panel: DELETE ───────────────────────────────────────────────
async function doDel() {
  const city = document.getElementById('del-city').value.trim().toLowerCase();
  if (!city) { setResponse('del-response', '⚠ Enter a city name.', 'error'); return; }
  setResponse('del-response', 'Deleting…', '');
  try {
    const res = await fetch(`${API_BASE}/cache/${encodeURIComponent(city)}`, { method: 'DELETE' });
    if (res.status === 404) { setResponse('del-response', `"${city}" is not in cache.`, 'error'); return; }
    if (!res.ok) { setResponse('del-response', `Error ${res.status}`, 'error'); return; }
    setResponse('del-response', `✓ "${city}" removed from cache.`, 'success');
    await refreshCache();
  } catch (_) { setResponse('del-response', '⚠ API unreachable.', 'error'); }
}

// ─── Flush ───────────────────────────────────────────────────────
async function flushCache() {
  try {
    await fetch(`${API_BASE}/cache`, { method: 'DELETE' });
    prevCacheKeys = []; cachedData = {};
    await refreshCache();
  } catch (_) { showGlobalError('⚠ Could not flush cache.'); }
}

// ─── Cache Refresh ───────────────────────────────────────────────
async function refreshCache() {
  try {
    const res  = await fetch(`${API_BASE}/cache`);
    const data = await res.json();
    const keys = data.cache || [];
    const evicted = prevCacheKeys.filter(k => !keys.includes(k));
    stats.evictions += evicted.length;
    prevCacheKeys = [...keys];
    await renderLiveSlots(keys);
    updateNavStats(keys.length);
    updateStatsPanel(keys.length);
  } catch (_) {}
}

// ─── Live Slots ──────────────────────────────────────────────────
async function renderLiveSlots(keys) {
  const container = document.getElementById('live-slots');
  if (keys.length === 0) {
    container.innerHTML = `<div class="live-empty"><div class="empty-globe">🌍</div><p>No cities cached.<br>Search a city above.</p></div>`;
    return;
  }
  const slots = await Promise.all(keys.map(async (city, i) => {
    if (!cachedData[city]) {
      try { const r = await fetch(`${API_BASE}/weather/${city}`); if (r.ok) cachedData[city] = await r.json(); } catch (_) {}
    }
    const d = cachedData[city];
    const isMRU = i === 0;
    const isLRU = i === keys.length - 1 && keys.length > 1;
    const tag = isMRU
      ? '<span class="slot-tag tag-mru">MRU</span>'
      : (isLRU ? '<span class="slot-tag tag-lru">LRU</span>' : '');
    return `
      <div class="live-slot" onclick="quickSearch('${city}')">
        <span class="slot-rank">${i + 1}</span>
        <span class="slot-city">${city}</span>
        <span class="slot-condition">${d ? getEmoji(d.condition) + ' ' + d.condition : ''}</span>
        <span class="slot-temp">${d ? d.temperature + '°C' : ''}</span>
        ${tag}
      </div>`;
  }));
  container.innerHTML = slots.join('');
}

// ─── Stats ───────────────────────────────────────────────────────
function updateStats(source) {
  stats.total++;
  if (source === 'cache') stats.hits++;
  else stats.misses++;
}

function updateNavStats(cacheSize) {
  document.getElementById('nav-cached').textContent    = cacheSize;
  document.getElementById('nav-hitrate').textContent   = stats.total > 0 ? Math.round((stats.hits / stats.total) * 100) + '%' : '0%';
  document.getElementById('nav-evictions').textContent = stats.evictions;
}

function updateStatsPanel(cacheSize) {
  const ratio = stats.total > 0 ? Math.round((stats.hits / stats.total) * 100) : 0;
  document.getElementById('sc-size').textContent      = `${cacheSize}/5`;
  document.getElementById('sc-hitrate').textContent   = ratio + '%';
  document.getElementById('sc-hits').textContent      = stats.hits;
  document.getElementById('sc-misses').textContent    = stats.misses;
  document.getElementById('sc-evictions').textContent = stats.evictions;
  document.getElementById('sc-total').textContent     = stats.total;
  document.getElementById('cb-fill').style.width      = `${(cacheSize / 5) * 100}%`;
  document.getElementById('cb-pct').textContent       = `${Math.round((cacheSize / 5) * 100)}%`;
  document.getElementById('cb-count').innerHTML       = `<strong>${cacheSize}</strong> / 5 cities`;
}

// ─── Events ──────────────────────────────────────────────────────
document.getElementById('btn-search').addEventListener('click', mainSearch);
document.getElementById('main-search').addEventListener('keydown', e => { if (e.key === 'Enter') mainSearch(); });
document.getElementById('get-city').addEventListener('keydown',   e => { if (e.key === 'Enter') doGet(); });
document.getElementById('del-city').addEventListener('keydown',   e => { if (e.key === 'Enter') doDel(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeWeatherResult(); });

// ─── Init ────────────────────────────────────────────────────────
refreshCache();
setInterval(refreshCache, 5000);
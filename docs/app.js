const state = {
  rows: [],
};

const filterModeEl = document.getElementById("filter-mode");
const labelFilterEl = document.getElementById("label-filter");
const searchEl = document.getElementById("search");
const rowsEl = document.getElementById("rows");
const lastUpdatedEl = document.getElementById("last-updated");
const refreshEl = document.getElementById("refresh");

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined) return "-";
  return Number(value).toFixed(decimals);
}

function render() {
  const mode = filterModeEl.value;
  const labelFilter = labelFilterEl.value;
  const query = searchEl.value.trim().toUpperCase();

  const filtered = state.rows.filter((row) => {
    if (mode === "strict" && row.risk_tag) return false;
    if (labelFilter && row.label !== labelFilter) return false;
    if (query && !row.ticker.includes(query)) return false;
    return true;
  });

  rowsEl.innerHTML = filtered
    .map((row) => {
      const labelClass = row.label.toLowerCase();
      return `
        <tr>
          <td>${row.ticker}</td>
          <td><span class="tag ${labelClass}">${row.label}</span></td>
          <td class="risk">${row.risk_tag || ""}</td>
          <td>${formatNumber(row.momentum_score)}</td>
          <td>${formatNumber(row.conviction_score)}</td>
          <td>${row.mention_count}</td>
          <td>${row.unique_authors}</td>
          <td>${formatNumber(row.engagement)}</td>
        </tr>
      `;
    })
    .join("");
}

function setTimestamp(epochSeconds) {
  if (!epochSeconds) return;
  const date = new Date(epochSeconds * 1000);
  lastUpdatedEl.textContent = `Updated: ${date.toUTCString()}`;
}

async function loadData() {
  try {
    const resp = await fetch("./data/latest.json", { cache: "no-store" });
    const data = await resp.json();
    state.rows = data.rows || [];

    if (data.filter_mode_default) {
      filterModeEl.value = data.filter_mode_default;
    }
    setTimestamp(data.generated_utc);
    render();
  } catch (err) {
    rowsEl.innerHTML = '<tr><td colspan="8">Failed to load data.</td></tr>';
  }
}

filterModeEl.addEventListener("change", render);
labelFilterEl.addEventListener("change", render);
searchEl.addEventListener("input", render);
refreshEl.addEventListener("click", loadData);

loadData();

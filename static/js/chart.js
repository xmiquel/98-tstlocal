/**
 * Candlestick chart viewer for OHLCV market data.
 * Uses Lightweight Charts v4 loaded from unpkg CDN.
 */

(function () {
  "use strict";

  const config = window.__chartConfig || {};
  if (!config.symbol) return;

  const chart = LightweightCharts.createChart(
    document.getElementById("chart"),
    {
      layout: {
        textColor: "#d1d4dc",
        background: { type: "solid", color: "#131722" },
      },
      grid: {
        vertLines: { color: "#2a2e39" },
        horzLines: { color: "#2a2e39" },
      },
    }
  );

  const series = chart.addCandlestickSeries();

  function buildUrl(sym, tf, lim, st, en) {
    let url = "/api/ohlc?symbol=" + encodeURIComponent(sym);
    url += "&timeframe=" + encodeURIComponent(tf);
    url += "&limit=" + lim;
    if (st) url += "&start=" + encodeURIComponent(st);
    if (en) url += "&end=" + encodeURIComponent(en);
    return url;
  }

  function loadData(sym, tf, lim, st, en) {
    var url = buildUrl(sym, tf, lim, st, en);
    fetch(url)
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        series.setData(data);
        chart.timeScale().fitContent();
      })
      .catch(function (err) {
        console.error("Failed to load OHLCV data:", err);
      });
  }

  // Initial load
  loadData(
    config.symbol,
    config.timeframe,
    config.limit,
    config.start,
    config.end
  );

  // Re-fetch on form submit (date change)
  document
    .getElementById("chart-controls")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      var form = e.target;
      var sym = form.querySelector("[name=symbol]").value;
      var tf = form.querySelector("[name=timeframe]").value;
      var lim = form.querySelector("[name=limit]").value;
      var st = form.querySelector("[name=start]").value;
      var en = form.querySelector("[name=end]").value;
      loadData(sym, tf, parseInt(lim, 10) || 200, st, en);
    });
})();

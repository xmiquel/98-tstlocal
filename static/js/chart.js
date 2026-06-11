/**
 * Candlestick chart viewer for OHLCV market data.
 * Uses Lightweight Charts v4 loaded from unpkg CDN.
 *
 * Exposes window.chartApi for external overlay management
 * by chart-indicators.js.
 */

(function () {
  "use strict";

  var config = window.__chartConfig || {};
  if (!config.symbol) return;

  var container = document.getElementById("chart");
  var chart = LightweightCharts.createChart(container, {
    layout: {
      textColor: "#d1d4dc",
      background: { type: "solid", color: "#131722" },
    },
    grid: {
      vertLines: { color: "#2a2e39" },
      horzLines: { color: "#2a2e39" },
    },
    timeScale: {
      timeVisible: true,
      secondsVisible: false,
    },
  });

  var series = chart.addCandlestickSeries();

  // Store raw data for tooltip lookup (Lightweight Charts strips custom props)
  var rawData = [];

  // --- Custom tooltip ---
  var tooltip = document.getElementById("chart-tooltip");

  chart.subscribeCrosshairMove(function (param) {
    if (!param.point || !param.seriesData || !param.time) {
      tooltip.style.display = "none";
      return;
    }
    // param.time is a UTC timestamp in seconds (business day based for daily, but fine for intraday)
    // Find matching data point in rawData by time
    var data = null;
    if (rawData.length > 0) {
      // param.time can be number (seconds) or object {year, month, day}
      var targetTime = typeof param.time === "number" ? param.time : null;
      if (targetTime) {
        // Find closest data point by time (exact match for 1m, nearest for others)
        for (var i = 0; i < rawData.length; i++) {
          if (rawData[i].time === targetTime) {
            data = rawData[i];
            break;
          }
        }
      }
    }
    if (!data) {
      tooltip.style.display = "none";
      return;
    }
    tooltip.style.display = "block";

    var dateStr = "";
    if (typeof data.time === "object" && data.time.year !== undefined) {
      dateStr =
        data.time.year +
        "-" +
        String(data.time.month).padStart(2, "0") +
        "-" +
        String(data.time.day).padStart(2, "0");
    } else {
      var d = new Date(data.time * 1000);
      dateStr = d.toLocaleString();
    }

    var spreadVal = data.spread !== undefined ? data.spread : "--";

    tooltip.innerHTML =
      '<div class="tt-time">' +
      dateStr +
      "</div>" +
      '<div class="tt-row"><span class="tt-label">O</span><span class="tt-val tt-val-o">' +
      data.open.toFixed(2) +
      "</span></div>" +
      '<div class="tt-row"><span class="tt-label">H</span><span class="tt-val tt-val-h">' +
      data.high.toFixed(2) +
      "</span></div>" +
      '<div class="tt-row"><span class="tt-label">L</span><span class="tt-val tt-val-l">' +
      data.low.toFixed(2) +
      "</span></div>" +
      '<div class="tt-row"><span class="tt-label">C</span><span class="tt-val tt-val-c">' +
      data.close.toFixed(2) +
      "</span></div>" +
      '<div class="tt-row"><span class="tt-label">V</span><span class="tt-val">' +
      (data.tickvol || 0).toLocaleString() +
      "</span></div>" +
      '<div class="tt-row"><span class="tt-label">Spr</span><span class="tt-val">' +
      spreadVal +
      "</span></div>";

    // Position tooltip near the crosshair
    var chartRect = container.getBoundingClientRect();
    var left = param.point.x + 15;
    var top = param.point.y - 10;
    if (left + 150 > chartRect.width) left = param.point.x - 160;
    if (top < 0) top = 10;
    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";
  });

  // --- Reload callbacks (for chart-indicators.js etc.) ---
  var reloadCallbacks = [];

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
        rawData = data; // Keep reference for tooltip lookup
        series.setData(data);
        chart.timeScale().fitContent();
        // Notify registered callbacks that new data was loaded
        for (var i = 0; i < reloadCallbacks.length; i++) {
          reloadCallbacks[i](sym, tf, lim, st, en);
        }
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

  // --- Public API for chart-indicators.js ---
  function getCurrentParams() {
    var form = document.getElementById("chart-controls");
    if (!form) return null;
    return {
      symbol: form.querySelector("[name=symbol]").value,
      timeframe: form.querySelector("[name=timeframe]").value,
      limit: parseInt(form.querySelector("[name=limit]").value, 10) || 200,
      start: form.querySelector("[name=start]").value,
      end: form.querySelector("[name=end]").value,
    };
  }

  window.chartApi = {
    getChart: function () {
      return chart;
    },
    getSeries: function () {
      return series;
    },
    onReload: function (cb) {
      if (typeof cb === "function") {
        reloadCallbacks.push(cb);
      }
    },
    getCurrentParams: getCurrentParams,
  };
})();

/**
 * Indicator overlay manager for the OHLCV chart.
 *
 * Depends on window.chartApi exposed by chart.js.
 * Handles:
 *  - Loading the indicator catalog into the select dropdown
 *  - Rendering config forms for selected indicators
 *  - Adding/removing overlay LineSeries
 *  - Crosshair-driven data panel updates
 *  - Reloading indicators when chart data changes
 */
(function () {
  "use strict";

  // Guard: chartApi must be present
  if (!window.chartApi) return;

  var chart = window.chartApi.getChart();
  if (!chart) return;

  // ── Palette (cycled) ──────────────────────────────────────────────────
  var COLORS = ["#2962FF", "#FF9800", "#9C27B0", "#FF5252", "#4CAF50"];
  var colorIndex = 0;

  // ── State ──────────────────────────────────────────────────────────────
  var activeOverlays = [];
  var nextId = 1;
  var catalog = []; // Cached catalog entries from API

  // ── DOM refs ───────────────────────────────────────────────────────────
  var selectEl = document.getElementById("indicator-select");
  var configBtn = document.getElementById("indicator-config-btn");
  var configArea = document.getElementById("indicator-config-area");
  var activeList = document.getElementById("active-indicators");
  var dataPanel = document.getElementById("data-panel");

  // ── Catalog loading ────────────────────────────────────────────────────

  function loadCatalog() {
    if (!selectEl) return;
    fetch("/api/indicators/catalog")
      .then(function (r) {
        if (!r.ok) throw new Error("Catalog fetch failed");
        return r.json();
      })
      .then(function (data) {
        catalog = data;
        renderCatalogOptions(data);
        if (configBtn) configBtn.disabled = false;
      })
      .catch(function (err) {
        console.error("Failed to load indicator catalog:", err);
        if (selectEl) {
          selectEl.innerHTML =
            '<option value="">Error loading catalog</option>';
        }
      });
  }

  function renderCatalogOptions(entries) {
    if (!selectEl) return;
    var html = '<option value="">— Select —</option>';
    for (var i = 0; i < entries.length; i++) {
      html +=
        '<option value="' +
        entries[i].name +
        '">' +
        entries[i].name +
        "</option>";
    }
    selectEl.innerHTML = html;
    selectEl.value = "";
  }

  // ── Config form rendering ──────────────────────────────────────────────

  function getCatalogEntry(name) {
    for (var i = 0; i < catalog.length; i++) {
      if (catalog[i].name === name) return catalog[i];
    }
    return null;
  }

  function renderConfigForm(indicatorName) {
    if (!configArea) return;
    var entry = getCatalogEntry(indicatorName);
    if (!entry) {
      configArea.innerHTML =
        '<div class="indicator-config-error">Unknown indicator: ' +
        indicatorName +
        "</div>";
      return;
    }

    var html =
      '<form id="indicator-config-form" class="indicator-config-form"' +
      ' onsubmit="return window.__submitIndicatorConfig(event)">' +
      '<input type="hidden" name="indicator" value="' +
      entry.name +
      '">' +
      '<h4 class="indicator-config-name">' +
      entry.name +
      "</h4>";

    var params = entry.params || [];
    for (var i = 0; i < params.length; i++) {
      var p = params[i];
      html += '<div class="indicator-param-row">';
      html +=
        '<label for="param-' +
        p.name +
        '">' +
        p.name +
        "</label>";

      if (p.type === "integer") {
        html +=
          '<input type="number" id="param-' +
          p.name +
          '" name="' +
          p.name +
          '" value="' +
          p.default +
          '" step="1" />';
      } else if (p.type === "float" || p.type === "number") {
        html +=
          '<input type="number" id="param-' +
          p.name +
          '" name="' +
          p.name +
          '" value="' +
          p.default +
          '" step="0.01" />';
      } else {
        html +=
          '<input type="text" id="param-' +
          p.name +
          '" name="' +
          p.name +
          '" value="' +
          p.default +
          '" />';
      }

      if (p.description) {
        html +=
          '<span class="indicator-param-desc">' +
          p.description +
          "</span>";
      }
      html += "</div>";
    }

    html +=
      '<button type="submit" class="indicator-submit-btn">Apply</button>';
    html += "</form>";
    configArea.innerHTML = html;
  }

  // ── Indicator calculation & overlay ────────────────────────────────────

  function getNextColor() {
    var c = COLORS[colorIndex % COLORS.length];
    colorIndex++;
    return c;
  }

  function addOverlay(indicator, params, values, label) {
    var id = nextId++;
    var color = getNextColor();

    var series = chart.addLineSeries({
      color: color,
      lineWidth: 2,
      lastValueVisible: true,
      priceLineVisible: false,
    });
    series.setData(values);

    var overlay = {
      id: id,
      indicator: indicator,
      params: params,
      series: series,
      label: label,
      color: color,
    };
    activeOverlays.push(overlay);

    renderOverlayList();
    return id;
  }

  function removeOverlay(id) {
    var idx = -1;
    for (var i = 0; i < activeOverlays.length; i++) {
      if (activeOverlays[i].id === id) {
        idx = i;
        break;
      }
    }
    if (idx === -1) return;

    var overlay = activeOverlays[idx];
    chart.removeSeries(overlay.series);
    activeOverlays.splice(idx, 1);
    renderOverlayList();

    if (activeOverlays.length === 0 && dataPanel) {
      dataPanel.innerHTML = "";
    }
  }

  // ── Config form submission ─────────────────────────────────────────────

  function submitIndicatorConfig(form) {
    var fd = new FormData(form);
    var indicator = fd.get("indicator");
    var params = {};
    var entry = getCatalogEntry(indicator);
    if (entry) {
      for (var i = 0; i < entry.params.length; i++) {
        var pName = entry.params[i].name;
        var val = fd.get(pName);
        if (val !== null) {
          if (entry.params[i].type === "integer") {
            params[pName] = parseInt(val, 10);
          } else if (
            entry.params[i].type === "float" ||
            entry.params[i].type === "number"
          ) {
            params[pName] = parseFloat(val);
          } else {
            params[pName] = val;
          }
        }
      }
    }

    var chartParams = window.chartApi.getCurrentParams();
    var body = JSON.stringify({
      symbol: chartParams ? chartParams.symbol : "",
      timeframe: chartParams ? chartParams.timeframe : "1m",
      indicator: indicator,
      params: params,
    });

    fetch("/api/indicators/calculate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body,
    })
      .then(function (r) {
        if (!r.ok)
          throw new Error("Calculation failed: " + r.statusText);
        return r.json();
      })
      .then(function (result) {
        addOverlay(indicator, params, result.values, result.label);
        // Clear config form after successful add
        if (configArea) configArea.innerHTML = "";
        if (selectEl) selectEl.value = "";
      })
      .catch(function (err) {
        console.error("Indicator calculation error:", err);
        if (configArea) {
          configArea.innerHTML =
            '<div class="indicator-config-error">' +
            "Failed to calculate indicator: " +
            err.message +
            "</div>";
        }
      });

    return false; // prevent form submission
  }

  // ── Reload all active overlays ─────────────────────────────────────────

  function reloadAll(symbol, timeframe) {
    if (activeOverlays.length === 0) return;

    for (var i = 0; i < activeOverlays.length; i++) {
      (function (overlay) {
        var body = JSON.stringify({
          symbol: symbol,
          timeframe: timeframe,
          indicator: overlay.indicator,
          params: overlay.params,
        });
        fetch("/api/indicators/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: body,
        })
          .then(function (r) {
            if (!r.ok) throw new Error("Indicator reload failed");
            return r.json();
          })
          .then(function (result) {
            overlay.series.setData(result.values);
            overlay.label = result.label;
            renderOverlayList();
          })
          .catch(function (err) {
            console.error(
              "Failed to reload indicator " + overlay.label + ":",
              err
            );
          });
      })(activeOverlays[i]);
    }
  }

  // ── Overlay list rendering ─────────────────────────────────────────────

  function renderOverlayList() {
    if (!activeList) return;

    if (activeOverlays.length === 0) {
      activeList.innerHTML =
        '<div class="indicator-empty">No indicators added.</div>';
      return;
    }

    var html = "";
    for (var i = 0; i < activeOverlays.length; i++) {
      var o = activeOverlays[i];
      html +=
        '<div class="indicator-row" data-id="' +
        o.id +
        '">' +
        '<span class="indicator-dot" style="background:' +
        o.color +
        '"></span>' +
        '<span class="indicator-label">' +
        o.label +
        "</span>" +
        '<button class="indicator-remove" ' +
        'onclick="window.__removeIndicator(' +
        o.id +
        ')" ' +
        'title="Remove ' +
        o.label +
        '">&times;</button>' +
        "</div>";
    }
    activeList.innerHTML = html;
  }

  // ── Crosshair data panel ───────────────────────────────────────────────

  function updateDataPanel(param) {
    if (!dataPanel) return;
    if (!param.point || !param.seriesData || activeOverlays.length === 0) {
      dataPanel.innerHTML = "";
      return;
    }

    var html = '<div class="dp-title">Indicators</div>';
    var hasValues = false;
    for (var i = 0; i < activeOverlays.length; i++) {
      var overlay = activeOverlays[i];
      var seriesData = param.seriesData.get(overlay.series);
      if (seriesData && typeof seriesData.value !== "undefined") {
        hasValues = true;
        html +=
          '<div class="dp-row">' +
          '<span class="dp-label" style="color:' +
          overlay.color +
          '">' +
          overlay.label +
          '</span>' +
          '<span class="dp-value">' +
          seriesData.value.toFixed(4) +
          "</span>" +
          "</div>";
      }
    }
    dataPanel.innerHTML = hasValues ? html : "";
  }

  // Subscribe to crosshair moves for the data panel
  chart.subscribeCrosshairMove(function (param) {
    updateDataPanel(param);
  });

  // ── Register reload callback ───────────────────────────────────────────

  window.chartApi.onReload(function (sym, tf) {
    reloadAll(sym, tf);
  });

  // ── Event bindings ─────────────────────────────────────────────────────

  // Configure button click: render config form for selected indicator
  if (configBtn && selectEl) {
    configBtn.addEventListener("click", function () {
      var val = selectEl.value;
      if (val) {
        renderConfigForm(val);
      }
    });

    // Enable/disable configure button based on selection
    selectEl.addEventListener("change", function () {
      configBtn.disabled = !this.value;
      // Clear config area when selection changes
      if (configArea) configArea.innerHTML = "";
    });
  }

  // ── Global API (called from inline HTML onclick/onsubmit) ──────────────

  window.__removeIndicator = removeOverlay;
  window.__submitIndicatorConfig = function (event) {
    event.preventDefault();
    return submitIndicatorConfig(event.target);
  };

  // ── Initialize ─────────────────────────────────────────────────────────
  loadCatalog();

  console.log("chart-indicators.js initialized");
})();

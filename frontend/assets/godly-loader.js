/**
 * =============================================================================
 * VyaparAI — Godly Wave Loader Controller (v2.5 Calacatta)
 * 60 FPS GPU-Accelerated Concentric Waves (Apple Blue & Florentine Gold)
 * Features:
 *  - AUTOMATIC snappy Wave Transition on EVERY page load / refresh (~750ms smooth reveal)
 *  - window.VyaparLoader.navigate(url): ~450ms wave surge then instant location switch
 *  - Global Click Interceptor: intercepts .dock-btn and navigation links (a[href$='.html'])
 *  - Zero-latency micro-haptics via Web Audio API
 *  - Complete dynamic DOM & CSS injection if absent
 *  - Escape key & backdrop click dismissal
 * =============================================================================
 */

(function (root, factory) {
  var api = factory();
  if (typeof root !== 'undefined') {
    root.VyaparLoader = api;
    root.previewGodlyLoader = api.preview;
    root.replayGodlyLoaderPreview = api.replay;
    root.dismissGodlyLoaderPreview = api.dismiss;
    root.triggerGodlyWaveLoader = api.show;
  }
  if (typeof define === 'function' && define.amd) {
    define([], function () { return api; });
  } else if (typeof module === 'object' && module.exports) {
    module.exports = api;
  }
})(typeof self !== 'undefined' ? self : (typeof window !== 'undefined' ? window : this), function () {
  'use strict';

  var activeTimeouts = [];
  var isPreviewActive = false;
  var isLoaderActive = false;
  var isNavigating = false;
  var currentCompletionCallback = null;

  // Zero-latency micro-haptic sound feedback
  function playAudioHaptic(freq1, freq2, duration, volume) {
    freq1 = typeof freq1 === 'number' ? freq1 : 160;
    freq2 = typeof freq2 === 'number' ? freq2 : 50;
    duration = typeof duration === 'number' ? duration : 0.025;
    volume = typeof volume === 'number' ? volume : 0.12;

    try {
      var AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      var ctx = new AudioCtx();
      var osc = ctx.createOscillator();
      var gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq1, ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(freq2, ctx.currentTime + duration);

      gain.gain.setValueAtTime(volume, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {
      // Audio autoplay policy catch
    }
  }

  function clearAllTimeouts() {
    for (var i = 0; i < activeTimeouts.length; i++) {
      clearTimeout(activeTimeouts[i]);
    }
    activeTimeouts = [];
  }

  function scheduleTimeout(fn, ms) {
    var t = setTimeout(fn, ms);
    activeTimeouts.push(t);
    return t;
  }

  /**
   * Helper: extract clean page label from URL for contextual phrase display
   */
  function getPageTitle(url) {
    if (!url) return 'Workspace';
    var clean = url.split('?')[0].split('#')[0].toLowerCase();
    if (clean.indexOf('alert') !== -1) return 'Low Stock Alerts & Breaches';
    if (clean.indexOf('inventory') !== -1) return 'Inventory Register & Stock';
    if (clean.indexOf('sale') !== -1) return 'Sales Ledger & Transactions';
    if (clean.indexOf('khata') !== -1) return 'Customer Register & Khata';
    if (clean.indexOf('customer') !== -1) return 'Customer Accounts';
    if (clean.indexOf('analytic') !== -1) return 'Analytics & SIH Intelligence';
    if (clean.indexOf('setting') !== -1) return 'Calacatta OS Settings';
    if (clean.indexOf('login') !== -1) return 'Authentication Gateway';
    if (clean.indexOf('index') !== -1) return 'VyaparAI Main Dashboard';
    return 'VyaparAI Terminal';
  }

  /**
   * Defensive injection: Ensures assets/godly-loader.css is attached
   */
  function ensureLoaderStyles() {
    if (typeof document === 'undefined') return;
    if (document.getElementById('godlyLoaderStyles')) return;
    var existing = document.querySelector('link[href*="godly-loader.css"]');
    if (!existing && document.head) {
      var link = document.createElement('link');
      link.id = 'godlyLoaderStyles';
      link.rel = 'stylesheet';
      link.href = 'assets/godly-loader.css';
      document.head.appendChild(link);
    }
  }

  /**
   * Invariant: Dynamically injects the full godlyLoaderScreen modal markup
   * into document.body if it doesn't exist, enabling ANY page to invoke VyaparLoader.
   */
  function ensureLoaderMarkup() {
    if (typeof document === 'undefined' || !document.body) return null;
    var existing = document.getElementById('godlyLoaderScreen');
    if (existing) return existing;

    var wrapper = document.createElement('div');
    wrapper.innerHTML = [
      '<div class="godly-loader-screen" id="godlyLoaderScreen" role="dialog" aria-modal="true" aria-label="VyaparAI Loading Screen">',
      '  <div class="godly-preview-controls-bar" id="godlyPreviewControls">',
      '    <button type="button" class="godly-preview-pill-btn" onclick="event.stopPropagation(); window.replayGodlyLoaderPreview();" title="Replay Wave Animation">',
      '      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">',
      '        <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>',
      '      </svg>',
      '      Replay Wave',
      '    </button>',
      '    <button type="button" class="godly-preview-pill-btn btn-dismiss" onclick="event.stopPropagation(); window.dismissGodlyLoaderPreview();" title="Dismiss Preview (Esc)">',
      '      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">',
      '        <line x1="18" y1="6" x2="6" y2="18"></line>',
      '        <line x1="6" y1="6" x2="18" y2="18"></line>',
      '      </svg>',
      '      Dismiss',
      '      <kbd class="godly-esc-badge">Esc</kbd>',
      '    </button>',
      '  </div>',
      '  <div class="skeleton-background-canvas" aria-hidden="true">',
      '    <div class="skel-dock">',
      '      <div class="skel-dock-icon logo-icon"></div>',
      '      <div class="skel-dock-divider"></div>',
      '      <div class="skel-dock-icon active"></div>',
      '      <div class="skel-dock-icon"></div>',
      '      <div class="skel-dock-icon"></div>',
      '      <div class="skel-dock-icon"></div>',
      '      <div class="skel-dock-icon"></div>',
      '    </div>',
      '    <div class="skel-main">',
      '      <div class="skel-header">',
      '        <div class="skel-header-left">',
      '          <div class="skel-brand-pill"></div>',
      '        </div>',
      '        <div class="skel-search-pill"></div>',
      '        <div class="skel-header-right">',
      '          <div class="skel-pill-btn"></div>',
      '        </div>',
      '      </div>',
      '      <div class="skel-row1">',
      '        <div class="skel-card">',
      '          <div class="skel-card-head">',
      '            <div class="skel-card-title"></div>',
      '            <div class="skel-card-badge"></div>',
      '          </div>',
      '          <div class="skel-metrics-trio">',
      '            <div class="skel-metric-box"><div class="skel-metric-label"></div><div class="skel-metric-val"></div></div>',
      '            <div class="skel-metric-box"><div class="skel-metric-label"></div><div class="skel-metric-val"></div></div>',
      '            <div class="skel-metric-box"><div class="skel-metric-label"></div><div class="skel-metric-val"></div></div>',
      '          </div>',
      '        </div>',
      '        <div class="skel-card skel-chart-card">',
      '          <div class="skel-card-head">',
      '            <div class="skel-card-title" style="width: 170px;"></div>',
      '            <div class="skel-card-badge" style="background: rgba(0, 113, 227, 0.2);"></div>',
      '          </div>',
      '          <div class="skel-chart-wave-wrap">',
      '            <svg viewBox="0 0 540 130" class="skel-chart-wave-svg" preserveAspectRatio="none">',
      '              <defs>',
      '                <linearGradient id="skelChartWaveFillDynamic" x1="0" y1="0" x2="0" y2="1">',
      '                  <stop offset="0%" stop-color="rgba(0, 113, 227, 0.45)" />',
      '                  <stop offset="50%" stop-color="rgba(201, 169, 110, 0.25)" />',
      '                  <stop offset="100%" stop-color="rgba(0, 113, 227, 0.0)" />',
      '                </linearGradient>',
      '                <linearGradient id="skelChartStrokeGradDynamic" x1="0" y1="0" x2="1" y2="0">',
      '                  <stop offset="0%" stop-color="rgba(0, 113, 227, 0.9)" />',
      '                  <stop offset="45%" stop-color="rgba(201, 169, 110, 0.95)" />',
      '                  <stop offset="100%" stop-color="rgba(0, 113, 227, 0.85)" />',
      '                </linearGradient>',
      '              </defs>',
      '              <line x1="0" y1="35" x2="540" y2="35" stroke="rgba(255, 255, 255, 0.18)" stroke-dasharray="4 4" />',
      '              <line x1="0" y1="75" x2="540" y2="75" stroke="rgba(255, 255, 255, 0.18)" stroke-dasharray="4 4" />',
      '              <line x1="0" y1="115" x2="540" y2="115" stroke="rgba(255, 255, 255, 0.18)" stroke-dasharray="4 4" />',
      '              <path d="M0,115 C60,110 110,65 170,80 C230,95 280,35 340,48 C400,60 450,22 540,25 L540,130 L0,130 Z" fill="url(#skelChartWaveFillDynamic)" />',
      '              <path d="M0,115 C60,110 110,65 170,80 C230,95 280,35 340,48 C400,60 450,22 540,25" fill="none" stroke="url(#skelChartStrokeGradDynamic)" stroke-width="3" stroke-linecap="round" />',
      '              <circle cx="170" cy="80" r="4.5" fill="#ffffff" stroke="rgba(0, 113, 227, 0.9)" stroke-width="2.5" />',
      '              <circle cx="340" cy="48" r="4.5" fill="#ffffff" stroke="rgba(201, 169, 110, 0.95)" stroke-width="2.5" />',
      '              <circle cx="500" cy="24" r="5" fill="#ffffff" stroke="rgba(0, 113, 227, 0.95)" stroke-width="2.5" />',
      '            </svg>',
      '          </div>',
      '        </div>',
      '      </div>',
      '      <div class="skel-row2">',
      '        <div class="skel-card">',
      '          <div class="skel-card-head"><div class="skel-card-title"></div><div class="skel-card-badge"></div></div>',
      '          <div class="skel-stock-rows">',
      '            <div class="skel-stock-item"><div class="skel-stock-text"></div><div class="skel-bar-track"><div class="skel-bar-fill" style="width: 82%;"></div></div></div>',
      '            <div class="skel-stock-item"><div class="skel-stock-text"></div><div class="skel-bar-track"><div class="skel-bar-fill coral" style="width: 26%;"></div></div></div>',
      '            <div class="skel-stock-item"><div class="skel-stock-text"></div><div class="skel-bar-track"><div class="skel-bar-fill" style="width: 48%;"></div></div></div>',
      '          </div>',
      '        </div>',
      '        <div class="skel-card">',
      '          <div class="skel-card-head"><div class="skel-card-title"></div><div class="skel-card-badge" style="background: rgba(255, 95, 87, 0.25);"></div></div>',
      '          <div class="skel-stock-rows">',
      '            <div class="skel-stock-item"><div class="skel-stock-text" style="width: 75%;"></div><div class="skel-bar-track"><div class="skel-bar-fill coral" style="width: 75%;"></div></div></div>',
      '            <div class="skel-stock-item"><div class="skel-stock-text" style="width: 60%;"></div><div class="skel-bar-track"><div class="skel-bar-fill" style="width: 60%;"></div></div></div>',
      '          </div>',
      '        </div>',
      '        <div class="skel-card">',
      '          <div class="skel-card-head"><div class="skel-card-title"></div><div class="skel-card-badge" style="background: rgba(37, 211, 102, 0.25);"></div></div>',
      '          <div class="skel-stock-rows">',
      '            <div class="skel-stock-item"><div class="skel-stock-text" style="width: 80%;"></div><div class="skel-bar-track"><div class="skel-bar-fill" style="width: 88%;"></div></div></div>',
      '            <div class="skel-stock-item"><div class="skel-stock-text" style="width: 55%;"></div><div class="skel-bar-track"><div class="skel-bar-fill" style="width: 40%;"></div></div></div>',
      '          </div>',
      '        </div>',
      '      </div>',
      '    </div>',
      '  </div>',
      '  <div class="logo-wave-stage">',
      '    <div class="wave-ambient-halo"></div>',
      '    <div class="wave-rings-container">',
      '      <div class="wave-ring wave-1"></div>',
      '      <div class="wave-ring wave-2"></div>',
      '      <div class="wave-ring wave-3"></div>',
      '      <div class="wave-ring wave-4"></div>',
      '    </div>',
      '    <div class="central-logo-card">',
      '      <img src="assets/logo.png" alt="VyaparAI V Logo" class="central-logo-img" onerror="this.onerror=null;this.src=\'data:image/svg+xml;utf8,<svg xmlns=\\\'http://www.w3.org/2000/svg\\\' width=\\\'104\\\' height=\\\'104\\\' viewBox=\\\'0 0 104 104\\\'><rect width=\\\'104\\\' height=\\\'104\\\' rx=\\\'26\\\' fill=\\\'%230f2e31\\\'/><path d=\\\'M26 26 L52 78 L78 26 L64 26 L52 54 L40 26 Z\\\' fill=\\\'%23c9a96e\\\'/></svg>\';" />',
      '    </div>',
      '    <div class="loader-status-block">',
      '      <div class="loader-brand-title">',
      '        VyaparAI Store Operating System',
      '        <span class="luxury-tag">Calacatta 2.4</span>',
      '      </div>',
      '      <div class="loader-dynamic-phrase" id="loaderDynamicPhrase">Verifying vendor terminal security token...</div>',
      '      <div class="loader-progress-track">',
      '        <div class="loader-progress-bar" id="loaderProgressBar"></div>',
      '      </div>',
      '    </div>',
      '  </div>',
      '</div>'
    ].join('\n');

    var loaderEl = wrapper.firstElementChild;
    document.body.appendChild(loaderEl);
    return loaderEl;
  }

  function updatePhrase(phraseEl, newText) {
    if (!phraseEl) return;
    phraseEl.classList.add('phrase-crossfade');
    setTimeout(function () {
      phraseEl.textContent = newText;
      phraseEl.classList.remove('phrase-crossfade');
    }, 100);
  }

  /**
   * Main Programmatic Wave Loader Trigger
   */
  function showWaveLoader(options, legacyPhrase) {
    if (typeof options === 'number') {
      options = {
        duration: options,
        successPhrase: legacyPhrase || null,
        isPreview: false
      };
    } else {
      options = options || {};
    }

    ensureLoaderStyles();
    var loader = ensureLoaderMarkup();
    if (!loader) return { cancel: function () {}, element: null };

    var progress = document.getElementById('loaderProgressBar');
    var phrase = document.getElementById('loaderDynamicPhrase');

    clearAllTimeouts();
    isLoaderActive = true;
    isPreviewActive = Boolean(options.isPreview);
    currentCompletionCallback = options.onComplete || null;

    if (progress) progress.style.width = '0%';
    loader.classList.remove('preview-mode', 'controls-visible');

    if (isPreviewActive || options.showControls) {
      loader.classList.add('preview-mode', 'controls-visible');
    }

    loader.classList.add('active');
    playAudioHaptic(180, 70, 0.03, 0.14);

    var defaultSteps = [
      { pct: 20, text: "Verifying Kirana Vendor Security Token (DEMO_KIRANA_KOP)...", delay: 280 },
      { pct: 45, text: "Connecting to Cloud Supabase & Kolhapur Kirana Catalog...", delay: 680 },
      { pct: 70, text: "Engaging 60 FPS Apple Blue & Florentine Gold Wave Engine...", delay: 1100 },
      { pct: 90, text: "Synchronizing WhatsApp Voice & 30-min Auto-Undo Ledger...", delay: 1500 },
      { pct: 100, text: options.successPhrase || "Calacatta OS Ready • Store Ingress Authenticated", delay: 1850 }
    ];

    var steps = (options.steps && options.steps.length > 0) ? options.steps : defaultSteps;

    steps.forEach(function (step) {
      scheduleTimeout(function () {
        if (!isLoaderActive) return;

        if (progress) progress.style.width = step.pct + '%';
        if (phrase && step.text) updatePhrase(phrase, step.text);
        playAudioHaptic(120 + (step.pct * 2), 40 + (step.pct * 1.5), 0.02, 0.08);

        if (step.pct >= 100) {
          scheduleTimeout(function () {
            if (!isLoaderActive) return;

            if (typeof currentCompletionCallback === 'function') {
              try {
                currentCompletionCallback();
              } catch (err) {
                console.error('[VyaparLoader] onComplete error:', err);
              }
            }

            if (options.redirect) {
              window.location.href = options.redirect;
            } else if (!isPreviewActive) {
              scheduleTimeout(function () {
                hideWaveLoader();
              }, 400);
            }
          }, 300);
        }
      }, step.delay);
    });

    return {
      cancel: hideWaveLoader,
      element: loader
    };
  }

  /**
   * Hide the Godly Wave Loader with a sleek fade-out
   */
  function hideWaveLoader() {
    clearAllTimeouts();
    isLoaderActive = false;
    isPreviewActive = false;
    isNavigating = false;
    currentCompletionCallback = null;

    var loader = document.getElementById('godlyLoaderScreen');
    if (loader) {
      loader.classList.remove('active', 'preview-mode', 'controls-visible');
    }

    playAudioHaptic(100, 30, 0.02, 0.06);

    setTimeout(function () {
      var progress = document.getElementById('loaderProgressBar');
      var phrase = document.getElementById('loaderDynamicPhrase');
      if (progress) progress.style.width = '0%';
      if (phrase) phrase.textContent = 'Verifying vendor terminal security token...';
    }, 420);
  }

  /**
   * Programmatic Smooth Page Navigation with Wave Transition
   * Shows the wave animation for ~450ms then switches to target URL
   */
  function navigateToUrl(url, customPhrase) {
    if (!url) return;
    if (isNavigating) return;
    isNavigating = true;

    // Safety timeout in case navigation is prevented
    scheduleTimeout(function () {
      isNavigating = false;
    }, 3000);

    ensureLoaderStyles();
    var loader = ensureLoaderMarkup();
    if (!loader) {
      window.location.href = url;
      return;
    }

    clearAllTimeouts();
    isLoaderActive = true;
    isPreviewActive = false;

    var progress = document.getElementById('loaderProgressBar');
    var phrase = document.getElementById('loaderDynamicPhrase');

    if (progress) progress.style.width = '0%';
    loader.classList.remove('preview-mode', 'controls-visible');

    var pageLabel = getPageTitle(url);
    var phraseText = customPhrase || ('Opening ' + pageLabel + ' • Calacatta OS');

    if (phrase) phrase.textContent = phraseText;
    loader.classList.add('active');
    playAudioHaptic(190, 75, 0.025, 0.14);

    // Fast surge progress animation
    scheduleTimeout(function () {
      if (progress) progress.style.width = '55%';
      playAudioHaptic(240, 90, 0.02, 0.09);
    }, 140);

    scheduleTimeout(function () {
      if (progress) progress.style.width = '100%';
      playAudioHaptic(280, 110, 0.025, 0.11);
    }, 320);

    scheduleTimeout(function () {
      window.location.href = url;
    }, 450);
  }

  /**
   * Automatic Snappy Wave Ingress on Initial Page Load / Refresh
   * Plays for ~750ms with concentric ripples and smoothly fades out to reveal content.
   */
  function onInitialPageLoad() {
    ensureLoaderStyles();
    var loader = ensureLoaderMarkup();
    if (!loader) return;

    // If already in preview or mid-navigation, do not override
    if (isPreviewActive || isNavigating) return;

    var progress = document.getElementById('loaderProgressBar');
    var phrase = document.getElementById('loaderDynamicPhrase');

    clearAllTimeouts();
    isLoaderActive = true;
    isPreviewActive = false;

    if (progress) progress.style.width = '0%';
    loader.classList.remove('preview-mode', 'controls-visible');
    loader.classList.add('active');

    var isFreshLogin = false;
    try {
      if (sessionStorage.getItem('just_logged_in') === 'true') {
        isFreshLogin = true;
        sessionStorage.removeItem('just_logged_in');
      }
    } catch (e) {}

    var initialText = isFreshLogin
      ? "Welcome to VyaparAI Kirana Enterprise..."
      : "VyaparAI Calacatta OS • Synchronizing Terminal...";
    var finalText = isFreshLogin
      ? "Store Ingress Authenticated • Calacatta Ready"
      : "Calacatta OS Ready • Store Ingress Authenticated";

    if (phrase) phrase.textContent = initialText;
    playAudioHaptic(170, 70, 0.025, 0.11);

    // Timeline for ~750ms snappy delight:
    scheduleTimeout(function () {
      if (!isLoaderActive) return;
      if (progress) progress.style.width = '35%';
      playAudioHaptic(200, 80, 0.02, 0.07);
    }, 180);

    scheduleTimeout(function () {
      if (!isLoaderActive) return;
      if (progress) progress.style.width = '75%';
      if (phrase) updatePhrase(phrase, finalText);
      playAudioHaptic(240, 95, 0.02, 0.08);
    }, 420);

    scheduleTimeout(function () {
      if (!isLoaderActive) return;
      if (progress) progress.style.width = '100%';
    }, 600);

    scheduleTimeout(function () {
      if (!isLoaderActive) return;
      hideWaveLoader();
    }, 750);
  }

  /**
   * Interactive Full-Length Preview Mode (for manual testing via console / shortcut)
   */
  function previewLoader() {
    return showWaveLoader({
      isPreview: true,
      showControls: true,
      successPhrase: "Calacatta OS 2.4 Active • Store Ingress Ready (Esc to Dismiss)",
      steps: [
        { pct: 22, text: "Verifying Kirana Vendor Security Token (DEMO_KIRANA_KOP)...", delay: 280 },
        { pct: 50, text: "Connecting to Cloud Supabase & Kolhapur Kirana Catalog...", delay: 720 },
        { pct: 75, text: "Engaging 60 FPS Apple Blue & Florentine Gold Wave Engine...", delay: 1180 },
        { pct: 92, text: "Synchronizing WhatsApp Voice & 30-min Auto-Undo Engine...", delay: 1600 },
        { pct: 100, text: "Calacatta OS 2.4 Active • Store Ingress Ready (Esc to Dismiss)", delay: 2000 }
      ]
    });
  }

  function replayPreview() {
    playAudioHaptic(220, 80, 0.04, 0.16);
    previewLoader();
  }

  /**
   * Global Click Interceptor: Intercepts clicks on dock buttons (.dock-btn),
   * dock logo, and internal navigation links (a[href$='.html']) to play the wave transition.
   */
  function handleGlobalNavClick(e) {
    // Primary left-click only, ignore modified clicks (Ctrl, Cmd, Shift, Alt)
    if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

    var el = e.target.closest('.dock-btn, .dock-brand-logo, a[href$=".html"], a[href*=".html"], [data-nav-href]');
    if (!el) return;

    // Do not intercept preview controls or dismiss buttons
    if (el.classList.contains('godly-preview-pill-btn') || el.closest('.godly-preview-controls-bar')) {
      return;
    }

    var onclickAttr = el.getAttribute('onclick') || '';

    // Ignore interactive non-page modal triggers (such as WhatsApp Drawer toggle)
    if (onclickAttr.indexOf('toggleWhatsAppDrawer') !== -1 ||
        onclickAttr.indexOf('openVideoSweepModal') !== -1 ||
        onclickAttr.indexOf('previewGodlyLoader') !== -1 ||
        onclickAttr.indexOf('replayGodlyLoader') !== -1 ||
        onclickAttr.indexOf('dismissGodlyLoader') !== -1) {
      return;
    }

    var targetUrl = null;

    // 1. Direct Anchor tag check
    if (el.tagName === 'A') {
      var href = el.getAttribute('href');
      if (href && !href.startsWith('#') && !href.startsWith('javascript:') &&
          !href.startsWith('http://') && !href.startsWith('https://')) {
        targetUrl = href;
      }
    }

    // 2. data-nav-href attribute check
    if (!targetUrl && el.getAttribute('data-nav-href')) {
      targetUrl = el.getAttribute('data-nav-href');
    }

    // 3. Inline onclick location assignment extraction
    if (!targetUrl && onclickAttr) {
      var match = onclickAttr.match(/(?:window\.)?location(?:\.href)?\s*=\s*['"]([^'"]+)['"]/);
      if (match && match[1]) {
        targetUrl = match[1];
      }
    }

    if (targetUrl) {
      // If this is a logout action, clear the session storage tokens
      if (onclickAttr.indexOf('removeItem') !== -1 || targetUrl.indexOf('login.html') !== -1) {
        try {
          localStorage.removeItem('vyaparai_auth_user');
          localStorage.removeItem('vyaparai_auth_token');
          sessionStorage.removeItem('just_logged_in');
        } catch (err) {}
      }

      e.preventDefault();
      e.stopPropagation();
      if (typeof e.stopImmediatePropagation === 'function') {
        e.stopImmediatePropagation();
      }

      navigateToUrl(targetUrl);
    }
  }

  function setupGlobalListeners() {
    // 1. Escape key dismissal listener
    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' || e.keyCode === 27) {
        var loader = document.getElementById('godlyLoaderScreen');
        if (loader && loader.classList.contains('active')) {
          hideWaveLoader();
        }
      }
    });

    // 2. Back/Forward Cache listener (prevents loader from being stuck when navigating back)
    window.addEventListener('pageshow', function (e) {
      if (e.persisted) {
        hideWaveLoader();
      }
    });

    // 3. Global Click Interceptor for seamless transitions (using Capture phase for priority)
    document.addEventListener('click', handleGlobalNavClick, true);
  }

  // Auto-init on page load
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        setupGlobalListeners();
        onInitialPageLoad();
      });
    } else {
      setupGlobalListeners();
      onInitialPageLoad();
    }
  }

  var api = {
    show: showWaveLoader,
    hide: hideWaveLoader,
    dismiss: hideWaveLoader,
    navigate: navigateToUrl,
    preview: previewLoader,
    replay: replayPreview,
    playHaptic: playAudioHaptic,
    ensureMarkup: ensureLoaderMarkup,
    ensureStyles: ensureLoaderStyles
  };

  return api;
});

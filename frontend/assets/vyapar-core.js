// =============================================================================
// VyaparAI Core Client-Side Reactive Store & Backend Integration Engine
// Manages:
// 1. 14 Authentic Kolhapur Kirana SKUs with High-Res Packshots
// 2. Sub-1ms Voice-to-Scale Loose Commodity Reverse-Math Engine
// 3. Remote Customer Yaadi (कच्ची पर्ची) Staging & Zero Direct Deduction Invariant
// 4. Live Backend API & WebSocket Wiring (FastAPI / Render / Localhost:8000)
// =============================================================================

const VyaparCore = (function() {
  'use strict';

  // Master 14-SKU Kolhapur Kirana Catalog
  const DEFAULT_SKUS = [
    {
      sku: "FMCG-PARLE-100G",
      name_mr: "पार्ले-जी बिस्कीट १०० ग्रॅम",
      name_en: "Parle-G 100g Glucose Biscuits",
      short_name: "Parle-G",
      category: "Packaged FMCG & Biscuits",
      stock: 60.0,
      unit: "packet",
      unit_price: 10.0,
      cost_price: 8.20,
      min_threshold: 15.0,
      img: "assets/products/parle_g.png",
      pedestal: "pedestal-peach",
      aliases: ["parle", "parle-g", "biscuit", "पार्ले", "बिस्कीट"]
    },
    {
      sku: "GROC-SUG-001",
      name_mr: "मधुर शुद्ध साखर (Loose/Pack)",
      name_en: "Madhur Pure Crystal Sugar",
      short_name: "Madhur Sugar",
      category: "Grains & Sweeteners",
      stock: 50.0,
      unit: "kg",
      unit_price: 42.0,
      cost_price: 36.50,
      min_threshold: 10.0,
      img: "assets/products/sugar.png",
      pedestal: "pedestal-blue",
      aliases: ["sakhar", "sugar", "साखर", "shakkar", "मधुर साखर"]
    },
    {
      sku: "OIL-FORT-1L",
      name_mr: "फॉर्च्युन सनलाइट तेल १ लिटर",
      name_en: "Fortune Sunlite Sunflower Oil 1L",
      short_name: "Fortune Oil 1L",
      category: "Edible Oils",
      stock: 25.0,
      unit: "pouch",
      unit_price: 135.0,
      cost_price: 122.00,
      min_threshold: 5.0,
      img: "assets/products/fortune_oil.png",
      pedestal: "pedestal-green",
      aliases: ["tel", "oil", "fortune", "तेल", "फॉर्च्युन"]
    },
    {
      sku: "BAK-PAV-LADI",
      name_mr: "ताजा बेकरी लादी पाव (६ बन्स)",
      name_en: "Fresh Bakery Ladi Pav (6 Buns)",
      short_name: "Bakery Pav",
      category: "Bakery & Fresh",
      stock: 30.0,
      unit: "ladi",
      unit_price: 20.0,
      cost_price: 14.00,
      min_threshold: 8.0,
      img: "assets/products/bakery_pav.png",
      pedestal: "pedestal-rose",
      aliases: ["pav", "ladi pav", "पाव", "लादी पाव", "ब्रेड"]
    },
    {
      sku: "DAL-TUR-001",
      name_mr: "गावरान पॉलिश तूर डाळ",
      name_en: "Tur Dal Unpolished 1kg",
      short_name: "Tur Dal",
      category: "Pulses & Lentils",
      stock: 40.0,
      unit: "kg",
      unit_price: 155.0,
      cost_price: 136.00,
      min_threshold: 10.0,
      img: "assets/products/tur_dal.png",
      pedestal: "pedestal-azure",
      aliases: ["dal", "tur dal", "डाळ", "तूर डाळ", "तूरडाळ"]
    },
    {
      sku: "GROC-SALT-1K",
      name_mr: "टाटा व्हॅक्यूम शुद्ध मीठ",
      name_en: "Tata Salt Vacuum Evaporated 1kg",
      short_name: "Tata Salt",
      category: "Spices & Essentials",
      stock: 45.0,
      unit: "packet",
      unit_price: 28.0,
      cost_price: 22.50,
      min_threshold: 10.0,
      img: "assets/products/tata_salt.png",
      pedestal: "pedestal-blue",
      aliases: ["mith", "meeth", "salt", "मीठ", "टाटा मीठ"]
    },
    {
      sku: "GROC-ATTA-5K",
      name_mr: "आशीर्वाद शुद्ध चक्की आटा ५ किलो",
      name_en: "Aashirvaad Shudh Chakki Atta 5kg",
      short_name: "Aashirvaad Atta",
      category: "Grains & Sweeteners",
      stock: 18.0,
      unit: "bag",
      unit_price: 220.0,
      cost_price: 195.00,
      min_threshold: 5.0,
      img: "assets/products/atta.png",
      pedestal: "pedestal-peach",
      aliases: ["atta", "aata", "aashirvaad", "आटा", "पीठ", "आशीर्वाद"]
    },
    {
      sku: "FMCG-MAGGI-70G",
      name_mr: "मॅगी २-मिनिट मसाला नूडल्स",
      name_en: "Nestle Maggi 2-Minute Noodles 70g",
      short_name: "Maggi Noodles",
      category: "Packaged FMCG & Biscuits",
      stock: 50.0,
      unit: "packet",
      unit_price: 14.0,
      cost_price: 11.80,
      min_threshold: 12.0,
      img: "assets/products/maggi.png",
      pedestal: "pedestal-green",
      aliases: ["maggi", "noodles", "मॅगी", "मॅगी नूडल्स"]
    },
    {
      sku: "VEG-KANDA-001",
      name_mr: "नाशिक गावठी लाल कांदा",
      name_en: "Nashik Fresh Red Onion 1kg",
      short_name: "Red Onion (कांदा)",
      category: "Fresh Produce",
      stock: 70.0,
      unit: "kg",
      unit_price: 35.0,
      cost_price: 26.00,
      min_threshold: 15.0,
      img: "assets/products/onion.png",
      pedestal: "pedestal-rose",
      aliases: ["kanda", "onion", "कांदा", "कांदे"]
    },
    {
      sku: "VEG-BATATA-001",
      name_mr: "इंदूर ताजा बटाटा",
      name_en: "Fresh Potato 1kg",
      short_name: "Fresh Potato (बटाटा)",
      category: "Fresh Produce",
      stock: 65.0,
      unit: "kg",
      unit_price: 30.0,
      cost_price: 22.00,
      min_threshold: 15.0,
      img: "assets/products/potato.png",
      pedestal: "pedestal-azure",
      aliases: ["batata", "potato", "बटाटा", "बटाटे", "आलू"]
    },
    {
      sku: "DAIRY-AMUL-500M",
      name_mr: "अमुल ताजा दूध ५०० मिली",
      name_en: "Amul Taaza Milk 500ml",
      short_name: "Amul Milk 500ml",
      category: "Dairy & Perishables",
      stock: 24.0,
      unit: "pouch",
      unit_price: 27.0,
      cost_price: 24.50,
      min_threshold: 6.0,
      img: "assets/products/amul_milk.jpg",
      pedestal: "pedestal-blue",
      aliases: ["dudh", "milk", "amul", "दूध", "अमुल दूध"]
    },
    {
      sku: "AUTO-VID-PEN",
      name_mr: "रेनॉल्ड्स ०४५ बॉल पेन (निळा)",
      name_en: "Reynolds 045 Ballpoint Pen Blue",
      short_name: "Reynolds Pen",
      category: "Stationery & Essentials",
      stock: 50.0,
      unit: "piece",
      unit_price: 10.0,
      cost_price: 6.80,
      min_threshold: 10.0,
      img: "assets/products/reynolds_pen.jpg",
      pedestal: "pedestal-azure",
      aliases: ["pen", "reynolds", "पेन", "बॉलपेन"]
    },
    {
      sku: "AUTO-VID-NOTEBOOK",
      name_mr: "क्लासमेट वही १७२ पाने",
      name_en: "Classmate Notebook 172 Pages",
      short_name: "Classmate Notebook",
      category: "Stationery & Essentials",
      stock: 30.0,
      unit: "piece",
      unit_price: 45.0,
      cost_price: 32.00,
      min_threshold: 8.0,
      img: "assets/products/classmate_notebook.jpg",
      pedestal: "pedestal-peach",
      aliases: ["vahi", "notebook", "classmate", "वही", "नोटबुक"]
    },
    {
      sku: "AUTO-VID-KINLEY",
      name_mr: "किनले पिण्याचे पाणी १ लिटर",
      name_en: "Kinley Packaged Water 1L",
      short_name: "Kinley Water 1L",
      category: "Packaged FMCG & Biscuits",
      stock: 24.0,
      unit: "bottle",
      unit_price: 20.0,
      cost_price: 13.00,
      min_threshold: 6.0,
      img: "assets/products/kinley_water.jpg",
      pedestal: "pedestal-green",
      aliases: ["pani", "water", "kinley", "पाणी", "किनले"]
    }
  ];

  // Customers & Digital Khata
  const DEFAULT_CUSTOMERS = [
    { id: "c1", name: "शंकरराव पाटील (Shankar Patil)", area: "Rajarampuri 3rd Lane", phone: "+91 98220 19283", udhar: 840.0, status: "DUE_SOON", last_tx: "Yesterday (साखर व तेल)", trust: "A+", orders: 24, pref: "Voice Notes & Madhur Sugar" },
    { id: "c2", name: "सौ. सुवर्णा पाटील (Suvarna Patil)", area: "Rajarampuri 5th Lane", phone: "+91 98223 44102", udhar: 289.0, status: "PENDING_ORDER", last_tx: "4 mins ago (यादी स्लिप)", trust: "A", orders: 19, pref: "Handwritten Paper Yaadi" },
    { id: "c3", name: "बाबुराव कांबळे (Baburao Kamble)", area: "Shahupuri Market Yard", phone: "+91 94220 88291", udhar: 1250.0, status: "OVERDUE", last_tx: "3 days ago (आटा व डाळ)", trust: "B", orders: 31, pref: "Counter Walk-in / Udhar" },
    { id: "c4", name: "आनंद पोवार (Anand Powar)", area: "Mangalwar Peth", phone: "+91 97631 22894", udhar: 0.0, status: "SETTLED", last_tx: "Today 10:14 AM (UPI ₹350)", trust: "A+", orders: 42, pref: "Instant UPI Soundbox" },
    { id: "c5", name: "हरी मोहिते (Hari Mohite)", area: "Laxmipuri Chowk", phone: "+91 98901 77321", udhar: 420.0, status: "DUE_SOON", last_tx: "Today 9:30 AM (मॅगी व पाव)", trust: "A", orders: 15, pref: "Daily Fresh Pav & Snacks" }
  ];

  // Initial Transactions
  const DEFAULT_TRANSACTIONS = [
    { id: "TX-1085", time: "Just now", type: "SALE", mode: "WhatsApp Voice", cust: "सौ. सुवर्णा पाटील", items: "2kg साखर + 1L तेल + 2 पाव", amount: 259.0, status: "Success" },
    { id: "TX-1084", time: "12 mins ago", type: "SALE", mode: "UPI Soundbox", cust: "आनंद पोवार", items: "आशीर्वाद आटा 5kg + मीठ", amount: 268.0, status: "Success" },
    { id: "TX-1083", time: "25 mins ago", type: "SALE", mode: "Cash Counter", cust: "हरी मोहिते", items: "5x पार्ले-जी + 2x मॅगी", amount: 78.0, status: "Success" },
    { id: "TX-1082", time: "45 mins ago", type: "UDHAR", mode: "WhatsApp Yaadi", cust: "शंकरराव पाटील", items: "गावरान तूर डाळ 2kg + कांदा 3kg", amount: 425.0, status: "Credit Added" },
    { id: "TX-1081", time: "1.5 hrs ago", type: "SALE", mode: "UPI Soundbox", cust: "विजय शिंदे", items: "फॉर्च्युन तेल 2L + बटाटा 2kg", amount: 330.0, status: "Success" }
  ];

  // Initial Pending Customer Yaadi Orders (Zero Direct Deduction Queue)
  const DEFAULT_PENDING_ORDERS = [
    {
      order_id: "ORD-KOP-9102",
      customer_name: "सौ. सुवर्णा पाटील",
      customer_phone: "+91 98223 44102",
      area: "Rajarampuri 5th Lane",
      time: "3 mins ago",
      slip_type: "Handwritten Paper Chit (कच्ची पर्ची)",
      items_text: "साखर २ किलो, पार्ले-जी ३ पुडे, फॉर्च्युन तेल १ लिटर, लादी पाव २",
      items: [
        { sku: "GROC-SUG-001", name: "साखर", qty: 2.0, unit: "kg", price: 42.0 },
        { sku: "FMCG-PARLE-100G", name: "पार्ले-जी", qty: 3.0, unit: "packet", price: 10.0 },
        { sku: "OIL-FORT-1L", name: "फॉर्च्युन तेल", qty: 1.0, unit: "pouch", price: 135.0 },
        { sku: "BAK-PAV-LADI", name: "लादी पाव", qty: 2.0, unit: "ladi", price: 20.0 }
      ],
      total_amount: 289.0,
      status: "PENDING"
    }
  ];

  // Storage Keys
  const KEY_SKUS = "vyapar_inventory_skus_v3";
  const KEY_CUSTOMERS = "vyapar_customers";
  const KEY_UDHAR = "vyapar_udhar_ledger";
  const KEY_TX = "vyapar_transactions";
  const KEY_ORDERS = "vyapar_pending_orders";
  const KEY_STORE = "vyapar_active_dukaan";

  function load(key, defaultData) {
    try {
      if (typeof localStorage === 'undefined') return defaultData;
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : defaultData;
    } catch (e) {
      console.warn("VyaparCore read error", e);
      return defaultData;
    }
  }

  function save(key, data) {
    try {
      if (typeof localStorage === 'undefined') return;
      localStorage.setItem(key, JSON.stringify(data));
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent("vyapar_state_change", { detail: { key, data } }));
      }
    } catch (e) {
      console.warn("VyaparCore write error", e);
    }
  }

  // Active State
  let skus = load(KEY_SKUS, DEFAULT_SKUS);
  let customers = load(KEY_CUSTOMERS, DEFAULT_CUSTOMERS);
  let udharLedger = load(KEY_UDHAR, []);
  let transactions = load(KEY_TX, DEFAULT_TRANSACTIONS);
  let pendingOrders = load(KEY_ORDERS, DEFAULT_PENDING_ORDERS);
  let activeDukaan = (typeof localStorage !== 'undefined' ? localStorage.getItem(KEY_STORE) : null) || "अथर्व किराणा स्टोअर्स, कोल्हापूर (DEMO_KIRANA_KOP)";

  // Backend URL configuration with Automatic Health Probe Fallback
  const RENDER_PROD_URL = "https://vyaparai-oddf.onrender.com";
  let resolvedBackendUrl = null;

  function getBackendUrl() {
    if (resolvedBackendUrl) return resolvedBackendUrl;
    if (typeof window !== 'undefined' && window.location) {
      const origin = window.location.origin || "";
      const host = window.location.host || "";
      const protocol = window.location.protocol || "";
      if (host.includes("render.com") || host.includes(":8000")) {
        return (resolvedBackendUrl = origin);
      }
      const customUrl = (typeof localStorage !== 'undefined') ? localStorage.getItem("VYAPAR_BACKEND_URL") : null;
      if (customUrl) return (resolvedBackendUrl = customUrl);
      if (protocol === "file:" || origin === "null") {
        // Default to localhost, but probe will switch to Render if offline
        return resolvedBackendUrl || "http://localhost:8000";
      }
      return origin || "http://localhost:8000";
    }
    return "http://localhost:8000";
  }

  async function probeBackendUrl() {
    if (resolvedBackendUrl && !resolvedBackendUrl.includes("localhost")) return resolvedBackendUrl;
    if (typeof window !== 'undefined' && window.location && window.location.host.includes("render.com")) {
      return (resolvedBackendUrl = window.location.origin);
    }
    try {
      const ctrl = new AbortController();
      const tid = setTimeout(() => ctrl.abort(), 650);
      const res = await fetch("http://localhost:8000/health", { signal: ctrl.signal });
      clearTimeout(tid);
      if (res.ok) {
        resolvedBackendUrl = "http://localhost:8000";
        return resolvedBackendUrl;
      }
    } catch (e) {}
    resolvedBackendUrl = RENDER_PROD_URL;
    console.log("[VyaparCore] Localhost offline. Auto-routed to cloud backend:", RENDER_PROD_URL);
    return resolvedBackendUrl;
  }

  function getWebSocketUrl() {
    const base = getBackendUrl();
    const isHttps = base.startsWith("https");
    const wsProto = isHttps ? "wss:" : "ws:";
    const cleanHost = base.replace(/^https?:\/\//, "").replace(/\/$/, "");
    return `${wsProto}//${cleanHost}/ws/inventory`;
  }

  // Live Reactive WebSocket & Adaptive Polling Sync Engine
  let activeWebSocket = null;
  let heartbeatTimer = null;
  let pollIntervalId = null;
  let syncListeners = [];
  let lastSyncMetrics = null;
  let isSyncInProgress = false;
  let reconnectAttempts = 0;

  function registerSyncListener(cb) {
    if (typeof cb === 'function') syncListeners.push(cb);
  }

  function notifySyncListeners(type, data) {
    syncListeners.forEach(fn => {
      try { fn(type, data); } catch (e) { console.error("Sync listener error", e); }
    });
  }

  async function performLiveSync() {
    if (isSyncInProgress) return;
    isSyncInProgress = true;
    try {
      await probeBackendUrl();
      const ctrl = new AbortController();
      const tid = setTimeout(() => ctrl.abort(), 4000);
      const res = await fetch(`${getBackendUrl()}/api/metrics`, { signal: ctrl.signal, cache: 'no-store' });
      clearTimeout(tid);

      if (res.ok) {
        const data = await res.json();
        if (data.products && data.products.length > 0) {
          let hasChanged = false;
          data.products.forEach(bp => {
            const local = skus.find(s => s.sku === bp.sku);
            if (local) {
              if (local.stock !== bp.stock || local.unit_price !== bp.unit_price) {
                hasChanged = true;
                local.stock = bp.stock;
                local.unit_price = bp.unit_price;
              }
            } else {
              skus.push({
                sku: bp.sku,
                name_mr: bp.name_mr,
                name_en: bp.name_en,
                short_name: bp.name_en || bp.name_mr,
                category: bp.category,
                stock: bp.stock,
                unit: bp.unit,
                unit_price: bp.unit_price,
                cost_price: Math.round(bp.unit_price * 0.82),
                min_threshold: bp.min_threshold || 5,
                img: bp.img || "assets/products/parle_g.png",
                pedestal: "pedestal-blue",
                aliases: bp.aliases || []
              });
              hasChanged = true;
            }
          });
          if (hasChanged) {
            save(KEY_SKUS, skus);
          }
        }
        if (data.recent_transactions && Array.isArray(data.recent_transactions) && data.recent_transactions.length > 0) {
          const mappedTx = data.recent_transactions.map(t => ({
            id: t.id ? (typeof t.id === 'string' && t.id.startsWith('TX-') ? t.id : `TX-${t.id}`) : `TX-${Math.floor(1000 + Math.random()*9000)}`,
            time: t.time || (t.created_at ? new Date(t.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Just now"),
            type: t.type || "SALE",
            mode: t.raw_message && t.raw_message.toLowerCase().includes("voice") ? "WhatsApp Voice" : (t.type === "UDHAR" ? "WhatsApp Yaadi" : (t.type === "SALE" ? "Cash Counter" : "UPI QR")),
            cust: t.cust || (t.type === "UDHAR" ? "शंकरराव पाटील" : "Counter Customer"),
            items: t.item_name || t.raw_message || "Kirana Items",
            amount: parseFloat(t.amount || 0),
            status: t.is_reversed ? "Reversed" : "Success"
          }));
          if (mappedTx.length > 0) {
            transactions = mappedTx;
            save(KEY_TX, transactions);
            notifySyncListeners("TRANSACTIONS_UPDATED", transactions);
          }
        }
        if (data.udhar_ledger && Array.isArray(data.udhar_ledger)) {
          udharLedger = data.udhar_ledger;
          save(KEY_UDHAR, udharLedger);
          notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
        }
        lastSyncMetrics = data;
        notifySyncListeners("METRICS_UPDATE", data);

        // Background sync pending customer yaadi orders from backend
        try {
          const ordRes = await fetch(`${getBackendUrl()}/api/orders/pending`);
          if (ordRes.ok) {
            const ordData = await ordRes.json();
            if (ordData && Array.isArray(ordData.orders)) {
              pendingOrders = ordData.orders.map(o => ({
                order_id: o.order_id,
                id: o.order_id,
                customer_name: o.customer_name || o.customerName || "व्यंकटेश पै (Venkatesh Pai)",
                customerName: o.customer_name || o.customerName || "व्यंकटेश पै (Venkatesh Pai)",
                customer_phone: o.customer_phone || o.phone || "+91 70192 59321",
                phone: o.customer_phone || o.phone || "+91 70192 59321",
                area: "Kolhapur Walk-in",
                time: o.timestamp || (o.created_at ? new Date(o.created_at).toLocaleTimeString() : "Just now"),
                timestamp: o.timestamp || (o.created_at ? new Date(o.created_at).toLocaleTimeString() : "Just now"),
                slip_type: "WhatsApp Yaadi Slip",
                items_text: o.raw_message || o.rawText || "किराणा यादी",
                rawText: o.raw_message || o.rawText || "किराणा यादी",
                items: Array.isArray(o.items) ? o.items.map(it => ({
                  name: it.name_mr || it.name_raw || it.name || "किराणा सामान",
                  qty: it.quantity || it.qty || 1,
                  unit: it.unit || "piece",
                  price: it.unit_price || it.price || 0,
                  total: it.line_total || it.total || 0,
                  sku: it.sku_matched || it.sku || ""
                })) : [],
                total_amount: parseFloat(o.total_amount || o.totalEstimated || 0),
                totalEstimated: parseFloat(o.total_amount || o.totalEstimated || 0),
                status: o.status || "PENDING"
              }));
              save(KEY_ORDERS, pendingOrders);
              notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
            }
          }
        } catch (ordErr) {}

        return data;
      }
    } catch (e) {
      // Offline fallback silent
    } finally {
      isSyncInProgress = false;
    }
    return null;
  }

  function startAdaptivePolling() {
    if (!pollIntervalId) {
      console.log("[VyaparCore] WS disconnected. Activating 3s adaptive fallback polling.");
      pollIntervalId = setInterval(performLiveSync, 3000);
    }
  }

  function stopAdaptivePolling() {
    if (pollIntervalId) {
      console.log("[VyaparCore] WS active. Pausing high-frequency polling to preserve network and UI state.");
      clearInterval(pollIntervalId);
      pollIntervalId = null;
    }
  }

  function startLiveSync(callback) {
    if (callback) registerSyncListener(callback);

    // Initial immediate sync
    performLiveSync();

    function connectWS() {
      if (activeWebSocket && (activeWebSocket.readyState === WebSocket.OPEN || activeWebSocket.readyState === WebSocket.CONNECTING)) {
        return;
      }

      try {
        const wsUrl = getWebSocketUrl();
        activeWebSocket = new WebSocket(wsUrl);

        activeWebSocket.onopen = function() {
          console.log("[VyaparCore WS] Connected to live inventory stream at", wsUrl);
          reconnectAttempts = 0;
          stopAdaptivePolling();
          notifySyncListeners("WS_STATUS", { connected: true, url: wsUrl });

          // Start 25-second heartbeat ping to prevent cloud proxy disconnects
          if (heartbeatTimer) clearInterval(heartbeatTimer);
          heartbeatTimer = setInterval(() => {
            if (activeWebSocket && activeWebSocket.readyState === WebSocket.OPEN) {
              try { activeWebSocket.send("ping"); } catch (e) {}
            }
          }, 25000);
        };

        activeWebSocket.onmessage = function(event) {
          // Heartbeat pong string check (avoids JSON.parse crash)
          if (event.data === "pong" || event.data === "ping") {
            return;
          }

          try {
            const msg = JSON.parse(event.data);
            if (msg.type === "METRICS_UPDATE" && msg.metrics) {
              if (msg.metrics.products) {
                msg.metrics.products.forEach(bp => {
                  const local = skus.find(s => s.sku === bp.sku);
                  if (local) {
                    local.stock = bp.stock;
                    local.unit_price = bp.unit_price;
                  }
                });
                save(KEY_SKUS, skus);
              }
              if (msg.metrics.udhar_ledger && Array.isArray(msg.metrics.udhar_ledger)) {
                udharLedger = msg.metrics.udhar_ledger;
                save(KEY_UDHAR, udharLedger);
                notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
              }
              lastSyncMetrics = msg.metrics;
              notifySyncListeners("METRICS_UPDATE", msg.metrics);
            } else if (msg.type === "NEW_CUSTOMER_YAADI" || msg.event === "NEW_CUSTOMER_YAADI") {
              if (msg.order) {
                VyaparCore.addPendingCustomerOrder(msg.order);
              }
              notifySyncListeners("NEW_CUSTOMER_YAADI", msg.order);
              performLiveSync();
            } else if (msg.type === "ORDER_EXPIRED_ROLLBACK" || msg.event === "ORDER_EXPIRED_ROLLBACK") {
              const expiredId = msg.order_id || (msg.order ? msg.order.order_id : null);
              if (expiredId) {
                pendingOrders = pendingOrders.filter(o => o.order_id !== expiredId && o.id !== expiredId);
                save(KEY_ORDERS, pendingOrders);
                notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
              }
              performLiveSync();
            } else if (msg.type === "ORDER_CONFIRMED" || msg.event === "ORDER_CONFIRMED") {
              const confirmedOrder = msg.order;
              if (confirmedOrder) {
                const match = pendingOrders.find(o => o.order_id === confirmedOrder.order_id || o.id === confirmedOrder.order_id);
                if (match) {
                  match.status = "CONFIRMED";
                  match.confirmed_by_customer = true;
                  save(KEY_ORDERS, pendingOrders);
                  notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
                }
              }
              performLiveSync();
            } else if (msg.type === "CUSTOMER_ORDER_PACKED" || msg.event === "CUSTOMER_ORDER_PACKED") {
              const packedId = msg.order_id || (msg.order ? msg.order.order_id : null);
              if (packedId) {
                const match = pendingOrders.find(o => o.order_id === packedId || o.id === packedId);
                if (match) {
                  match.status = "PACKED";
                  save(KEY_ORDERS, pendingOrders);
                  notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
                }
              }
              performLiveSync();
            } else if (msg.type === "CATALOG_ONBOARDED" || msg.event === "CATALOG_ONBOARDED") {
              performLiveSync();
            }
          } catch (err) {
            console.error("WS Parse error", err);
          }
        };

        activeWebSocket.onclose = function() {
          if (heartbeatTimer) clearInterval(heartbeatTimer);
          notifySyncListeners("WS_STATUS", { connected: false });
          startAdaptivePolling();
          reconnectAttempts++;
          const delay = Math.min(1000 * Math.pow(1.5, reconnectAttempts), 20000) + Math.random() * 500;
          setTimeout(connectWS, delay);
        };

        activeWebSocket.onerror = function() {
          try { activeWebSocket.close(); } catch (e) {}
        };
      } catch (err) {
        console.error("WS connect failed", err);
        startAdaptivePolling();
      }
    }

    connectWS();
  }

  return {
    // -------------------------------------------------------------------------
    // 1. INVENTORY METHODS
    // -------------------------------------------------------------------------
    get inventory() {
      return skus;
    },
    getSKUs: function() {
      return skus;
    },
    getSKU: function(skuCode) {
      return skus.find(s => s.sku === skuCode);
    },
    addStock: async function(skuCode, addQty, reason = "Manual UI Stock Add") {
      const item = skus.find(s => s.sku === skuCode);
      if (item) {
        item.stock = Math.max(0, parseFloat((Number(item.stock) + Number(addQty)).toFixed(2)));
        save(KEY_SKUS, skus);
        notifySyncListeners("METRICS_UPDATE", { products: skus });
      }
      try {
        const url = `${getBackendUrl()}/api/items/stock-delta`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ sku: skuCode, delta: Number(addQty), reason: reason })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Stock-delta sync failed:", e);
      }
      return null;
    },
    undoLastTransaction: async function() {
      let undoneTx = null;
      if (transactions && transactions.length > 0) {
        undoneTx = transactions.shift();
        save(KEY_TX, transactions);
        notifySyncListeners("TRANSACTIONS_UPDATED", transactions);
      }
      try {
        const url = `${getBackendUrl()}/api/transactions/undo`;
        const res = await fetch(url, { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            if (data.metrics.products) {
              data.metrics.products.forEach(bp => {
                const local = skus.find(s => s.sku === bp.sku);
                if (local) {
                  local.stock = bp.stock;
                }
              });
              save(KEY_SKUS, skus);
            }
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Undo transaction failed:", e);
      }
      return undoneTx ? { status: "SUCCESS", undone: undoneTx } : null;
    },
    settleKhata: async function(creditId, amount, mode = "CASH", notes = "") {
      try {
        const url = `${getBackendUrl()}/api/udhar/${creditId}/pay`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount: Number(amount), payment_mode: mode, notes: notes })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            if (data.metrics.udhar_ledger) {
              udharLedger = data.metrics.udhar_ledger;
              save(KEY_UDHAR, udharLedger);
              notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
            }
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          // Also settle locally in customers if matched
          const cidStr = String(creditId);
          const localCust = customers.find(c => c.id === cidStr || String(c.id).includes(cidStr));
          if (localCust) {
            localCust.udhar = Math.max(0, (localCust.udhar || 0) - Number(amount));
            if (localCust.udhar <= 0) localCust.status = "SETTLED";
            localCust.last_tx = `Just now (Paid ₹${amount})`;
            save(KEY_CUSTOMERS, customers);
          }
          // Log a transaction
          this.addTransaction({
            type: "SALE",
            mode: mode.includes("UPI") ? "UPI Soundbox" : "Cash Counter",
            cust: (data.credit && data.credit.customer_name) || (localCust && localCust.name) || "Khata Customer",
            items: `Khata Udhar Payment (₹${amount})`,
            amount: Number(amount),
            status: "Success"
          });
          this.playSoundboxChime(Number(amount));
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Settle khata failed:", e);
      }
      return null;
    },
    getUdharLedger: async function(vendorId = "DEMO_KIRANA_KOP") {
      try {
        const res = await fetch(`${getBackendUrl()}/api/udhar/ledger?vendor_id=${vendorId}`);
        if (res.ok) {
          const ledger = await res.json();
          if (Array.isArray(ledger)) {
            udharLedger = ledger;
            save(KEY_UDHAR, udharLedger);
            notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
            return udharLedger;
          }
        }
      } catch (e) {
        console.warn("[VyaparCore] Get udhar ledger failed:", e);
      }
      return udharLedger && udharLedger.length > 0 ? udharLedger : DEFAULT_CUSTOMERS;
    },
    getCachedUdharLedger: function() {
      return udharLedger && udharLedger.length > 0 ? udharLedger : DEFAULT_CUSTOMERS;
    },
    getCustomers: function() {
      return customers;
    },
    sendUdharReminder: async function(creditId, sendWhatsApp = true) {
      try {
        const url = `${getBackendUrl()}/api/udhar/remind/${creditId}?send_whatsapp=${sendWhatsApp}`;
        const res = await fetch(url, { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            if (data.metrics.udhar_ledger) {
              udharLedger = data.metrics.udhar_ledger;
              save(KEY_UDHAR, udharLedger);
              notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
            }
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Send udhar reminder failed:", e);
      }
      return null;
    },
    bulkRemindUdhar: async function(vendorId = "DEMO_KIRANA_KOP") {
      try {
        const url = `${getBackendUrl()}/api/udhar/bulk-remind?vendor_id=${vendorId}`;
        const res = await fetch(url, { method: "POST" });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            if (data.metrics.udhar_ledger) {
              udharLedger = data.metrics.udhar_ledger;
              save(KEY_UDHAR, udharLedger);
              notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
            }
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Bulk remind failed:", e);
      }
      return null;
    },
    createCustomerAccount: async function(payload) {
      try {
        const url = `${getBackendUrl()}/api/udhar/accounts`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            customer_name: payload.customer_name || payload.name,
            customer_phone: payload.customer_phone || payload.phone,
            amount_due: parseFloat(payload.amount_due || payload.amount || 0),
            vendor_id: payload.vendor_id || "DEMO_KIRANA_KOP",
            due_date: payload.due_date || "तात्काळ (Immediate)",
            notes: payload.notes || "New Counter Customer"
          })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.metrics) {
            lastSyncMetrics = data.metrics;
            if (data.metrics.udhar_ledger) {
              udharLedger = data.metrics.udhar_ledger;
              save(KEY_UDHAR, udharLedger);
              notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
            }
            notifySyncListeners("METRICS_UPDATE", data.metrics);
          }
          // Also add to local customers list
          const newCust = {
            id: data.credit ? String(data.credit.id) : "c" + (customers.length + 1),
            name: payload.customer_name || payload.name,
            area: payload.notes || payload.area || "Kolhapur Ward",
            phone: payload.customer_phone || payload.phone,
            udhar: parseFloat(payload.amount_due || payload.amount || 0),
            status: "DUE_SOON",
            last_tx: "Just now (Account Opened)",
            trust: "A",
            orders: 1,
            pref: "Counter Walk-in / Udhar"
          };
          customers.unshift(newCust);
          save(KEY_CUSTOMERS, customers);
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Create customer account failed:", e);
      }
      return null;
    },
    getWhatsAppReminderLink: function(customer, shopName = "अथर्व किराणा स्टोअर्स") {
      const rawPhone = (customer.customer_phone || customer.phone || "").replace(/[^0-9]/g, "");
      const phone = rawPhone.length === 10 ? "91" + rawPhone : (rawPhone || "919579869506");
      const name = customer.customer_name || customer.name || "ग्राहक";
      const cleanName = name.replace(" शेठ", "").replace("शेठ", "").trim();
      const amount = Math.round(customer.amount_due !== undefined ? customer.amount_due : (customer.udhar || 0));
      const message = `🙏 नमस्कार ${cleanName} शेठ! आपल्या ${shopName}मधील ₹${amount} चे उधारी बिल प्रलंबित आहे. कृपया सवडीने Google Pay किंवा रोख भरणा करावा ही नम्र विनंती. - ${shopName} 🏪`;
      return {
        phone: phone,
        message: message,
        waUrl: `https://wa.me/${phone}?text=${encodeURIComponent(message)}`
      };
    },
    restock: function(skuCode, addQty) {
      return this.addStock(skuCode, addQty);
    },
    deductStock: function(skuCode, qty) {
      const item = skus.find(s => s.sku === skuCode);
      if (item) {
        item.stock = Math.max(0, parseFloat((item.stock - qty).toFixed(2)));
        save(KEY_SKUS, skus);
        return item;
      }
      return null;
    },
    addSKUsBulk: function(newItems) {
      newItems.forEach(item => {
        const existing = skus.find(s => s.sku === item.sku || s.short_name.toLowerCase() === item.short_name.toLowerCase());
        if (existing) {
          existing.stock = Math.max(0, parseFloat((existing.stock + item.stock).toFixed(2)));
        } else {
          skus.push(item);
        }
      });
      save(KEY_SKUS, skus);
    },
    getLowStockCount: function() {
      return skus.filter(s => s.stock <= s.min_threshold).length;
    },
    getInventoryValuation: function() {
      return skus.reduce((acc, s) => acc + (s.stock * s.unit_price), 0);
    },

    // -------------------------------------------------------------------------
    // 2. TRANSACTION & SALES METHODS
    // -------------------------------------------------------------------------
    get transactions() {
      return transactions;
    },
    getTransactions: function() {
      return transactions;
    },
    addTransaction: function(tx) {
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const newTx = {
        id: "TX-" + (1086 + transactions.length),
        time: timeStr,
        type: tx.type || "SALE",
        mode: tx.mode || "Cash Counter",
        cust: tx.cust || "Counter Customer",
        items: tx.items || "Kirana Items",
        amount: parseFloat(tx.amount || 0),
        status: tx.status || "Success"
      };
      transactions.unshift(newTx);
      save(KEY_TX, transactions);
      return newTx;
    },
    getDailyMetrics: function() {
      let totalRev = 0;
      let cashTotal = 0;
      let upiTotal = 0;
      let udharTotal = 0;
      let billCount = 0;

      transactions.forEach(t => {
        if (t.type === "SALE" || t.type === "UDHAR") {
          totalRev += t.amount;
          billCount++;
          if (t.mode.includes("UPI") || t.mode.includes("Soundbox")) {
            upiTotal += t.amount;
          } else if (t.mode.includes("Cash")) {
            cashTotal += t.amount;
          } else if (t.mode.includes("Udhar") || t.type === "UDHAR") {
            udharTotal += t.amount;
          } else {
            upiTotal += t.amount;
          }
        }
      });

      return {
        totalRevenue: totalRev,
        cashTotal: cashTotal,
        upiTotal: upiTotal,
        udharTotal: udharTotal,
        orderCount: billCount,
        lowStockCount: this.getLowStockCount()
      };
    },

    // -------------------------------------------------------------------------
    // 3. REMOTE YAADI (CUSTOMER ORDER QUEUE & ZERO DIRECT DEDUCTION INVARIANT)
    // -------------------------------------------------------------------------
    getPendingOrders: function() {
      return pendingOrders.filter(o => o.status === "PENDING");
    },
    addPendingCustomerOrder: function(order) {
      const newOrder = {
        order_id: order.order_id || ("ORD-KOP-" + Math.floor(1000 + Math.random() * 9000)),
        customer_name: order.customer_name || "WhatsApp Customer",
        customer_phone: order.customer_phone || "+91 98000 00000",
        area: order.area || "Kolhapur Walk-in",
        time: "Just now",
        slip_type: order.slip_type || "WhatsApp Yaadi Slip",
        items_text: order.items_text || "किराणा यादी",
        items: order.items || [],
        total_amount: parseFloat(order.total_amount || 0),
        status: "PENDING"
      };
      pendingOrders.unshift(newOrder);
      save(KEY_ORDERS, pendingOrders);
      return newOrder;
    },
    packAndFulfillOrder: function(orderId) {
      const order = pendingOrders.find(o => o.order_id === orderId);
      if (order && order.status === "PENDING") {
        // Note: Stock was already safely soft-reserved by backend on order arrival.
        // We only commit sales ledger locally and await backend atomic fulfillment confirmation.

        // Add to Sales Ledger
        this.addTransaction({
          type: "SALE",
          mode: "WhatsApp Yaadi (Fulfilled)",
          cust: order.customer_name,
          items: order.items_text,
          amount: order.total_amount,
          status: "Success"
        });

        order.status = "PACKED";
        order.fulfilled_at = new Date().toLocaleTimeString();
        save(KEY_ORDERS, pendingOrders);

        // Synchronize with cloud backend
        fetch(`${getBackendUrl()}/api/orders/${orderId}/pack`, { method: "POST" })
          .then(r => r.json())
          .then(res => {
            if (res && res.metrics) {
              performLiveSync();
            }
          })
          .catch(e => console.log("[PACK API WARN]:", e));

        this.playSoundboxChime(order.total_amount);
        return { success: true, order };
      }
      return { success: false, message: "Order not found or already packed" };
    },

    // -------------------------------------------------------------------------
    // 4. SUB-1ms REVERSE-MATH ENGINE (Voice-to-Scale)
    // -------------------------------------------------------------------------
    calculateReverseMath: function(query) {
      const text = (query || "").trim().toLowerCase();
      const t0 = performance.now();

      // Check colloquial units
      let isPavsher = text.includes("पावशेर") || text.includes("pavsher") || text.includes("पाव किलो") || text.includes("pav kilo");
      let isArdha = text.includes("अर्धा") || text.includes("ardha") || text.includes("half");
      let isSavva = text.includes("सव्वा") || text.includes("savva");

      // Match item from catalog
      let matchedSKU = null;
      for (const item of skus) {
        if (text.includes(item.short_name.toLowerCase())) {
          matchedSKU = item;
          break;
        }
        if (item.aliases && item.aliases.some(a => text.includes(a.toLowerCase()))) {
          matchedSKU = item;
          break;
        }
      }

      if (!matchedSKU) {
        matchedSKU = skus.find(s => s.sku === "GROC-SUG-001"); // Default sugar fallback
      }

      const latency = (performance.now() - t0 + 0.015).toFixed(3);

      if (isPavsher) {
        const grams = 250;
        const bill = (grams / 1000) * matchedSKU.unit_price;
        return {
          mode: "COLLOQUIAL_WEIGHT",
          grams: grams,
          bill: bill,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `⚖️ काट्यावर ठेवा: २५० ग्रॅम ${matchedSKU.name_mr}`,
          reply_text: `⚖️ काट्यावर ठेवा: २५० ग्रॅम ${matchedSKU.name_mr} (दर: ₹${matchedSKU.unit_price}/किग्रॅ, बिल: ₹${bill.toFixed(2)})`
        };
      }

      if (isArdha) {
        const grams = 500;
        const bill = (grams / 1000) * matchedSKU.unit_price;
        return {
          mode: "COLLOQUIAL_WEIGHT",
          grams: grams,
          bill: bill,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `⚖️ काट्यावर ठेवा: ५०० ग्रॅम ${matchedSKU.name_mr}`,
          reply_text: `⚖️ काट्यावर ठेवा: ५०० ग्रॅम ${matchedSKU.name_mr} (दर: ₹${matchedSKU.unit_price}/किग्रॅ, बिल: ₹${bill.toFixed(2)})`
        };
      }

      if (isSavva) {
        const grams = 1250;
        const bill = (grams / 1000) * matchedSKU.unit_price;
        return {
          mode: "COLLOQUIAL_WEIGHT",
          grams: grams,
          bill: bill,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `⚖️ काट्यावर ठेवा: १२५० ग्रॅम (१.२५ किग्रॅ) ${matchedSKU.name_mr}`,
          reply_text: `⚖️ काट्यावर ठेवा: १२५० ग्रॅम ${matchedSKU.name_mr} (दर: ₹${matchedSKU.unit_price}/किग्रॅ, बिल: ₹${bill.toFixed(2)})`
        };
      }

      // 1. Money-to-Weight (e.g. "20 chi sakhar", "100 rupyachi tur dal", "50 rs sugar")
      const moneyMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:chi|che|chya|ची|चे|च्या|रुपयांची|रुपयांचे|rs|inr|रुपये)/i);
      if (moneyMatch) {
        const money = parseFloat(moneyMatch[1]);
        const grams = Math.round((money / matchedSKU.unit_price) * 1000);
        return {
          mode: "MONEY_TO_WEIGHT",
          money: money,
          grams: grams,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `⚖️ काट्यावर ठेवा: ${grams} ग्रॅम ${matchedSKU.name_mr}`,
          reply_text: `⚖️ काट्यावर ठेवा: ${grams} ग्रॅम ${matchedSKU.name_mr} (दर: ₹${matchedSKU.unit_price}/किग्रॅ, एकूण: ₹${money.toFixed(2)})`
        };
      }

      // 2. Weight-to-Money (e.g. "350 gm shengdana", "500g tur dal", "2 kg atta")
      const weightMatch = text.match(/(\d+(?:\.\d+)?)\s*(?:gm|g|gram|grams|ग्रॅम|किलो|kg|kilo)/i);
      if (weightMatch) {
        const rawWeight = parseFloat(weightMatch[1]);
        const isKg = text.includes("kg") || text.includes("किलो") || text.includes("kilo");
        const grams = isKg ? rawWeight * 1000 : rawWeight;
        const bill = parseFloat(((grams / 1000) * matchedSKU.unit_price).toFixed(2));
        return {
          mode: "WEIGHT_TO_MONEY",
          grams: grams,
          bill: bill,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `💰 बिल: ₹${bill.toFixed(2)}`,
          reply_text: `💰 बिल: ₹${bill.toFixed(2)} (${grams} ग्रॅम ${matchedSKU.name_mr} @ ₹${matchedSKU.unit_price}/किग्रॅ)`
        };
      }

      return null;
    },

    // -------------------------------------------------------------------------
    // 5. BACKEND API INTEGRATION CLIENT
    // -------------------------------------------------------------------------
    backend: {
      getBaseUrl: getBackendUrl,
      getWsUrl: getWebSocketUrl,
      startLiveSync: startLiveSync,
      registerListener: registerSyncListener,
      getLastMetrics: function() { return lastSyncMetrics; },
      syncLiveMetrics: performLiveSync,

      // Send text message (Merchant Sale / Query / Reverse-Math)
      sendMessage: async function(text, vendorId = "DEMO_KIRANA_KOP") {
        try {
          const res = await fetch(`${getBackendUrl()}/api/simulator/send`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, vendor_id: vendorId })
          });
          if (res.ok) {
            return await res.json();
          }
        } catch (e) {
          console.log("Backend send error, using offline simulation", e);
        }
        return null;
      },

      // Submit Customer Handwritten / Text Yaadi
      submitCustomerYaadi: async function(text, file = null, customerPhone = "+91 98223 44102") {
        try {
          const formData = new FormData();
          formData.append("customer_phone", customerPhone);
          formData.append("text_message", text || "");
          if (file) {
            formData.append("file", file);
          }
          const res = await fetch(`${getBackendUrl()}/api/simulator/customer-yaadi`, {
            method: 'POST',
            body: formData
          });
          if (res.ok) {
            return await res.json();
          }
        } catch (e) {
          console.log("Backend yaadi submit error", e);
        }
        return null;
      },

      // 15-Second Shelf Video Ingestion
      uploadShelfVideo: async function(file) {
        try {
          const formData = new FormData();
          formData.append("file", file);
          const res = await fetch(`${getBackendUrl()}/api/simulator/video`, {
            method: 'POST',
            body: formData
          });
          if (res.ok) {
            return await res.json();
          }
        } catch (e) {
          console.log("Backend video onboarding error", e);
        }
        return null;
      },

      // Export GST Report CSV
      exportGSTCSV: function() {
        window.open(`${getBackendUrl()}/api/export-gst-csv`, '_blank');
      },

      // Trojan Horse: Quick Add Dairy
      quickAddDairy: async function() {
        try {
          const res = await fetch(`${getBackendUrl()}/api/items/quick-add-dairy`, { method: 'POST' });
          if (res.ok) return await res.json();
        } catch (e) {
          console.log("Dairy add fallback", e);
        }
        return null;
      }
    },

    // -------------------------------------------------------------------------
    // 6. AUDIO & SOUNDBOX CHIME
    // -------------------------------------------------------------------------
    playSoundboxChime: function(amount) {
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
          const ctx = new AudioContext();
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain);
          gain.connect(ctx.destination);

          osc.type = "sine";
          osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
          osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.12); // A5
          osc.frequency.setValueAtTime(1174.66, ctx.currentTime + 0.24); // D6
          gain.gain.setValueAtTime(0.3, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
          osc.start();
          osc.stop(ctx.currentTime + 0.6);
        }
      } catch (e) {
        // silent fallback
      }
    },

    // Settle Khata
    settleCustomerKhata: function(idOrPhone) {
      const cust = customers.find(c => c.id === idOrPhone || c.phone === idOrPhone || c.name.includes(idOrPhone));
      if (cust) {
        const amt = cust.udhar;
        cust.udhar = 0.0;
        cust.status = "SETTLED";
        cust.last_tx = "Just now (Full Payment Settle)";
        save(KEY_CUSTOMERS, customers);
        if (amt > 0) {
          this.addTransaction({
            type: "SALE",
            mode: "UPI Soundbox",
            cust: cust.name,
            items: "Khata Udhar Settle",
            amount: amt,
            status: "Success"
          });
        }
        return cust;
      }
      return null;
    },

    // Reset Store to Factory Defaults
    resetDefaults: function() {
      skus = JSON.parse(JSON.stringify(DEFAULT_SKUS));
      customers = JSON.parse(JSON.stringify(DEFAULT_CUSTOMERS));
      transactions = JSON.parse(JSON.stringify(DEFAULT_TRANSACTIONS));
      pendingOrders = JSON.parse(JSON.stringify(DEFAULT_PENDING_ORDERS));
      activeDukaan = "अथर्व किराणा स्टोअर्स, कोल्हापूर (DEMO_KIRANA_KOP)";
      save(KEY_SKUS, skus);
      save(KEY_CUSTOMERS, customers);
      save(KEY_TX, transactions);
      save(KEY_ORDERS, pendingOrders);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem(KEY_STORE, activeDukaan);
      }
    },

    performLiveSync: performLiveSync,

    resetAllAndRestock: async function() {
      this.resetDefaults();
      try {
        await fetch(`${getBackendUrl()}/api/reset-demo`, { method: 'POST' });
      } catch(e) {}
      await performLiveSync();
      return skus;
    }
  };
})();

// Universal Export
if (typeof window !== "undefined") {
  window.VyaparCore = VyaparCore;
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = VyaparCore;
}

// Cross-frame messaging support (for WhatsApp console inside iframe)
if (typeof window !== "undefined" && window.addEventListener) {
  window.addEventListener("message", function(event) {
    if (event.data && event.data.type === "VYAPAR_SALE") {
      VyaparCore.addTransaction(event.data.payload);
      if (typeof refreshCurrentPageUI === "function") {
        refreshCurrentPageUI();
      }
    } else if (event.data && event.data.type === "VYAPAR_RESTOCK") {
      VyaparCore.restock(event.data.sku, event.data.qty);
      if (typeof refreshCurrentPageUI === "function") {
        refreshCurrentPageUI();
      }
    } else if (event.data && event.data.type === "NEW_CUSTOMER_YAADI") {
      VyaparCore.addPendingCustomerOrder(event.data.order);
      if (typeof renderPendingOrdersQueue === "function") {
        renderPendingOrdersQueue();
      }
    }
  });
}

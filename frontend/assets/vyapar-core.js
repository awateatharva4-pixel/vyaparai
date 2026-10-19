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
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/parle_g.jpg",
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
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/sugar.jpg",
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
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/fortune_oil.jpg",
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
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/ladi_pav.jpg",
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
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/tur_dal.jpg",
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
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/tata_salt.jpg",
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
      max_capacity: 30.0,
      full_stock: 30.0,
      img: "assets/products/aashirvaad_atta.jpg",
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
      max_capacity: 80.0,
      full_stock: 80.0,
      img: "assets/products/maggi.jpg",
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
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/red_onion.jpg",
      pedestal: "pedestal-rose",
      aliases: ["kanda", "onion", "कांदा", "कांदे", "PROD-ONION-1K", "prod-onion-1k"]
    },
    {
      sku: "PROD-ONION-1K",
      name_mr: "नाशिक गावठी लाल कांदा १ किलो",
      name_en: "Nashik Red Onion 1kg",
      short_name: "Red Onion 1kg",
      category: "Fresh Produce",
      stock: 70.0,
      unit: "kg",
      unit_price: 35.0,
      cost_price: 26.00,
      min_threshold: 15.0,
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/red_onion.jpg",
      pedestal: "pedestal-rose",
      aliases: ["onion", "kanda", "कांदा", "कांदे", "VEG-KANDA-001"]
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
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/potato.jpg",
      pedestal: "pedestal-azure",
      aliases: ["batata", "potato", "बटाटा", "बटाटे", "आलू"]
    },
    {
      sku: "DAIRY-MILK-500ML",
      name_mr: "गोकुळ / अमूल ताझा दूध (५०० मिली)",
      name_en: "Gokul / Amul Taaza Milk 500ml",
      short_name: "Gokul / Amul Milk",
      category: "Dairy & Perishables",
      stock: 24.0,
      unit: "pouch",
      unit_price: 27.0,
      cost_price: 24.50,
      min_threshold: 6.0,
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/amul_milk.jpg",
      pedestal: "pedestal-blue",
      aliases: ["दूध", "अमुल दूध", "गोकुळ दूध", "milk", "taaza milk", "fresh milk", "dudh", "doodh", "पिशवी दूध", "amul", "gokul"]
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
      max_capacity: 50.0,
      full_stock: 50.0,
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
      max_capacity: 100.0,
      full_stock: 100.0,
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
      max_capacity: 50.0,
      full_stock: 50.0,
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
      max_capacity: 40.0,
      full_stock: 40.0,
      img: "assets/products/kinley_water.jpg",
      pedestal: "pedestal-green",
      aliases: ["pani", "water", "kinley", "पाणी", "किनले"]
    },
    {
      sku: "GROC-SHENG-001",
      name_mr: "गावरान शेंगदाणे (बारीक/जाड)",
      name_en: "Raw Peanuts (Shengdana) 1kg",
      short_name: "Shengdana",
      category: "Grains & Sweeteners",
      stock: 35.0,
      unit: "kg",
      unit_price: 140.0,
      cost_price: 118.00,
      min_threshold: 8.0,
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/sugar.jpg",
      pedestal: "pedestal-peach",
      aliases: ["shengdana", "shengadana", "peanuts", "शेंगदाणे", "शेंगदाणा", "दाणे", "मूंगफली"]
    },
    {
      sku: "GROC-GAHU-001",
      name_mr: "गावरान लोकवन गहू (Loose)",
      name_en: "Lokwan Whole Wheat Grains 1kg",
      short_name: "Lokwan Wheat (गहू)",
      category: "Grains & Sweeteners",
      stock: 55.0,
      unit: "kg",
      unit_price: 38.0,
      cost_price: 31.00,
      min_threshold: 10.0,
      max_capacity: 100.0,
      full_stock: 100.0,
      img: "assets/products/aashirvaad_atta.jpg",
      pedestal: "pedestal-peach",
      aliases: ["gahu", "gahhu", "wheat", "गहू", "लोकवन", "लोकवन गहू"]
    },
    {
      sku: "FMCG-COLG-100G",
      name_mr: "कोलगेट स्ट्रॉंग टीथ १०० ग्रॅम",
      name_en: "Colgate Strong Teeth 100g",
      short_name: "Colgate",
      category: "Personal Care & Hygiene",
      stock: 8.0,
      unit: "tube",
      unit_price: 65.0,
      cost_price: 52.00,
      min_threshold: 15.0,
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/colgate.jpg",
      pedestal: "pedestal-rose",
      aliases: ["colgate", "toothpaste", "कोलगेट", "दंतमंजन", "पेस्ट", "टूथपेस्ट"]
    },
    {
      sku: "OIL-GEM-1L",
      name_mr: "जेमिनी सूर्यफूल तेल १ लिटर",
      name_en: "Gemini Sunflower Oil 1L",
      short_name: "Gemini Oil 1L",
      category: "Edible Oils",
      stock: 20.0,
      unit: "pouch",
      unit_price: 130.0,
      cost_price: 115.00,
      min_threshold: 6.0,
      max_capacity: 30.0,
      full_stock: 30.0,
      img: "assets/products/fortune_oil.jpg",
      pedestal: "pedestal-green",
      aliases: ["gemini", "gemini oil", "जेमिनी", "जेमिनी तेल"]
    },
    {
      sku: "DAL-MOONG-1K",
      name_mr: "गावरान पिवळी मूग डाळ १ किलो",
      name_en: "Yellow Moong Dal 1kg",
      short_name: "Moong Dal",
      category: "Pulses & Lentils",
      stock: 25.0,
      unit: "kg",
      unit_price: 130.0,
      cost_price: 112.00,
      min_threshold: 8.0,
      max_capacity: 40.0,
      full_stock: 40.0,
      img: "assets/products/tur_dal.jpg",
      pedestal: "pedestal-azure",
      aliases: ["moong", "moong dal", "मूग", "मूग डाळ"]
    },
    {
      sku: "GROC-BESAN-500G",
      name_mr: "शुद्ध चणा डाळ बेसन ५०० ग्रॅम",
      name_en: "Pure Chana Dal Besan 500g",
      short_name: "Besan 500g",
      category: "Grains & Sweeteners",
      stock: 20.0,
      unit: "packet",
      unit_price: 55.0,
      cost_price: 44.00,
      min_threshold: 8.0,
      max_capacity: 40.0,
      full_stock: 40.0,
      img: "assets/products/aashirvaad_atta.jpg",
      pedestal: "pedestal-peach",
      aliases: ["besan", "chana besan", "बेसन", "चणा बेसन"]
    },
    {
      sku: "SPICE-CHILLI-100G",
      name_mr: "कोल्हापुरी लवंगी तिखट १०० ग्रॅम",
      name_en: "Kolhapuri Red Chilli Powder 100g",
      short_name: "Chilli Powder 100g",
      category: "Spices & Essentials",
      stock: 30.0,
      unit: "packet",
      unit_price: 45.0,
      cost_price: 36.00,
      min_threshold: 10.0,
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/tata_salt.jpg",
      pedestal: "pedestal-rose",
      aliases: ["tikhat", "mirchi", "chilli", "तिखट", "मिरची", "मिरची पावडर"]
    },
    {
      sku: "SPICE-TURM-100G",
      name_mr: "शुद्ध हळद पावडर १०० ग्रॅम",
      name_en: "Pure Turmeric Powder 100g",
      short_name: "Haldi Powder 100g",
      category: "Spices & Essentials",
      stock: 30.0,
      unit: "packet",
      unit_price: 35.0,
      cost_price: 27.00,
      min_threshold: 10.0,
      max_capacity: 50.0,
      full_stock: 50.0,
      img: "assets/products/tata_salt.jpg",
      pedestal: "pedestal-blue",
      aliases: ["halad", "haldi", "turmeric", "हळद", "हळदी"]
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
      order_id: "ORD-KOP-7019",
      customer_name: "व्यंकटेश पै (Venkatesh Pai)",
      customerName: "व्यंकटेश पै (Venkatesh Pai)",
      customer_phone: "+91 98220 12345",
      phone: "+91 98220 12345",
      area: "Rajarampuri, Kolhapur",
      time: "Just now",
      timestamp: "Just now",
      slip_type: "WhatsApp Yaadi Slip",
      items_text: "व्हॉट्सॲप किराणा यादी: २ किलो साखर, १ लिटर फॉर्च्युन तेल, ५ पार्ले-जी, १ गोकुळ दूध",
      rawText: "व्हॉट्सॲप किराणा यादी: २ किलो साखर, १ लिटर फॉर्च्युन तेल, ५ पार्ले-जी, १ गोकुळ दूध",
      raw_message: "व्हॉट्सॲप किराणा यादी: २ किलो साखर, १ लिटर फॉर्च्युन तेल, ५ पार्ले-जी, १ गोकुळ दूध",
      items: [
        { sku: "GROC-SUG-001", sku_matched: "GROC-SUG-001", name: "साखर (Sugar)", name_mr: "साखर", qty: 2.0, quantity: 2.0, unit: "kg", price: 42.0, unit_price: 42.0, line_total: 84.0, total: 84.0, is_available: true },
        { sku: "OIL-FORT-1L", sku_matched: "OIL-FORT-1L", name: "फॉर्च्युन तेल (Fortune Oil 1L)", name_mr: "फॉर्च्युन तेल", qty: 1.0, quantity: 1.0, unit: "pouch", price: 135.0, unit_price: 135.0, line_total: 135.0, total: 135.0, is_available: true },
        { sku: "FMCG-PARLE-100G", sku_matched: "FMCG-PARLE-100G", name: "पार्ले-जी (Parle-G 100g)", name_mr: "पार्ले-जी", qty: 5.0, quantity: 5.0, unit: "packet", price: 10.0, unit_price: 10.0, line_total: 50.0, total: 50.0, is_available: true },
        { sku: "DAIRY-MILK-500ML", sku_matched: "DAIRY-MILK-500ML", name: "गोकुळ दूध (Gokul Milk 500ml)", name_mr: "गोकुळ दूध", qty: 1.0, quantity: 1.0, unit: "pouch", price: 27.0, unit_price: 27.0, line_total: 27.0, total: 27.0, is_available: true }
      ],
      total_amount: 296.0,
      totalEstimated: 296.0,
      status: "PENDING",
      is_stock_reserved: false,
      confirmed_by_customer: false,
      timer_started_at: null,
      remaining_seconds: 1800
    }
  ];

  // Storage Keys
  const KEY_SKUS = "vyapar_inventory_skus_v4";
  const KEY_CUSTOMERS = "vyapar_customers";
  const KEY_UDHAR = "vyapar_udhar_ledger";
  const KEY_TX = "vyapar_transactions";
  const KEY_TXNS = KEY_TX;
  const KEY_ORDERS = "vyapar_pending_orders";
  const KEY_STORE = "vyapar_active_dukaan";

  function getCategoryPlaceholderSvg(category, name) {
    const cat = (category || '').toLowerCase();
    const nm = (name || '').toLowerCase();
    let icon = '📦';
    let label = 'Kirana Item';
    let bg1 = '#0f2e31';
    let bg2 = '#081c1e';
    let accent = '#c9a96e';

    if (cat.includes('dairy') || cat.includes('दुग्ध') || nm.includes('milk') || nm.includes('दूध')) {
      icon = '🥛';
      label = 'Dairy';
      bg1 = '#1e3a8a'; bg2 = '#172554'; accent = '#93c5fd';
    } else if (cat.includes('grain') || cat.includes('धान्य') || nm.includes('sugar') || nm.includes('atta') || nm.includes('साखर')) {
      icon = '🌾';
      label = 'Grocery';
      bg1 = '#854d0e'; bg2 = '#422006'; accent = '#fef08a';
    } else if (cat.includes('oil') || cat.includes('तेल') || nm.includes('oil')) {
      icon = '🌻';
      label = 'Edible Oil';
      bg1 = '#b45309'; bg2 = '#78350f'; accent = '#fde68a';
    } else if (cat.includes('veg') || cat.includes('produce') || cat.includes('भाजी')) {
      icon = '🥔';
      label = 'Produce';
      bg1 = '#15803d'; bg2 = '#14532d'; accent = '#86efac';
    } else if (cat.includes('snack') || cat.includes('biscuit') || cat.includes('fmcg')) {
      icon = '🍪';
      label = 'Packaged FMCG';
      bg1 = '#c2410c'; bg2 = '#7c2d12'; accent = '#fed7aa';
    } else if (cat.includes('bakery') || cat.includes('बेकरी') || nm.includes('pav')) {
      icon = '🍞';
      label = 'Bakery';
      bg1 = '#991b1b'; bg2 = '#450a0a'; accent = '#fecaca';
    } else if (cat.includes('pulse') || cat.includes('lentil') || cat.includes('डाळ')) {
      icon = '🥣';
      label = 'Pulses & Dal';
      bg1 = '#d97706'; bg2 = '#78350f'; accent = '#fef3c7';
    } else if (cat.includes('stationery') || cat.includes('office') || cat.includes('पेन') || cat.includes('वही')) {
      icon = '✏️';
      label = 'Stationery';
      bg1 = '#6d28d9'; bg2 = '#3b0764'; accent = '#ddd6fe';
    } else if (cat.includes('beverage') || cat.includes('water') || cat.includes('पेये') || cat.includes('पाणी')) {
      icon = '💧';
      label = 'Beverage';
      bg1 = '#0369a1'; bg2 = '#082f49'; accent = '#bae6fd';
    } else if (cat.includes('spice') || cat.includes('मीठ') || cat.includes('मसाले')) {
      icon = '🧂';
      label = 'Spices & Salt';
      bg1 = '#334155'; bg2 = '#0f172a'; accent = '#e2e8f0';
    }

    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><defs><linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="${bg1}"/><stop offset="100%" stop-color="${bg2}"/></linearGradient></defs><rect width="96" height="96" rx="20" fill="url(#g)"/><rect x="2" y="2" width="92" height="92" rx="18" fill="none" stroke="${accent}" stroke-width="1.5" stroke-opacity="0.35"/><text x="48" y="44" font-size="34" text-anchor="middle" dominant-baseline="central">${icon}</text><text x="48" y="74" font-family="-apple-system,BlinkMacSystemFont,sans-serif" font-size="10" font-weight="700" fill="${accent}" text-anchor="middle" letter-spacing="0.5">${label.toUpperCase()}</text></svg>`;
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(svg);
  }

  function resolveCatalogImg(sku, category, name) {
    const s = (sku || '').toUpperCase();
    if (s.includes('MILK') || s.includes('AMUL') || s.startsWith('DAIRY-')) return 'assets/products/amul_milk.jpg';
    if (s.includes('SUG')) return 'assets/products/sugar.jpg';
    if (s.includes('SALT')) return 'assets/products/tata_salt.jpg';
    if (s.includes('ATTA')) return 'assets/products/aashirvaad_atta.jpg';
    if (s.includes('MAGGI')) return 'assets/products/maggi.jpg';
    if (s.includes('PARLE')) return 'assets/products/parle_g.jpg';
    if (s.includes('FORT') || s.includes('OIL')) return 'assets/products/fortune_oil.jpg';
    if (s.includes('TUR') || s.includes('DAL')) return 'assets/products/tur_dal.jpg';
    if (s.includes('PAV') || s.includes('BAK')) return 'assets/products/ladi_pav.jpg';
    if (s.includes('KANDA') || s.includes('ONION')) return 'assets/products/red_onion.jpg';
    if (s.includes('BATATA') || s.includes('POTATO')) return 'assets/products/potato.jpg';
    if (s.includes('NOTEBOOK')) return 'assets/products/classmate_notebook.jpg';
    if (s.includes('PEN')) return 'assets/products/reynolds_pen.jpg';
    if (s.includes('KINLEY')) return 'assets/products/kinley_water.jpg';

    const n = ((name || '') + ' ' + (category || '')).toLowerCase();
    if (n.includes('milk') || n.includes('दूध') || n.includes('dairy')) return 'assets/products/amul_milk.jpg';
    if (n.includes('sugar') || n.includes('साखर')) return 'assets/products/sugar.jpg';
    if (n.includes('salt') || n.includes('मीठ')) return 'assets/products/tata_salt.jpg';
    if (n.includes('atta') || n.includes('आटा') || n.includes('पीठ')) return 'assets/products/aashirvaad_atta.jpg';
    if (n.includes('maggi') || n.includes('मॅगी')) return 'assets/products/maggi.jpg';
    if (n.includes('parle') || n.includes('पार्ले')) return 'assets/products/parle_g.jpg';
    if (n.includes('oil') || n.includes('तेल')) return 'assets/products/fortune_oil.jpg';
    if (n.includes('tur') || n.includes('dal') || n.includes('डाळ')) return 'assets/products/tur_dal.jpg';
    if (n.includes('pav') || n.includes('पाव')) return 'assets/products/ladi_pav.jpg';
    if (n.includes('kanda') || n.includes('onion') || n.includes('कांदा')) return 'assets/products/red_onion.jpg';
    if (n.includes('batata') || n.includes('potato') || n.includes('बटाटा')) return 'assets/products/potato.jpg';
    if (n.includes('notebook') || n.includes('वही')) return 'assets/products/classmate_notebook.jpg';
    if (n.includes('pen') || n.includes('पेन')) return 'assets/products/reynolds_pen.jpg';
    if (n.includes('water') || n.includes('पाणी')) return 'assets/products/kinley_water.jpg';

    return getCategoryPlaceholderSvg(category, name);
  }

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
  let skus = load(KEY_SKUS, null);
  if (!skus) {
    const oldV3 = load("vyapar_inventory_skus_v3", null);
    skus = oldV3 ? [...oldV3] : [...DEFAULT_SKUS];
  }
  if (Array.isArray(skus)) {
    // 1. Ensure all catalog default SKUs exist in active memory
    DEFAULT_SKUS.forEach(def => {
      const exists = skus.some(s => s.sku === def.sku || (s.aliases && s.aliases.includes(def.sku)));
      if (!exists) {
        skus.push({ ...def });
      }
    });

    // 2. Sanitize and synchronize max_capacity, full_stock & packshot mappings
    skus.forEach(s => {
      const def = DEFAULT_SKUS.find(d => d.sku === s.sku || (d.aliases && d.aliases.includes(s.sku)));
      if (def) {
        s.max_capacity = Number(def.max_capacity || 100);
        s.full_stock = Number(def.full_stock || def.max_capacity || 100);
      } else if (!s.max_capacity) {
        s.max_capacity = s.min_threshold ? s.min_threshold * 5 : 100.0;
        s.full_stock = s.max_capacity;
      }
      if (s.sku === "DAIRY-MILK-500ML" || s.sku === "DAIRY-AMUL-500M" || s.sku === "DAIRY-AMUL-500ML") {
        s.img = "assets/products/amul_milk.jpg";
      } else if (s.img && s.img.includes("parle_g") && !s.sku.includes("PARLE")) {
        s.img = resolveCatalogImg(s.sku, s.category, s.name_en || s.name_mr);
      }
    });
    save(KEY_SKUS, skus);
  }
  let customers = load(KEY_CUSTOMERS, DEFAULT_CUSTOMERS);
  let udharLedger = load(KEY_UDHAR, []);
  let transactions = load(KEY_TX, DEFAULT_TRANSACTIONS);
  let pendingOrders = load(KEY_ORDERS, DEFAULT_PENDING_ORDERS);
  let pendingOrdersNeedsSave = false;
  pendingOrders.forEach(o => {
    if (!o.timer_started_at) {
      o.timer_started_at = o.created_at ? new Date(o.created_at).getTime() : Date.now();
      pendingOrdersNeedsSave = true;
    }
    const elapsed = Math.floor((Date.now() - o.timer_started_at) / 1000);
    o.remaining_seconds = Math.max(0, 1800 - elapsed);
  });
  if (pendingOrdersNeedsSave) {
    save(KEY_ORDERS, pendingOrders);
  }
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

  // BroadcastChannel for cross-tab realtime sync (index.html <-> sales.html)
  let syncChannel = null;
  try {
    if (typeof BroadcastChannel !== 'undefined') {
      syncChannel = new BroadcastChannel('vyapar_realtime_sync');
      syncChannel.onmessage = function(ev) {
        if (ev.data && ev.data.type) {
          if (ev.data.type === 'PENDING_ORDERS_UPDATED') {
            pendingOrders = load(KEY_ORDERS, DEFAULT_PENDING_ORDERS);
          } else if (ev.data.type === 'TRANSACTIONS_UPDATED') {
            transactions = load(KEY_TX, DEFAULT_TRANSACTIONS);
          } else if (ev.data.type === 'METRICS_UPDATE' || ev.data.type === 'STOCK_UPDATED' || ev.data.type === 'VYAPAR_RESTOCK') {
            skus = load(KEY_SKUS, DEFAULT_SKUS);
          }
          const syncData = ev.data.data || (ev.data.products ? { products: ev.data.products } : { products: skus });
          notifySyncListeners(ev.data.type, syncData, false);
        }
      };
    }
  } catch(e) {}

  // Storage event listener for cross-tab reactive synchronization
  if (typeof window !== 'undefined' && window.addEventListener) {
    window.addEventListener('storage', (e) => {
      if (e.key === KEY_ORDERS) {
        try {
          pendingOrders = JSON.parse(e.newValue || '[]');
          if (Array.isArray(pendingOrders)) {
            pendingOrders.forEach(o => {
              if (!o.timer_started_at) {
                o.timer_started_at = o.created_at ? new Date(o.created_at).getTime() : Date.now();
              }
              const elapsed = Math.floor((Date.now() - o.timer_started_at) / 1000);
              o.remaining_seconds = Math.max(0, 1800 - elapsed);
            });
          }
        } catch(err){}
        notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
      } else if (e.key === KEY_SKUS) {
        try { skus = JSON.parse(e.newValue || '[]'); } catch(err){}
        notifySyncListeners("METRICS_UPDATE", { products: skus });
      } else if (e.key === KEY_TXNS || e.key === KEY_TX) {
        try { transactions = JSON.parse(e.newValue || '[]'); } catch(err){}
        notifySyncListeners("TRANSACTIONS_UPDATED", transactions);
      } else if (e.key === KEY_UDHAR) {
        try { udharLedger = JSON.parse(e.newValue || '[]'); } catch(err){}
        notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
      }
    });
  }

  function registerSyncListener(cb) {
    if (typeof cb === 'function') syncListeners.push(cb);
  }

  function notifySyncListeners(type, data, broadcast = true) {
    syncListeners.forEach(fn => {
      try { fn(type, data); } catch (e) { console.error("Sync listener error", e); }
    });
    if (broadcast && syncChannel) {
      try {
        const prodList = (data && data.products) ? data.products : skus;
        syncChannel.postMessage({ type, data, products: prodList });
      } catch(e) {}
    }
  }

  registerSyncListener((type, data) => {
    if (type === "PENDING_ORDERS_UPDATED") {
      if (typeof document !== 'undefined' && document.getElementById('yaadiOrdersFeedList')) {
        if (typeof VyaparCore !== 'undefined' && typeof VyaparCore.renderYaadiFeed === 'function') {
          VyaparCore.renderYaadiFeed('yaadiOrdersFeedList');
        } else if (typeof window !== 'undefined' && typeof window.renderPendingYaadiOrders === 'function') {
          window.renderPendingYaadiOrders('yaadiOrdersFeedList');
        }
      }
    }
  });

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
            const local = skus.find(s => s.sku === bp.sku || (bp.sku === 'DAIRY-MILK-500ML' && (s.sku === 'DAIRY-MILK-500ML' || s.sku === 'DAIRY-AMUL-500M' || s.sku === 'DAIRY-AMUL-500ML')) || (bp.sku === 'DAIRY-AMUL-500ML' && (s.sku === 'DAIRY-MILK-500ML' || s.sku === 'DAIRY-AMUL-500M')));
            const properImg = bp.img || resolveCatalogImg(bp.sku, bp.category, bp.name_en || bp.name_mr);
            if (local) {
              if (local.stock !== bp.stock || local.unit_price !== bp.unit_price) {
                hasChanged = true;
                local.stock = bp.stock;
                local.unit_price = bp.unit_price;
              }
              if (bp.max_capacity && local.max_capacity !== bp.max_capacity) {
                local.max_capacity = Number(bp.max_capacity);
                local.full_stock = Number(bp.full_stock || bp.max_capacity);
                hasChanged = true;
              }
              if (local.img && local.img.includes('parle_g') && !local.sku.includes('PARLE')) {
                local.img = properImg;
                hasChanged = true;
              }
            } else {
              const def = DEFAULT_SKUS.find(d => d.sku === bp.sku);
              const cap = Number(bp.max_capacity || (def ? def.max_capacity : (bp.min_threshold ? bp.min_threshold * 5 : 100)));
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
                max_capacity: cap,
                full_stock: cap,
                img: properImg,
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
              const existingMap = new Map();
              (pendingOrders || []).forEach(po => {
                const id = po.order_id || po.id;
                if (id) existingMap.set(id, po);
              });

              pendingOrders = ordData.orders.map(o => {
                const orderId = o.order_id || o.id;
                const existing = existingMap.get(orderId);
                // Permanent anchor timestamp: preserve existing anchor, or backend provided, or created_at, or Date.now()
                const timerStartedAt = (existing && existing.timer_started_at) ||
                  o.timer_started_at ||
                  (o.created_at ? new Date(o.created_at).getTime() : Date.now());
                const elapsed = Math.floor((Date.now() - timerStartedAt) / 1000);
                const remSecs = Math.max(0, 1800 - elapsed);

                return {
                  order_id: orderId,
                  id: orderId,
                  customer_name: o.customer_name || o.customerName || (existing && existing.customer_name) || "व्यंकटेश पै (Venkatesh Pai)",
                  customerName: o.customer_name || o.customerName || (existing && existing.customerName) || "व्यंकटेश पै (Venkatesh Pai)",
                  customer_phone: o.customer_phone || o.phone || (existing && existing.customer_phone) || "+91 70192 59321",
                  phone: o.customer_phone || o.phone || (existing && existing.phone) || "+91 70192 59321",
                  area: o.area || (existing && existing.area) || "Kolhapur Walk-in",
                  time: o.timestamp || (o.created_at ? new Date(o.created_at).toLocaleTimeString() : (existing && existing.time) || "Just now"),
                  timestamp: o.timestamp || (o.created_at ? new Date(o.created_at).toLocaleTimeString() : (existing && existing.timestamp) || "Just now"),
                  slip_type: o.slip_type || (existing && existing.slip_type) || "WhatsApp Yaadi Slip",
                  items_text: o.raw_message || o.rawText || (existing && existing.items_text) || "किराणा यादी",
                  rawText: o.raw_message || o.rawText || (existing && existing.rawText) || "किराणा यादी",
                  raw_message: o.raw_message || (existing && existing.raw_message) || "किराणा यादी",
                  items: Array.isArray(o.items) && o.items.length > 0 ? o.items.map(it => ({
                    name: it.name_mr || it.name_raw || it.name || "किराणा सामान",
                    qty: it.quantity || it.qty || 1,
                    unit: it.unit || "piece",
                    price: it.unit_price || it.price || 0,
                    total: it.line_total || it.total || 0,
                    sku: it.sku_matched || it.sku || ""
                  })) : ((existing && existing.items) || []),
                  total_amount: parseFloat(o.total_amount || o.totalEstimated || (existing && existing.total_amount) || 0),
                  totalEstimated: parseFloat(o.total_amount || o.totalEstimated || (existing && existing.totalEstimated) || 0),
                  status: o.status || (existing && existing.status) || "PENDING",
                  is_stock_reserved: o.is_stock_reserved !== undefined ? o.is_stock_reserved : (existing ? existing.is_stock_reserved : true),
                  confirmed_by_customer: o.confirmed_by_customer !== undefined ? o.confirmed_by_customer : (existing ? existing.confirmed_by_customer : false),
                  timer_started_at: timerStartedAt,
                  remaining_seconds: remSecs,
                  created_at: o.created_at || (existing && existing.created_at) || new Date(timerStartedAt).toISOString()
                };
              });

              // Retain any existing local orders that backend might not have yet
              existingMap.forEach((val, key) => {
                if (!pendingOrders.some(p => (p.order_id === key || p.id === key))) {
                  pendingOrders.push(val);
                }
              });

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

  let yaadiTimerTickerInterval = null;
  function startYaadiTimerTicker() {
    if (yaadiTimerTickerInterval || typeof window === 'undefined') return;
    yaadiTimerTickerInterval = setInterval(() => {
      if (!pendingOrders || pendingOrders.length === 0) return;
      pendingOrders.forEach(ord => {
        const orderId = ord.order_id || ord.id;
        if (!orderId) return;

        const status = (ord.status || 'PENDING').toUpperCase();
        const isFulfilled = status === 'PACKED' || status === 'FULFILLED';
        const isCancelled = status === 'CANCELLED' || status === 'EXPIRED_AUTO_CANCELLED' || status === 'EXPIRED';

        if (!isFulfilled && !isCancelled) {
          if (!ord.timer_started_at) {
            ord.timer_started_at = ord.created_at ? new Date(ord.created_at).getTime() : Date.now();
          }
          const elapsed = Math.floor((Date.now() - ord.timer_started_at) / 1000);
          const remSecs = Math.max(0, 1800 - elapsed);
          ord.remaining_seconds = remSecs;

          const timerEl = document.getElementById('order-timer-' + orderId);
          if (timerEl) {
            const m = Math.floor(remSecs / 60);
            const s = Math.floor(remSecs % 60);
            const formatted = (remSecs <= 0) ? "00:00 (Expired)" : `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
            timerEl.textContent = '⏳ ' + formatted;
            if (remSecs === 0) {
              timerEl.style.background = 'rgba(255, 69, 58, 0.25)';
            }
          }
        }
      });
    }, 1000);
  }

  function ensureYaadiStyles() {
    if (typeof document === 'undefined') return;
    if (document.getElementById('vyapar-yaadi-core-styles')) return;
    const style = document.createElement('style');
    style.id = 'vyapar-yaadi-core-styles';
    style.textContent = `
      .yaadi-order-box.cancelled {
        opacity: 0.65;
        background: rgba(255, 245, 245, 0.6);
        border-color: rgba(255, 69, 58, 0.3);
      }
      .yaadi-order-box.fulfilled {
        opacity: 0.65;
        background: rgba(245, 248, 245, 0.6);
        border-color: rgba(40, 205, 65, 0.3);
      }
      .yaadi-actions-btns {
        display: flex;
        gap: 6px;
        align-items: center;
      }
    `;
    document.head.appendChild(style);
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
      if (!skuCode) return null;
      let found = skus.find(s => s.sku === skuCode);
      if (found) return found;
      // Normalization / alias fallback
      if (skuCode === 'DAIRY-MILK-500ML' || skuCode === 'DAIRY-AMUL-500M' || skuCode === 'DAIRY-AMUL-500ML') {
        return skus.find(s => s.sku === 'DAIRY-MILK-500ML' || s.sku === 'DAIRY-AMUL-500M' || s.sku === 'DAIRY-AMUL-500ML');
      }
      return null;
    },
    getProductImage: function(item) {
      if (!item) return 'assets/products/placeholder.svg';
      const sku = (typeof item === 'string' ? item : item.sku) || '';
      const cat = (typeof item === 'object' ? item.category : '') || '';
      const name = (typeof item === 'object' ? (item.name_en || item.name_mr || '') : '') || '';
      const providedImg = (typeof item === 'object' && item.img) ? item.img : null;

      // Exact SKU mapping
      const skuMap = {
        'DAIRY-MILK-500ML': 'assets/products/amul_milk.jpg',
        'DAIRY-AMUL-500M': 'assets/products/amul_milk.jpg',
        'DAIRY-AMUL-500ML': 'assets/products/amul_milk.jpg',
        'GROC-SUG-001': 'assets/products/sugar.jpg',
        'GROC-SALT-1K': 'assets/products/tata_salt.jpg',
        'GROC-ATTA-5K': 'assets/products/aashirvaad_atta.jpg',
        'FMCG-MAGGI-70G': 'assets/products/maggi.jpg',
        'FMCG-PARLE-100G': 'assets/products/parle_g.jpg',
        'OIL-FORT-1L': 'assets/products/fortune_oil.jpg',
        'DAL-TUR-001': 'assets/products/tur_dal.jpg',
        'BAK-PAV-LADI': 'assets/products/ladi_pav.jpg',
        'VEG-KANDA-001': 'assets/products/red_onion.jpg',
        'VEG-BATATA-001': 'assets/products/potato.jpg',
        'AUTO-VID-NOTEBOOK': 'assets/products/classmate_notebook.jpg',
        'AUTO-VID-PEN': 'assets/products/reynolds_pen.jpg',
        'AUTO-VID-KINLEY': 'assets/products/kinley_water.jpg',
        'FMCG-COLG-100G': 'assets/products/colgate.jpg'
      };
      if (sku && skuMap[sku]) return skuMap[sku];

      // If valid image provided and it's NOT an erroneous parle_g fallback on a non-parle item
      if (providedImg && !providedImg.includes('placeholder')) {
        const isParleSku = sku.includes('PARLE') || name.toLowerCase().includes('parle');
        if (!providedImg.includes('parle_g') || isParleSku) {
          return providedImg;
        }
      }

      // Check catalog by SKU
      const catalogItem = this.getSKU(sku);
      if (catalogItem && catalogItem.img && (!catalogItem.img.includes('parle_g') || sku.includes('PARLE'))) {
        return catalogItem.img;
      }

      return resolveCatalogImg(sku, cat, name);
    },
    getFallbackImage: function(category, sku) {
      return resolveCatalogImg(sku, category, '');
    },
    addStock: async function(skuCode, addQty, reason = "Manual UI Stock Add") {
      let item = skus.find(s => s.sku === skuCode);
      if (!item && (skuCode === 'DAIRY-MILK-500ML' || skuCode === 'DAIRY-AMUL-500M' || skuCode === 'DAIRY-AMUL-500ML')) {
        item = skus.find(s => s.sku === 'DAIRY-MILK-500ML' || s.sku === 'DAIRY-AMUL-500M' || s.sku === 'DAIRY-AMUL-500ML');
      }
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
      const cidStr = String(creditId);
      const numAmt = Number(amount) || 0;

      // Ensure udharLedger is initialized
      if (!udharLedger || udharLedger.length === 0) {
        udharLedger = JSON.parse(JSON.stringify(customers && customers.length > 0 ? customers : DEFAULT_CUSTOMERS));
        save(KEY_UDHAR, udharLedger);
      }

      // Find target customer in ledger or customers list
      let targetCust = udharLedger.find(c => String(c.id) === cidStr || String(c.id).includes(cidStr)) ||
                       customers.find(c => String(c.id) === cidStr || String(c.id).includes(cidStr));

      if (targetCust) {
        if (targetCust.amount_due !== undefined) {
          targetCust.amount_due = Math.max(0, parseFloat((targetCust.amount_due - numAmt).toFixed(2)));
          if (targetCust.amount_due <= 0) targetCust.status = "PAID";
        }
        if (targetCust.udhar !== undefined) {
          targetCust.udhar = Math.max(0, parseFloat((targetCust.udhar - numAmt).toFixed(2)));
          if (targetCust.udhar <= 0) targetCust.status = "SETTLED";
        }
        targetCust.last_tx = `Just now (Paid ₹${numAmt} via ${mode})`;
        targetCust.last_payment_date = new Date().toISOString();
        save(KEY_UDHAR, udharLedger);
      }

      // Also ensure customers array entry is updated
      const localCust = customers.find(c => String(c.id) === cidStr || String(c.id).includes(cidStr));
      if (localCust) {
        localCust.udhar = Math.max(0, parseFloat(((localCust.udhar || 0) - numAmt).toFixed(2)));
        if (localCust.udhar <= 0) localCust.status = "SETTLED";
        localCust.last_tx = `Just now (Paid ₹${numAmt} via ${mode})`;
        save(KEY_CUSTOMERS, customers);
      }

      // Log transaction
      const custDisplayName = (targetCust && (targetCust.customer_name || targetCust.name)) || (localCust && localCust.name) || "Khata Customer";
      const loggedTx = this.addTransaction({
        type: "SALE",
        mode: mode.includes("UPI") ? "UPI Soundbox" : (mode.includes("Cash") ? "Cash Counter" : "UPI Soundbox"),
        cust: custDisplayName,
        items: `Khata Udhar Payment (₹${numAmt})`,
        amount: numAmt,
        status: "Success"
      });
      this.playSoundboxChime(numAmt);
      notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);

      // Attempt live backend synchronization
      try {
        const url = `${getBackendUrl()}/api/udhar/${creditId}/pay`;
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ amount: numAmt, payment_mode: mode, notes: notes })
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
          return data;
        }
      } catch (e) {
        console.warn("[VyaparCore] Backend settle khata sync failed (offline optimistic state active):", e);
      }
      return { status: "SUCCESS", offline: true, customer: targetCust || localCust, transaction: loggedTx };
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
        console.warn("[VyaparCore] Create customer account backend sync failed (saving locally):", e);
      }

      // Offline fallback: save locally
      const localId = "c" + (customers.length + 1);
      const offlineCust = {
        id: localId,
        customer_name: payload.customer_name || payload.name,
        name: payload.customer_name || payload.name,
        area: payload.notes || payload.area || "Kolhapur Ward",
        customer_phone: payload.customer_phone || payload.phone,
        phone: payload.customer_phone || payload.phone,
        amount_due: parseFloat(payload.amount_due || payload.amount || 0),
        udhar: parseFloat(payload.amount_due || payload.amount || 0),
        status: "DUE_SOON",
        due_date: payload.due_date || "तात्काळ (Immediate)",
        last_tx: "Just now (Account Opened)",
        trust: "A",
        orders: 1,
        pref: "Counter Walk-in / Udhar"
      };
      customers.unshift(offlineCust);
      save(KEY_CUSTOMERS, customers);
      if (Array.isArray(udharLedger)) {
        udharLedger.unshift(offlineCust);
        save(KEY_UDHAR, udharLedger);
        notifySyncListeners("UDHAR_LEDGER_UPDATED", udharLedger);
      }
      return { status: "SUCCESS", offline: true, credit: offlineCust };
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
        notifySyncListeners("METRICS_UPDATE", { products: skus });
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
      notifySyncListeners("METRICS_UPDATE", { products: skus });
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
      notifySyncListeners("TRANSACTIONS_UPDATED", transactions);
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
      let ordersUpdated = false;
      pendingOrders.forEach(order => {
        if (!order.timer_started_at) {
          order.timer_started_at = order.created_at ? new Date(order.created_at).getTime() : Date.now();
          ordersUpdated = true;
        }
        const elapsed = Math.floor((Date.now() - order.timer_started_at) / 1000);
        const remSecs = Math.max(0, 1800 - elapsed);
        if (order.remaining_seconds !== remSecs) {
          order.remaining_seconds = remSecs;
        }
      });
      if (ordersUpdated) {
        save(KEY_ORDERS, pendingOrders);
      }
      return pendingOrders;
    },
    addPendingCustomerOrder: function(order) {
      const orderId = order.order_id || order.id || ("ORD-KOP-" + Math.floor(1000 + Math.random() * 9000));
      const existing = pendingOrders.find(o => o.order_id === orderId || o.id === orderId);

      const timerStartedAt = (existing && existing.timer_started_at) ||
        order.timer_started_at ||
        (order.created_at ? new Date(order.created_at).getTime() : Date.now());
      const elapsed = Math.floor((Date.now() - timerStartedAt) / 1000);
      const remSecs = Math.max(0, 1800 - elapsed);

      const newOrder = {
        order_id: orderId,
        id: orderId,
        customer_name: order.customer_name || order.customerName || (existing && existing.customer_name) || "व्यंकटेश पै (Venkatesh Pai)",
        customerName: order.customer_name || order.customerName || (existing && existing.customerName) || "व्यंकटेश पै (Venkatesh Pai)",
        customer_phone: order.customer_phone || order.phone || (existing && existing.customer_phone) || "+91 98220 12345",
        phone: order.customer_phone || order.phone || (existing && existing.phone) || "+91 98220 12345",
        area: order.area || (existing && existing.area) || "Kolhapur Walk-in",
        time: order.time || order.timestamp || "Just now",
        timestamp: order.timestamp || order.time || "Just now",
        slip_type: order.slip_type || "WhatsApp Yaadi Slip",
        items_text: order.items_text || order.rawText || "किराणा यादी",
        rawText: order.items_text || order.rawText || "किराणा यादी",
        raw_message: order.raw_message || order.rawText || "किराणा यादी",
        items: order.items || (existing && existing.items) || [],
        total_amount: parseFloat(order.total_amount || order.totalEstimated || (existing && existing.total_amount) || 0),
        totalEstimated: parseFloat(order.total_amount || order.totalEstimated || (existing && existing.totalEstimated) || 0),
        status: order.status || (existing && existing.status) || "PENDING",
        is_stock_reserved: order.is_stock_reserved !== undefined ? order.is_stock_reserved : (existing ? existing.is_stock_reserved : false),
        confirmed_by_customer: order.confirmed_by_customer !== undefined ? order.confirmed_by_customer : (existing ? existing.confirmed_by_customer : false),
        timer_started_at: timerStartedAt,
        remaining_seconds: remSecs,
        created_at: order.created_at || (existing && existing.created_at) || new Date(timerStartedAt).toISOString()
      };

      if (existing) {
        Object.assign(existing, newOrder);
      } else {
        pendingOrders.unshift(newOrder);
      }
      save(KEY_ORDERS, pendingOrders);
      notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);
      return newOrder;
    },
    packAndFulfillOrder: function(orderId) {
      const order = pendingOrders.find(o => o.order_id === orderId || o.id === orderId);
      if (order && (order.status === "PENDING" || order.status === "CONFIRMED")) {
        // Zero Double-Deduction Guard: Decrement master stock from active inventory upon merchant fulfillment
        if (Array.isArray(order.items)) {
          order.items.forEach(item => {
            const skuCode = item.sku || item.sku_matched;
            const qty = parseFloat(item.qty || item.quantity || 0);
            if (skuCode && qty > 0) {
              const matched = skus.find(s => s.sku === skuCode);
              if (matched) {
                matched.stock = Math.max(0, parseFloat((Number(matched.stock) - qty).toFixed(2)));
              }
            }
          });
          save(KEY_SKUS, skus);
          notifySyncListeners("METRICS_UPDATE", { products: skus });
        }

        // Add to Sales Ledger
        const itemsSummary = order.items_text || order.rawText || (Array.isArray(order.items) ? order.items.map(i => `${i.qty || i.quantity || 1}x ${i.name || i.name_mr || 'Item'}`).join(' + ') : "किराणा यादी");
        const totalAmt = parseFloat(order.total_amount || order.totalEstimated || 0);
        this.addTransaction({
          type: "SALE",
          mode: "WhatsApp Yaadi (Fulfilled)",
          cust: order.customer_name || order.customerName || "व्यंकटेश पै",
          items: itemsSummary,
          amount: totalAmt,
          status: "Success"
        });

        order.status = "PACKED";
        order.fulfilled_at = new Date().toLocaleTimeString();
        save(KEY_ORDERS, pendingOrders);
        notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);

        // Synchronize with cloud backend
        const bUrl = typeof getBackendUrl === "function" ? getBackendUrl() : "";
        fetch(`${bUrl}/api/orders/${orderId}/pack`, { method: "POST" })
          .then(r => r.json())
          .then(res => {
            if (res && res.metrics) {
              performLiveSync();
            }
          })
          .catch(e => console.log("[PACK API WARN]:", e));

        this.playSoundboxChime(totalAmt);
        return { success: true, order };
      }
      return { success: false, message: "Order not found or already packed" };
    },
    cancelAndRestoreOrder: function(orderId) {
      const order = pendingOrders.find(o => o.order_id === orderId || o.id === orderId);
      if (order && (order.status === "PENDING" || order.status === "CONFIRMED")) {
        order.status = "CANCELLED";
        save(KEY_ORDERS, pendingOrders);
        notifySyncListeners("PENDING_ORDERS_UPDATED", pendingOrders);

        const bUrl = typeof getBackendUrl === "function" ? getBackendUrl() : "";
        fetch(`${bUrl}/api/orders/${orderId}/expire-now`, { method: "POST" })
          .then(r => r.json())
          .then(res => {
            if (res && res.metrics) {
              performLiveSync();
            }
          })
          .catch(e => console.log("[CANCEL API WARN]:", e));

        return { success: true, order };
      }
      return { success: false, message: "Order not found or already finalized" };
    },

    packCustomerOrder: function(orderId) {
      if (typeof window !== 'undefined' && window.haptics) {
        if (typeof window.haptics.tap === 'function') window.haptics.tap();
        else if (typeof window.haptics.playTick === 'function') window.haptics.playTick();
      }
      const res = this.packAndFulfillOrder(orderId);
      if (res && res.success) {
        const cust = res.order.customerName || res.order.customer_name || 'व्यंकटेश पै';
        const total = parseFloat(res.order.totalEstimated || res.order.total_amount || 0);
        if (typeof window !== 'undefined' && typeof window.showAppleToast === 'function') {
          window.showAppleToast(`Packed order for ${cust}! Stock finalized ₹${total}.`);
        }
        if (typeof document !== 'undefined') {
          const salesEl = document.getElementById('statTotalSales') || document.getElementById('statSalesToday');
          const ordersEl = document.getElementById('statOrdersCount') || document.getElementById('statInvoices');
          if (salesEl) {
            const cur = parseInt(salesEl.textContent.replace(/[₹,]/g, '')) || 0;
            if (typeof window.animateCounter === 'function') {
              window.animateCounter(salesEl.id, cur, cur + total, 800, '₹');
            } else {
              salesEl.textContent = '₹' + (cur + total).toLocaleString('en-IN');
            }
          }
          if (ordersEl) {
            const curO = parseInt(ordersEl.textContent) || 0;
            if (typeof window.animateCounter === 'function') {
              window.animateCounter(ordersEl.id, curO, curO + 1, 500);
            } else {
              ordersEl.textContent = (curO + 1);
            }
          }
          const feed = document.getElementById('recentSalesFeedList');
          if (feed) {
            const newRow = document.createElement('div');
            newRow.className = 'sale-feed-row';
            newRow.innerHTML = `
              <div class="sale-feed-left">
                <div class="sale-icon-box basket">
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                  </svg>
                </div>
                <div class="sale-meta-group">
                  <span class="sale-item-title">Customer Yaadi (${cust})</span>
                  <span class="sale-timestamp tabular-nums">Just now</span>
                </div>
              </div>
              <span class="sale-customer-tag" style="color: var(--apple-green); font-weight: 700;">+₹${total}</span>
            `;
            feed.insertBefore(newRow, feed.firstChild);
          }
          if (typeof window.updateSalesHeaderMetrics === 'function') {
            window.updateSalesHeaderMetrics();
          }
          if (typeof window.renderSalesTable === 'function') {
            window.renderSalesTable();
          }
        }
        this.renderYaadiFeed('yaadiOrdersFeedList');
      } else if (res && !res.success) {
        if (typeof window !== 'undefined' && typeof window.showAppleToast === 'function') {
          window.showAppleToast(res.message || res.error || "Failed to pack order");
        }
      }
      return res;
    },

    cancelCustomerOrder: function(orderId) {
      if (typeof window !== 'undefined' && window.haptics) {
        if (typeof window.haptics.tap === 'function') window.haptics.tap();
        else if (typeof window.haptics.playTick === 'function') window.haptics.playTick();
      }
      const res = this.cancelAndRestoreOrder(orderId);
      if (res && res.success) {
        if (typeof window !== 'undefined' && typeof window.showAppleToast === 'function') {
          window.showAppleToast(`🔄 Order ${orderId} cancelled & stock restored to active inventory!`);
        }
        this.renderYaadiFeed('yaadiOrdersFeedList');
      } else if (res && !res.success) {
        if (typeof window !== 'undefined' && typeof window.showAppleToast === 'function') {
          window.showAppleToast(res.message || res.error || "Failed to cancel order");
        }
      }
      return res;
    },

    formatTimerSeconds: function(secs) {
      if (secs === undefined || secs === null || isNaN(secs) || secs <= 0) return "00:00 (Expired)";
      const total = Math.floor(secs);
      const m = Math.floor(total / 60);
      const s = total % 60;
      return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
    },

    getOrderBoxBadgesHtml: function(order, remSecs) {
      const orderId = order.order_id || order.id;
      const isFulfilled = order.status === 'PACKED' || order.status === 'FULFILLED';
      const isCancelled = order.status === 'CANCELLED' || order.status === 'EXPIRED_AUTO_CANCELLED' || order.status === 'EXPIRED';
      const isConfirmed = (order.status === 'CONFIRMED' || order.confirmed_by_customer) && !isFulfilled && !isCancelled;

      if (isFulfilled) {
        return `
          <span class="status-pill status-in" style="font-size: 0.70rem; background: rgba(52, 199, 89, 0.15); color: #28cd41; border: 1px solid rgba(52, 199, 89, 0.3); font-weight: 600;">
            ✅ साठा वजा (Packed & Fulfilled)
          </span>
        `;
      } else if (isCancelled) {
        return `
          <span class="status-pill status-out" style="font-size: 0.70rem; background: rgba(255, 69, 58, 0.12); color: #ff453a; border: 1px solid rgba(255, 69, 58, 0.28); font-weight: 600;">
            ↩ रद्द / साठा पूर्ववत (Cancelled & Restituted)
          </span>
        `;
      } else if (isConfirmed) {
        return `
          <span class="status-pill status-in" style="font-size: 0.70rem; background: rgba(0, 113, 227, 0.12); color: #0071e3; border: 1px solid rgba(0, 113, 227, 0.28); font-weight: 600;">
            ✓ ग्राहक निश्चिती (Customer Confirmed)
          </span>
          <span class="order-timer-pill" id="order-timer-${orderId}" style="font-size: 0.70rem; padding: 2px 7px; border-radius: 999px; background: rgba(255, 149, 0, 0.12); color: #ff9500; font-weight: 700; border: 1px solid rgba(255, 149, 0, 0.28);">⏳ ${this.formatTimerSeconds(remSecs)}</span>
        `;
      } else {
        return `
          <span class="status-pill status-low" style="font-size: 0.70rem; background: rgba(255, 149, 0, 0.12); color: #ff9500; border: 1px solid rgba(255, 149, 0, 0.28); font-weight: 600;">
            📋 मागणी प्रलंबित (Pending Approval / Staged)
          </span>
          <span class="order-timer-pill" id="order-timer-${orderId}" style="font-size: 0.70rem; padding: 2px 7px; border-radius: 999px; background: rgba(255, 69, 58, 0.12); color: #ff453a; font-weight: 700; border: 1px solid rgba(255, 69, 58, 0.28);">⏳ ${this.formatTimerSeconds(remSecs)}</span>
        `;
      }
    },

    getOrderBoxButtonsHtml: function(order) {
      const orderId = order.order_id || order.id;
      const safeOrderId = String(orderId).replace(/'/g, "\\'");
      const isFulfilled = order.status === 'PACKED' || order.status === 'FULFILLED';
      const isCancelled = order.status === 'CANCELLED' || order.status === 'EXPIRED_AUTO_CANCELLED' || order.status === 'EXPIRED';

      return `
        <button 
          class="btn-pack-order" 
          onclick="VyaparCore.packCustomerOrder('${safeOrderId}')"
          ${(isFulfilled || isCancelled) ? 'disabled style="opacity: 0.6; cursor: not-allowed;"' : ''}>
          ${isFulfilled ? '✓ Delivered' : (isCancelled ? '✕ Cancelled' : 'Pack & Fulfill ✓')}
        </button>
        ${(!isFulfilled && !isCancelled) ? `
        <button 
          class="btn-stock" 
          style="font-size: 0.72rem; padding: 5px 10px; border-radius: 999px; background: rgba(255, 69, 58, 0.12); color: #ff453a; border: 1px solid rgba(255, 69, 58, 0.25); cursor: pointer;"
          onclick="VyaparCore.cancelCustomerOrder('${safeOrderId}')"
          title="30-min Auto-Undo: Cancel order and restitute reserved stock immediately">
          Undo Stock 🔄
        </button>` : ''}
      `;
    },

    getOrderBoxInnerHtml: function(order, remSecs) {
      const custName = order.customerName || order.customer_name || "व्यंकटेश पै (Venkatesh Pai)";
      const custPhone = order.phone || order.customer_phone || "+91 98220 12345";
      const totalEst = parseFloat(order.totalEstimated || order.total_amount || 0);
      const orderItems = Array.isArray(order.items) ? order.items : [];

      return `
        <div class="yaadi-order-header">
          <div class="yaadi-cust-info">
            <div class="yaadi-cust-avatar">${custName.charAt(0)}</div>
            <div>
              <div class="yaadi-cust-name">${custName}</div>
              <div class="yaadi-cust-phone">${custPhone} • ${order.timestamp || order.time || 'Just now'}</div>
            </div>
          </div>
          <div class="yaadi-status-badges" style="display: flex; gap: 6px; align-items: center; flex-wrap: wrap;">
            ${this.getOrderBoxBadgesHtml(order, remSecs)}
          </div>
        </div>
        
        <div class="yaadi-items-list">
          <strong>Order Slip:</strong> "${order.rawText || order.raw_message || order.items_text || 'किराणा यादी'}"<br/>
          <span style="font-size: 0.75rem; color: var(--text-tertiary);">Parsed items: ${orderItems.map(i => `${i.qty || i.quantity || 1}x ${i.name || i.name_mr || 'सामान'}`).join(', ') || 'साखर २ किलो, तेल १ लिटर, पार्ले-जी ५ पुडे, गोकुळ दूध १ पिशवी'}</span>
        </div>

        <div class="yaadi-footer-row" style="display: flex; justify-content: space-between; align-items: center; gap: 8px;">
          <div class="yaadi-est-total">Est. Total: ₹${totalEst}</div>
          <div class="yaadi-actions-btns" style="display: flex; gap: 6px;">
            ${this.getOrderBoxButtonsHtml(order)}
          </div>
        </div>
      `;
    },

    renderYaadiFeed: function(containerId = 'yaadiOrdersFeedList', options = {}) {
      if (typeof document === 'undefined') return;
      ensureYaadiStyles();
      let targetId = 'yaadiOrdersFeedList';
      if (typeof containerId === 'string' && containerId.trim()) {
        targetId = containerId.trim();
      } else if (containerId && typeof containerId === 'object' && containerId.containerId) {
        targetId = containerId.containerId;
      } else if (options && options.containerId) {
        targetId = options.containerId;
      }

      const container = typeof targetId === 'string' ? document.getElementById(targetId) : targetId;
      if (!container) return;

      const orders = this.getPendingOrders();
      if (!orders || orders.length === 0) {
        if (!container.querySelector('.yaadi-empty-placeholder')) {
          container.innerHTML = `
            <div class="yaadi-empty-placeholder" style="text-align: center; padding: 24px; color: var(--text-tertiary, #8e8e93); font-size: 0.82rem;">
              No pending customer yaadi slips right now. Orders arriving on WhatsApp (+91 98230...) will appear here live.
            </div>
          `;
        }
        return;
      }

      const placeholder = container.querySelector('.yaadi-empty-placeholder');
      if (placeholder) {
        placeholder.remove();
      }

      const activeOrderIds = new Set();
      orders.forEach((order, index) => {
        const orderId = order.order_id || order.id;
        if (!orderId) return;
        activeOrderIds.add(orderId);

        if (!order.timer_started_at) {
          order.timer_started_at = order.created_at ? new Date(order.created_at).getTime() : Date.now();
        }
        const elapsed = Math.floor((Date.now() - order.timer_started_at) / 1000);
        const remSecs = Math.max(0, 1800 - elapsed);
        order.remaining_seconds = remSecs;

        const isFulfilled = order.status === 'PACKED' || order.status === 'FULFILLED';
        const isCancelled = order.status === 'CANCELLED' || order.status === 'EXPIRED_AUTO_CANCELLED' || order.status === 'EXPIRED';
        const targetClass = `yaadi-order-box ${isFulfilled ? 'fulfilled' : (isCancelled ? 'cancelled' : '')}`;

        let box = document.getElementById('yaadi-order-' + orderId);
        if (box) {
          const currentStatus = (box.dataset && box.dataset.orderStatus) || (box.getAttribute && box.getAttribute('data-order-status'));
          if (currentStatus !== order.status) {
            if (box.dataset) box.dataset.orderStatus = order.status;
            if (box.setAttribute) box.setAttribute('data-order-status', order.status);
            box.className = targetClass;
            const badges = box.querySelector ? box.querySelector('.yaadi-status-badges') : null;
            if (badges) badges.innerHTML = this.getOrderBoxBadgesHtml(order, remSecs);
            const btns = box.querySelector ? box.querySelector('.yaadi-actions-btns') : null;
            if (btns) btns.innerHTML = this.getOrderBoxButtonsHtml(order);
          } else {
            const timerEl = document.getElementById('order-timer-' + orderId);
            if (timerEl) {
              timerEl.textContent = '⏳ ' + this.formatTimerSeconds(remSecs);
              if (remSecs === 0 && (order.status === 'PENDING' || order.status === 'CONFIRMED')) {
                if (timerEl.style) timerEl.style.background = 'rgba(255, 69, 58, 0.25)';
              }
            }
          }
        } else {
          box = document.createElement('div');
          box.id = 'yaadi-order-' + orderId;
          if (box.dataset) box.dataset.orderStatus = order.status;
          if (box.setAttribute) box.setAttribute('data-order-status', order.status);
          box.className = targetClass;
          box.innerHTML = this.getOrderBoxInnerHtml(order, remSecs);
          container.appendChild(box);
        }

        const currentBoxes = Array.from(container.children).filter(el => el.classList && el.classList.contains('yaadi-order-box'));
        if (currentBoxes[index] !== box) {
          if (index < currentBoxes.length) {
            container.insertBefore(box, currentBoxes[index]);
          } else {
            container.appendChild(box);
          }
        }
      });

      const existingBoxes = container.querySelectorAll('.yaadi-order-box');
      existingBoxes.forEach(b => {
        const id = b.id.replace('yaadi-order-', '');
        if (!activeOrderIds.has(id)) {
          b.remove();
        }
      });

      startYaadiTimerTicker();
    },

    // -------------------------------------------------------------------------
    // 4. SUB-1ms REVERSE-MATH ENGINE (Voice-to-Scale)
    // -------------------------------------------------------------------------
    calculateReverseMath: function(query) {
      const marathiDigits = ['\u0966', '\u0967', '\u0968', '\u0969', '\u096a', '\u096b', '\u096c', '\u096d', '\u096e', '\u096f'];
      let cleanText = (query || "").trim().toLowerCase();
      marathiDigits.forEach((d, i) => { cleanText = cleanText.replaceAll(d, i.toString()); });

      const t0 = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();

      // Check colloquial units
      const isPavsher = cleanText.includes("पावशेर") || cleanText.includes("pavsher") || cleanText.includes("पाव किलो") || cleanText.includes("pav kilo");
      const isArdha = cleanText.includes("अर्धा") || cleanText.includes("ardha") || cleanText.includes("half");
      const isSavva = cleanText.includes("सव्वा") || cleanText.includes("savva");
      const isDidh = cleanText.includes("दीड") || cleanText.includes("didh") || cleanText.includes("deedh");

      // Mask colloquial weight terms to prevent false-matching items like "पाव" in "पावशेर"
      const textForItemMatch = cleanText
        .replace(/पावशेर|pavsher|पाव\s*किलो|pav\s*kilo/g, " ")
        .replace(/सव्वा\s*(?:किलो)?|savva/g, " ")
        .replace(/अर्धा\s*(?:किलो)?|ardha|half/g, " ")
        .replace(/दीड\s*(?:किलो)?|didh|deedh/g, " ");

      // Match item from catalog
      let matchedSKU = null;
      for (const item of skus) {
        if (textForItemMatch.includes(item.short_name.toLowerCase())) {
          matchedSKU = item;
          break;
        }
        if (item.name_mr && textForItemMatch.includes(item.name_mr.toLowerCase())) {
          matchedSKU = item;
          break;
        }
        if (item.aliases && item.aliases.some(a => textForItemMatch.includes(a.toLowerCase()))) {
          matchedSKU = item;
          break;
        }
      }

      if (!matchedSKU) {
        matchedSKU = skus.find(s => s.sku === "GROC-SUG-001") || skus[0];
      }

      const tNow = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();
      const latency = (tNow - t0 + 0.015).toFixed(3);

      if (isPavsher) {
        const grams = 250;
        const bill = parseFloat(((grams / 1000) * matchedSKU.unit_price).toFixed(2));
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
        const bill = parseFloat(((grams / 1000) * matchedSKU.unit_price).toFixed(2));
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
        const bill = parseFloat(((grams / 1000) * matchedSKU.unit_price).toFixed(2));
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

      if (isDidh) {
        const grams = 1500;
        const bill = parseFloat(((grams / 1000) * matchedSKU.unit_price).toFixed(2));
        return {
          mode: "COLLOQUIAL_WEIGHT",
          grams: grams,
          bill: bill,
          sku: matchedSKU.sku,
          item_name: matchedSKU.name_mr,
          latency_ms: latency,
          scale_display: `⚖️ काट्यावर ठेवा: १५०० ग्रॅम (१.५ किग्रॅ) ${matchedSKU.name_mr}`,
          reply_text: `⚖️ काट्यावर ठेवा: १५०० ग्रॅम ${matchedSKU.name_mr} (दर: ₹${matchedSKU.unit_price}/किग्रॅ, बिल: ₹${bill.toFixed(2)})`
        };
      }

      // 1. Money-to-Weight (e.g. "20 chi sakhar", "साखर २० रु", "50 rupayache tel", "100 rupyachi tur dal", "50 rs sugar")
      const moneyMatch = cleanText.match(/(?:(?:rs\.?|inr|₹|रु\.?|रुपये|रुपयांची|रुपयांचे|rupees)\s*(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)\s*(?:chi|che|chya|ची|चे|च्या|rupayache|rupayachi|rupayanche|rupaye|rupees|rs\.?|inr|₹|रु\.?|रुपये|रुपयांची|रुपयांचे))/i);
      if (moneyMatch) {
        const money = parseFloat(moneyMatch[1] || moneyMatch[2]);
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
      const weightMatch = cleanText.match(/(\d+(?:\.\d+)?)\s*(?:gm|g|gram|grams|ग्रॅम|किलो|kg|kilo|kilos)/i);
      if (weightMatch) {
        const rawWeight = parseFloat(weightMatch[1]);
        const isKg = cleanText.includes("kg") || cleanText.includes("किलो") || cleanText.includes("kilo");
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
      getBackendUrl: getBackendUrl,
      getWsUrl: getWebSocketUrl,
      startLiveSync: startLiveSync,
      registerListener: registerSyncListener,
      getLastMetrics: function() { return lastSyncMetrics; },
      syncLiveMetrics: performLiveSync,
      performLiveSync: performLiveSync,

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
      const resetEpoch = Date.now();
      pendingOrders.forEach(o => {
        o.timer_started_at = resetEpoch;
        o.remaining_seconds = 1800;
        o.created_at = new Date(resetEpoch).toISOString();
      });
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
    startLiveSync: startLiveSync,
    registerListener: registerSyncListener,

    restockAllToCapacity: async function() {
      if (!skus || !Array.isArray(skus) || skus.length === 0) {
        skus = JSON.parse(JSON.stringify(DEFAULT_SKUS));
      }

      // 1. Loops over skus: sets sku.stock = Number(sku.max_capacity || 100).
      skus.forEach(sku => {
        const def = DEFAULT_SKUS.find(d => d.sku === sku.sku || (d.aliases && d.aliases.includes(sku.sku)));
        const targetCap = Number(sku.max_capacity || (def ? def.max_capacity : null) || sku.full_stock || 100);
        sku.stock = targetCap;
        sku.max_capacity = targetCap;
        sku.full_stock = targetCap;
      });

      // 2. Saves to KEY_SKUS.
      save(KEY_SKUS, skus);
      if (typeof localStorage !== 'undefined') {
        localStorage.setItem('vyapar_alerts_restocked', 'true');
      }

      // 3. Broadcasts via BroadcastChannel('vyapar_realtime_sync') with { type: 'METRICS_UPDATE', products: skus }.
      try {
        if (typeof BroadcastChannel !== 'undefined') {
          const channel = new BroadcastChannel('vyapar_realtime_sync');
          channel.postMessage({ type: 'METRICS_UPDATE', products: skus, data: { products: skus }, timestamp: Date.now() });
          channel.close();
        }
      } catch (e) {
        console.warn('BroadcastChannel error:', e);
      }

      // 4. Dispatches window.dispatchEvent(new CustomEvent('vyapar_state_change', ...)).
      if (typeof window !== 'undefined' && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('vyapar_state_change', {
          detail: { key: KEY_SKUS, data: skus, type: 'METRICS_UPDATE' }
        }));
      }

      // 5. Calls notifySyncListeners('METRICS_UPDATE', { products: skus }).
      notifySyncListeners('METRICS_UPDATE', { products: skus });
      notifySyncListeners('STOCK_UPDATED', { products: skus });

      // 6. Sends POST /api/inventory/restock-all (or /api/reset-demo?full=true) to backend.
      try {
        const backend = getBackendUrl();
        if (backend) {
          const res = await fetch(`${backend}/api/inventory/restock-all`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
          }).catch(() => null);
          if (!res || !res.ok) {
            await fetch(`${backend}/api/reset-demo?full=true`, { method: 'POST' }).catch(() => {});
          }
        }
      } catch (e) {
        console.log('Backend restock-all fetch note:', e);
      }

      return skus;
    },

    resetAllAndRestock: async function() {
      this.resetDefaults();
      return await this.restockAllToCapacity();
    },

    // Merchant Authentication & Session State
    getAuthUser: function() {
      try {
        const raw = (typeof localStorage !== 'undefined') ? localStorage.getItem('vyaparai_auth_user') : null;
        return raw ? JSON.parse(raw) : null;
      } catch(e) {
        return null;
      }
    },

    logout: function() {
      if (typeof localStorage !== 'undefined') {
        localStorage.removeItem('vyaparai_auth_user');
        localStorage.removeItem('vyaparai_auth_token');
        localStorage.removeItem('vyaparai_active_store');
      }
      if (typeof sessionStorage !== 'undefined') {
        sessionStorage.removeItem('just_logged_in');
      }
      if (typeof window !== 'undefined') {
        window.location.replace('login.html');
      }
    },

    syncAuthUI: function() {
      if (typeof window === 'undefined' || typeof document === 'undefined') return;
      try {
        const raw = localStorage.getItem('vyaparai_auth_user');
        if (!raw) return;
        const user = JSON.parse(raw);
        const merchantName = user.name || 'अथर्व आवटे';
        const vendorId = user.vendor_id || 'DEMO_KIRANA_KOP';
        const storeName = user.store || 'अथर्व किराणा स्टोअर्स, कोल्हापूर';
        const formattedLabel = `${merchantName} (${vendorId})`;

        const nameEls = document.querySelectorAll('#headerMerchantName, .merchant-display-name');
        nameEls.forEach(el => el.textContent = formattedLabel);

        const storeEls = document.querySelectorAll('#currentDukaanName, .store-display-name');
        storeEls.forEach(el => {
          if (el.tagName === 'INPUT') {
            el.value = storeName;
          } else if (el.id === 'currentDukaanName') {
            el.textContent = '🏪 ' + storeName;
          }
        });
      } catch(e) {}
    }
  };
})();

// Universal Export
if (typeof window !== "undefined") {
  window.VyaparCore = VyaparCore;
  window.logoutMerchant = function() {
    VyaparCore.logout();
  };
  window.syncMerchantSessionUI = function() {
    VyaparCore.syncAuthUI();
  };
  window.renderPendingYaadiOrders = function(containerId = 'yaadiOrdersFeedList') {
    return VyaparCore.renderYaadiFeed(containerId);
  };
  window.packCustomerOrder = function(orderId) {
    return VyaparCore.packCustomerOrder(orderId);
  };
  window.cancelAndRestoreOrderStock = function(orderId) {
    return VyaparCore.cancelCustomerOrder(orderId);
  };
  window.cancelCustomerOrder = function(orderId) {
    return VyaparCore.cancelCustomerOrder(orderId);
  };

  if (typeof VyaparCore.startTimerTicker === 'function') {
    VyaparCore.startTimerTicker();
  }
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        if (typeof VyaparCore.startTimerTicker === 'function') VyaparCore.startTimerTicker();
        if (document.getElementById('yaadiOrdersFeedList')) {
          VyaparCore.renderYaadiFeed('yaadiOrdersFeedList');
        }
      });
    } else {
      if (document.getElementById('yaadiOrdersFeedList')) {
        VyaparCore.renderYaadiFeed('yaadiOrdersFeedList');
      }
    }
  }
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

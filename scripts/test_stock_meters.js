const fs = require('fs');
const path = require('path');

console.log("=== RUNNING STOCK OVERVIEW & METER SYNCHRONIZATION TESTS ===");

// 1. Setup Mock DOM & Browser Environment
class MockElement {
  constructor(tagName) {
    this.tagName = (tagName || 'div').toUpperCase();
    this.children = [];
    this.attributes = {};
    this.style = {};
    this.className = '';
    this.textContent = '';
    this._innerHTML = '';
  }

  get innerHTML() {
    return this._innerHTML;
  }

  set innerHTML(val) {
    this._innerHTML = val;
    this.children = [];
    // Basic parser for child elements in templates
    const matches = val.match(/<div class="([^"]+)"([^>]*)>([\s\S]*?)<\/div>/g);
    if (matches) {
      matches.forEach(m => {
        const clsMatch = m.match(/class="([^"]+)"/);
        const child = new MockElement('div');
        if (clsMatch) child.className = clsMatch[1];
        
        // Check for style="width: 0%;"
        const styleMatch = m.match(/style="([^"]+)"/);
        if (styleMatch) {
          const wMatch = styleMatch[1].match(/width:\s*([^;]+)/);
          if (wMatch) child.style.width = wMatch[1].trim();
        }

        // Inner spans
        const spanMatches = m.match(/<span class="([^"]+)"[^>]*>([\s\S]*?)<\/span>/g);
        if (spanMatches) {
          spanMatches.forEach(sm => {
            const spanCls = sm.match(/class="([^"]+)"/);
            const spanText = sm.replace(/<[^>]+>/g, '').trim();
            const span = new MockElement('span');
            if (spanCls) span.className = spanCls[1];
            span.textContent = spanText;
            child.children.push(span);
          });
        }

        // Inner nested divs (like meter-track -> meter-fill)
        const innerDivMatches = m.match(/<div class="([^"]+)"([^>]*)><\/div>/g);
        if (innerDivMatches) {
          innerDivMatches.forEach(idm => {
            const innerCls = idm.match(/class="([^"]+)"/);
            const innerDiv = new MockElement('div');
            if (innerCls) innerDiv.className = innerCls[1];
            const innerStyle = idm.match(/style="([^"]+)"/);
            if (innerStyle) {
              const iwMatch = innerStyle[1].match(/width:\s*([^;]+)/);
              if (iwMatch) innerDiv.style.width = iwMatch[1].trim();
            }
            child.children.push(innerDiv);
          });
        }

        this.children.push(child);
      });
    }
  }

  setAttribute(name, val) {
    this.attributes[name] = String(val);
  }

  getAttribute(name) {
    return this.attributes[name] || null;
  }

  appendChild(el) {
    this.children.push(el);
    return el;
  }

  querySelector(selector) {
    return this._find(selector);
  }

  querySelectorAll(selector) {
    const results = [];
    this._findAll(selector, results);
    return results;
  }

  _find(selector) {
    const list = this.querySelectorAll(selector);
    return list.length > 0 ? list[0] : null;
  }

  _findAll(selector, results) {
    for (const child of this.children) {
      if (this._matches(child, selector)) {
        results.push(child);
      }
      child._findAll(selector, results);
    }
  }

  _matches(el, selector) {
    if (selector.startsWith('.')) {
      const cls = selector.slice(1);
      // Handles .stock-meter-row[data-key="val"]
      if (cls.includes('[')) {
        const [c, attrPart] = cls.split('[');
        const attrName = attrPart.split('=')[0];
        const attrVal = attrPart.split('=')[1].replace(/[\]"]/g, '');
        return el.className.split(' ').includes(c) && el.getAttribute(attrName) === attrVal;
      }
      return el.className.split(' ').includes(cls);
    }
    if (selector.startsWith('#')) {
      return el.id === selector.slice(1);
    }
    return false;
  }
}

// Global elements
const elements = {
  stockOverviewMeterList: new MockElement('div'),
  btnRestockAll: new MockElement('button'),
  inventoryTableBody: new MockElement('tbody'),
  appleToastNotification: new MockElement('div'),
  appleToastMessage: new MockElement('div'),
  statTotalSales: new MockElement('div'),
  statOrdersCount: new MockElement('div'),
  recentSalesFeedList: new MockElement('div')
};
elements.stockOverviewMeterList.id = 'stockOverviewMeterList';
elements.btnRestockAll.id = 'btnRestockAll';
elements.statTotalSales.textContent = '₹12,450';
elements.statOrdersCount.textContent = '42';

const storageMap = {};
global.localStorage = {
  getItem: (k) => storageMap[k] || null,
  setItem: (k, v) => { storageMap[k] = String(v); },
  removeItem: (k) => { delete storageMap[k]; }
};

global.sessionStorage = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {}
};

// Set auth user so index.html doesn't redirect
localStorage.setItem('vyaparai_auth_user', JSON.stringify({ phone: '9579869506', name: 'Demo Merchant' }));

global.window = {
  addEventListener: () => {},
  location: { replace: () => {}, href: '' },
  localStorage: global.localStorage,
  sessionStorage: global.sessionStorage,
  AudioContext: class {
    createOscillator() { return { connect: () => {}, start: () => {}, stop: () => {} }; }
    createGain() { return { connect: () => {}, gain: { setValueAtTime: () => {}, exponentialRampToValueAtTime: () => {} } }; }
  }
};

global.document = {
  getElementById: (id) => elements[id] || null,
  querySelector: (sel) => {
    if (sel.startsWith('#')) {
      const id = sel.slice(1);
      return elements[id] || null;
    }
    return null;
  },
  createElement: (tag) => new MockElement(tag),
  addEventListener: () => {},
  readyState: 'complete'
};

global.requestAnimationFrame = (fn) => fn();
global.haptics = { tap: () => {} };
global.showAppleToast = (msg) => { global.lastToast = msg; };
global.animateCounter = () => {};

// 2. Load VyaparCore
const VyaparCore = require('../frontend/assets/vyapar-core.js');
global.window.VyaparCore = VyaparCore;
global.VyaparCore = VyaparCore;

// 3. Extract and execute renderStockOverview and handleRestockAllDemo from index.html
const indexHtml = fs.readFileSync(path.join(__dirname, '../frontend/index.html'), 'utf8');

// Extract renderStockOverview
const renderStockOverviewMatch = indexHtml.match(/function renderStockOverview\([\s\S]*?\n    \}/);
if (!renderStockOverviewMatch) {
  throw new Error("Could not find renderStockOverview in index.html");
}
eval(renderStockOverviewMatch[0]);

// Extract handleRestockAllDemo
const handleRestockAllDemoMatch = indexHtml.match(/async function handleRestockAllDemo\([\s\S]*?\n    \}/);
if (!handleRestockAllDemoMatch) {
  throw new Error("Could not find handleRestockAllDemo in index.html");
}
eval(handleRestockAllDemoMatch[0]);

async function runTests() {
  console.log("\n--- TEST 1: Initial State & Catalog Capacity Verification ---");
  const skus = VyaparCore.getSKUs();
  console.log(`Loaded ${skus.length} SKUs from VyaparCore.`);
  
  // Render initially
  renderStockOverview(skus);
  const container = elements.stockOverviewMeterList;
  console.log(`Rendered ${container.children.length} meters initially.`);
  if (container.children.length !== 8) {
    throw new Error(`Expected exactly 8 meter rows, found ${container.children.length}`);
  }
  console.log("✔ TEST 1 PASSED: Container has exactly 8 stock meters.");

  console.log("\n--- TEST 2: Calling handleRestockAllDemo() ---");
  await handleRestockAllDemo();
  console.log(`Apple Toast Message: "${global.lastToast}"`);
  if (!global.lastToast || !global.lastToast.includes("All 16+ SKUs Restocked to 100% Full Capacity")) {
    throw new Error(`Toast mismatch: ${global.lastToast}`);
  }
  console.log("✔ Toast matches required format.");

  console.log("\n--- TEST 3: Verifying 100% Capacities, Blue Fills, and Zero Warnings ---");
  const expectedItems = [
    { key: "parle", name: "Parle-G", expectedText: "100 packets left • 100%" },
    { key: "sugar", name: "Sugar", expectedText: "100 kg left • 100%" },
    { key: "milk", name: "Amul Milk", expectedText: "50 pouches left • 100%" },
    { key: "oil", name: "Fortune Oil", expectedText: "50 pouches left • 100%" },
    { key: "tur", name: "Tur Dal", expectedText: "50 kg left • 100%" },
    { key: "atta", name: "Aashirvaad Atta", expectedText: "30 bags left • 100%" },
    { key: "onion", name: "Red Onion", expectedText: "100 kg left • 100%" },
    { key: "maggi", name: "Maggi Noodles", expectedText: "80 packets left • 100%" }
  ];

  expectedItems.forEach(item => {
    const row = container.querySelector(`.stock-meter-row[data-key="${item.key}"]`);
    if (!row) {
      throw new Error(`Missing meter row for key: ${item.key}`);
    }

    const valEl = row.querySelector('.meter-percent-val');
    const fillEl = row.querySelector('.meter-fill');

    if (!valEl) throw new Error(`Missing .meter-percent-val in row ${item.key}`);
    if (!fillEl) throw new Error(`Missing .meter-fill in row ${item.key}`);

    const text = valEl.textContent.trim();
    const width = fillEl.style.width;
    const fillClass = fillEl.className;
    const valClass = valEl.className;

    console.log(`[${item.name}]: Text="${text}" | Width=${width} | FillClass="${fillClass}"`);

    // Verify 100% width
    if (width !== "100%") {
      throw new Error(`Expected 100% width for ${item.name}, got ${width}`);
    }

    // Verify .fill-blue
    if (!fillClass.includes("fill-blue")) {
      throw new Error(`Expected fill-blue class for ${item.name}, got ${fillClass}`);
    }

    // Verify ZERO orange warnings
    if (fillClass.includes("fill-warning") || valClass.includes("val-warning")) {
      throw new Error(`Orange warning detected on ${item.name}! FillClass: ${fillClass}, ValClass: ${valClass}`);
    }

    // Verify label text
    if (text !== item.expectedText) {
      throw new Error(`Text mismatch for ${item.name}: expected "${item.expectedText}", got "${text}"`);
    }
  });

  console.log("✔ TEST 3 PASSED: All 8 meters are at 100% capacity with .fill-blue, exact text, and zero orange warnings!");

  console.log("\n--- TEST 4: Dynamic Re-Rendering on Stock Deduction ---");
  // Deduct 2 packets of Parle-G
  VyaparCore.deductStock("FMCG-PARLE-100G", 2);
  renderStockOverview(VyaparCore.getSKUs());
  const parleRow = container.querySelector(`.stock-meter-row[data-key="parle"]`);
  const parleVal = parleRow.querySelector('.meter-percent-val');
  const parleFill = parleRow.querySelector('.meter-fill');
  console.log(`After deducting 2 Parle-G: Text="${parleVal.textContent}" | Width=${parleFill.style.width}`);
  if (parleVal.textContent !== "98 packets left • 98%" || parleFill.style.width !== "98%") {
    throw new Error(`Dynamic deduction failed: ${parleVal.textContent}`);
  }
  console.log("✔ Parle-G correctly updated to 98%!");

  // Restock again
  await handleRestockAllDemo();
  console.log(`After restock: Text="${parleVal.textContent}" | Width=${parleFill.style.width}`);
  if (parleVal.textContent !== "100 packets left • 100%" || parleFill.style.width !== "100%") {
    throw new Error(`Restock back to 100% failed: ${parleVal.textContent}`);
  }
  console.log("✔ Parle-G smoothly animated back to 100% full capacity!");

  console.log("\n=== ALL TESTS PASSED SUCCESSFULLY! ===");
  process.exit(0);
}

runTests().catch(err => {
  console.error("TEST FAILED:", err);
  process.exit(1);
});

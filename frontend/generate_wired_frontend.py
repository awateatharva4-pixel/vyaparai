# -*- coding: utf-8 -*-
"""
Master Subpage & Index Generator for VyaparAI
Generates:
1. index.html (exact replica of index (2).html with active dock wiring)
2. inventory.html (Master Inventory & SKU Register)
3. sales.html (Sales & Billing Ledger / POS)
4. customers.html & khata.html (Digital Khata Book & Customer Ledger)
5. analytics.html (Business Intelligence & AI Predictions)
6. settings.html (Dukaan & Hardware / WhatsApp Configurations)

All pages use 100% of Venkatesh's authentic CSS, Italian Calacatta marble substrate,
macOS dock rail, floating island header, and titanium iPhone WhatsApp drawer.
"""

import os

ORIGINAL_INDEX_PATH = r"C:\Users\HP\Downloads\index (2).html"
ORIGINAL_WHATSAPP_PATH = r"C:\Users\HP\Downloads\whatsapp-console (1).html"
OUT_DIR = r"E:\front end vyapar"

with open(ORIGINAL_INDEX_PATH, "r", encoding="utf-8") as f:
    master_index = f.read()

# -----------------------------------------------------------------------------
# 1. CREATE index.html
# -----------------------------------------------------------------------------
# Replace only the dock button handlers in master_index to link to subpages
index_html = master_index

# Update Overview button
index_html = index_html.replace(
    '<button class="dock-btn active" title="Dashboard">',
    '<button class="dock-btn active" title="Dashboard" onclick="window.location.href=\'index.html\'">'
)
# Update Sales button
index_html = index_html.replace(
    '<button class="dock-btn" title="Sales & Ledger" onclick="showAppleToast(\'Opening Sales Ledger...\')">',
    '<button class="dock-btn" title="Sales & Ledger" onclick="window.location.href=\'sales.html\'">'
)
# Update Customers button
index_html = index_html.replace(
    '<button class="dock-btn" title="Customers & Khata" onclick="showAppleToast(\'Opening Customer Khata Book...\')">',
    '<button class="dock-btn" title="Customers & Khata" onclick="window.location.href=\'customers.html\'">'
)
# Update Inventory button
index_html = index_html.replace(
    '<button class="dock-btn" title="Inventory Stock" onclick="showAppleToast(\'Opening Stock Inventory...\')">',
    '<button class="dock-btn" title="Inventory Stock" onclick="window.location.href=\'inventory.html\'">'
)
# Update Analytics button
index_html = index_html.replace(
    '<button class="dock-btn" title="Analytics & SIH Reports" onclick="showAppleToast(\'Loading Analytics...\')">',
    '<button class="dock-btn" title="Analytics & SIH Reports" onclick="window.location.href=\'analytics.html\'">'
)
# Update Settings button
index_html = index_html.replace(
    '<button class="dock-btn" title="Settings" onclick="showAppleToast(\'Settings Panel\')">',
    '<button class="dock-btn" title="Settings" onclick="window.location.href=\'settings.html\'">'
)

with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html)
with open(os.path.join(OUT_DIR, "index (1).html"), "w", encoding="utf-8") as f:
    f.write(index_html)
print("Successfully generated index.html and index (1).html with wired navigation.")

# Extract head & style from index (2).html
style_start = master_index.find("<style>")
style_end = master_index.find("</style>") + len("</style>")
master_style = master_index[style_start:style_end]

head_start = master_index.find("<head>")
head_meta = master_index[head_start + len("<head>"):style_start].strip()

# Common Dock Generator
def make_dock(active_tab):
    tabs = [
        ("overview", "Dashboard", "index.html", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7" rx="2"></rect>
              <rect x="14" y="3" width="7" height="7" rx="2"></rect>
              <rect x="14" y="14" width="7" height="7" rx="2"></rect>
              <rect x="3" y="14" width="7" height="7" rx="2"></rect>
            </svg>'''),
        ("sales", "Sales & Ledger", "sales.html", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="5" width="20" height="14" rx="2"></rect>
              <line x1="2" y1="10" x2="22" y2="10"></line>
            </svg>'''),
        ("customers", "Customers & Khata", "customers.html", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>'''),
        ("inventory", "Inventory Stock", "inventory.html", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>'''),
        ("analytics", "Analytics & SIH Reports", "analytics.html", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>'''),
        ("whatsapp", "WhatsApp AI Ingress", "toggle_drawer", '''
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
            </svg>''')
    ]

    items_html = []
    for tab_id, title, target, svg in tabs:
        act = " active" if tab_id == active_tab else ""
        if target == "toggle_drawer":
            click = 'onclick="toggleWhatsAppDrawer()" style="color: #25d366;"'
        else:
            click = f'onclick="window.location.href=\'{target}\'"'
        items_html.append(f'''          <!-- {title} -->
          <button class="dock-btn{act}" title="{title}" {click}>
            {svg.strip()}
          </button>''')

    set_act = " active" if active_tab == "settings" else ""
    return f'''    <!-- 1. Apple macOS Dock-Style Sidebar Rail -->
    <aside class="apple-dock-rail">
      <div class="dock-top-cluster">
        <div class="dock-brand-logo" title="VyaparAI Enterprise" onclick="window.location.href='index.html'">V</div>
        
        <nav class="dock-items-group">
{chr(10).join(items_html)}
        </nav>
      </div>

      <div class="dock-bottom-cluster">
        <button class="dock-btn{set_act}" title="Settings" onclick="window.location.href='settings.html'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
      </div>
    </aside>'''

# Common Header Generator
def make_header(subhead_title):
    return f'''      <!-- Floating Island Top Header -->
      <header class="floating-island-header">
        <div class="header-left-cluster">
          <div class="brand-title" onclick="window.location.href='index.html'" style="cursor: pointer;">
            VyaparAI
            <span class="luxury-sub">{subhead_title}</span>
          </div>

          <!-- Apple ⌘K Search Bar -->
          <div class="apple-search-wrap">
            <svg class="search-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <input type="text" class="apple-search-input" id="globalSearchInput" placeholder="Search {subhead_title.lower()}... ⌘K" oninput="handleTableSearch(this.value)" />
            <span class="search-cmd-k">⌘K</span>
          </div>
        </div>

        <div class="header-right-cluster">
          <!-- Store Selector -->
          <div class="store-select-pill" onclick="cycleDukaans()">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
            <span id="currentDukaanName">All Dukaans</span> ▾
          </div>

          <!-- Admin Pill -->
          <div class="header-pill-item" onclick="showAppleToast('Admin: Ganesh Kirana Store')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="3"></circle>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
            </svg>
            Admin
          </div>

          <!-- Profile Pill -->
          <div class="header-pill-item" onclick="showAppleToast('Profile: Atharva (Owner)')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            Profile
          </div>

          <!-- Live WhatsApp Ingress Status Indicator -->
          <div class="header-pill-item" onclick="toggleWhatsAppDrawer()" style="color: #25d366; cursor: pointer;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: #25d366; display: inline-block; box-shadow: 0 0 8px #25d366;"></span>
            WhatsApp
          </div>
        </div>
      </header>'''

# Common Footer & Scripts
def make_footer_and_scripts(extra_js=""):
    return f'''  <!-- 3. Floating WhatsApp Ingress Trigger Pill -->
  <div class="whatsapp-floating-island" onclick="toggleWhatsAppDrawer()" title="Open iPhone WhatsApp AI Console">
    <div class="pulse-dot"></div>
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
    </svg>
    <span>WhatsApp AI Ingress</span>
  </div>

  <!-- 4. iPhone 15 Pro Titanium Slide-Over Frame Drawer -->
  <div class="iphone-drawer-backdrop" id="iphoneDrawerBackdrop" onclick="closeDrawerOnBackdrop(event)">
    <div class="iphone-drawer-panel" id="iphoneDrawerPanel">
      
      <div class="drawer-header">
        <div class="drawer-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="color: #25d366;">
            <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
          </svg>
          WhatsApp AI Ingress Console
        </div>
        <button class="close-drawer-btn" onclick="toggleWhatsAppDrawer()" title="Close Drawer">✕</button>
      </div>

      <p style="font-size: 0.78rem; color: var(--text-tertiary); margin-bottom: 14px;">
        Interactive WhatsApp Voice & Ingress Simulation — Orders recorded here synchronize live with the VyaparAI dashboard.
      </p>

      <!-- iPhone Titanium Frame Housing -->
      <div class="iphone-frame-bezel">
        <!-- Dynamic Island Pill -->
        <div class="dynamic-island">
          <div class="dynamic-island-cam"></div>
          <div class="dynamic-island-sensor"></div>
        </div>

        <!-- Embedded Interactive Console -->
        <div class="iphone-screen-content">
          <iframe src="whatsapp-console.html" class="iphone-iframe" id="whatsappConsoleIframe" title="WhatsApp Ingress Console"></iframe>
        </div>
      </div>

      <div style="margin-top: 14px; display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 0.74rem; color: var(--emerald-700); font-weight: 600;">VyaparAI Live Ingress Hook Active</span>
        <a href="whatsapp-console.html" target="_blank" style="font-size: 0.74rem; color: var(--apple-blue); font-weight: 600; text-decoration: none;">
          Open Fullscreen ↗
        </a>
      </div>

    </div>
  </div>

  <!-- Apple Global Interactive Toast -->
  <div class="apple-toast" id="appleToastNotification">
    <div class="toast-icon">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
    </div>
    <span id="appleToastMessage">Action completed successfully</span>
  </div>

  <!-- Apple-Grade Micro-Interactions, Haptics & Sync -->
  <script>
    const inrFormatter = new Intl.NumberFormat('en-IN');

    class AppleHapticEngine {{
      constructor() {{
        this.ctx = null;
        this.unlocked = false;
        this.bindUnlock();
      }}

      bindUnlock() {{
        const unlock = () => {{
          if (!this.unlocked) {{
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {{
              this.ctx = new AudioContext();
              if (this.ctx.state === 'suspended') {{
                this.ctx.resume();
              }}
              this.unlocked = true;
            }}
            window.removeEventListener('click', unlock);
            window.removeEventListener('keydown', unlock);
          }}
        }};
        window.addEventListener('click', unlock, {{ passive: true }});
        window.addEventListener('keydown', unlock, {{ passive: true }});
      }}

      playTick() {{
        if (!this.unlocked || !this.ctx) return;
        try {{
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(120, this.ctx.currentTime);
          osc.frequency.exponentialRampToValueAtTime(40, this.ctx.currentTime + 0.035);
          gain.gain.setValueAtTime(0.045, this.ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.035);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(this.ctx.currentTime + 0.035);
        }} catch(e) {{}}
      }}

      playSuccess() {{
        if (!this.unlocked || !this.ctx) return;
        try {{
          const now = this.ctx.currentTime;
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(523.25, now);
          osc.frequency.setValueAtTime(659.25, now + 0.06);
          gain.gain.setValueAtTime(0.05, now);
          gain.gain.exponentialRampToValueAtTime(0.001, now + 0.14);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start();
          osc.stop(now + 0.14);
        }} catch(e) {{}}
      }}
    }}

    const haptics = new AppleHapticEngine();

    let toastTimeout = null;
    function showAppleToast(msg) {{
      const toast = document.getElementById('appleToastNotification');
      const text = document.getElementById('appleToastMessage');
      if (!toast || !text) return;
      text.textContent = msg;
      toast.classList.add('visible');
      haptics.playTick();
      if (toastTimeout) clearTimeout(toastTimeout);
      toastTimeout = setTimeout(() => {{
        toast.classList.remove('visible');
      }}, 3200);
    }}

    function toggleWhatsAppDrawer() {{
      const backdrop = document.getElementById('iphoneDrawerBackdrop');
      if (!backdrop) return;
      const isOpen = backdrop.classList.contains('open');
      if (isOpen) {{
        backdrop.classList.remove('open');
        document.body.style.overflow = '';
      }} else {{
        backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        haptics.playTick();
      }}
    }}

    function closeDrawerOnBackdrop(e) {{
      if (e.target.id === 'iphoneDrawerBackdrop') {{
        toggleWhatsAppDrawer();
      }}
    }}

    const dukaans = ['All Dukaans', 'Ganesh Kirana (Shahupuri)', 'Laxmi Stores (Rajarampuri)', 'Kolhapur Central Depot'];
    let dIndex = 0;
    function cycleDukaans() {{
      dIndex = (dIndex + 1) % dukaans.length;
      const el = document.getElementById('currentDukaanName');
      if (el) {{
        el.textContent = dukaans[dIndex];
        showAppleToast(`Active Store: ${{dukaans[dIndex]}}`);
      }}
    }}

    function handleTableSearch(val) {{
      val = val.toLowerCase().trim();
      const rows = document.querySelectorAll('table tbody tr');
      rows.forEach(r => {{
        const txt = r.textContent.toLowerCase();
        r.style.display = txt.includes(val) ? '' : 'none';
      }});
    }}

    function animateCounter(id, start, end, duration, prefix = '') {{
      const obj = document.getElementById(id);
      if (!obj) return;
      let startTimestamp = null;
      const step = (timestamp) => {{
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const easeProgress = 1 - Math.pow(1 - progress, 4);
        const currentVal = Math.floor(easeProgress * (end - start) + start);
        obj.textContent = `${{prefix}}${{inrFormatter.format(currentVal)}}`;
        if (progress < 1) {{
          window.requestAnimationFrame(step);
        }}
      }};
      window.requestAnimationFrame(step);
    }}

    window.addEventListener('message', (event) => {{
      if (event.data && event.data.type === 'NEW_SALE') {{
        const sale = event.data.payload || {{}};
        showAppleToast(`New WhatsApp Order: ₹${{sale.amount || '340'}} (${{sale.item || 'Order'}})!`);
        haptics.playSuccess();
      }}
    }});

    document.addEventListener('keydown', (e) => {{
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {{
        e.preventDefault();
        const inp = document.getElementById('globalSearchInput');
        if (inp) {{
          inp.focus();
          inp.select();
        }}
      }}
      if (e.key === 'Escape') {{
        const backdrop = document.getElementById('iphoneDrawerBackdrop');
        if (backdrop && backdrop.classList.contains('open')) {{
          toggleWhatsAppDrawer();
        }}
      }}
    }});

    {extra_js}
  </script>'''

# -----------------------------------------------------------------------------
# 2. CREATE inventory.html (Master Inventory & SKU Register)
# -----------------------------------------------------------------------------
inventory_bento = '''
      <!-- Bento Grid Content System -->
      <div class="bento-grid">

        <!-- ROW 1: Inventory Summary Trio (Cols 1-8) & Stock Health Chart (Cols 9-12) -->
        <div class="glass-card quick-summary-card">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                <line x1="12" y1="22.08" x2="12" y2="12"></line>
              </svg>
              Inventory Health Summary
            </h2>
            <span class="store-select-pill" style="font-size: 0.76rem; padding: 4px 10px;" onclick="cycleDukaans()">
              All Dukaans ▾
            </span>
          </div>

          <div class="summary-metrics-trio">
            <!-- Metric 1: Total Stock Valuation -->
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Stock Valuation</span>
                <span class="metric-pill-badge badge-green">48 SKUs</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statStockVal">₹3,42,850</div>
            </div>

            <!-- Metric 2: Total Items In Stock -->
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Units in Hand</span>
                <div class="badge-icon-box">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>
                  </svg>
                </div>
              </div>
              <div class="metric-value-num tabular-nums" id="statUnitsCount">1,840</div>
            </div>

            <!-- Metric 3: Critical Low Stock Count -->
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Critical Low Stock</span>
                <span class="status-pill status-low">3 Urgent</span>
              </div>
              <div class="metric-prod-name" style="color: var(--apple-coral);">Parle-G, Oil, Colgate</div>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- Stock Health Doughnut Card (Cols 9-12) -->
        <div class="glass-card daily-sales-card">
          <div class="card-header-row" style="margin-bottom: 8px;">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 2a10 10 0 0 1 10 10h-10z"></path>
              </svg>
              Stock Health Status
            </h2>
            <span style="font-size: 0.72rem; color: var(--apple-green); font-weight: 600;">82% Healthy</span>
          </div>
          
          <div style="height: 125px; width: 100%; position: relative;">
            <canvas id="stockHealthChart"></canvas>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 2: Master Inventory Table (Cols 1-12) -->
        <div class="glass-card inventory-status-card" style="grid-column: span 12;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <line x1="3" y1="9" x2="21" y2="9"></line>
                <line x1="9" y1="21" x2="9" y2="9"></line>
              </svg>
              Master Stock Register & Reorder Points
            </h2>
            <div style="display: flex; gap: 8px; align-items: center;">
              <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Opening CSV Import Modal...')">+ Import CSV</button>
              <button class="restock-btn" onclick="showAppleToast('Opening Add Product Form...')">+ New SKU</button>
            </div>
          </div>

          <div class="table-scroll-wrap" style="max-height: 480px;">
            <table class="data-table-custom">
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>SKU Code</th>
                  <th>Category</th>
                  <th style="text-align: right;">In Stock</th>
                  <th style="text-align: right;">Unit MRP</th>
                  <th style="text-align: right;">Cost Price</th>
                  <th style="text-align: right;">Margin %</th>
                  <th style="text-align: center;">Status</th>
                  <th style="text-align: center;">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/parle_g.png" alt="Parle-G" class="table-prod-thumb" />
                      <div>
                        <strong>Parle-G Gluco Biscuits</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">Pack 100g • Fast Mover</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P01</td>
                  <td>Biscuits</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">22 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹10</td>
                  <td style="text-align: right;" class="tabular-nums">₹8.20</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">18%</td>
                  <td style="text-align: center;"><span class="status-pill status-low">Critical Low</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Reorder Parle-G: 50 units ordered via Parle Depot!')">+ Reorder</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/sugar.png" alt="Sugar" class="table-prod-thumb" />
                      <div>
                        <strong>Madhur Pure Crystal Sugar</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">1kg Pouch • Refined</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P02</td>
                  <td>Staples</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">16 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹48</td>
                  <td style="text-align: right;" class="tabular-nums">₹41.50</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">13.5%</td>
                  <td style="text-align: center;"><span class="status-pill status-low">Low Stock</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Reorder Sugar: 50kg bag added!')">+ Reorder</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/maggi.png" alt="Maggi" class="table-prod-thumb" />
                      <div>
                        <strong>Nestle Maggi 2-Min Noodles</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">70g Masala Pack</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P03</td>
                  <td>Instant Foods</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">70 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹14</td>
                  <td style="text-align: right;" class="tabular-nums">₹11.80</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">15.7%</td>
                  <td style="text-align: center;"><span class="status-pill status-in">In Stock</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Stock adjusted: +24 units')">+ Stock</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/alert_sunflower_oil.png" alt="Fortune Oil" class="table-prod-thumb" />
                      <div>
                        <strong>Fortune Sunlite Refined Oil</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">1 Litre Pouch</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P04</td>
                  <td>Edible Oils</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">12 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹155</td>
                  <td style="text-align: right;" class="tabular-nums">₹142.00</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">8.4%</td>
                  <td style="text-align: center;"><span class="status-pill status-low">Critical Low</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Reorder 20 Pouches via Adani Wilmar Depot')">+ Reorder</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/alert_colgate.png" alt="Colgate" class="table-prod-thumb" />
                      <div>
                        <strong>Colgate Strong Teeth</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">100g Dental Cream</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P05</td>
                  <td>Personal Care</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">8 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹62</td>
                  <td style="text-align: right;" class="tabular-nums">₹51.00</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">17.7%</td>
                  <td style="text-align: center;"><span class="status-pill status-low">Critical Low</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Reorder Colgate: 36 units PO sent!')">+ Reorder</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/dove.png" alt="Dove" class="table-prod-thumb" />
                      <div>
                        <strong>Dove White Beauty Bar</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">100g Bathing Bar</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P06</td>
                  <td>Personal Care</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">45 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹68</td>
                  <td style="text-align: right;" class="tabular-nums">₹56.00</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">17.6%</td>
                  <td style="text-align: center;"><span class="status-pill status-in">In Stock</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Stock adjusted: +12 units')">+ Stock</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/tata_salt.png" alt="Tata Salt" class="table-prod-thumb" />
                      <div>
                        <strong>Tata Salt (Desh Ka Namak)</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">1kg Vacuum Evaporated</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P07</td>
                  <td>Staples</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">85 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹28</td>
                  <td style="text-align: right;" class="tabular-nums">₹23.50</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">16.1%</td>
                  <td style="text-align: center;"><span class="status-pill status-in">In Stock</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Stock adjusted: +50 units')">+ Stock</button>
                  </td>
                </tr>

                <tr>
                  <td>
                    <div class="table-prod-cell">
                      <img src="assets/products/bakery_pav.png" alt="Bakery Pav" class="table-prod-thumb" />
                      <div>
                        <strong>Fresh Kolhapur Bakery Pav</strong>
                        <div style="font-size: 0.68rem; color: var(--text-tertiary);">Ladi of 6 buns • Daily Fresh</div>
                      </div>
                    </div>
                  </td>
                  <td class="tabular-nums">P08</td>
                  <td>Bakery</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">40 left</td>
                  <td style="text-align: right;" class="tabular-nums">₹25</td>
                  <td style="text-align: right;" class="tabular-nums">₹18.00</td>
                  <td style="text-align: right;" class="tabular-nums" style="color: var(--apple-green); font-weight: 600;">28%</td>
                  <td style="text-align: center;"><span class="status-pill status-in">In Stock</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Bakery Pav: Morning order logged')">+ Stock</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 3: AI Smart Reorder Suggestions & Supplier Purchase Order -->
        <div class="glass-card low-stock-alerts-card" style="grid-column: span 6;">
          <div class="card-header-row">
            <h2 class="card-heading" style="color: var(--brass-700);">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              AI Smart Reorder Forecast (Kolhapur Yard)
            </h2>
            <span class="status-pill status-in">AI Engine</span>
          </div>

          <div class="alerts-list-wrap">
            <div class="alert-item-box">
              <div class="alert-left-details">
                <img src="assets/products/parle_g.png" alt="Parle-G" class="alert-thumb" />
                <div class="alert-text-group">
                  <span class="alert-prod-name">Parle-G (Velocity: 18/day)</span>
                  <span class="alert-category-tag">Stockout in 28 hrs • Reorder 50 units (Depot)</span>
                </div>
              </div>
              <button class="restock-btn" onclick="showAppleToast('WhatsApp PO sent to Parle Depot Kolhapur!')">Send PO ↗</button>
            </div>

            <div class="alert-item-box">
              <div class="alert-left-details">
                <img src="assets/products/alert_sunflower_oil.png" alt="Fortune Oil" class="alert-thumb" />
                <div class="alert-text-group">
                  <span class="alert-prod-name">Fortune Sunflower (Velocity: 6/day)</span>
                  <span class="alert-category-tag">Stockout in 40 hrs • Reorder 24 Pouches</span>
                </div>
              </div>
              <button class="restock-btn" onclick="showAppleToast('WhatsApp PO sent to Wilmar Distributor!')">Send PO ↗</button>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <div class="glass-card recent-sales-card" style="grid-column: span 6;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
              </svg>
              Quick Stock Inward Voucher
            </h2>
            <span style="font-size: 0.72rem; color: var(--brass-600); font-weight: 600;">Voucher #INW-409</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 6px;">
            <div style="display: flex; gap: 10px;">
              <input type="text" class="apple-search-input" placeholder="Supplier: Kolhapur Wholesale Market" style="flex: 1;" />
              <input type="text" class="apple-search-input" placeholder="Invoice Amount (₹)" style="width: 140px;" />
            </div>
            <div style="display: flex; gap: 10px;">
              <input type="text" class="apple-search-input" placeholder="Scan Barcode or SKU" style="flex: 1;" />
              <input type="number" class="apple-search-input" placeholder="Qty" value="10" style="width: 80px;" />
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px;">
              <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Voucher Draft Saved')">Save Draft</button>
              <button class="restock-btn" onclick="showAppleToast('Stock Added & Inventory Ledger Updated!')">Accept Inward</button>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

      </div>
'''

inventory_js = '''
    document.addEventListener('DOMContentLoaded', () => {
      animateCounter('statStockVal', 0, 342850, 1100, '₹');
      animateCounter('statUnitsCount', 0, 1840, 900);

      const ctx = document.getElementById('stockHealthChart');
      if (ctx) {
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['Healthy', 'Low Stock', 'Out of Stock'],
            datasets: [{
              data: [82, 14, 4],
              backgroundColor: ['#28cd41', '#ff9500', '#ff3b30'],
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: { boxWidth: 10, font: { size: 9.5 } }
              }
            },
            cutout: '72%'
          }
        });
      }
    });
'''

inventory_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head_meta}
  {master_style}
</head>
<body>
  <div class="app-viewport">
{make_dock("inventory")}
    <main class="dashboard-canvas">
{make_header("Inventory Register")}
{inventory_bento}
    </main>
  </div>
{make_footer_and_scripts(inventory_js)}
</body>
</html>'''

with open(os.path.join(OUT_DIR, "inventory.html"), "w", encoding="utf-8") as f:
    f.write(inventory_full)
print("Successfully generated inventory.html")

# -----------------------------------------------------------------------------
# 3. CREATE sales.html (Sales & Billing Ledger / POS)
# -----------------------------------------------------------------------------
sales_bento = '''
      <!-- Bento Grid Content System -->
      <div class="bento-grid">

        <!-- ROW 1: Sales Metrics Trio & Hourly Sales Line Chart -->
        <div class="glass-card quick-summary-card">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="5" width="20" height="14" rx="2"></rect>
                <line x1="2" y1="10" x2="22" y2="10"></line>
              </svg>
              Today's Sales Performance
            </h2>
            <span class="store-select-pill" style="font-size: 0.76rem; padding: 4px 10px;" onclick="cycleDukaans()">
              All Dukaans ▾
            </span>
          </div>

          <div class="summary-metrics-trio">
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Today's Revenue</span>
                <span class="metric-pill-badge badge-green">+18.4%</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statSalesToday">₹18,450</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">UPI / Digital (66%)</span>
                <div class="badge-icon-box green-box">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                </div>
              </div>
              <div class="metric-value-num tabular-nums" id="statUPI">₹12,200</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Total Invoices</span>
                <div class="badge-icon-box">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  </svg>
                </div>
              </div>
              <div class="metric-value-num tabular-nums" id="statInvoices">64</div>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- Hourly Peak Sales Chart -->
        <div class="glass-card daily-sales-card">
          <div class="card-header-row" style="margin-bottom: 8px;">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              Hourly Sales Rhythm
            </h2>
            <span style="font-size: 0.72rem; color: var(--apple-blue); font-weight: 600;">Peak: 6 PM - 8 PM</span>
          </div>
          
          <div style="height: 125px; width: 100%; position: relative;">
            <canvas id="hourlySalesChart"></canvas>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 2: Live Ingress Feed & Sales Ledger Table (Cols 1-8) + Instant POS Bill Card (Cols 9-12) -->
        <div class="glass-card inventory-status-card" style="grid-column: span 8;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
              Sales Ledger & Tax Invoices
            </h2>
            <span style="font-size: 0.72rem; color: var(--emerald-600); font-weight: 600;">Live Feed Active</span>
          </div>

          <div class="table-scroll-wrap" style="max-height: 420px;">
            <table class="data-table-custom">
              <thead>
                <tr>
                  <th>Invoice ID</th>
                  <th>Time</th>
                  <th>Customer</th>
                  <th>Items Purchased</th>
                  <th style="text-align: right;">Total</th>
                  <th style="text-align: center;">Payment Mode</th>
                  <th style="text-align: center;">Receipt</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td class="tabular-nums font-bold">#INV-1082</td>
                  <td class="tabular-nums">2 mins ago</td>
                  <td>Rohan Patil</td>
                  <td>5x Parle-G, 1kg Sugar</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹130</td>
                  <td style="text-align: center;"><span class="status-pill status-in">UPI QR</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('WhatsApp receipt sent to Rohan (+91 98220...)!')">Share ↗</button></td>
                </tr>

                <tr>
                  <td class="tabular-nums font-bold">#INV-1081</td>
                  <td class="tabular-nums">14 mins ago</td>
                  <td>Sunita Deshmukh</td>
                  <td>2x Fortune Sunflower 1L</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹310</td>
                  <td style="text-align: center;"><span class="status-pill status-in" style="background: rgba(0, 113, 227, 0.12); color: #0071e3;">Cash</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('Receipt printed on 58mm printer')">Print</button></td>
                </tr>

                <tr>
                  <td class="tabular-nums font-bold">#INV-1080</td>
                  <td class="tabular-nums">32 mins ago</td>
                  <td>Anand Traders</td>
                  <td>1x Aashirvaad 5kg, Tata Salt</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹285</td>
                  <td style="text-align: center;"><span class="status-pill status-low">Khata (Udhar)</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('Logged to Anand Traders Khata passbook')">Khata</button></td>
                </tr>

                <tr>
                  <td class="tabular-nums font-bold">#INV-1079</td>
                  <td class="tabular-nums">48 mins ago</td>
                  <td>Prakash Rao</td>
                  <td>4x Maggi Noodles, Dove Soap</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹160</td>
                  <td style="text-align: center;"><span class="status-pill status-in">UPI QR</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('Receipt sent on WhatsApp!')">Share ↗</button></td>
                </tr>

                <tr>
                  <td class="tabular-nums font-bold">#INV-1078</td>
                  <td class="tabular-nums">1 hr ago</td>
                  <td>Mahesh Kadam</td>
                  <td>3x Bakery Pav, Amul Butter</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹90</td>
                  <td style="text-align: center;"><span class="status-pill status-in">UPI QR</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('Receipt sent on WhatsApp!')">Share ↗</button></td>
                </tr>

                <tr>
                  <td class="tabular-nums font-bold">#INV-1077</td>
                  <td class="tabular-nums">1.5 hrs ago</td>
                  <td>Shrikant Joshi</td>
                  <td>10x Parle-G, 1kg Tur Dal</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹265</td>
                  <td style="text-align: center;"><span class="status-pill status-in" style="background: rgba(0, 113, 227, 0.12); color: #0071e3;">Cash</span></td>
                  <td style="text-align: center;"><button class="apple-pill-btn btn-stock" onclick="showAppleToast('Printed receipt')">Print</button></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- Instant POS Terminal Card (Cols 9-12) -->
        <div class="glass-card top-products-card" style="grid-column: span 4;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2"></rect>
                <line x1="8" y1="21" x2="16" y2="21"></line>
              </svg>
              Quick POS Terminal
            </h2>
            <span class="status-pill status-in">Online</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 8px;">
            <input type="text" class="apple-search-input" placeholder="Scan Barcode or Type Product..." id="posProductInput" />
            
            <div style="background: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 12px; border: var(--glass-border-subtle);">
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                <span>Parle-G 100g (x3)</span>
                <span class="tabular-nums font-bold">₹30</span>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px;">
                <span>Madhur Sugar 1kg (x1)</span>
                <span class="tabular-nums font-bold">₹48</span>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.8rem; border-top: 1px dashed #ccc; padding-top: 6px; margin-top: 4px; font-weight: 700; color: var(--emerald-800);">
                <span>Subtotal</span>
                <span class="tabular-nums">₹78</span>
              </div>
            </div>

            <div style="display: flex; gap: 6px;">
              <button class="apple-pill-btn btn-stock" style="flex: 1;" onclick="showAppleToast('Cash ₹78 received. Invoice saved!')">Cash</button>
              <button class="apple-pill-btn btn-stock" style="flex: 1; background: #0071e3; color: #fff;" onclick="showAppleToast('UPI QR displayed on customer screen')">UPI QR</button>
              <button class="apple-pill-btn btn-stock" style="flex: 1; color: var(--apple-amber);" onclick="showAppleToast('Added to Udhar Khata')">Khata</button>
            </div>

            <button class="restock-btn" style="width: 100%; padding: 10px; justify-content: center;" onclick="showAppleToast('Invoice #INV-1083 generated & synced!')">
              Complete Sale & Print Bill
            </button>
          </div>
          <div class="specular-sweep"></div>
        </div>

      </div>
'''

sales_js = '''
    document.addEventListener('DOMContentLoaded', () => {
      animateCounter('statSalesToday', 0, 18450, 1100, '₹');
      animateCounter('statUPI', 0, 12200, 1000, '₹');
      animateCounter('statInvoices', 0, 64, 800);

      const ctx = document.getElementById('hourlySalesChart');
      if (ctx) {
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 120);
        gradient.addColorStop(0, 'rgba(0, 113, 227, 0.28)');
        gradient.addColorStop(1, 'rgba(0, 113, 227, 0.00)');

        new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['9 AM', '11 AM', '1 PM', '3 PM', '5 PM', '7 PM', '9 PM'],
            datasets: [{
              label: 'Hourly Sales',
              data: [850, 2400, 1900, 1400, 3800, 5600, 2500],
              borderColor: '#0071e3',
              borderWidth: 2.2,
              tension: 0.42,
              fill: true,
              backgroundColor: gradient,
              pointRadius: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { display: false } },
              y: { grid: { color: 'rgba(0,0,0,0.04)' } }
            }
          }
        });
      }
    });
'''

sales_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head_meta}
  {master_style}
</head>
<body>
  <div class="app-viewport">
{make_dock("sales")}
    <main class="dashboard-canvas">
{make_header("Sales & Ledger")}
{sales_bento}
    </main>
  </div>
{make_footer_and_scripts(sales_js)}
</body>
</html>'''

with open(os.path.join(OUT_DIR, "sales.html"), "w", encoding="utf-8") as f:
    f.write(sales_full)
print("Successfully generated sales.html")

# -----------------------------------------------------------------------------
# 4. CREATE customers.html & khata.html (Customer Khata Book & Digital Ledger)
# -----------------------------------------------------------------------------
customers_bento = '''
      <!-- Bento Grid Content System -->
      <div class="bento-grid">

        <!-- ROW 1: Khata Metrics Trio (Cols 1-8) & Recovery Trend Chart (Cols 9-12) -->
        <div class="glass-card quick-summary-card">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              </svg>
              Khata Ledger & Credit Status
            </h2>
            <span class="store-select-pill" style="font-size: 0.76rem; padding: 4px 10px;" onclick="cycleDukaans()">
              All Dukaans ▾
            </span>
          </div>

          <div class="summary-metrics-trio">
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Total Outstanding Udhar</span>
                <span class="metric-pill-badge badge-green">38 Accounts</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statKhataTotal">₹42,800</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Recovered This Month</span>
                <div class="badge-icon-box green-box">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                </div>
              </div>
              <div class="metric-value-num tabular-nums" id="statRecovered">₹68,500</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Overdue > 30 Days</span>
                <span class="status-pill status-low">4 Critical</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statOverdue" style="color: var(--apple-coral);">₹6,400</div>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- Khata Repayment Rate Chart -->
        <div class="glass-card daily-sales-card">
          <div class="card-header-row" style="margin-bottom: 8px;">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              Recovery Health
            </h2>
            <span style="font-size: 0.72rem; color: var(--apple-green); font-weight: 600;">91.4% Repaid</span>
          </div>
          
          <div style="height: 125px; width: 100%; position: relative;">
            <canvas id="khataRecoveryChart"></canvas>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 2: Customer Khata Directory Table (Cols 1-12) -->
        <div class="glass-card inventory-status-card" style="grid-column: span 12;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="4" width="20" height="16" rx="2"></rect>
                <path d="M7 15h10M7 9h10"></path>
              </svg>
              Customer Khata Directory (Kolhapur Wards)
            </h2>
            <div style="display: flex; gap: 8px;">
              <button class="apple-pill-btn btn-stock" onclick="showAppleToast('WhatsApp Reminders sent to all 8 pending accounts!')">
                ⚡ 1-Click WhatsApp Reminders (All)
              </button>
              <button class="restock-btn" onclick="showAppleToast('Opening New Khata Registration Modal...')">
                + New Customer
              </button>
            </div>
          </div>

          <div class="table-scroll-wrap" style="max-height: 480px;">
            <table class="data-table-custom">
              <thead>
                <tr>
                  <th>Customer Name</th>
                  <th>Phone Number</th>
                  <th>Kolhapur Locality</th>
                  <th style="text-align: right;">Outstanding Balance</th>
                  <th>Last Payment</th>
                  <th style="text-align: center;">Trust Score</th>
                  <th style="text-align: center;">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Rahul Patil</strong></td>
                  <td class="tabular-nums">+91 98220 14820</td>
                  <td>Rajarampuri Ward 4</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">₹3,450</td>
                  <td>3 days ago (₹1,000)</td>
                  <td style="text-align: center;"><span class="status-pill status-in">98% High Trust</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('WhatsApp payment reminder sent to Rahul with UPI QR!')">Send Reminder ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected: Recorded in Ledger')">Collect ₹</button>
                  </td>
                </tr>

                <tr>
                  <td><strong>Sunita Deshmukh</strong></td>
                  <td class="tabular-nums">+91 94232 55100</td>
                  <td>Shahupuri 2nd Lane</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹1,200</td>
                  <td>Yesterday (₹500)</td>
                  <td style="text-align: center;"><span class="status-pill status-in">95% High Trust</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('WhatsApp reminder sent to Sunita!')">Send Reminder ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected')">Collect ₹</button>
                  </td>
                </tr>

                <tr>
                  <td><strong>Anand Traders</strong></td>
                  <td class="tabular-nums">+91 98901 88234</td>
                  <td>Market Yard Depot</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹8,900</td>
                  <td>18 days ago (₹4,000)</td>
                  <td style="text-align: center;"><span class="status-pill status-in">88% Verified</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Formal Statement PDF sent on WhatsApp!')">Send Statement ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected')">Collect ₹</button>
                  </td>
                </tr>

                <tr>
                  <td><strong>Prakash Rao</strong></td>
                  <td class="tabular-nums">+91 97631 22910</td>
                  <td>Tarabai Park</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">₹4,800</td>
                  <td>34 days ago</td>
                  <td style="text-align: center;"><span class="status-pill status-low">64% Overdue</span></td>
                  <td style="text-align: center;">
                    <button class="restock-btn" onclick="showAppleToast('Urgent Overdue Notice sent on WhatsApp!')">Urgent Notice ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected')">Collect ₹</button>
                  </td>
                </tr>

                <tr>
                  <td><strong>Shrikant Joshi</strong></td>
                  <td class="tabular-nums">+91 99224 77312</td>
                  <td>Rankala Chowk</td>
                  <td style="text-align: right;" class="tabular-nums font-bold">₹2,150</td>
                  <td>12 days ago (₹800)</td>
                  <td style="text-align: center;"><span class="status-pill status-in">92% Reliable</span></td>
                  <td style="text-align: center;">
                    <button class="apple-pill-btn btn-stock" onclick="showAppleToast('Reminder sent with Google Pay link!')">Send Reminder ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected')">Collect ₹</button>
                  </td>
                </tr>

                <tr>
                  <td><strong>Mahesh Kadam</strong></td>
                  <td class="tabular-nums">+91 98812 33490</td>
                  <td>Mangalwar Peth</td>
                  <td style="text-align: right;" class="tabular-nums font-bold" style="color: var(--apple-coral);">₹6,400</td>
                  <td>45 days ago</td>
                  <td style="text-align: center;"><span class="status-pill status-low">52% High Risk</span></td>
                  <td style="text-align: center;">
                    <button class="restock-btn" onclick="showAppleToast('Legal Khata Notice drafted and sent via WhatsApp!')">Send Notice ↗</button>
                    <button class="apple-pill-btn btn-stock" style="margin-left: 4px;" onclick="showAppleToast('Payment collected')">Collect ₹</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 3: Automated WhatsApp Reminder Template Preview -->
        <div class="glass-card low-stock-alerts-card" style="grid-column: span 12;">
          <div class="card-header-row">
            <h2 class="card-heading" style="color: #25d366;">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
              </svg>
              Automated Marathi WhatsApp Payment Reminder Engine
            </h2>
            <span class="status-pill status-in">Template v2.4</span>
          </div>

          <div style="background: rgba(255, 255, 255, 0.65); padding: 14px 18px; border-radius: 14px; border: var(--glass-border-subtle); display: flex; justify-content: space-between; align-items: center;">
            <div>
              <div style="font-weight: 600; color: var(--emerald-900); margin-bottom: 4px;">Smart Marathi Polite Format:</div>
              <div style="font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5;">
                "नमस्कार <strong>[Customer Name]</strong> जी, गणेश किराणा स्टोअर्सकडून नम्र स्मरणपत्र. आपले <strong>₹[Amount]</strong> बाकी आहेत. कृपया सोयीनुसार खालील लिंकवर क्लिक करून UPI द्वारे पेमेंट करावे: <span style="color: var(--apple-blue);">upi://pay?pa=ganeshkirana@upi</span>. धन्यवाद!"
              </div>
            </div>
            <button class="restock-btn" style="white-space: nowrap; margin-left: 20px;" onclick="showAppleToast('Test template sent to shopkeeper phone!')">
              Test on WhatsApp ↗
            </button>
          </div>
          <div class="specular-sweep"></div>
        </div>

      </div>
'''

customers_js = '''
    document.addEventListener('DOMContentLoaded', () => {
      animateCounter('statKhataTotal', 0, 42800, 1100, '₹');
      animateCounter('statRecovered', 0, 68500, 1000, '₹');
      animateCounter('statOverdue', 0, 6400, 800, '₹');

      const ctx = document.getElementById('khataRecoveryChart');
      if (ctx) {
        new Chart(ctx, {
          type: 'bar',
          data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [{
              label: 'Recovered',
              data: [14200, 18500, 16900, 18900],
              backgroundColor: '#28cd41',
              borderRadius: 6
            }, {
              label: 'Credit Given',
              data: [9800, 11200, 10500, 11300],
              backgroundColor: '#ff9500',
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { display: false } },
              y: { grid: { color: 'rgba(0,0,0,0.04)' } }
            }
          }
        });
      }
    });
'''

customers_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head_meta}
  {master_style}
</head>
<body>
  <div class="app-viewport">
{make_dock("customers")}
    <main class="dashboard-canvas">
{make_header("Customers & Khata")}
{customers_bento}
    </main>
  </div>
{make_footer_and_scripts(customers_js)}
</body>
</html>'''

with open(os.path.join(OUT_DIR, "customers.html"), "w", encoding="utf-8") as f:
    f.write(customers_full)
with open(os.path.join(OUT_DIR, "khata.html"), "w", encoding="utf-8") as f:
    f.write(customers_full)
print("Successfully generated customers.html and khata.html")

# -----------------------------------------------------------------------------
# 5. CREATE analytics.html (Business Intelligence & SIH Reports)
# -----------------------------------------------------------------------------
analytics_bento = '''
      <!-- Bento Grid Content System -->
      <div class="bento-grid">

        <!-- ROW 1: Executive KPI Trio & Growth Chart -->
        <div class="glass-card quick-summary-card">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
              Executive Growth & Margin Matrix
            </h2>
            <span class="store-select-pill" style="font-size: 0.76rem; padding: 4px 10px;" onclick="cycleDukaans()">
              All Dukaans ▾
            </span>
          </div>

          <div class="summary-metrics-trio">
            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Monthly Gross Volume</span>
                <span class="metric-pill-badge badge-green">+24.2%</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statMonthlyRev">₹3,84,200</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Net Profit Margin</span>
                <span class="metric-pill-badge badge-green">Healthy</span>
              </div>
              <div class="metric-value-num tabular-nums" id="statMargin">23.8%</div>
            </div>

            <div class="metric-sub-card">
              <div class="metric-top-bar">
                <span class="metric-title">Customer Repeat Rate</span>
                <div class="badge-icon-box green-box">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
              </div>
              <div class="metric-value-num tabular-nums" id="statRepeat">88.4%</div>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- Monthly Sales Growth Chart -->
        <div class="glass-card daily-sales-card">
          <div class="card-header-row" style="margin-bottom: 8px;">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              Quarterly Revenue Velocity
            </h2>
            <span style="font-size: 0.72rem; color: var(--apple-blue); font-weight: 600;">FY26 Q3</span>
          </div>
          
          <div style="height: 125px; width: 100%; position: relative;">
            <canvas id="quarterlyGrowthChart"></canvas>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 2: Category Revenue Breakdown (Cols 1-6) + Fast Movers vs Dead Stock (Cols 7-12) -->
        <div class="glass-card inventory-status-card" style="grid-column: span 6;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 2a10 10 0 0 1 10 10h-10z"></path>
              </svg>
              Sales Share by Category
            </h2>
            <span style="font-size: 0.72rem; color: var(--brass-600); font-weight: 600;">Top: Staples (42%)</span>
          </div>

          <div style="height: 220px; width: 100%; position: relative; margin-top: 10px;">
            <canvas id="categoryShareChart"></canvas>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <div class="glass-card top-products-card" style="grid-column: span 6;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              Product Velocity Index
            </h2>
            <span style="font-size: 0.72rem; color: var(--apple-green); font-weight: 600;">Turnover / 30 Days</span>
          </div>

          <div class="top-products-list">
            <div class="top-product-item">
              <div class="top-prod-left">
                <img src="assets/products/parle_g.png" alt="Parle-G" class="table-prod-thumb" />
                <div class="top-prod-meta">
                  <span class="top-prod-name">Parle-G Biscuits</span>
                  <span class="top-prod-sku tabular-nums">Velocity: 94/100 • 540 packs sold</span>
                </div>
              </div>
              <span class="status-pill status-in">Super Mover</span>
            </div>

            <div class="top-product-item">
              <div class="top-prod-left">
                <img src="assets/products/sugar.png" alt="Sugar" class="table-prod-thumb" />
                <div class="top-prod-meta">
                  <span class="top-prod-name">Madhur Crystal Sugar</span>
                  <span class="top-prod-sku tabular-nums">Velocity: 88/100 • 320 kg sold</span>
                </div>
              </div>
              <span class="status-pill status-in">Super Mover</span>
            </div>

            <div class="top-product-item">
              <div class="top-prod-left">
                <img src="assets/products/alert_colgate.png" alt="Colgate" class="table-prod-thumb" />
                <div class="top-prod-meta">
                  <span class="top-prod-name">Colgate Strong Teeth</span>
                  <span class="top-prod-sku tabular-nums">Velocity: 72/100 • 95 units sold</span>
                </div>
              </div>
              <span class="status-pill status-in">Moderate</span>
            </div>

            <div class="top-product-item">
              <div class="top-prod-left">
                <img src="assets/products/dove.png" alt="Dove" class="table-prod-thumb" />
                <div class="top-prod-meta">
                  <span class="top-prod-name">Dove Soap (100g)</span>
                  <span class="top-prod-sku tabular-nums">Velocity: 32/100 • 28 units sold</span>
                </div>
              </div>
              <span class="status-pill status-low">Slow Mover</span>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 3: AI Profit Recommendations & Hackathon SIH Deck -->
        <div class="glass-card low-stock-alerts-card" style="grid-column: span 12;">
          <div class="card-header-row">
            <h2 class="card-heading" style="color: var(--brass-700);">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              AI Profit Optimization Recommendations (SIH Hackathon Engine)
            </h2>
            <span class="status-pill status-in">Estimated Gain: +₹14,200/mo</span>
          </div>

          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 6px;">
            <div style="background: rgba(255, 255, 255, 0.65); padding: 14px; border-radius: 14px; border: var(--glass-border-subtle);">
              <div style="font-weight: 700; color: var(--emerald-900); margin-bottom: 4px;">Edible Oil 5L Can Conversion</div>
              <p style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4;">
                Stocking 5L Fortune Cans instead of 1L pouches increases net margin from 8.4% to 14.2% via wholesale discount at Kolhapur Yard.
              </p>
              <div style="margin-top: 10px; font-weight: 700; color: var(--apple-green); font-size: 0.78rem;">+₹4,800/mo Profit</div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.65); padding: 14px; border-radius: 14px; border: var(--glass-border-subtle);">
              <div style="font-weight: 700; color: var(--emerald-900); margin-bottom: 4px;">Evening Tea Combo Bundle</div>
              <p style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4;">
                64% of 5 PM - 7 PM walk-ins buy Parle-G + Sugar. Bundling with Wagh Bakri Tea at ₹135 boosts basket size by 22%.
              </p>
              <div style="margin-top: 10px; font-weight: 700; color: var(--apple-green); font-size: 0.78rem;">+₹5,600/mo Profit</div>
            </div>

            <div style="background: rgba(255, 255, 255, 0.65); padding: 14px; border-radius: 14px; border: var(--glass-border-subtle);">
              <div style="font-weight: 700; color: var(--emerald-900); margin-bottom: 4px;">Automated Udhar WhatsApp Recovery</div>
              <p style="font-size: 0.78rem; color: var(--text-secondary); line-height: 1.4;">
                Sending polite automated Marathi reminders on Day 7 reduces overdue credit cycles from 28 days to 9 days.
              </p>
              <div style="margin-top: 10px; font-weight: 700; color: var(--apple-green); font-size: 0.78rem;">+₹3,800 Working Capital</div>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

      </div>
'''

analytics_js = '''
    document.addEventListener('DOMContentLoaded', () => {
      animateCounter('statMonthlyRev', 0, 384200, 1100, '₹');
      animateCounter('statRepeat', 0, 88.4, 900, '%');

      const ctxGrowth = document.getElementById('quarterlyGrowthChart');
      if (ctxGrowth) {
        new Chart(ctxGrowth, {
          type: 'line',
          data: {
            labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
            datasets: [{
              label: 'Revenue',
              data: [280000, 310000, 345000, 330000, 360000, 384200],
              borderColor: '#28cd41',
              backgroundColor: 'rgba(40, 205, 65, 0.12)',
              fill: true,
              tension: 0.4,
              borderWidth: 2.2,
              pointRadius: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: { grid: { display: false } },
              y: { grid: { color: 'rgba(0,0,0,0.04)' } }
            }
          }
        });
      }

      const ctxCat = document.getElementById('categoryShareChart');
      if (ctxCat) {
        new Chart(ctxCat, {
          type: 'doughnut',
          data: {
            labels: ['Staples', 'Biscuits & Snacks', 'Edible Oils', 'Personal Care', 'Dairy & Bakery'],
            datasets: [{
              data: [42, 24, 16, 10, 8],
              backgroundColor: ['#2d6a6f', '#c9a96e', '#0071e3', '#ff9500', '#28cd41'],
              borderWidth: 0
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'right',
                labels: { boxWidth: 10, font: { size: 9.5 } }
              }
            },
            cutout: '68%'
          }
        });
      }
    });
'''

analytics_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head_meta}
  {master_style}
</head>
<body>
  <div class="app-viewport">
{make_dock("analytics")}
    <main class="dashboard-canvas">
{make_header("Analytics & SIH Reports")}
{analytics_bento}
    </main>
  </div>
{make_footer_and_scripts(analytics_js)}
</body>
</html>'''

with open(os.path.join(OUT_DIR, "analytics.html"), "w", encoding="utf-8") as f:
    f.write(analytics_full)
print("Successfully generated analytics.html")

# -----------------------------------------------------------------------------
# 6. CREATE settings.html (Dukaan & Hardware / WhatsApp Configurations)
# -----------------------------------------------------------------------------
settings_bento = '''
      <!-- Bento Grid Content System -->
      <div class="bento-grid">

        <!-- ROW 1: Dukaan Profile Card (Cols 1-7) & Cloud Sync Status (Cols 8-12) -->
        <div class="glass-card quick-summary-card" style="grid-column: span 7;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                <polyline points="9 22 9 12 15 12 15 22"></polyline>
              </svg>
              Dukaan Profile & Legal Entity
            </h2>
            <span class="status-pill status-in">Verified GST</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 8px;">
            <div style="display: flex; gap: 12px;">
              <div style="flex: 1;">
                <label style="font-size: 0.72rem; color: var(--text-tertiary); font-weight: 600;">Store Name</label>
                <input type="text" class="apple-search-input" value="Ganesh Kirana Stores" style="width: 100%; margin-top: 2px;" />
              </div>
              <div style="width: 180px;">
                <label style="font-size: 0.72rem; color: var(--text-tertiary); font-weight: 600;">GSTIN</label>
                <input type="text" class="apple-search-input" value="27AABCG1234F1Z5" style="width: 100%; margin-top: 2px;" />
              </div>
            </div>

            <div>
              <label style="font-size: 0.72rem; color: var(--text-tertiary); font-weight: 600;">Store Address</label>
              <input type="text" class="apple-search-input" value="Shop #14, Main Cloth Market, Shahupuri, Kolhapur 416001" style="width: 100%; margin-top: 2px;" />
            </div>

            <div style="display: flex; gap: 12px;">
              <div style="flex: 1;">
                <label style="font-size: 0.72rem; color: var(--text-tertiary); font-weight: 600;">Owner Contact Phone</label>
                <input type="text" class="apple-search-input" value="+91 98220 99881" style="width: 100%; margin-top: 2px;" />
              </div>
              <div style="flex: 1;">
                <label style="font-size: 0.72rem; color: var(--text-tertiary); font-weight: 600;">UPI VPA Address</label>
                <input type="text" class="apple-search-input" value="ganeshkirana@icici" style="width: 100%; margin-top: 2px;" />
              </div>
            </div>

            <div style="display: flex; justify-content: flex-end; margin-top: 6px;">
              <button class="restock-btn" onclick="showAppleToast('Dukaan profile updated successfully!')">Save Profile</button>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <div class="glass-card daily-sales-card" style="grid-column: span 5;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="2" y1="12" x2="22" y2="12"></line>
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
              </svg>
              Cloud & Offline Sync Engine
            </h2>
            <span class="status-pill status-in">● Live Synced</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px; font-size: 0.8rem;">
            <div style="display: flex; justify-content: space-between;">
              <span style="color: var(--text-secondary);">Local SQLite Cache:</span>
              <span class="tabular-nums font-bold">14.8 MB (Synced)</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: var(--text-secondary);">Cloud Replica Status:</span>
              <span style="color: var(--apple-green); font-weight: 600;">Connected (0ms lag)</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: var(--text-secondary);">Last Automatic Backup:</span>
              <span class="tabular-nums">Today 07:12 AM</span>
            </div>
            <div style="margin-top: 14px; display: flex; gap: 8px;">
              <button class="apple-pill-btn btn-stock" style="flex: 1;" onclick="showAppleToast('Full offline backup downloaded (.json)')">Backup Now</button>
              <button class="apple-pill-btn btn-stock" style="flex: 1;" onclick="showAppleToast('Cloud sync forced: 100% synchronized')">Force Sync</button>
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <!-- ROW 2: WhatsApp Voice & NLP AI Engine Settings (Cols 1-7) & Hardware Printer (Cols 8-12) -->
        <div class="glass-card inventory-status-card" style="grid-column: span 7;">
          <div class="card-header-row">
            <h2 class="card-heading" style="color: #25d366;">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path>
              </svg>
              WhatsApp Voice AI & Auto-Ingress Rules
            </h2>
            <span class="status-pill status-in">Gemini Omni Active</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 12px; margin-top: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255, 255, 255, 0.6); border-radius: 12px;">
              <div>
                <div style="font-weight: 600; font-size: 0.82rem;">Marathi Speech-to-Order Recognition</div>
                <div style="font-size: 0.72rem; color: var(--text-tertiary);">Parses "दोन किलो साखर आणि पार्ले-जी" directly into SKU line items</div>
              </div>
              <input type="checkbox" checked style="accent-color: #25d366; width: 18px; height: 18px;" />
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255, 255, 255, 0.6); border-radius: 12px;">
              <div>
                <div style="font-weight: 600; font-size: 0.82rem;">Automatic Bill & UPI QR Dispatch</div>
                <div style="font-size: 0.72rem; color: var(--text-tertiary);">Instantly replies to customer with itemized digital bill and payment link</div>
              </div>
              <input type="checkbox" checked style="accent-color: #25d366; width: 18px; height: 18px;" />
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255, 255, 255, 0.6); border-radius: 12px;">
              <div>
                <div style="font-weight: 600; font-size: 0.82rem;">Auto-Confirm Orders Below ₹500</div>
                <div style="font-size: 0.72rem; color: var(--text-tertiary);">Orders > ₹500 request voice confirmation from shopkeeper</div>
              </div>
              <input type="checkbox" checked style="accent-color: #25d366; width: 18px; height: 18px;" />
            </div>
          </div>
          <div class="specular-sweep"></div>
        </div>

        <div class="glass-card top-products-card" style="grid-column: span 5;">
          <div class="card-header-row">
            <h2 class="card-heading">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 6 2 18 2 18 9"></polyline>
                <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                <rect x="6" y="14" width="12" height="8"></rect>
              </svg>
              Thermal Printer & Hardware
            </h2>
            <span class="status-pill status-in">Ready</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 8px;">
            <div style="font-size: 0.8rem; color: var(--text-secondary);">
              Connected Printer: <strong>Everycom 58mm Bluetooth ESC/POS</strong>
            </div>
            <div style="font-size: 0.76rem; color: var(--text-tertiary);">
              Paper Width: 58mm (Roll) • Auto-Cut: Disabled • Baud: 9600
            </div>
            
            <button class="apple-pill-btn btn-stock" style="margin-top: 8px;" onclick="showAppleToast('Printing test slip on thermal printer...')">
              🖨️ Print Test Receipt
            </button>
            <button class="restock-btn" style="justify-content: center;" onclick="showAppleToast('Searching for nearby Bluetooth / USB devices...')">
              Pair New Printer
            </button>
          </div>
          <div class="specular-sweep"></div>
        </div>

      </div>
'''

settings_full = f'''<!DOCTYPE html>
<html lang="en">
<head>
  {head_meta}
  {master_style}
</head>
<body>
  <div class="app-viewport">
{make_dock("settings")}
    <main class="dashboard-canvas">
{make_header("Settings & Hardware")}
{settings_bento}
    </main>
  </div>
{make_footer_and_scripts()}
</body>
</html>'''

with open(os.path.join(OUT_DIR, "settings.html"), "w", encoding="utf-8") as f:
    f.write(settings_full)
print("Successfully generated settings.html")

print("\nALL SUBPAGES AND MASTER INDEX SUCCESSFULLY GENERATED WITH 100% THEME UNIFORMITY!")

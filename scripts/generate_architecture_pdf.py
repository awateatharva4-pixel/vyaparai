import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Don't draw header on first page
        if self._pageNumber > 1:
            self.drawString(54, 750, "VyaparAI — Complete Backend Architecture, Execution Flow & Algorithm Guide")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)

        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        
        footer_text = "Atharva Awate | B.Tech AIML, Kolhapur Institute of Technology (KIT)"
        self.drawString(54, 32, footer_text)
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_pdf(filename="VyaparAI_Backend_Architecture_and_Workflow_Guide.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Palette
    c_primary = colors.HexColor("#0f3d32")      # Deep Emerald
    c_secondary = colors.HexColor("#1b6352")    # Mid Emerald
    c_accent = colors.HexColor("#c9a96e")       # Calacatta Brass / Gold
    c_dark = colors.HexColor("#1e293b")         # Charcoal Slate
    c_body = colors.HexColor("#334155")         # Body text slate
    c_light_bg = colors.HexColor("#f8fafc")     # Light card background
    c_callout_bg = colors.HexColor("#f0fdf4")   # Soft emerald callout
    c_border = colors.HexColor("#cbd5e1")       # Border slate

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b")
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_secondary,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=c_body,
        spaceAfter=7
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_body,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_block_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=8
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_primary
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#14532d")
    )

    story = []

    # ---------------------------------------------------------
    # COVER / HEADER BANNER
    # ---------------------------------------------------------
    story.append(Paragraph("VyaparAI: Backend Architecture & Technical Defense Guide", title_style))
    story.append(Paragraph("Clean Architecture, System Lifecycle (main.py), Core Algorithms, and Evaluation Post-Mortem", subtitle_style))
    
    meta_text = (
        "<b>Author:</b> Atharva Awate | <b>Institution:</b> Kolhapur Institute of Technology (KIT) — B.Tech 1st Year AIML<br/>"
        "<b>Project:</b> VyaparAI (Autonomous Retail Digitization for Kolhapur Kirana Stores) | <b>Version:</b> 2.0 Production<br/>"
        "<b>Prepared For:</b> Academic Mentors, External Examiners, Hackathon Reviewers & Technical Portfolio"
    )
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=4, spaceAfter=14))

    # ---------------------------------------------------------
    # SECTION 1: EXECUTIVE SUMMARY & POST-MORTEM
    # ---------------------------------------------------------
    story.append(Paragraph("1. Executive Summary & Review Post-Mortem", h1_style))
    p1 = (
        "VyaparAI is a specialized, zero-touch retail operating system designed for tier-2/3 Indian kirana stores "
        "(specifically modeled after traditional grocery stores in Kolhapur, Maharashtra). It digitizes counter commerce "
        "via multimodal WhatsApp ingress (handwritten yaadi slips, Marathi voice notes, and 15-second shelf sweep videos) "
        "and couples it with sub-millisecond loose commodity reverse-math, a zero-deduction staged ordering queue, "
        "and real-time WebSocket dashboard synchronization."
    )
    story.append(Paragraph(p1, body_style))

    p_postmortem = (
        "<b>The Evaluation Review & Pacing Lesson:</b> During the HELLO WORLD 2026 Hackathon, the external faculty/judges "
        "reviewed the project while active codebase updates were in flight. While the project concept and technical ambition "
        "were recognized as outstanding, the sir noted two crucial areas of inquiry:<br/>"
        "1. <i>'Why are there so many folders and modular layers?'</i> (Understanding production Clean Architecture vs. single-file scripts).<br/>"
        "2. <i>'How does the backend actually start, where does it start (main.py), and what is the exact algorithm and workflow?'</i><br/>"
        "This document provides the definitive architectural defense, execution trace, and algorithmic specification to "
        "answer every question with absolute technical rigor."
    )
    
    # Callout Box for Post-Mortem
    callout_data = [[Paragraph(p_postmortem, callout_style)]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_callout_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#86efac")),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # SECTION 2: WHY THIS FOLDER STRUCTURE? (CLEAN ARCHITECTURE)
    # ---------------------------------------------------------
    story.append(Paragraph("2. Architectural Design: Why So Many Folders?", h1_style))
    p2 = (
        "Beginner student projects often place all code into a single 3,000-line <code>app.py</code> file. "
        "While this looks simple at first glance, it creates <b>spaghetti architecture</b>: database queries, business rules, "
        "AI parsing, and HTTP routes become hopelessly entangled. If one function breaks, the entire application crashes, "
        "unit testing becomes impossible, and scaling is blocked."
    )
    story.append(Paragraph(p2, body_style))

    p2_clean = (
        "VyaparAI adheres strictly to <b>Domain-Driven Clean Layered Architecture</b> (Enterprise FastAPI Standard). "
        "Each folder has a single, strictly isolated responsibility adhering to the Separation of Concerns (SoC) principle:"
    )
    story.append(Paragraph(p2_clean, body_style))

    # Directory explanation table
    dir_data = [
        [
            Paragraph("Folder / File", table_header_style),
            Paragraph("Layer Name", table_header_style),
            Paragraph("Role & Architectural Responsibility", table_header_style)
        ],
        [
            Paragraph("<code>app/main.py</code>", table_cell_bold),
            Paragraph("Application Orchestrator", table_cell_style),
            Paragraph("Root ASGI application entrypoint. Initializes database, launches lifespan background daemon workers, mounts middleware, static assets, and sub-routers.", table_cell_style)
        ],
        [
            Paragraph("<code>app/core/</code>", table_cell_bold),
            Paragraph("Infrastructure & Config", table_cell_style),
            Paragraph("Manages environment variables via Pydantic <code>BaseSettings</code> (<code>config.py</code>), SQLAlchemy database engine and session factories (<code>database.py</code>), and WAL checkpointing.", table_cell_style)
        ],
        [
            Paragraph("<code>app/models/</code>", table_cell_bold),
            Paragraph("Data Domain Entities", table_cell_style),
            Paragraph("Pure SQLAlchemy ORM entity models (<code>Product</code>, <code>CustomerOrder</code>, <code>Transaction</code>, <code>CustomerCredit</code>). Maps relational database tables cleanly without business logic pollution.", table_cell_style)
        ],
        [
            Paragraph("<code>app/routers/</code>", table_cell_bold),
            Paragraph("API Controllers / Ingress", table_cell_style),
            Paragraph("HTTP/WebSocket traffic controllers (<code>webhook.py</code>, <code>inventory.py</code>, <code>simulator.py</code>). Validates incoming payloads, extracts headers, and delegates execution to services.", table_cell_style)
        ],
        [
            Paragraph("<code>app/services/</code>", table_cell_bold),
            Paragraph("Domain Business Logic", table_cell_style),
            Paragraph("Core intelligence engine: Gemini 2.5 Flash Vision Multimodal OCR (<code>gemini_service.py</code>), loose commodity reverse-math and state machines (<code>inventory_service.py</code>), audio normalization (<code>audio_service.py</code>), and WhatsApp gateway (<code>whatsapp_service.py</code>).", table_cell_style)
        ],
        [
            Paragraph("<code>data/</code>", table_cell_bold),
            Paragraph("Durable Persistence & Seed", table_cell_style),
            Paragraph("Stores immutable 14-SKU Kolhapur kirana seed data (<code>seed_inventory.json</code>) and crash-resilient atomic state snapshots (<code>vyaparai_state.json</code>).", table_cell_style)
        ],
        [
            Paragraph("<code>frontend/</code>", table_cell_bold),
            Paragraph("Client Presentation Layer", table_cell_style),
            Paragraph("Modern, Calacatta marble single-page dashboard (HTML5, Apple VisionOS design system, Chart.js, sub-millisecond reverse-math scale UI). Communicates via WebSockets.", table_cell_style)
        ],
        [
            Paragraph("<code>tests/</code>", table_cell_bold),
            Paragraph("Verification & Regression", table_cell_style),
            Paragraph("Automated pytest test suite validating order lifecycles, stock deduction invariants, and Gemini OCR parser accuracy.", table_cell_style)
        ]
    ]

    t_dir = Table(dir_data, colWidths=[110, 114, 280])
    t_dir.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_light_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_dir)
    story.append(Spacer(1, 14))

    # ---------------------------------------------------------
    # SECTION 3: SYSTEM LIFECYCLE (HOW CODE STARTS FROM MAIN.PY)
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("3. How the Code Starts: Execution Journey from main.py", h1_style))
    p3 = (
        "When an examiner asks: <i>'Where does execution start?'</i>, the exact answer is: "
        "<b>The Uvicorn ASGI Server boots the application by binding to <code>app.main:app</code>.</b> "
        "Here is the precise microsecond-by-microsecond sequence:"
    )
    story.append(Paragraph(p3, body_style))

    story.append(Paragraph("Step 1: Process Invocation & Dependency Graph Loading", h2_style))
    story.append(Paragraph(
        "• Command executed: <code>uvicorn app.main:app --host 0.0.0.0 --port 8000</code><br/>"
        "• Python loads <code>app/main.py</code>. This causes <code>app.core.config.settings</code> to read environment variables "
        "from <code>.env</code> (Gemini API keys, Green-API instance tokens, database connection URIs).<br/>"
        "• <code>app.core.database</code> creates the SQLAlchemy <code>engine</code> and sets SQLite into Write-Ahead Logging (WAL) "
        "mode (<code>PRAGMA journal_mode=WAL</code>), guaranteeing zero database corruption during simultaneous writes.",
        bullet_style
    ))

    story.append(Paragraph("Step 2: ASGI Lifespan Hook & Self-Healing Database Seed", h2_style))
    story.append(Paragraph(
        "FastAPI executes the modern <code>@asynccontextmanager async def lifespan(app: FastAPI)</code> hook before "
        "accepting any incoming HTTP traffic:<br/>"
        "1. <b>Self-Healing Catalog Ingestion:</b> <code>InventoryService.seed_initial_catalog(db)</code> is called. It checks if the "
        "database has the 14 master Kolhapur Kirana products (Parle-G, Sugar, Sunflower Oil, Pav, Classmate Notebook, etc.). "
        "If the tables are empty or newly initialized, it automatically seeds them from <code>data/seed_inventory.json</code>.<br/>"
        "2. <b>Order Expiration Background Daemon:</b> An asynchronous background task <code>order_expiration_worker()</code> is launched "
        "using <code>asyncio.create_task()</code>. This daemon runs continuously in the background, waking every 30 seconds to enforce "
        "the 30-minute auto-restitution lifecycle on unfulfilled customer yaadi orders.",
        bullet_style
    ))

    code_lifespan = (
        "@asynccontextmanager\n"
        "async def lifespan(app: FastAPI):\n"
        "    # 1. Self-healing database initialization on boot\n"
        "    db = SessionLocal()\n"
        "    try:\n"
        "        InventoryService.seed_initial_catalog(db)\n"
        "    finally:\n"
        "        db.close()\n\n"
        "    # 2. Launch background auto-restitution worker\n"
        "    worker_task = asyncio.create_task(order_expiration_worker())\n"
        "    yield  # Application runs and serves requests\n"
        "    worker_task.cancel()  # Graceful shutdown\n"
        "    await worker_task"
    )
    story.append(Paragraph(code_lifespan.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_block_style))

    story.append(Paragraph("Step 3: Middleware Pipeline & Exception Handling", h2_style))
    story.append(Paragraph(
        "• <b>CORSMiddleware:</b> Configured to permit cross-origin communication between the frontend dashboard and FastAPI.<br/>"
        "• <b>Global Safe Exception Handler:</b> Catches unhandled exceptions, logs internal stack traces to server logs, "
        "and returns clean, standardized JSON errors without exposing internal directory paths.",
        bullet_style
    ))

    story.append(Paragraph("Step 4: Static File Mounts & Sub-Router Attachment", h2_style))
    story.append(Paragraph(
        "• Static directories mounted: <code>/frontend</code>, <code>/assets</code>, and <code>/static</code> serve client assets.<br/>"
        "• Modular sub-routers attached via <code>app.include_router()</code>:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;→ <code>webhook.router</code>: WhatsApp messaging, image OCR ingress, voice notes, video sweep.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;→ <code>inventory.router</code>: Metrics, GST CSV export, catalog inspection, manual restock.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;→ <code>simulator.router</code>: Customer yaadi queue management, order packing, simulation tools.<br/>"
        "• Real-time WebSocket: <code>@app.websocket(\"/ws/inventory\")</code> opens reactive metric streaming directly to browser clients.",
        bullet_style
    ))

    # ---------------------------------------------------------
    # SECTION 4: THE CORE ALGORITHMS & WORKFLOWS
    # ---------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(Paragraph("4. Core Algorithms & Execution Workflows", h1_style))
    
    story.append(Paragraph("Algorithm A: Multimodal WhatsApp Ingress & Intent Classification", h2_style))
    p_algo_a = (
        "<b>Workflow:</b> When a message hits <code>/api/v1/webhook/whatsapp</code>:<br/>"
        "1. <b>Idempotency Check:</b> The message ID (<code>idMessage</code>) is verified against cached delivery receipts to discard duplicate retries.<br/>"
        "2. <b>Caller Role Disambiguation:</b> If sender is Atharva (<code>9579869506</code>), route to <i>Merchant Admin</i>. "
        "If sender is Venkatesh Pai (<code>7019259321</code>), route to <i>Customer Yaadi Processing</i>.<br/>"
        "3. <b>Multimodal Parsing:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Handwritten Image Slip:</b> Download image bytes → Pass to Gemini 2.5 Flash Vision with Devanagari prompt → "
        "Extract items, normalized quantities, unit prices → Stage in Pending Queue with zero direct deduction.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Audio Voice Note:</b> Normalize via FFmpeg bandpass filter → Transcribe via Gemini Audio → "
        "Classify intent (<code>SALE</code>, <code>PURCHASE</code>, <code>UDHAR</code>) → Update ledger.<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;• <b>15-Second Shelf Video:</b> Upload to GenAI File API → Detect SKUs and shelf quantities → "
        "Auto-generate Marathi aliases → Ingest into active inventory."
    )
    story.append(Paragraph(p_algo_a, body_style))

    story.append(Paragraph("Algorithm B: Sub-1ms Loose Commodity Reverse-Math", h2_style))
    p_algo_b = (
        "In Indian kirana stores, customers never buy loose commodities by round weights (e.g., they ask: <i>'20 chi sakhar dya'</i> — "
        "give ₹20 worth of sugar). Traditional POS software fails because it expects weight input first.<br/>"
        "<b>Mathematical Formula:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Target Weight (kg) = Requested Budget (₹) ÷ Item Unit Price (₹/kg)</b><br/>"
        "<b>Vernacular Parser Mapping:</b><br/>"
        "• <code>'20 chi sakhar'</code> → ₹20 ÷ ₹42/kg = <b>0.476 kg (476 grams)</b> on the digital scale OLED.<br/>"
        "• <code>'पावशेर साखर'</code> (Paw-sher) → Pre-mapped vernacular constant = <b>250 grams</b>.<br/>"
        "• <code>'सव्वा किलो गहू'</code> (Savva Kilo) → Pre-mapped vernacular constant = <b>1.250 kg</b>.<br/>"
        "Execution benchmark: <b>0.022 milliseconds</b> (pure client-side reverse-math execution)."
    )
    story.append(Paragraph(p_algo_b, body_style))

    story.append(Paragraph("Algorithm C: Zero Direct-Deduction State Machine (Customer Yaadi Queue)", h2_style))
    p_algo_c = (
        "<b>The Kirana Invariant:</b> Master stock must <i>never</i> be deducted directly when a customer sends a raw WhatsApp yaadi, "
        "because physical items might be damaged, substituted, or out of stock.<br/>"
        "<b>State Machine Lifecycle:</b><br/>"
        "1. Order arrives via WhatsApp → Enters <code>PENDING</code> state.<br/>"
        "2. Soft reservation: Items are marked as <code>🔒 साठा वजा (Reserved)</code> on the merchant dashboard.<br/>"
        "3. <b>30-Minute Auto-Restitution:</b> A 1-second countdown timer runs on the UI, mirrored by <code>order_expiration_worker()</code> "
        "on the backend. If the merchant does not fulfill the order within 30 minutes, status transitions to <code>EXPIRED</code> and "
        "soft-reserved quantities return to available stock.<br/>"
        "4. <b>Pack & Fulfill:</b> When merchant clicks 'Pack & Fulfill', the order transitions atomically to <code>COMPLETED</code>, "
        "master inventory is permanently decremented, and a formatted digital receipt with total bill is sent back via WhatsApp."
    )
    story.append(Paragraph(p_algo_c, body_style))

    # ---------------------------------------------------------
    # SECTION 5: VIVA & PROFESSOR DEFENSE GUIDE
    # ---------------------------------------------------------
    story.append(PageBreak())
    story.append(Paragraph("5. Viva & Project Defense Guide (Questions for Sir / Judges)", h1_style))
    p5 = (
        "Use these structured answers when your college faculty, external examiner, or hackathon judges evaluate your project:"
    )
    story.append(Paragraph(p5, body_style))

    qa_data = [
        (
            "Q1: Why did you split the code into so many folders instead of keeping it in one or two files?",
            "<b>Answer:</b> 'Sir, keeping 3,000 lines of code in a single file is considered an anti-pattern in modern software engineering. We followed Enterprise Clean Architecture (Layered Pattern). We separated Models (database schemas), Routers (HTTP API endpoints), Services (business logic & AI processing), and Core (configuration & database pooling). This guarantees that if we modify our Gemini AI prompt or swap our WhatsApp API gateway, the database and frontend remain completely unaffected. It also enables automated unit testing and clean team development.'"
        ),
        (
            "Q2: Where does execution start in the backend, and what happens on startup?",
            "<b>Answer:</b> 'Sir, execution starts in <code>app/main.py</code> when Uvicorn launches the ASGI application. Before handling any HTTP request, FastAPI triggers the <code>lifespan</code> event. Here, it establishes database connection pooling with SQLite WAL mode, runs a self-healing catalog check to ensure all 14 Kirana products exist in the database, and spawns an asynchronous background worker (<code>order_expiration_worker</code>) that runs every 30 seconds to handle the 30-minute auto-undo timer for pending yaadi orders.'"
        ),
        (
            "Q3: How do you handle WhatsApp messages if the customer sends audio in Marathi or a handwritten paper note?",
            "<b>Answer:</b> 'Sir, our webhook router (<code>app/routers/webhook.py</code>) inspects the MIME type of the payload. If it is an image of a handwritten slip, we pass it to Gemini 2.5 Flash Vision with a specialized Devanagari prompt that parses local handwriting into structured JSON items, quantities, and prices. If it is a voice note, our <code>AudioNormalizer</code> applies bandpass filtering and loudness normalization before transcribing and extracting intent with Gemini. The order is then safely staged into our Pending Queue.'"
        ),
        (
            "Q4: What is the 'Reverse Math' feature and why is it important?",
            "<b>Answer:</b> 'Sir, in local grocery stores, customers routinely ask for commodities by rupee value rather than weight (e.g. <i>\"₹20 chi sakhar dya\"</i>). Standard POS software forces shopkeepers to calculate weight manually. Our reverse-math engine parses colloquial Marathi queries in sub-millisecond time (0.022ms) and solves <i>Weight = Budget ÷ Unit Price</i>, displaying the exact target in grams (476g) directly on our digital scale OLED display.'"
        ),
        (
            "Q5: How does your system prevent inventory count corruption?",
            "<b>Answer:</b> 'Sir, we enforce the Zero Direct-Deduction Invariant. When a customer sends an order, stock is NEVER subtracted immediately. It is placed into a 30-minute staged PENDING queue with soft reservation. The merchant retains full control to click \"Pack & Fulfill\" to commit the deduction, or let the 30-minute timer automatically restore the reserved stock back to available inventory.'"
        )
    ]

    for q, a in qa_data:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(a, body_style))
        story.append(Spacer(1, 4))

    # ---------------------------------------------------------
    # CONCLUSION & SIGN-OFF
    # ---------------------------------------------------------
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=c_accent, spaceBefore=6, spaceAfter=10))
    closing_text = (
        "<b>Summary for Examiners:</b> VyaparAI demonstrates a complete, production-ready full-stack AI engineering workflow. "
        "It integrates real-time WebSockets, multimodal GenAI vision/audio processing, asynchronous background workers, "
        "and resilient database architecture tailored specifically for Bharat's retail economy."
    )
    story.append(Paragraph(closing_text, body_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    out_pdf = "VyaparAI_Backend_Architecture_and_Workflow_Guide.pdf"
    if len(sys.argv) > 1:
        out_pdf = sys.argv[1]
    build_pdf(out_pdf)

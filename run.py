import uvicorn
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"\n" + "="*60)
    print(f"  VYAPARAI SERVER INITIALIZING")
    print(f"  Team: Shadow (Atharva Awate & Venkatesh Pai)")
    print(f"  Event: HELLO WORLD 2026 Hackathon Finals (KIT CSE Lab)")
    print(f"  Merchant Portal: http://localhost:{port}/dashboard")
    print(f"  WhatsApp Simulator: http://localhost:{port}/test-console")
    print(f"  API Docs (Swagger): http://localhost:{port}/docs")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

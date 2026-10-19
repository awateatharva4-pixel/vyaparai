# VyaparAI Project Rules

- **Subagents First**: Always use specialized subagents for audits, multi-vector testing, frontend-backend synchronization, and feature builds. Never hesitate to invoke multiple parallel subagents to ensure deep coverage and zero blind spots.
- **Single Store Authority**: Locked strictly to 'अथर्व किराणा स्टोअर्स, कोल्हापूर' (DEMO_KIRANA_KOP).
- **Dual-Role Communication**:
  - Merchant Admin (+91 95798 69506) = Full control, fulfillment, alerts.
  - Customer (+91 70192 59321) = Yaadi order placement, staged queue.
- **100% UI to Backend Parity**: Every clickable element in the UI must have a corresponding, persistent backend API endpoint and reactive state sync.

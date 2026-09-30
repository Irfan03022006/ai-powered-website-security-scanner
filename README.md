# AI-Powered Website Security Scanner

A beginner-friendly, defensive web application that performs an **authorized,
non-destructive** security assessment of a website and uses AI to explain the
findings in plain language with remediation guidance.

> ⚠️ **Only scan websites you own or have explicit written authorization to
> test.** This tool performs safe, read-only checks. It does not attempt
> exploitation, brute-forcing, credential attacks, or denial-of-service, and
> it is **not** a replacement for a professional penetration test.

---

## 1. Problem Statement

Security scan output is often full of jargon that's hard for non-experts to
act on. Existing tools such as OWASP ZAP provide extensive, professional
security testing capabilities. This project does not attempt to replace
them. Instead, it focuses on a simplified, AI-assisted workflow for
**understanding** findings and **improving** security over time:

```
DETECT → EXPLAIN → RECOMMEND → FIX → RESCAN → COMPARE
```

## 2. Objectives

- Run safe, non-destructive checks against an authorized target
- Turn raw technical findings into plain-language explanations
- Give a transparent, documented risk score (0–100)
- Let users fix issues, rescan, and see a before/after comparison
- Never behave as an SSRF tool against internal infrastructure

## 3. Proposed Solution / Architecture

```
Browser (dashboard UI)
   │  REST calls
   ▼
Flask app (app.py)
   │
   ├── scanner/            → SSRF-safe URL validation + 5 scan modules + risk engine
   ├── ai/analyzer.py       → sends structured findings to an LLM (or fallback)
   ├── models/               → SQLAlchemy models (Scan, Finding)
   └── routes/               → scan / report / comparison REST endpoints
   │
   ▼
SQLite database (scanner.db)
```

Data flow per the required workflow:

```
User enters authorized URL
   → validate URL (SSRF checks)
   → run scan modules (HTTPS, headers, cookies, config, disclosure)
   → generate findings
   → calculate risk score
   → AI explains each finding
   → store scan + findings
   → render dashboard / findings / report
   → user fixes issues → rescan → compare before/after
```

## 4. Technology Stack

- **Frontend:** HTML5, CSS3 (custom, no build step), vanilla JavaScript
- **Backend:** Python 3, Flask, REST API
- **Database:** SQLite via SQLAlchemy
- **Scanning:** `requests`, `ssl`, `socket`, `urllib` (standard library-first)
- **AI:** Configurable provider (Anthropic or OpenAI) via environment
  variable, with a rule-based fallback when no key is configured
- **Reporting:** Server-rendered HTML report, JSON export, optional PDF
  export (via `xhtml2pdf`)

## 5. Scanner Modules

| Module | What it checks |
|---|---|
| `https_scanner.py` | HTTPS enabled, HTTP→HTTPS redirect, certificate expiry, TLS version, cert validation failures |
| `headers_scanner.py` | CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy |
| `cookie_scanner.py` | Secure / HttpOnly / SameSite flags (cookie **values** are never stored or logged) |
| `configuration_scanner.py` | Reachability, redirect behavior, risky HTTP methods advertised via OPTIONS |
| `disclosure_scanner.py` | Server/framework/version headers that leak stack information |
| `risk_engine.py` | Turns findings into a transparent 0–100 score |

All modules only issue safe `GET` / `HEAD` / `OPTIONS` requests through
`scanner/safe_request.py`, which enforces timeouts, a redirect cap, and a
response-size cap.

## 6. AI Workflow

`ai/analyzer.py` sends **one structured finding at a time** (never raw page
content) to the configured LLM with a system prompt that:

- forbids inventing vulnerabilities beyond what the finding supports
- forbids claiming exploitability unless the scanner established it
- requires the response to separate "what it means" / "why it matters" /
  "possible impact" / "recommended action" / "priority"

If `AI_API_KEY` is not set, or the AI call fails for any reason, the app
transparently falls back to a rule-based explanation generator built from
the finding's own description/impact/recommendation fields, tagged
`"source": "fallback"`, so the app always produces a complete result.

## 7. Risk Scoring (documented logic)

```
High   finding = 3 points
Medium finding = 2 points
Low    finding = 1 point

penalty = sum of points across all findings
security_score = max(0, 100 - penalty * 4)
```

This is a simplified, transparent, **educational** scoring model — it is
explicitly not presented as an industry-standard penetration-test score.
See `scanner/risk_engine.py` for the exact logic.

## 8. Database Design

- **scans**: id, url, timestamp, security_score, status, error_message
- **findings**: id, scan_id (FK), title, category, severity, description,
  evidence, impact, recommendation, scanner_module, plus stored AI
  explanation fields

No passwords, session cookies, authentication tokens, or other secrets are
ever stored.

## 9. SSRF / Scanner Self-Protection

Because this app accepts arbitrary URLs, `scanner/url_validator.py` enforces:

- Only `http`/`https` schemes
- No embedded credentials in the URL
- Rejects `localhost` / `0.0.0.0` / metadata hostnames
- Resolves the hostname and blocks private, loopback, link-local, reserved,
  multicast, and unspecified IP ranges (also catches DNS-rebinding-style
  tricks where a public hostname resolves to an internal IP)
- Only a small allow-list of common web ports (80, 443, 8080, 8443)
- Outbound requests use bounded timeouts, a redirect cap, and a response
  size cap (`scanner/safe_request.py`)
- A simple in-memory rate limiter caps scans per IP per time window

**Known limitation:** DNS is resolved once during validation and again by
`requests` when it connects; a sophisticated DNS-rebinding attack timed
between those two lookups is a theoretical residual risk in this
educational implementation. Production deployments should pin the resolved
IP for the request itself.

## 10. Installation

```bash
cd ai-security-scanner
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

## 11. Configuration

Edit `.env`:

```
SECRET_KEY=some-random-string
AI_PROVIDER=anthropic          # anthropic | openai | none
AI_API_KEY=                    # leave blank to use the fallback explainer
AI_MODEL=claude-sonnet-4-6
```

If `AI_API_KEY` is blank, the app still works end-to-end using the
fallback explanation generator.

## 12. How to Run

```bash
python app.py
```

Then open http://127.0.0.1:5000

## 13. How to Perform an Authorized Scan

1. Confirm you own the target site or have written authorization to test it.
2. Enter the URL on the home page and click **Start Security Scan**.
3. Review the dashboard (score, risk distribution, categories).
4. Open **Findings** to read each AI-explained finding and its fix.
5. Apply the recommended fixes on your site.
6. Click **Fix Issues, Then Rescan** on the dashboard.
7. Review the **Before vs After** comparison and score delta.

## 14. Example Output

```
BEFORE:
Security Score: 68/100
High: 2   Medium: 4   Low: 3

AFTER:
Security Score: 86/100
High: 0   Medium: 2   Low: 3

+18 point improvement
Issues fixed: 4
Issues still present: 5
New issues: 0
```

## 15. API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/scan` | Start a new scan (`{"url": "..."}`) |
| GET | `/api/scan/<id>` | Scan summary |
| GET | `/api/scan/<id>/findings` | Full findings list |
| GET | `/api/scan/<id>/report` | JSON report |
| POST | `/api/scan/<id>/rescan` | Re-scan the same target |
| GET | `/api/compare/<old_id>/<new_id>` | Before/after comparison |
| GET | `/api/scans` | Recent scan history |

## 16. Testing

```bash
python -m unittest discover tests -v
```

Tests cover URL validation/SSRF protection, each scanner module (via
mocked HTTP responses — **no live sites are scanned during tests**), risk
scoring, and AI fallback behavior.

## 17. Limitations

- Read-only, unauthenticated checks only — no login-flow or business-logic
  testing
- Does not test API endpoints, mobile apps, or infrastructure beyond the
  supplied URL
- Not a replacement for a professional, authorized penetration test
- AI explanations are only as good as the underlying scanner findings; the
  AI is instructed not to invent issues, but always review findings yourself

## 18. Future Scope (not implemented in this mini-project)

- API security assessment
- Malware / file reputation checking
- Source-code security analysis
- Dependency vulnerability scanning
- Continuous monitoring and alerts
- Team dashboards / multi-user accounts
- Deeper OWASP-aligned active checks (with explicit authorization workflow)
- AI-assisted auto-remediation suggestions as pull requests
- CI/CD pipeline integration

## 19. Security Considerations

- This tool must only ever be pointed at systems you are authorized to test.
- The scanner intentionally avoids anything destructive: no brute force, no
  exploitation, no DoS, no malware.
- Cookie values, credentials, and tokens are never stored.
- Outbound requests are bounded (timeout, redirect cap, size cap) and
  target IPs are checked against private/internal ranges before every scan.
- Report a security issue in this project by opening an issue in your own
  repository fork — do not use this tool against systems without permission.

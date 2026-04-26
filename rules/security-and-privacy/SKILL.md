---
name: security-and-privacy
description: Guides secure-by-default development: threat modeling, authentication/authorization, secrets management, input validation, secure headers, dependency hygiene, logging redaction, and privacy (data mapping, minimization, consent, retention, DSR). Use when adding auth, handling PII, integrating third parties, or hardening services.
license: Complete terms in LICENSE.txt
---

# Security and Privacy

## Principles
Least privilege. Defense in depth. Secure by default. Privacy by design. Visibility and accountability.

## Instructions

### Step 1: Classify data and scope
- Identify PII/PHI/financial data; tag sensitivity.
- Map data flows and storage locations; define purpose and legal basis.

### Step 2: Threat model (STRIDE baseline)
- Identify actors, assets, entry points, and trust boundaries.
- Enumerate risks: spoofing, tampering, repudiation, information disclosure, DoS, elevation of privilege.
- Decide mitigations and owners; record assumptions.

### Step 3: Authentication and session
- Prefer federated auth or strong password policies with lockouts.
- JWT: short-lived access; verify `iss`, `aud`, `exp`, algorithm; rotate keys.
- Sessions: `Secure`, `HttpOnly`, `SameSite=Strict`; CSRF tokens on state-changing requests.

### Step 4: Authorization
- Enforce RBAC/ABAC checks in service layer; deny-by-default.
- Resource ownership checks; scope queries by tenant/user.

### Step 5: Input/output handling
- Validate and normalize inputs at boundaries with schemas.
- Use parameterized queries; escape/encode outputs to prevent XSS.
- CSRF protection for browser clients; double-submit or token pattern.

### Step 6: Transport and headers
- TLS 1.2+; HSTS with preload (after verifying HTTPS readiness).
- Security headers: CSP, frame-ancestors (or X-Frame-Options), X-Content-Type-Options, Referrer-Policy, Permissions-Policy.

### Step 7: Secrets and dependencies
- Store secrets in a vault or environment, not in VCS; rotate regularly.
- Principle of least privilege for DB/users/API keys; scoped tokens.
- Maintain SBOM; run SCA; pin versions; enable auto-updates; SAST/DAST in CI.

### Step 8: File handling and SSRF protections
- Validate mime/extension/size; antivirus scanning for uploads; store outside web root.
- SSRF: egress allowlist; block metadata endpoints; sanitize URLs; disable proxying untrusted targets.

### Step 9: Abuse prevention
- Rate limits per-IP and per-identity; anomaly detection.
- Idempotency keys for unsafe operations; replay protection.

### Step 10: Logging, monitoring, incident readiness
- Structured logs with correlation IDs; redact PII/secrets.
- Alerts for auth failures, rate-limit breaches, anomalous spikes.
- Incident runbooks, on-call rotation, contact list; practice tabletop exercises.

## Privacy
- Data inventory and mapping; minimization and purpose limitation.
- Consent and preference management where required (e.g., EEA).
- Retention schedules; deletion/DSR workflows with audit logs.
- Cross-border transfers; SCCs or appropriate safeguards.
- Privacy notices and records of processing activities (RoPA).

## Checklists

### App security checklist
- Authn/z enforced; secure defaults; no hardcoded secrets.
- Input validation and output encoding; CSRF protection where applicable.
- Secure transport and headers configured; rate limits in place.
- Logs redact secrets/PII; alerts configured; backups encrypted.

### Privacy checklist
- Data categories and legal bases documented.
- Consent flows implemented where needed; user access/erasure supported.
- Retention and deletion policies enforced and automated.

## Troubleshooting
- JWT validation failures: check clock skew, audience/issuer, key rotation, algorithm mismatch.
- CSP breaking UI: start with `Report-Only`, audit reports, then tighten directives.
- Over-permissive roles: audit policies; move to least-privilege roles with explicit conditions.

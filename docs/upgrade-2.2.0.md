# Upgrade Guide — v2.1.0 → v2.2.0

## What changed

This release completes the CRA compliance module against the actual text of Regulation (EU) 2024/2847.

**Regulation accuracy fixes (no user action required)**
- All 18 CRA requirement `article` fields now cite exact Annex I section numbers (e.g. `Annex I Part I §2` instead of `Art. 13`)
- CRA-14 (24h reporting) correctly labelled as an Art. 14 procedural obligation — not an Annex I Part II item
- CRA-09 now covers Annex I Part I §1 (no known exploitable vulnerabilities at market placement) and §10 (security update capability), plus Part II §7–§8 (update distribution and automatic patching)
- CRA-13 now explicitly covers §4–§6 (disclosure, CVD policy, contact address)
- Automotive exclusion corrected from Art. 2(5)(a) to **Art. 2(2)(c)**

**New features**
- Art. 24 open-source steward path — classification wizard now distinguishes non-commercial stewards (security attestation) from commercial open-source vendors (Module A)
- Art. 13 conformity workflow — new **Conformity** tab in each assessment with a 7-step checklist: conformity assessment, Declaration of Conformity, CE marking, EU central database registration (Art. 31), 10-year documentation retention (Art. 23(1)), post-market surveillance plan, EOSS publication
- Annex II user-information checklist — new **Annex II** tab listing all 9 mandatory user-information items; support-period item auto-resolves from stored EOSS date

---

## Required steps

### 1. Run the database migration

```bash
cd /path/to/QuickTARA
source .venv/bin/activate
alembic upgrade head
```

This creates one new table: `cra_conformity_checklists`. All existing data is preserved. The migration is reversible (`alembic downgrade -1`).

**Verify:**
```bash
alembic current
# should show: j0k1l2m3n4o5 (head)
```

### 2. Restart the API

```bash
# Docker
docker compose restart api

# Direct
pkill -f "uvicorn api.app" && uvicorn api.app:app --reload
```

### 3. Rebuild and redeploy the frontend

```bash
cd tara-web
npm run build
# then serve /build as before
```

---

## What users will see

- **Classification wizard** — when "Free/open-source" is selected, a second option appears: "Non-commercial open-source steward? Art. 24". Selecting it produces a `steward` classification with the security attestation path instead of Module A/B+C.
- **Assessment detail page** — two new tabs appear after Annex VII:
  - **Conformity** — tick off each Art. 13 obligation as it is completed; add module name, signatory, registration ID, EOSS URL inline
  - **Annex II** — review all 9 mandatory user-information items; support-period status is auto-derived from the EOSS date set in Overview

---

## Rollback

If anything goes wrong:

```bash
# Revert the migration
alembic downgrade -1

# Revert to previous release
git checkout v2.1.0
alembic upgrade head
```

The `cra_conformity_checklists` table is the only schema change. All other changes are in Python/TypeScript and carry no data risk.

---

## Checklist for ops

- [ ] `alembic upgrade head` run on production DB
- [ ] API restarted — check `/docs` shows version `2.2.0`
- [ ] Frontend rebuilt and redeployed
- [ ] Open any CRA assessment — confirm **Conformity** and **Annex II** tabs are visible
- [ ] Run classification wizard on a test assessment — confirm steward option appears when open-source is selected

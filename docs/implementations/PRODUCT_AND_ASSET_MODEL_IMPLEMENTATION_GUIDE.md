# Product and Asset Model Implementation Guide

## Overview

> **Migration Requirement:**
> The current data models and APIs **must be updated** to support this product-centric structure. This is a required migration for the QuickTARA codebase. All existing and new features must align with this approach.

This document specifies the implementation requirements for a product-centric asset identification model in QuickTARA. The goal is to ensure that the system supports a workflow where:
- **Scope** represents a product (e.g., an ECU such as the DCC3 Converter)
- **Assets** are the valuable items within that product (e.g., Calibration Parameters, Firmware, Diagnostic Data)

This approach aligns with ISO/SAE 21434 and UNECE R155, supporting clear traceability from product definition through asset identification and risk assessment.

## Model Structure

---

## Traceability and Version Handling (Required)

To ensure regulatory compliance, auditability, and robust lifecycle management, all implementations must support:

### 1. Traceability
- Every asset must reference its parent product (scope) via `scope_id` (foreign key).
- All related entities (damage scenarios, threat scenarios, assessments, etc.) must reference the relevant `asset_id` and/or `scope_id`.
- Include metadata on all entities:
  - `created_at`, `updated_at`, `created_by`, `updated_by`
  - (Optional but recommended) `change_reason`, `change_source`
- Maintain a full audit trail of all changes (create, update, delete) with entity type, action, old/new values, timestamp, and user.

### 2. Version Handling
- All major entities (scope, asset, scenario) must include:
  - `version` (integer, auto-incremented)
  - `revision_notes` (text, optional)
  - `is_current` (boolean)
- On significant change, increment the version and retain the previous version (either soft copy or in a versioned/history table).
- When a product (scope) is versioned, all its assets and related entities should reference the correct `scope_version` for full historical reconstruction.
- Provide API endpoints to retrieve the full history and any specific version of any entity.

### 3. Example (Minimal Model)

```json
{
  "scope_id": "dcc3_converter",
  "version": 3,
  "is_current": true,
  "name": "DCC3 Converter",
  "created_at": "...",
  "updated_at": "...",
  "created_by": "userA",
  "updated_by": "userB",
  "revision_notes": "Updated interfaces to add LIN bus"
}
```

```json
{
  "asset_id": "dcc3_firmware",
  "scope_id": "dcc3_converter",
  "scope_version": 3,
  "version": 2,
  "is_current": true,
  "name": "DCC3 Firmware",
  "created_at": "...",
  "updated_at": "...",
  "created_by": "userA",
  "updated_by": "userC",
  "revision_notes": "Firmware updated to v2.1"
}
```

### 4. Best Practices
- Use database-level foreign keys for all parent-child relationships.
- Store both current and historical versions for compliance and rollback.
- Provide UI and API access to version history and restoration.
- Clearly display parent-child and version relationships in the UI.
- Ensure all changes are logged for audit purposes.

---

### 1. Scope (Product Level)

The `Scope` entity represents a product, such as an ECU. Product-wide properties are defined at this level.

**Example:**
```json
{
  "scope_id": "dcc3_converter",
  "name": "DCC3 Converter",
  "system_type": "product",
  "description": "DC-DC Converter ECU for hybrid vehicles",
  "boundaries": ["Powertrain domain", "12V/48V bus"],
  "objectives": ["Convert voltage", "Support hybrid operation"],
  "stakeholders": ["OEM", "Supplier", "Integrator"],
  "safety_level": "ASIL_D",
  "interfaces": ["CAN", "Ethernet"],
  "access_points": ["OBD-II", "Debug Port"],
  "location": "Engine Bay",
  "trust_zone": "Critical"
}
```

### 2. Asset (Component) Level

Each asset is a valuable element within the product. Only asset-specific fields are included at this level. Asset types may be used for filtering or reporting, but are optional.

**Example:**
```json
[
  {
    "asset_id": "calib_params",
    "scope_id": "dcc3_converter",
    "name": "Calibration Parameters",
    "description": "Tuning parameters for the converter",
    "data_types": ["Calibration Data"],
    "storage_location": "Internal Flash",
    "confidentiality": "High",
    "integrity": "High",
    "availability": "Medium",
    "authenticity_required": true,
    "authorization_required": true
  },
  {
    "asset_id": "dcc3_firmware",
    "scope_id": "dcc3_converter",
    "name": "DCC3 Firmware",
    "description": "Embedded software controlling the converter",
    "data_types": ["Binary Image", "Logs"],
    "storage_location": "Internal Flash",
    "confidentiality": "High",
    "integrity": "High",
    "availability": "High",
    "authenticity_required": true,
    "authorization_required": true
  },
  {
    "asset_id": "diagnostic_data",
    "scope_id": "dcc3_converter",
    "name": "Diagnostic Data",
    "description": "Data collected for diagnostics and troubleshooting",
    "data_types": ["DTCs", "Live Data"],
    "storage_location": "Internal RAM",
    "confidentiality": "Medium",
    "integrity": "Medium",
    "availability": "High",
    "authenticity_required": false,
    "authorization_required": true
  }
]
```

## Implementation Requirements

### Database Schema
- Add product-wide fields (e.g., `safety_level`, `interfaces`, `access_points`, `trust_zone`) to the `Scope` model.
- Define assets as entities linked to a scope (product), with asset-specific fields only.
- Remove or avoid duplicating product-wide fields at the asset level.

### API and Validation
- Ensure the API supports creating, updating, and retrieving scopes (products) with all product-wide fields.
- Ensure the API supports creating, updating, and retrieving assets linked to a scope.
- Validate that asset fields are asset-specific and do not duplicate product-level information.

### UI/UX
- In the UI, clearly distinguish between product-level (scope) and asset-level fields.
- When viewing or editing an asset, show relevant product-level fields for context, but do not allow editing them at the asset level.
- When creating a new product, prompt for all required product-level fields.
- When adding an asset, prompt only for asset-specific fields.

### Traceability and Compliance
- Maintain clear links between each asset and its parent product (scope).
- Ensure all fields required for ISO/SAE 21434 and UNECE R155 compliance are captured at the appropriate level.

## Example Workflow
1. **Create Product (Scope):** Enter all product-wide details.
2. **Add Assets:** For each asset within the product, enter asset-specific details.
3. **Proceed with TARA:** Use the product and asset model as the foundation for subsequent risk analysis, impact rating, and threat scenario modeling.

## References
- See `DAMAGE_SCENARIOS_IMPLEMENTATION_GUIDE.md` and `CIA_IMPLEMENTATION_GUIDE.md` for database and API documentation style.
- Aligns with ISO/SAE 21434 and UNECE R155 requirements for asset identification and traceability.

---

This guide must be followed for all future product and asset modeling in QuickTARA.

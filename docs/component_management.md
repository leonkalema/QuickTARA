# Component Management

Components are the individual parts of the system you are analysing. Each one represents a physical or logical element: an ECU, a sensor, a gateway, or a communication bus. You define a component once and reuse it across damage scenarios, threat scenarios, and risk assessments.

---

## Adding a Component

Click "Add Component" on the Components page. Fill in the required fields and click "Save Component".

**Required fields:**

| Field | What to enter |
|-------|---------------|
| Component ID | A unique code with no spaces (e.g. ECU-001). Alphanumeric characters, hyphens, and underscores are accepted. |
| Name | A plain-language name (e.g. Engine Control Unit) |
| Type | ECU, Sensor, Gateway, or another listed type |

**Optional but recommended fields:**

| Field | Purpose |
|-------|---------|
| Safety Level | ASIL A, B, C, D, or QM. This feeds into risk calculations. |
| Location | Internal or External. Indicates whether the component sits inside the vehicle boundary. |
| Trust Zone | Critical, Boundary, Standard, or Untrusted. This affects threat scenario generation. |
| Interfaces | Communication protocols the component uses (CAN, FlexRay, Ethernet, LIN). |
| Access Points | Physical or debug interfaces (OBD-II, JTAG, Debug Port). |
| Data Types | The nature of data the component handles (Control Commands, Sensor Data). |
| Connected Components | IDs of other components this one communicates with. |

---

## Editing and Deleting

Click a component card to open its details. Click "Edit" to change any field. Click "Delete" to remove the component.

Deleting a component removes it from all linked scenarios. Confirm before you proceed.

---

## Importing from CSV

You can create many components at once by uploading a CSV file.

**Required headers:**
```
component_id,name,type,safety_level,interfaces,access_points,data_types,location,trust_zone,connected_to
```

Separate multiple values in a single field with a pipe character (`|`):
```
ECU001,Engine Control Unit,ECU,ASIL D,CAN|FlexRay,OBD-II|Debug Port,Control Commands|Sensor Data,Internal,Critical,ECU002|ECU003
```

Click "Import", select your file, and click "Import Components". The page shows a result list with any rows that failed and the reason for each failure.

---

## Exporting to CSV

Click "Export" on the Components page. The system downloads a CSV of all components in your current product. Use this to back up your data, share it with colleagues, or prepare a bulk edit.

---

## Finding Components

Use the search box to filter by component ID or name. Use the dropdowns to filter by type, safety level, or trust zone. Filters stack, so you can narrow to Gateway components at ASIL C with a Boundary trust zone in three clicks.

---

## Component Properties Reference

| Property | Description | Example values |
|----------|-------------|----------------|
| component_id | Unique identifier | ECU001, SNS001 |
| name | Human-readable name | Engine Control Unit |
| type | Component type | ECU, Sensor, Gateway |
| safety_level | Automotive Safety Integrity Level | ASIL D, ASIL C, QM |
| interfaces | Communication protocols | CAN, FlexRay, Ethernet |
| access_points | Physical or debug interfaces | OBD-II, Debug Port |
| data_types | Nature of data handled | Control Commands, Sensor Data |
| location | Physical placement | Internal, External |
| trust_zone | Security domain | Critical, Boundary, Untrusted |
| connected_to | Connected component IDs | ECU002, SNS001 |

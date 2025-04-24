# Report Generation Service Implementation

This document outlines the implementation of the report generation service for QuickTARA.

## 1. Report Database Models ✓

### Pydantic Models (API)

The following Pydantic models have been implemented in `api/models/report.py`:

- `ReportFormat` - Enum defining supported formats (TXT, JSON, XLSX, PDF)
- `ReportStatus` - Enum tracking report generation status (PENDING, GENERATING, COMPLETED, FAILED)
- `ReportType` - Enum distinguishing between PRELIMINARY (automated) and FINAL (after review) reports
- `ReportConfiguration` - Configuration options for report generation
- `ReportCreate` - Request model for creating a new report
- `Report` - Complete report model
- `ReportSummary` - Simplified report model for listings
- `ReportList` - Paginated list of reports
- `ReportError` - Details about errors during report generation

### SQLAlchemy Models (Database)

The SQLAlchemy `Report` model has been added to `db/base.py` with the following structure:

```python
class Report(Base):
    """SQLAlchemy model for reports"""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), index=True)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    format = Column(String, nullable=False)  # Report format (txt, json, xlsx, pdf)
    report_type = Column(String, nullable=False)  # Report type (preliminary, final)
    status = Column(String, nullable=False)  # Report status (pending, generating, completed, failed)
    file_path = Column(String, nullable=True)  # Path to the generated file
    file_size = Column(Integer, nullable=True)  # Size of the generated file in bytes
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)
    
    # Configuration options (stored as JSON)
    configuration = Column(JSON)
    
    # Error information for failed reports (stored as JSON)
    error_info = Column(JSON, nullable=True)
    
    # Relationships
    analysis = relationship("Analysis", backref="reports")
```

## 2. Report Generation Service ✓

### 2.1. Service Implementation

The report generation service has been implemented in `api/services/report_service.py` and provides the following functionality:

1. **Report Creation**: Creates a new report record in the database
2. **Report Generation**: Generates reports in all supported formats (TXT, JSON, XLSX, PDF)
3. **Background Processing**: Supports asynchronous report generation in a background thread
4. **Error Handling**: Tracks and reports errors during generation
5. **Status Tracking**: Updates report status through the generation process

The implementation leverages the existing export functionality from `export_formats.py` and adds a custom text report generator.

Key features of the service:

- **Pydantic Model Conversion**: Seamless conversion between database and API models
- **Configuration Options**: Support for customizing report content
- **File Management**: Proper handling of file storage and cleanup
- **Async Generation**: Background processing to avoid blocking API responses

### 2.2. Report File Storage

The service handles report files as follows:

- **Storage Location**: Reports are stored in the configured `reports_dir` directory 
- **Naming Scheme**: Files use the pattern `{report_id}_{timestamp}.{format}`
- **File Tracking**: File paths and sizes are stored in the database
- **File Cleanup**: Files are deleted when reports are deleted

## 3. API Endpoints ✓

The report routes have been implemented in `api/routes/reports.py` and provide the following endpoints:

1. **POST /api/reports** - Create a new report and start generation
2. **GET /api/reports** - List available reports with pagination
3. **GET /api/reports/{report_id}** - Get report details
4. **GET /api/reports/{report_id}/download** - Download a generated report
5. **DELETE /api/reports/{report_id}** - Delete a report

The endpoints handle file serving, error conditions, and dependency injection for the report service.

## 4. Frontend Integration (Future Implementation)

The frontend implementation will include:

1. UI for report configuration
2. Report status tracking
3. Report download functionality
4. Report history display

## 5. Format Support

The service supports the following report formats:

1. **JSON** ✓ - Machine-readable format using the existing `export_to_json` function
2. **XLSX** ✓ - Excel format with multiple sheets using the existing `export_to_excel` function
3. **PDF** ✓ - PDF format using the existing `export_to_pdf` function
4. **TXT** ✓ - Plain text format using the new `_generate_txt_report` function

Each format presents the analysis data in a structured manner appropriate for the format.

## Testing Plan

A comprehensive testing plan should include:

1. **Unit Tests**:
   - Test report creation
   - Test format conversion
   - Test error handling

2. **Integration Tests**:
   - Test complete report generation workflow
   - Test all supported formats
   - Test with large data sets

3. **Performance Tests**:
   - Test generation time for large reports
   - Test memory usage during generation

## Progress Tracking

- ✓ Report database models
- ✓ Report generation service
  - ✓ Basic service structure
  - ✓ Database operations
  - ✓ Actual report generation
  - ✓ Background processing
  - ✓ Error handling
- ✓ API endpoints
  - ✓ Report creation
  - ✓ Report listing
  - ✓ Report downloading
  - ✓ Report deletion
- ✓ File storage implementation
- ✓ Format support:
  - ✓ JSON
  - ✓ TXT
  - ✓ XLSX
  - ✓ PDF
- ✓ Documentation
  - ✓ Database models documentation
  - ✓ Service documentation
  - ✓ API documentation
- □ Tests
  - □ Unit tests
  - □ Integration tests

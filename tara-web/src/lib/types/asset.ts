export interface Asset {
  asset_id: string;
  name: string;
  description?: string;
  asset_type: AssetType;
  data_types: string[];
  storage_location?: string;
  scope_id: string;
  scope_version?: number;
  confidentiality: SecurityLevel;
  integrity: SecurityLevel;
  availability: SecurityLevel;
  authenticity_required: boolean;
  authorization_required: boolean;
  version: number;
  is_current: boolean;
  revision_notes?: string;
  created_at: string;
  updated_at: string;
  created_by?: string;
  updated_by?: string;
}

export interface CreateAssetRequest {
  name: string;
  description?: string;
  asset_type: AssetType;
  data_types: string[];
  storage_location?: string;
  scope_id: string;
  confidentiality: SecurityLevel;
  integrity: SecurityLevel;
  availability: SecurityLevel;
  authenticity_required: boolean;
  authorization_required: boolean;
  asset_id?: string;
}

export interface AssetsResponse {
  assets: Asset[];
  total: number;
}

export enum AssetType {
  FIRMWARE = "Firmware",
  SOFTWARE = "Software", 
  CONFIGURATION = "Configuration",
  CALIBRATION = "Calibration",
  DATA = "Data",
  DIAGNOSTIC = "Diagnostic",
  COMMUNICATION = "Communication",
  HARDWARE = "Hardware",
  INTERFACE = "Interface",
  OTHER = "Other"
}

export enum SecurityLevel {
  HIGH = "High",
  MEDIUM = "Medium",
  LOW = "Low",
  NOT_APPLICABLE = "N/A"
}

export class AssetApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AssetApiError';
  }
}

export type ProductStatus = 'development' | 'testing' | 'production' | 'deprecated';

export type ProductType =
  | 'automotive'
  | 'industrial'
  | 'iot'
  | 'medical'
  | 'aerospace'
  | 'other'
  | 'ECU'
  | 'Gateway'
  | 'Sensor'
  | 'Actuator'
  | 'Network'
  | 'ExternalDevice'
  | 'Other';

export interface Product {
  scope_id: string;
  name: string;
  description?: string;
  product_type: ProductType;
  version?: string;
  status?: ProductStatus;
  owner_team?: string;
  compliance_standards?: string[];
  organization_id?: string;
  safety_level?: 'QM' | 'ASIL-A' | 'ASIL-B' | 'ASIL-C' | 'ASIL-D' | string;
  interfaces?: string[];
  access_points?: string[];
  location?: string;
  trust_zone?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateProductRequest {
  name: string;
  description?: string;
  product_type: Product['product_type'];
  version?: string;
  status?: ProductStatus;
  owner_team?: string;
  compliance_standards?: string[];
  organization_id?: string;
  safety_level?: Product['safety_level'];
  interfaces?: string[];
  access_points?: string[];
  location?: string;
  trust_zone?: string;
  boundaries?: string[];
  objectives?: string[];
  stakeholders?: string[];
}

export interface ProductPermissions {
  scope_id: string;
  organization_id: string | null;
  can_view: boolean;
  can_edit: boolean;
  can_delete: boolean;
  can_manage_assets: boolean;
  can_manage_scenarios: boolean;
  can_approve_risks: boolean;
  role: string | null;
}

export interface ProductsResponse {
  scopes: Product[];
  total: number;
}

export interface ProductStats {
  total_products: number;
  by_status: Record<ProductStatus, number>;
  by_type: Record<ProductType, number>;
}

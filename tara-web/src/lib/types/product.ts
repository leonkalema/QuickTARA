export interface Product {
  scope_id: string;
  name: string;
  description?: string;
  product_type: 'automotive' | 'industrial' | 'iot' | 'medical' | 'aerospace' | 'other';
  version: string;
  status: 'development' | 'testing' | 'production' | 'deprecated';
  owner_team?: string;
  compliance_standards?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateProductRequest {
  name: string;
  description?: string;
  product_type: Product['product_type'];
  version: string;
  status: Product['status'];
  owner_team?: string;
  compliance_standards?: string[];
}

export interface ProductsResponse {
  scopes: Product[];
  total: number;
}

export interface ProductStats {
  total_products: number;
  by_status: Record<Product['status'], number>;
  by_type: Record<Product['product_type'], number>;
}

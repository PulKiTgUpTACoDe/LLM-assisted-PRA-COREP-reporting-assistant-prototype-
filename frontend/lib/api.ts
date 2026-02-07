import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface QueryRequest {
  question: string;
  template_id: string;
  context?: Record<string, any>;
}

export interface TemplateField {
  field_code: string;
  row_code: string;
  col_code: string;
  label: string;
  value: any;
  data_type: string;
  justification?: string;
  source_rules: string[];
  confidence: 'high' | 'medium' | 'low' | 'unknown';
}

export interface ValidationIssue {
  field_code: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  suggestion?: string;
}

export interface AuditLogEntry {
  field_code: string;
  value: any;
  reasoning: string;
  source_rules: Array<{
    rule_id: string;
    rule_text: string;
    relevance_score: string;
  }>;
  confidence: 'high' | 'medium' | 'low' | 'unknown';
  retrieved_at: string;
}

export interface TemplateResponse {
  query_id: string;
  template_id: string;
  template_name: string;
  fields: TemplateField[];
  validation_issues: ValidationIssue[];
  audit_log: AuditLogEntry[];
  missing_data: string[];
  assumptions: string[];
  metadata: Record<string, any>;
}

export interface TemplateInfo {
  template_id: string;
  name: string;
  description: string;
  row_count: number;
  col_count: number;
  field_count: number;
  status: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  services: Record<string, string>;
}

// API Functions
export const queryAPI = {
  // Process a COREP query
  processQuery: async (request: QueryRequest): Promise<TemplateResponse> => {
    const response = await api.post<TemplateResponse>('/query', request);
    return response.data;
  },

  // Get query result by ID
  getQueryResult: async (queryId: string): Promise<TemplateResponse> => {
    const response = await api.get<TemplateResponse>(`/query/${queryId}`);
    return response.data;
  },
};

export const templatesAPI = {
  // List available templates
  listTemplates: async (): Promise<TemplateInfo[]> => {
    const response = await api.get<TemplateInfo[]>('/templates');
    return response.data;
  },

  // Get specific template info
  getTemplate: async (templateId: string): Promise<TemplateInfo> => {
    const response = await api.get<TemplateInfo>(`/templates/${templateId}`);
    return response.data;
  },
};

export const healthAPI = {
  // Check API health
  checkHealth: async (): Promise<HealthResponse> => {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  },
};

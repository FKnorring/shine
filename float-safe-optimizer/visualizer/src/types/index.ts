export interface DriverGenOptions {
  unoptRiseFile: string;
  optRiseFile?: string;
  dimension?: number;
  iterations?: number;
  precision?: number;
  outputFile?: string;
  floatType?: 'normal' | 'subnormal' | 'mixed' | 'magnitude';
  prefix?: string;
  includeNegatives?: boolean;
  metricsFile?: string;
}

export interface OutFile {
  path: string;
  name: string;
  size: number;
  timestamp: number; // Last modified timestamp in milliseconds
  isExecutable?: boolean;
  content?: string | null;
  isMetrics?: boolean;
  error?: string;
}

export interface MetricsData {
  // Configuration
  dimension?: number;
  float_type?: string;
  include_negatives?: boolean;
  precision?: number;
  iterations?: number;
  
  // Performance metrics
  unopt_time?: number;
  opt_time?: number;
  mpfr_time?: number;
  speedup?: number;
  
  // Accuracy metrics
  unopt_value?: number;
  opt_value?: number;
  mpfr_value?: number;
  unopt_abs_error?: number;
  opt_mean_abs_error?: number;
  unopt_rel_error?: number;
  opt_mean_rel_error?: number;
  unopt_ulps?: number;
  opt_mean_ulps?: number;
}

export interface CommandOutput {
  success?: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
} 
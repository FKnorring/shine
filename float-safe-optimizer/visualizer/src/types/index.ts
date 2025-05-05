export interface ArrayInputConfig {
  size: number;
  float_type?: 'normal' | 'subnormal' | 'mixed' | 'magnitude';
  include_negatives?: boolean;
  values?: number[];
}

export interface InputConfig {
  dimensions?: Record<string, number>;
  inputs: Array<number | ArrayInputConfig>;
  output?: {
    size: number;
  };
}

export interface DriverGenOptions {
  unoptRiseFile: string;
  optRiseFile?: string;
  dimension: number;
  iterations: number;
  precision: number;
  outputFile: string;
  floatType: string;
  prefix?: string;
  includeNegatives: boolean;
  metricsFile: string;
  skipCompilation?: boolean;
  inputConfig?: InputConfig;
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
  summary: {
    dimension: number;
    optimized_time: number;
    unoptimized_time: number;
    mpfr_time: number;
    max_abs_error: number;
    max_rel_error: number;
    avg_abs_error: number;
    avg_rel_error: number;
    speedup_vs_unopt: number;
    speedup_vs_mpfr: number;
  };
  iterations?: {
    abs_errors: number[];
    rel_errors: number[];
    opt_times: number[];
    unopt_times: number[];
    opt_results?: number[];
  };
}

export interface CommandOutput {
  success?: boolean;
  stdout?: string;
  stderr?: string;
  error?: string;
} 
export interface DriverGenOptions {
  unoptRiseFile: string;
  optRiseFile?: string;
  dimension: number;
  iterations: number;
  precision: number;
  outputFile: string;
  floatType: 'normal' | 'subnormal' | 'mixed' | 'magnitude';
  prefix?: string;
  includeNegatives: boolean;
  metricsFile: string;
  skipCompilation: boolean;
  inputConfig?: InputConfig;
}

export interface InputConfig {
  dimensions?: Record<string, number>;
  inputs: Array<InputConfigItem>;
  output?: {
    size: number;
  };
}

export type InputConfigItem = 
  | number  // For scalar inputs
  | {
      size: number;
      float_type?: 'normal' | 'subnormal' | 'mixed' | 'magnitude';
      include_negatives?: boolean;
      values?: number[];
    };

// ... existing types ... 
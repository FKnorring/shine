import { MetricsData } from '@/types';

// Extended metrics data with dynamic properties
interface ExtendedMetricsData extends MetricsData {
  opt_times?: number[];
  unopt_times?: number[];
  opt_results?: number[];
  opt_mean_time?: number;
  opt_median_time?: number;
  opt_min_time?: number;
  opt_max_time?: number;
  unopt_mean_time?: number;
  unopt_median_time?: number;
  unopt_min_time?: number;
  unopt_max_time?: number;
  opt_mean_result?: number;
  opt_median_result?: number;
  opt_min_result?: number;
  opt_max_result?: number;
  [key: string]: string | number | boolean | undefined | number[];
}

/**
 * Parse CSV content from metrics file into a structured object
 */
export function parseMetricsCSV(csvContent: string): MetricsData {
  const lines = csvContent.trim().split('\n');
  const data: Record<string, string | number | boolean> = {};
  
  // Skip header line and process each data line
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    // Only extract the metric and value parts
    const parts = line.split(',');
    const metric = parts[0];
    const valueStr = parts[1];
    
    // Skip if metric or valueStr is undefined
    if (!metric || valueStr === undefined) continue;
    
    // Convert string value to appropriate type (number or boolean)
    let value: number | boolean | string = valueStr;
    
    if (valueStr && valueStr.toLowerCase() === 'true') {
      value = true;
    } else if (valueStr && valueStr.toLowerCase() === 'false') {
      value = false;
    } else if (valueStr && !isNaN(Number(valueStr))) {
      value = Number(valueStr);
    }
    
    // Add to data object
    data[metric] = value;
  }
  
  return data as unknown as MetricsData;
}

/**
 * Parse iteration data from CSV files
 */
export function parseIterationCSV(csvContent: string): { iteration: number, value: number }[] {
  const lines = csvContent.trim().split('\n');
  const data: { iteration: number, value: number }[] = [];
  
  // Skip header line
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    const parts = line.split(',');
    
    if (parts.length < 2) continue;
    
    const iteration = parseInt(parts[0], 10);
    const valueStr = parts[1];
    
    if (isNaN(iteration) || !valueStr) continue;
    
    // Convert value to number
    const value = Number(valueStr);
    
    if (!isNaN(value)) {
      data.push({ iteration, value });
    }
  }
  
  return data;
}

/**
 * Combine iteration data with main metrics
 */
export function combineMetricsData(
  baseMetrics: MetricsData, 
  optTimings?: string, 
  unoptTimings?: string, 
  optResults?: string
): MetricsData {
  const metrics = { ...baseMetrics } as ExtendedMetricsData;
  
  // Parse iteration data if available
  const optTimingData = optTimings ? parseIterationCSV(optTimings) : [];
  const unoptTimingData = unoptTimings ? parseIterationCSV(unoptTimings) : [];
  const optResultData = optResults ? parseIterationCSV(optResults) : [];
  
  // Store iteration data arrays
  metrics.opt_times = optTimingData.map(item => item.value);
  metrics.unopt_times = unoptTimingData.map(item => item.value);
  metrics.opt_results = optResultData.map(item => item.value);
  
  // Calculate statistics if we have iteration data
  if (optTimingData.length > 0) {
    metrics.opt_mean_time = metrics.opt_times.reduce((a, b) => a + b, 0) / metrics.opt_times.length;
    metrics.opt_median_time = metrics.opt_times.sort((a, b) => a - b)[Math.floor(metrics.opt_times.length / 2)];
    metrics.opt_min_time = Math.min(...metrics.opt_times);
    metrics.opt_max_time = Math.max(...metrics.opt_times);
  }
  
  if (unoptTimingData.length > 0) {
    metrics.unopt_mean_time = metrics.unopt_times.reduce((a, b) => a + b, 0) / metrics.unopt_times.length;
    metrics.unopt_median_time = metrics.unopt_times.sort((a, b) => a - b)[Math.floor(metrics.unopt_times.length / 2)];
    metrics.unopt_min_time = Math.min(...metrics.unopt_times);
    metrics.unopt_max_time = Math.max(...metrics.unopt_times);
  }
  
  if (optResultData.length > 0) {
    metrics.opt_mean_result = metrics.opt_results.reduce((a, b) => a + b, 0) / metrics.opt_results.length;
    metrics.opt_median_result = metrics.opt_results.sort((a, b) => a - b)[Math.floor(metrics.opt_results.length / 2)];
    metrics.opt_min_result = Math.min(...metrics.opt_results);
    metrics.opt_max_result = Math.max(...metrics.opt_results);
  }
  
  return metrics;
}

/**
 * Generate the performance comparison chart data
 */
export function getPerformanceChartData(metrics: MetricsData) {
  const extendedMetrics = metrics as ExtendedMetricsData;
  
  // If we have mean times from multiple runs, use those
  if (extendedMetrics.unopt_mean_time !== undefined && extendedMetrics.opt_mean_time !== undefined) {
    return [
      { 
        name: 'Unoptimized', 
        time: extendedMetrics.unopt_mean_time
      },
      { 
        name: 'Optimized', 
        time: extendedMetrics.opt_mean_time
      },
    ];
  }
  
  // Fallback to single-run times if means aren't available
  return [
    { 
      name: 'Unoptimized', 
      time: extendedMetrics.unopt_time || 0 
    },
    { 
      name: 'Optimized', 
      time: extendedMetrics.opt_time || 0 
    },
  ];
}

/**
 * Generate the accuracy comparison chart data for ULPs
 */
export function getULPsChartData(metrics: MetricsData) {
  return [
    { name: 'Unoptimized vs MPFR', ulps: metrics.ulps_unopt_mpfr || 0 },
    { name: 'Optimized vs MPFR', ulps: metrics.ulps_opt_mpfr || 0 },
  ];
}

/**
 * Generate the relative error chart data
 */
export function getRelativeErrorChartData(metrics: MetricsData) {
  const extendedMetrics = metrics as ExtendedMetricsData;
  return [
    { 
      name: 'Unoptimized vs MPFR',
      error: extendedMetrics.unopt_rel_error || extendedMetrics.rel_diff_unopt_mpfr || 0
    },
    { 
      name: 'Optimized vs MPFR',
      error: extendedMetrics.opt_mean_rel_error || extendedMetrics.rel_diff_opt_mpfr || 0
    },
  ];
}

/**
 * Generate the absolute difference chart data
 */
export function getAbsoluteDifferenceChartData(metrics: MetricsData) {
  return [
    { 
      name: 'Unoptimized vs MPFR',
      difference: metrics.abs_diff_unopt_mpfr || 0
    },
    { 
      name: 'Optimized vs MPFR',
      difference: metrics.abs_diff_opt_mpfr || 0
    },
  ];
}

/**
 * Extract iteration timing data for visualization
 */
export function getIterationTimingData(metrics: MetricsData) {
  const extendedMetrics = metrics as ExtendedMetricsData;
  const optData = (extendedMetrics.opt_times || []).map((time, i) => ({
    iteration: i,
    time
  }));
  
  const unoptData = (extendedMetrics.unopt_times || []).map((time, i) => ({
    iteration: i,
    time
  }));
  
  return { optData, unoptData };
}

/**
 * Extract iteration result data for visualization
 */
export function getIterationResultData(metrics: MetricsData) {
  const extendedMetrics = metrics as ExtendedMetricsData;
  return (extendedMetrics.opt_results || []).map((result, i) => ({
    iteration: i,
    result
  }));
}

/**
 * Get metrics data as a table for display
 */
export function getMetricsTableData(metrics: MetricsData) {
  // Convert the metrics object to an array of rows for the table
  return Object.entries(metrics)
    // Filter out iteration-specific data to keep the table clean
    .filter(([key]) => !key.match(/^(opt|unopt)_(time|result)_\d+$/))
    .map(([key, value]) => {
    let formattedValue = value;
    
    // Format numeric values
    if (typeof value === 'number') {
      formattedValue = formatNumber(value);
    }
    
    // Get the description based on key
    const descriptions: Record<string, string> = {
      // Configuration
      dimension: 'Array dimension size',
      float_type: 'Type of floating point values',
      include_negatives: 'Whether negative values were included',
      precision: 'MPFR precision bits',
      iterations: 'Number of benchmark iterations',
      
      // Performance metrics
      unopt_time: 'Unoptimized execution time (seconds)',
      opt_time: 'Optimized execution time (seconds)',
      mpfr_time: 'MPFR execution time (seconds)',
      speedup: 'Optimization speedup ratio',
      
      // Accuracy metrics
      unopt_value: 'Unoptimized result value',
      opt_value: 'Optimized result value',
      mpfr_value: 'MPFR reference value',
      abs_diff_unopt_mpfr: 'Absolute difference: |Unopt - MPFR|',
      abs_diff_opt_mpfr: 'Absolute difference: |Opt - MPFR|',
      abs_diff_opt_unopt: 'Absolute difference: |Opt - Unopt|',
      rel_diff_unopt_mpfr: 'Relative difference: |Unopt - MPFR|/|MPFR|',
      rel_diff_opt_mpfr: 'Relative difference: |Opt - MPFR|/|MPFR|',
      ulps_unopt_mpfr: 'ULPs difference: Unopt vs MPFR',
      ulps_opt_mpfr: 'ULPs difference: Opt vs MPFR',
    };
    
    return {
      metric: key,
      value: formattedValue,
      description: descriptions[key] || 'No description available',
    };
  });
}

/**
 * Format number for display with appropriate precision
 */
export function formatNumber(num: number): string {
  if (num === 0) return '0';
  
  // Use scientific notation for very large or very small numbers
  if (Math.abs(num) < 0.0001 || Math.abs(num) > 10000) {
    return num.toExponential(4);
  }
  
  // Otherwise use fixed precision
  return num.toFixed(4);
}

/**
 * Format a number to show its full decimal representation
 * @param value The number to format
 * @returns A string representation of the number with all significant digits
 */
export function formatFullNumber(value: number): string {
  if (value === 0) return "0";
  if (!isFinite(value)) return value.toString();
  
  // Convert to string and remove trailing zeros after decimal point
  let str = value.toString();
  
  // If it's in scientific notation, convert to decimal
  if (str.includes('e')) {
    const [base, exponent] = str.split('e');
    const exp = parseInt(exponent);
    const [whole, decimal] = base.split('.');
    
    if (exp > 0) {
      // Move decimal point right
      const digits = decimal || '';
      const zeros = '0'.repeat(exp - digits.length);
      str = whole + digits + zeros;
    } else {
      // Move decimal point left
      const zeros = '0'.repeat(-exp - 1);
      str = '0.' + zeros + whole + (decimal || '');
    }
  }
  
  // Remove trailing zeros after decimal point
  if (str.includes('.')) {
    str = str.replace(/\.?0+$/, '');
  }
  
  return str;
} 
#!/usr/bin/env python3
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from typing import List, Dict, Tuple


def load_metrics(csv_path: str) -> pd.DataFrame:
    """
    Load metrics from a CSV file.
    
    Args:
        csv_path: Path to the metrics CSV file
        
    Returns:
        DataFrame containing the metrics
    """
    try:
        df = pd.read_csv(csv_path)
        # Convert to a more usable format (from long to wide)
        df = df.set_index('metric')
        
        # Convert numeric values to float
        # Need to handle the case where the value column contains mixed data types
        numeric_indices = [
            'speedup', 'unopt_time', 'opt_time', 'mpfr_time',
            'unopt_value', 'opt_value', 'mpfr_value',
            'abs_diff_unopt_mpfr', 'abs_diff_opt_mpfr', 'abs_diff_opt_unopt',
            'rel_diff_unopt_mpfr', 'rel_diff_opt_mpfr',
            'ulps_unopt_mpfr', 'ulps_opt_mpfr',
            'dimension', 'precision', 'iterations'
        ]
        
        # Convert only numeric rows to float
        for idx in numeric_indices:
            if idx in df.index:
                try:
                    df.loc[idx, 'value'] = pd.to_numeric(df.loc[idx, 'value'])
                except:
                    print(f"Could not convert {idx} to numeric")
        
        return df
    except Exception as e:
        print(f"Error loading metrics from {csv_path}: {e}")
        return None


def load_multiple_metrics(csv_paths: List[str]) -> List[Tuple[str, pd.DataFrame]]:
    """
    Load metrics from multiple CSV files.
    
    Args:
        csv_paths: List of paths to metrics CSV files
        
    Returns:
        List of (name, DataFrame) tuples
    """
    results = []
    for path in csv_paths:
        name = os.path.basename(path).replace(".csv", "")
        df = load_metrics(path)
        if df is not None:
            results.append((name, df))
    return results


def create_performance_accuracy_plot(metrics_list: List[Tuple[str, pd.DataFrame]], 
                                     output_dir: str):
    """
    Create a plot showing the tradeoff between performance and accuracy.
    
    Args:
        metrics_list: List of (name, DataFrame) tuples
        output_dir: Directory to save the plot
    """
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot speedup vs ULPs
    for name, df in metrics_list:
        try:
            # Safely convert values to float
            try:
                speedup = float(df.loc['speedup', 'value'])
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert speedup for {name}: {e}")
                continue
                
            try:
                ulps_opt = float(df.loc['ulps_opt_mpfr', 'value'])
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert ULPs for {name}: {e}")
                continue
                
            # Get other display values
            try:
                float_type = str(df.loc['float_type', 'value'])
            except:
                float_type = "unknown"
                
            try:
                dimensions = float(df.loc['dimension', 'value'])
            except:
                dimensions = 0
            
            label = f"{name} (dim={dimensions}, {float_type})"
            ax1.scatter(speedup, ulps_opt, label=label, s=80, alpha=0.7)
            ax1.annotate(name, (speedup, ulps_opt), 
                        xytext=(5, 5), textcoords='offset points')
        except Exception as e:
            print(f"Skipping {name} in speedup vs ULPs plot - error: {e}")
    
    ax1.set_xlabel('Speedup (higher is better)')
    ax1.set_ylabel('ULPs Difference (lower is better)')
    ax1.set_title('Performance vs Accuracy Tradeoff')
    ax1.grid(True, alpha=0.3)
    
    # Handle log scale if needed
    ulps_values = []
    for name, df in metrics_list:
        try:
            if 'ulps_opt_mpfr' in df.index:
                ulps_values.append(float(df.loc['ulps_opt_mpfr', 'value']))
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not convert ULPs value for {name}: {e}")
    
    if ulps_values and any(u > 1000 for u in ulps_values):
        ax1.set_yscale('log')
    
    # Plot relative error vs execution time
    for name, df in metrics_list:
        try:
            # Safely convert values to float
            try:
                opt_time = float(df.loc['opt_time', 'value'])
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert time for {name}: {e}")
                continue
                
            try:
                rel_error = float(df.loc['rel_diff_opt_mpfr', 'value'])
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not convert error for {name}: {e}")
                continue
                
            # Get other display values
            try:
                float_type = str(df.loc['float_type', 'value'])
            except:
                float_type = "unknown"
                
            try:
                dimensions = float(df.loc['dimension', 'value'])
            except:
                dimensions = 0
            
            label = f"{name} (dim={dimensions}, {float_type})"
            ax2.scatter(opt_time, rel_error, label=label, s=80, alpha=0.7)
            ax2.annotate(name, (opt_time, rel_error), 
                        xytext=(5, 5), textcoords='offset points')
        except Exception as e:
            print(f"Skipping {name} in time vs error plot - error: {e}")
    
    ax2.set_xlabel('Execution Time (seconds, lower is better)')
    ax2.set_ylabel('Relative Error (lower is better)')
    ax2.set_title('Time vs Error Tradeoff')
    ax2.grid(True, alpha=0.3)
    
    # Handle log scale if needed
    error_values = []
    for name, df in metrics_list:
        try:
            if 'rel_diff_opt_mpfr' in df.index:
                error_values.append(float(df.loc['rel_diff_opt_mpfr', 'value']))
        except (ValueError, TypeError) as e:
            print(f"Warning: Could not convert error value for {name}: {e}")
    
    if error_values and any(e > 1e-6 for e in error_values):
        ax2.set_yscale('log')
    
    plt.tight_layout()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'performance_accuracy_tradeoff.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved performance vs accuracy plot to {output_path}")
    plt.close()


def create_detailed_metrics_plot(metrics_list: List[Tuple[str, pd.DataFrame]], 
                                output_dir: str):
    """
    Create detailed metric comparisons across different runs.
    
    Args:
        metrics_list: List of (name, DataFrame) tuples
        output_dir: Directory to save the plot
    """
    # Extract the relevant metrics for comparison
    names = []
    speedups = []
    abs_errors = []
    rel_errors = []
    ulps_errors = []
    
    for name, df in metrics_list:
        try:
            names.append(name)
            
            # Extract values with safe conversion to float
            try:
                speedups.append(float(df.loc['speedup', 'value']))
            except (KeyError, ValueError, TypeError) as e:
                print(f"Warning: Could not get speedup for {name}: {e}")
                speedups.append(0.0)  # Default value
                
            try:
                abs_errors.append(float(df.loc['abs_diff_opt_mpfr', 'value']))
            except (KeyError, ValueError, TypeError) as e:
                print(f"Warning: Could not get absolute error for {name}: {e}")
                abs_errors.append(0.0)  # Default value
                
            try:
                if 'rel_diff_opt_mpfr' in df.index:
                    rel_errors.append(float(df.loc['rel_diff_opt_mpfr', 'value']))
                else:
                    rel_errors.append(0.0)
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not get relative error for {name}: {e}")
                rel_errors.append(0.0)
                
            try:
                if 'ulps_opt_mpfr' in df.index:
                    ulps_errors.append(float(df.loc['ulps_opt_mpfr', 'value']))
                else:
                    ulps_errors.append(0.0)
            except (ValueError, TypeError) as e:
                print(f"Warning: Could not get ULPs error for {name}: {e}")
                ulps_errors.append(0.0)
                
        except Exception as e:
            print(f"Skipping {name} in detailed metrics plot - error: {e}")
    
    if not names:
        print("No valid data for detailed metrics plot")
        return
    
    # Create the plot with multiple subplots
    fig, axes = plt.subplots(4, 1, figsize=(10, 15))
    
    # Normalize values for easier comparison
    max_speedup = max(speedups) if speedups else 1
    norm_speedups = [s/max_speedup for s in speedups]
    
    # Plot normalized metrics
    axes[0].barh(names, norm_speedups, color='green', alpha=0.7)
    axes[0].set_title('Normalized Speedup (higher is better)')
    axes[0].set_xlim(0, 1.2)
    
    # For errors, log scale is often better
    if abs_errors:
        log_abs_errors = [np.log10(e) if e > 0 else -20 for e in abs_errors]
        axes[1].barh(names, log_abs_errors, color='red', alpha=0.7)
        axes[1].set_title('Log10 Absolute Error (lower is better)')
    
    if rel_errors:
        log_rel_errors = [np.log10(e) if e > 0 else -20 for e in rel_errors]
        axes[2].barh(names, log_rel_errors, color='orange', alpha=0.7)
        axes[2].set_title('Log10 Relative Error (lower is better)')
    
    if ulps_errors:
        log_ulps = [np.log10(e) if e > 0 else 0 for e in ulps_errors]
        axes[3].barh(names, log_ulps, color='purple', alpha=0.7)
        axes[3].set_title('Log10 ULPs Error (lower is better)')
    
    # Add the actual values as text
    for i, s in enumerate(speedups):
        axes[0].text(norm_speedups[i] + 0.05, i, f"{s:.2f}x", va='center')
    
    for i, e in enumerate(abs_errors):
        axes[1].text(log_abs_errors[i] + 0.5, i, f"{e:.2e}", va='center')
    
    for i, e in enumerate(rel_errors):
        axes[2].text(log_rel_errors[i] + 0.5, i, f"{e:.2e}", va='center')
    
    for i, e in enumerate(ulps_errors):
        axes[3].text(log_ulps[i] + 0.5, i, f"{e:.2f}", va='center')
    
    plt.tight_layout()
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'detailed_metrics_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved detailed metrics comparison to {output_path}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Visualize performance and accuracy metrics')
    parser.add_argument('--metrics_files', nargs='+', help='Paths to metrics CSV files')
    parser.add_argument('--metrics_dir', help='Directory containing metrics CSV files')
    parser.add_argument('--output_dir', default='plots', help='Directory to save plots')
    
    args = parser.parse_args()
    
    # Get list of metrics files
    metrics_files = []
    if args.metrics_files:
        metrics_files.extend(args.metrics_files)
    if args.metrics_dir:
        metrics_files.extend(glob.glob(os.path.join(args.metrics_dir, '*.csv')))
    
    if not metrics_files:
        print("Error: No metrics files specified. Use --metrics_files or --metrics_dir")
        return
    
    print(f"Loading metrics from {len(metrics_files)} files...")
    metrics_list = load_multiple_metrics(metrics_files)
    
    if not metrics_list:
        print("Error: No valid metrics data found")
        return
    
    print(f"Creating performance vs accuracy tradeoff plot...")
    create_performance_accuracy_plot(metrics_list, args.output_dir)
    
    print(f"Creating detailed metrics comparison plot...")
    create_detailed_metrics_plot(metrics_list, args.output_dir)
    
    print("Visualization complete!")


if __name__ == "__main__":
    main() 
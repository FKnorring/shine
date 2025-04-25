# Metrics and Visualization for Performance-Accuracy Tradeoffs

This extension adds metrics collection and visualization capabilities to the float-safe-optimizer driver generator. The goal is to enable easier analysis of the tradeoffs between computational performance and numerical accuracy.

## Features

- Automatic output of metrics to CSV files during benchmarking
- Visualization tools for comparing performance vs. accuracy tradeoffs
- Support for comparing multiple optimization approaches

## Usage

### Generating Metrics

Use the `--metrics_file` parameter when running the driver generator to specify where to save the metrics:

```bash
python driver_gen.py path/to/your/unopt.rise -o path/to/your/opt.rise --metrics_file my_metrics.csv
```

Additional options:

- `--float_type`: Choose from `normal`, `subnormal`, `mixed`, or `magnitude` to test with different floating-point distributions
- `--include_negatives`: Include negative values in the test data
- `--dimension`: Set the array dimension size
- `--iterations`: Set the number of benchmark iterations
- `--prefix`: Add a prefix to all generated files

### Visualizing Metrics

Once you've generated metrics files for different optimization approaches, use the visualization script to generate plots:

```bash
# Visualize a single metrics file
python visualize_metrics.py --metrics_files out/my_metrics.csv --output_dir plots

# Visualize multiple metrics files for comparison
python visualize_metrics.py --metrics_files out/method1_metrics.csv out/method2_metrics.csv --output_dir plots

# Visualize all metrics files in a directory
python visualize_metrics.py --metrics_dir out --output_dir plots
```

## Output Visualizations

The script generates two main types of visualizations:

1. **Performance vs. Accuracy Tradeoff**: This plot shows:
   - Speedup vs. ULPs Difference: Shows how much accuracy is traded for performance
   - Execution Time vs. Relative Error: Another view of the same tradeoff

2. **Detailed Metrics Comparison**: This plot compares multiple metrics across different methods:
   - Normalized Speedup (higher is better)
   - Log10 Absolute Error (lower is better)
   - Log10 Relative Error (lower is better)
   - Log10 ULPs Error (lower is better)

## Understanding the Metrics

- **Speedup**: How much faster the optimized version is compared to the unoptimized version
- **Absolute Error**: The absolute difference between the optimized result and the MPFR reference
- **Relative Error**: The absolute error divided by the MPFR reference value
- **ULPs Difference**: Units in the Last Place - a measure of how many representable floating-point values separate the result from the reference

## Requirements

The visualization script requires the following Python packages:
- pandas
- matplotlib
- numpy

You can install them with:

```bash
pip install pandas matplotlib numpy
```

## Metrics CSV Format

The generated metrics CSV file uses a simple format:

```
metric,value,description
dimension,256,Array dimension size
float_type,normal,Type of floating point values
...
```

Each row contains:
- `metric`: The name of the metric being measured
- `value`: The value of the metric (numeric or string)
- `description`: A short description of what the metric represents

The CSV format was chosen for its simplicity, making it easy to parse with any data analysis tool or language.

When comparing multiple optimization approaches, it's helpful to use descriptive file names for your metrics files, as the file names (without the .csv extension) will be used as labels in the visualization. 
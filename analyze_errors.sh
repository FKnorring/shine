#!/bin/bash

echo "===== Floating-Point Error Analysis ====="
echo "Generating basic error analysis plots..."
python3 plot_errors.py

echo -e "\nGenerating detailed error pattern analysis..."
python3 plot_error_patterns.py

echo -e "\nGenerating subnormal precision focus analysis..."
python3 plot_subnormal_focus.py

echo -e "\nAnalysis complete! Generated visualization files:"
echo "- floating_point_error_analysis.png: Basic error comparison across float types"
echo "- error_pattern_analysis.png: Detailed patterns and distributions of errors"
echo "- subnormal_precision_analysis.png: Focus on extraordinary precision of subnormal numbers"

echo -e "\nReview the terminal output for detailed error analysis." 
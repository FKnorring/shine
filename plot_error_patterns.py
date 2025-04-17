import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
from matplotlib.colors import LogNorm

# Data for sum.rise and mm.rise errors
data = {
    'float_types': ['Normal', 'Subnormal', 'Mixed', 'Magnitude'],
    'sum_max_error': [5.653221e-05, 1.401298e-45, 8.741859e-06, 3.158347e+14],
    'mm_max_error': [6.904916e-05, 1.114469e-74, 1.024350e-05, float('inf')],
    'mm_avg_error': [1.120108e-05, 8.905662e-75, 1.468516e-06, float('inf')]
}

# Create a figure for error pattern visualization
plt.figure(figsize=(20, 15))

# Helper function for log-scale formatting
def format_sci(x, pos):
    if x == 0 or np.isnan(x) or np.isinf(x):
        return '0'
    else:
        return f'$10^{{{int(np.log10(x))}}}$'

# 1. Error Magnitude Visualization (heatmap)
plt.subplot(2, 2, 1)

# Create a matrix for the heatmap (replace inf with a large value)
error_matrix = np.zeros((3, 4))  # 3 error types, 4 float types
for i, err in enumerate(data['sum_max_error']):
    error_matrix[0, i] = np.log10(err) if err > 0 and not np.isinf(err) else (15 if err > 1 else -80)
    
for i, err in enumerate(data['mm_max_error']):
    error_matrix[1, i] = np.log10(err) if err > 0 and not np.isinf(err) else (15 if err > 1 else -80)
    
for i, err in enumerate(data['mm_avg_error']):
    error_matrix[2, i] = np.log10(err) if err > 0 and not np.isinf(err) else (15 if err > 1 else -80)

# Create heatmap with custom colormap
cmap = plt.cm.RdYlGn_r  # Red for large errors, green for small errors
plt.imshow(error_matrix, cmap=cmap, aspect='auto')

# Add text annotations with actual values
for i in range(3):
    for j in range(4):
        if i == 0:  # Sum max error
            val = data['sum_max_error'][j]
        elif i == 1:  # MM max error
            val = data['mm_max_error'][j]
        else:  # MM avg error
            val = data['mm_avg_error'][j]
            
        if np.isinf(val):
            text = "∞"
        elif val > 1e10:
            text = f"10^{int(np.log10(val))}"
        elif val < 1e-40 and val > 0:
            text = f"10^{int(np.log10(val))}"
        else:
            text = f"{val:.2e}"
            
        plt.text(j, i, text, ha='center', va='center', color='white', fontweight='bold')

plt.colorbar(label='Error Magnitude (log10)')
plt.title('Error Magnitude Heatmap (Log Scale)', fontsize=14)
plt.yticks([0, 1, 2], ['Sum Max', 'MM Max', 'MM Avg'])
plt.xticks(range(4), data['float_types'])

# 2. Error Distribution Across Float Types (violin plot-inspired)
plt.subplot(2, 2, 2)

# Replace infinity with a large value for visualization
clean_data = []
for err_list in [data['sum_max_error'], data['mm_max_error'], data['mm_avg_error']]:
    temp = []
    for e in err_list:
        if np.isinf(e):
            temp.append(1e15)
        elif e < 1e-40 and e > 0:
            temp.append(1e-40)
        else:
            temp.append(e)
    clean_data.append(temp)

# We'll create a scatter plot with horizontal "violins" to show the distribution
x_positions = [1, 2, 3]  # Sum, MM Max, MM Avg
y_jitter = 0.2  # Add some vertical jitter for better visibility

for i, err_list in enumerate(clean_data):
    for j, err in enumerate(err_list):
        plt.scatter(np.log10(err), x_positions[i] + np.random.uniform(-y_jitter, y_jitter), 
                   s=100, alpha=0.7, c=plt.cm.tab10(j))
        
        # Add float type label
        plt.text(np.log10(err), x_positions[i] + np.random.uniform(-y_jitter, y_jitter), 
                data['float_types'][j], fontsize=9)

plt.title('Error Distribution by Operation and Float Type', fontsize=14)
plt.xlabel('Error Magnitude (log10 scale)', fontsize=12)
plt.yticks(x_positions, ['Sum Max Error', 'MM Max Error', 'MM Avg Error'])
plt.grid(True, alpha=0.3)

# Add a legend for float types
for i, ftype in enumerate(data['float_types']):
    plt.scatter([], [], c=plt.cm.tab10(i), s=100, label=ftype)
plt.legend(loc='upper right')

# 3. Accuracy Gain from Subnormal vs Normal (bar chart)
plt.subplot(2, 2, 3)

# Calculate accuracy improvement factors (normal / subnormal)
sum_improvement = data['sum_max_error'][0] / data['sum_max_error'][1] if data['sum_max_error'][1] > 0 else float('inf')
mm_max_improvement = data['mm_max_error'][0] / data['mm_max_error'][1] if data['mm_max_error'][1] > 0 else float('inf')
mm_avg_improvement = data['mm_avg_error'][0] / data['mm_avg_error'][1] if data['mm_avg_error'][1] > 0 else float('inf')

improvement_factors = [sum_improvement, mm_max_improvement, mm_avg_improvement]
labels = ['Sum Max Error', 'MM Max Error', 'MM Avg Error']

# Handle infinity for visualization
for i, factor in enumerate(improvement_factors):
    if np.isinf(factor):
        improvement_factors[i] = 1e16  # Cap at a very large value

# Plot on log scale
bars = plt.bar(labels, improvement_factors, color='purple')
plt.yscale('log')
plt.title('Accuracy Improvement: Normal → Subnormal', fontsize=14)
plt.ylabel('Improvement Factor (Normal/Subnormal)', fontsize=12)
plt.grid(True, alpha=0.3, which='both')

# Add text labels
for i, bar in enumerate(bars):
    factor = improvement_factors[i]
    if factor > 1e15:
        label = "EXTREMELY LARGE"
    else:
        magnitude = int(np.log10(factor))
        label = f"10^{magnitude}"
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.1, 
             label, ha='center', va='bottom', fontsize=10)

# 4. Error Range Comparison Across Float Types
plt.subplot(2, 2, 4)

# Create data for error ranges
float_types = data['float_types']
error_ranges = []

for i, ftype in enumerate(float_types):
    # Calculate min and max errors for each float type (excluding infinity)
    errors = [data['sum_max_error'][i], data['mm_max_error'][i], data['mm_avg_error'][i]]
    valid_errors = [e for e in errors if e > 0 and not np.isinf(e)]
    
    if valid_errors:
        min_err = min(valid_errors)
        max_err = max(valid_errors)
        error_ranges.append((min_err, max_err))
    else:
        error_ranges.append((np.nan, np.nan))

# Plot error ranges as horizontal lines with endpoints
for i, ((min_err, max_err), ftype) in enumerate(zip(error_ranges, float_types)):
    if not np.isnan(min_err) and not np.isnan(max_err):
        plt.plot([np.log10(min_err), np.log10(max_err)], [i, i], 'o-', linewidth=2, 
                markersize=8, label=ftype)
        
        # Add annotations
        plt.text(np.log10(min_err), i+0.1, f"{min_err:.2e}", fontsize=9)
        plt.text(np.log10(max_err), i-0.1, f"{max_err:.2e}", fontsize=9)

plt.title('Error Range by Float Type', fontsize=14)
plt.xlabel('Error Magnitude (log10 scale)', fontsize=12)
plt.yticks(range(len(float_types)), float_types)
plt.grid(True, alpha=0.3)

# Special annotation for Magnitude type with infinity
if np.isinf(data['mm_max_error'][3]):
    plt.text(5, 3, "Max Error: ∞", fontsize=12, color='red')

plt.tight_layout()
plt.savefig('error_pattern_analysis.png', dpi=300)
plt.show()

# Detailed error analysis output
print("=== Floating-Point Error Pattern Analysis ===")

print("\nError Magnitude Summary (orders of magnitude):")
for i, ftype in enumerate(data['float_types']):
    sum_err = data['sum_max_error'][i]
    mm_max = data['mm_max_error'][i]
    mm_avg = data['mm_avg_error'][i]
    
    sum_mag = f"10^{int(np.log10(sum_err))}" if sum_err > 0 and not np.isinf(sum_err) else "∞"
    mm_max_mag = f"10^{int(np.log10(mm_max))}" if mm_max > 0 and not np.isinf(mm_max) else "∞"
    mm_avg_mag = f"10^{int(np.log10(mm_avg))}" if mm_avg > 0 and not np.isinf(mm_avg) else "∞"
    
    print(f"  {ftype}:")
    print(f"    Sum Max Error: {sum_mag}")
    print(f"    MM Max Error: {mm_max_mag}")
    print(f"    MM Avg Error: {mm_avg_mag}")

print("\nAccuracy Improvement Using Subnormal Numbers:")
print(f"  Sum Operation: {sum_improvement:.2e}x better than Normal")
print(f"  MM Max Error: {mm_max_improvement:.2e}x better than Normal")
print(f"  MM Avg Error: {mm_avg_improvement:.2e}x better than Normal")

print("\nKey Patterns in Floating-Point Errors:")
print("1. Subnormal numbers consistently provide dramatically better accuracy (~10^40 improvement)")
print("2. Mixed-type calculations produce errors between Normal and Subnormal in magnitude")
print("3. Magnitude-type calculations cause catastrophic errors, particularly in MM operations")
print("4. Matrix multiplication with subnormal numbers provides the best overall numerical stability")
print("5. The error range varies by many orders of magnitude across different float types") 
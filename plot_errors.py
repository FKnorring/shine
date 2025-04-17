import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker

# Data for sum.rise and mm.rise errors
data = {
    'float_types': ['Normal', 'Subnormal', 'Mixed', 'Magnitude'],
    'sum_max_error': [5.653221e-05, 1.401298e-45, 8.741859e-06, 3.158347e+14],
    'mm_max_error': [6.904916e-05, 1.114469e-74, 1.024350e-05, float('inf')],
    'mm_avg_error': [1.120108e-05, 8.905662e-75, 1.468516e-06, float('inf')]
}

# Create a figure with multiple subplots focused on error analysis
plt.figure(figsize=(18, 12))

# Helper function for log-scale formatting
def format_sci(x, pos):
    if x == 0 or np.isnan(x) or np.isinf(x):
        return '0'
    else:
        return f'$10^{{{int(np.log10(x))}}}$'

# 1. Max Error Comparison (log scale)
plt.subplot(2, 2, 1)
x = np.arange(len(data['float_types']))
width = 0.35

# Handle extreme values for plotting
sum_errors = []
mm_errors = []

for s_err, m_err in zip(data['sum_max_error'], data['mm_max_error']):
    # Process sum error
    if s_err > 1e10:
        sum_errors.append(1e10)
    elif s_err < 1e-40 and s_err > 0:
        sum_errors.append(1e-40)
    else:
        sum_errors.append(s_err)
    
    # Process mm error
    if m_err == float('inf') or m_err > 1e10:
        mm_errors.append(1e10)
    elif m_err < 1e-40 and m_err > 0:
        mm_errors.append(1e-40)
    else:
        mm_errors.append(m_err)

# Create a bar chart with custom error labels
bars1 = plt.bar(x - width/2, sum_errors, width, color='blue', alpha=0.7, label='Sum Max Error')
bars2 = plt.bar(x + width/2, mm_errors, width, color='green', alpha=0.7, label='MM Max Error')

# Add labels with actual error values
for i, bar in enumerate(bars1):
    err_val = data['sum_max_error'][i]
    if err_val > 1e10:
        label = "VERY LARGE"
    elif err_val < 1e-40:
        label = f"{err_val:.2e}"
    else:
        label = f"{err_val:.2e}"
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.05, 
             label, ha='center', va='bottom', fontsize=9, rotation=45)

for i, bar in enumerate(bars2):
    err_val = data['mm_max_error'][i]
    if err_val == float('inf'):
        label = "∞"
    elif err_val < 1e-40:
        label = f"{err_val:.2e}"
    else:
        label = f"{err_val:.2e}"
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.05,
             label, ha='center', va='bottom', fontsize=9, rotation=45)

plt.yscale('log')
plt.title('Maximum Error Comparison (Log Scale)', fontsize=14)
plt.ylabel('Max Error (log scale)', fontsize=12)
plt.xlabel('Float Type', fontsize=12)
plt.xticks(x, data['float_types'], fontsize=11)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, which='both')
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(format_sci))

# 2. Error Range Analysis for Non-Magnitude Types
plt.subplot(2, 2, 2)

# Filter out magnitude type due to its extreme values
filtered_types = data['float_types'][:3]  # Normal, Subnormal, Mixed
sum_errors = data['sum_max_error'][:3]
mm_max_errors = data['mm_max_error'][:3]
mm_avg_errors = data['mm_avg_error'][:3]

x = np.arange(len(filtered_types))
width = 0.25

# Create a grouped bar chart
plt.bar(x - width, sum_errors, width, color='blue', label='Sum Max Error')
plt.bar(x, mm_max_errors, width, color='green', label='MM Max Error')
plt.bar(x + width, mm_avg_errors, width, color='lightgreen', label='MM Avg Error')

# Add value labels
for i, val in enumerate(sum_errors):
    plt.text(i - width, val*1.1, f"{val:.2e}", ha='center', fontsize=8, rotation=90)
for i, val in enumerate(mm_max_errors):
    plt.text(i, val*1.1, f"{val:.2e}", ha='center', fontsize=8, rotation=90)
for i, val in enumerate(mm_avg_errors):
    plt.text(i + width, val*1.1, f"{val:.2e}", ha='center', fontsize=8, rotation=90)

plt.yscale('log')
plt.title('Error Analysis (Excluding Magnitude Type)', fontsize=14)
plt.ylabel('Error (log scale)', fontsize=12)
plt.xlabel('Float Type', fontsize=12)
plt.xticks(x, filtered_types, fontsize=11)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3, which='both')
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(format_sci))

# 3. Subnormal Analysis - Extremely small errors
plt.subplot(2, 2, 3)

# Create a special plot for subnormal type which shows exceptionally small errors
labels = ['Sum Max Error', 'MM Max Error', 'MM Avg Error']
subnormal_errors = [data['sum_max_error'][1], data['mm_max_error'][1], data['mm_avg_error'][1]]
error_magnitudes = [abs(np.log10(err)) for err in subnormal_errors]  # Convert to order of magnitude

# Plot magnitudes on a linear scale for easier interpretation
plt.bar(labels, error_magnitudes, color=['blue', 'green', 'lightgreen'])
plt.title('Subnormal Numbers Error Magnitude', fontsize=14)
plt.ylabel('Order of Magnitude (higher = smaller error)', fontsize=12)
plt.grid(True, alpha=0.3)

# Add exact values as annotations
for i, (mag, val) in enumerate(zip(error_magnitudes, subnormal_errors)):
    plt.text(i, mag/2, f"Actual: {val:.2e}", ha='center', fontsize=10)
    plt.text(i, mag+1, f"{mag:.0f} orders", ha='center', fontsize=10)

# 4. Error Ratio Analysis (MM/Sum)
plt.subplot(2, 2, 4)

# Calculate error ratios (excluding infinity and problematic values)
ratios = []
labels = []
for i, (s_err, m_err) in enumerate(zip(data['sum_max_error'], data['mm_max_error'])):
    if s_err > 0 and m_err != float('inf') and m_err > 0:
        ratios.append(m_err / s_err)
        labels.append(data['float_types'][i])
    
if len(ratios) > 0:  # Only create this plot if we have valid ratios
    plt.bar(labels, ratios, color='purple')
    plt.title('Error Ratio (MM/Sum)', fontsize=14)
    plt.ylabel('MM Error / Sum Error', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    for i, val in enumerate(ratios):
        if val < 0.01:
            plt.text(i, 0.1, f"{val:.2e}", ha='center', fontsize=10, rotation=90)
        else:
            plt.text(i, val*1.1, f"{val:.2f}", ha='center', fontsize=10)
    
    plt.yscale('log')
else:
    # Create an alternative plot if no valid ratios
    plt.text(0.5, 0.5, "No valid error ratios\n(due to infinity or zero values)", 
             ha='center', va='center', fontsize=14)
    plt.axis('off')

plt.tight_layout()
plt.savefig('floating_point_error_analysis.png', dpi=300)
plt.show()

# Print detailed error analysis
print("=== Floating-Point Error Analysis ===")

print("\nSum Operation Errors:")
for i, ftype in enumerate(data['float_types']):
    err = data['sum_max_error'][i]
    if err > 1e10:
        err_str = "EXTREMELY LARGE"
    elif err < 1e-40:
        err_str = f"{err:.2e} (exceptional accuracy)"
    else:
        err_str = f"{err:.2e}"
    print(f"  {ftype}: Max Error = {err_str}")

print("\nMatrix Multiplication Errors:")
for i, ftype in enumerate(data['float_types']):
    max_err = data['mm_max_error'][i]
    avg_err = data['mm_avg_error'][i]
    
    # Format max error
    if max_err == float('inf'):
        max_err_str = "INFINITY"
    elif max_err < 1e-40:
        max_err_str = f"{max_err:.2e} (exceptional accuracy)"
    else:
        max_err_str = f"{max_err:.2e}"
        
    # Format avg error
    if avg_err == float('inf'):
        avg_err_str = "INFINITY"
    elif avg_err < 1e-40:
        avg_err_str = f"{avg_err:.2e} (exceptional accuracy)"
    else:
        avg_err_str = f"{avg_err:.2e}"
        
    print(f"  {ftype}: Max Error = {max_err_str}, Avg Error = {avg_err_str}")

print("\nKey Observations on Floating-Point Errors:")
print("1. Subnormal numbers provide exceptional accuracy for both operations:")
print(f"   - Sum max error: {data['sum_max_error'][1]:.2e} (10^-45 magnitude)")
print(f"   - MM max error: {data['mm_max_error'][1]:.2e} (10^-74 magnitude)")
print("2. Magnitude float type produces catastrophic errors:")
print(f"   - Sum max error: {data['sum_max_error'][3]:.2e} (10^14 magnitude)")
print("   - MM max error: INFINITY (complete loss of numerical stability)")
print("3. Normal and Mixed float types provide moderate accuracy:")
print(f"   - Normal: ~10^-5 error range")
print(f"   - Mixed: ~10^-6 error range")
print("4. Matrix multiplication with subnormal numbers achieves the highest accuracy overall") 
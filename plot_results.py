import matplotlib.pyplot as plt
import numpy as np

# Data for sum.rise
sum_data = {
    'float_types': ['Normal', 'Subnormal', 'Mixed', 'Magnitude'],
    'standard_time': [0.000002, 0.000001, 0.000001, 0.000001],
    'mpfr_time': [0.000021, 0.000028, 0.000021, 0.000022],
    'max_error': [5.653221e-05, 1.401298e-45, 8.741859e-06, 3.158347e+14],
    'slowdown': [9.02, 19.63, 20.92, 21.51]
}

# Data for mm.rise
mm_data = {
    'float_types': ['Normal', 'Subnormal', 'Mixed', 'Magnitude'],
    'standard_time': [0.054332, 0.060825, 0.061029, 0.072665],
    'mpfr_time': [2.886673, 3.011549, 3.112069, 3.653813],
    'max_error': [6.904916e-05, 1.114469e-74, 1.024350e-05, float('inf')],
    'avg_error': [1.120108e-05, 8.905662e-75, 1.468516e-06, float('inf')],
    'slowdown': [53.13, 49.51, 50.99, 50.28]
}

# Set up the figure with a 2x2 grid of subplots
plt.figure(figsize=(15, 12))

# 1. Execution Time Comparison
plt.subplot(2, 2, 1)
x = np.arange(len(sum_data['float_types']))
width = 0.35

plt.bar(x - width/2, sum_data['standard_time'], width, label='Sum Standard')
plt.bar(x + width/2, mm_data['standard_time'], width, label='MM Standard')

plt.title('Standard Execution Time Comparison')
plt.ylabel('Time (seconds per iteration)')
plt.xlabel('Float Type')
plt.xticks(x, sum_data['float_types'])
plt.legend()
plt.grid(True, alpha=0.3)

# 2. MPFR Execution Time Comparison
plt.subplot(2, 2, 2)
plt.bar(x - width/2, sum_data['mpfr_time'], width, label='Sum MPFR')
plt.bar(x + width/2, mm_data['mpfr_time'], width, label='MM MPFR')

plt.title('MPFR Execution Time Comparison')
plt.ylabel('Time (seconds per iteration)')
plt.xlabel('Float Type')
plt.xticks(x, sum_data['float_types'])
plt.legend()
plt.grid(True, alpha=0.3)

# 3. Maximum Error (log scale)
plt.subplot(2, 2, 3)
# Handle infinite values for logarithmic scale
sum_errors = np.array(sum_data['max_error'])
mm_errors = np.array([e if e != float('inf') else np.nan for e in mm_data['max_error']])

# Plot on a log scale
plt.semilogy(x, sum_errors, 'bo-', label='Sum Max Error')
plt.semilogy(x, mm_errors, 'ro-', label='MM Max Error')

plt.title('Maximum Absolute Error (Log Scale)')
plt.ylabel('Error')
plt.xlabel('Float Type')
plt.xticks(x, sum_data['float_types'])
plt.legend()
plt.grid(True, alpha=0.3)

# 4. MPFR Slowdown Factor
plt.subplot(2, 2, 4)
plt.bar(x - width/2, sum_data['slowdown'], width, label='Sum Slowdown')
plt.bar(x + width/2, mm_data['slowdown'], width, label='MM Slowdown')

plt.title('MPFR Slowdown Factor')
plt.ylabel('Slowdown (x times)')
plt.xlabel('Float Type')
plt.xticks(x, sum_data['float_types'])
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('float_comparison_results.png')
plt.show()

# Summary statistics
print("Summary of Results:")
print("\nSum.rise Performance:")
print(f"  Average Standard Execution Time: {np.mean(sum_data['standard_time']):.8f} seconds")
print(f"  Average MPFR Execution Time: {np.mean(sum_data['mpfr_time']):.8f} seconds")
print(f"  Average Slowdown Factor: {np.mean(sum_data['slowdown']):.2f}x")

print("\nMM.rise Performance:")
print(f"  Average Standard Execution Time: {np.mean(mm_data['standard_time']):.8f} seconds")
print(f"  Average MPFR Execution Time: {np.mean(mm_data['mpfr_time']):.8f} seconds")
print(f"  Average Slowdown Factor: {np.mean(mm_data['slowdown']):.2f}x")

print("\nKey Observations:")
print("1. Matrix multiplication (MM) is significantly slower than the sum operation")
print("2. MPFR slowdown is more pronounced for MM (~50x) compared to sum (~18x)")
print("3. The 'Magnitude' float type produces extremely large errors for both operations")
print("4. 'Subnormal' numbers show very small errors but with increased performance cost") 
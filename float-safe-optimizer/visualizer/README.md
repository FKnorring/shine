# Float-Safe Optimizer Visualizer

A Next.js application for visualizing, analyzing, and comparing the performance and accuracy of optimized floating-point code using the float-safe-optimizer.

## Features

- Interactive form to run the driver generator with all available options
- View the output of driver generation and compilation
- See the files generated in the out directory
- Run the compiled driver executables
- Visualize performance and accuracy metrics using charts
- Compare unoptimized, optimized, and MPFR reference implementations
- Clear the out directory with a single click

## Getting Started

### Prerequisites

- Node.js 18 or later
- npm
- MPFR library installed on your system
- Python 3
- Access to the float-safe-optimizer codebase

### Installation

1. Navigate to the float-safe-optimizer directory
2. Run the visualizer:

```bash
cd visualizer
npm install
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

1. **Select a RISE File**: Choose an unoptimized RISE source file from the dropdown (and optionally an optimized version)
2. **Configure Options**: Set dimension size, iterations, precision, etc.
3. **Generate Driver**: Click "Generate & Compile Driver" to create and compile the driver
4. **View Output**: See the output of the driver generation process
5. **Run Driver**: Click "Run" next to the executable in the output files section
6. **Analyze Results**: View the performance and accuracy charts generated from metrics.csv
7. **Clear Output**: Click "Clear Out Directory" to reset and start over

## Understanding the Visualizations

### Performance Comparison
- Shows execution time for unoptimized, optimized, and MPFR implementations
- Displays the speedup ratio between implementations

### Accuracy Comparison
- ULPs (Units in the Last Place) difference between implementations
- Relative error between implementations and MPFR reference
- Actual result values to compare precision

## Options Explained

- **Dimension**: Size for arrays in the test (higher values stress-test the implementation)
- **Iterations**: Number of benchmark runs (higher values give more stable performance metrics)
- **MPFR Precision**: Precision in bits for the MPFR reference implementation
- **Float Type**: Type of floating-point values to generate:
  - Normal: Normal distribution floating-point values
  - Subnormal: Very small values to test denormalized behavior
  - Mixed: A mix of normal and subnormal values
  - Magnitude: High and low magnitude values to test range handling
- **Include Negatives**: Whether to include negative numbers in the test data

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

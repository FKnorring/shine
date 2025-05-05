# Input Configuration for Float-Safe-Optimizer

This document explains how to use the input configuration feature to customize the inputs to your RISE program benchmarks.

## Basic Usage

You can provide an input configuration either as a JSON file or as a JSON string directly on the command line:

```bash
# Using a JSON file
python driver_generator/driver_gen.py path/to/unopt.rise --input_config input_config_example.json

# Using a JSON string
python driver_generator/driver_gen.py path/to/unopt.rise --input_config '{"dimensions":{"N":128},"inputs":[42.0]}'
```

## Configuration Format

The input configuration is a JSON object with the following structure:

```json
{
  "dimensions": {
    "dimension_name1": size1,
    "dimension_name2": size2,
    ...
  },
  "inputs": [
    input1_config,
    input2_config,
    ...
  ],
  "output": {
    "size": output_size
  }
}
```

### Dimensions

The `dimensions` field allows you to customize the sizes of the dimensions in your RISE program. If a dimension is not specified, the default value from the `--dimension` command-line option will be used.

Example:
```json
"dimensions": {
  "N": 128,
  "M": 64
}
```

### Inputs

The `inputs` field is an array that specifies the configurations for each input parameter to your RISE function. The order of the inputs must match the order of input parameters in your RISE function.

Inputs can be specified in several ways:

#### Scalar Inputs

For scalar inputs (single values), you can simply provide the value directly:

```json
"inputs": [
  42.0,
  3.14
]
```

#### Array Inputs

For array inputs, you can provide a more detailed configuration:

```json
"inputs": [
  {
    "size": 128,
    "float_type": "normal",
    "include_negatives": true,
    "values": [1.0, 2.0, 3.0, 4.0]
  }
]
```

Options for array inputs:

- `size`: The size of the array (must be consistent with dimension calculations)
- `float_type`: The type of floating-point values to generate. Options are:
  - `"normal"`: Regular floating-point values (default)
  - `"subnormal"`: Subnormal floating-point values (very small)
  - `"mixed"`: A mix of normal and subnormal values
  - `"magnitude"`: Values with varying magnitudes
- `include_negatives`: Whether to include negative values (boolean)
- `values`: An array of specific values to use. If fewer values are provided than the array size, the rest will be generated according to the specified `float_type` and `include_negatives` settings.

### Output

The `output` field allows you to customize the size of the output array:

```json
"output": {
  "size": 128
}
```

## Example Configuration

Here's a complete example of an input configuration file:

```json
{
  "dimensions": {
    "N": 128,
    "M": 64
  },
  "inputs": [
    {
      "size": 128,
      "float_type": "normal",
      "include_negatives": true,
      "values": [1.0, 2.0, 3.0, 4.0]
    },
    {
      "size": 64,
      "float_type": "subnormal",
      "include_negatives": false
    },
    42.0
  ],
  "output": {
    "size": 128
  }
}
```

This configuration:
1. Sets the dimension `N` to 128 and `M` to 64
2. Configures the first input as an array of 128 elements, using normal floating-point values with negative values enabled, and sets the first 4 elements to specific values
3. Configures the second input as an array of 64 elements using subnormal floating-point values without negative values
4. Sets the third input as a scalar value of 42.0
5. Sets the output array size to 128

## Validation

The driver generator will validate your input configuration against the RISE program:
- It checks that all dimensions in the configuration exist in the RISE program
- It verifies that the number of inputs matches the expected number
- It validates size consistency when specific sizes are provided

If there are any inconsistencies, warnings or errors will be displayed. 
#!/bin/bash
# compile_rise.sh
# This script takes a path to a RISE program as input and compiles it to C code
# using the float-safe-optimizer.

# Check for correct number of arguments.
if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 PATH_TO_RISE_FILE [--mpfr]"
  exit 1
fi

RISE_SOURCE="$1"
USE_MPFR="false"

# Check if MPFR flag is provided
if [ "$#" -eq 2 ] && [ "$2" = "--mpfr" ]; then
  USE_MPFR="true"
fi

# Extract the function name from the file name (remove path and extension)
FUNCTION_NAME=$(basename "$RISE_SOURCE" .rise)
if [ "$USE_MPFR" = "true" ]; then
  FUNCTION_NAME="${FUNCTION_NAME}_mpfr"
fi

# Create out directory if it doesn't exist
OUT_DIR="out"
mkdir -p "$OUT_DIR"

# Construct the output file path in the out directory
OUTPUT="${OUT_DIR}/${FUNCTION_NAME}.c"

# Check if the source file exists.
if [ ! -f "$RISE_SOURCE" ]; then
  echo "Error: RISE source file '$RISE_SOURCE' not found."
  exit 1
fi

echo "Compiling RISE source '$RISE_SOURCE' to C file '$OUTPUT' using function name '$FUNCTION_NAME'..."

# Run the optimizer command.
java -Xss20m -Xms512m -Xmx4G -jar ../../float-safe-optimizer.jar "$FUNCTION_NAME" "$RISE_SOURCE" "$OUTPUT" "$USE_MPFR"

# Check if the command succeeded.
if [ $? -eq 0 ]; then
  echo "Compilation successful. Output written to '$OUTPUT'."
  # Return the path to the generated C file
  echo "$OUTPUT"
else
  echo "Compilation failed."
  exit 1
fi

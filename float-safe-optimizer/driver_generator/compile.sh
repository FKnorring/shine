#!/bin/bash
# compile_rise.sh
# This script takes a path to unoptimized RISE program and optionally a path to an optimized RISE program
# and compiles them to C code using the float-safe-optimizer.

# Check for correct number of arguments.
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 PATH_TO_UNOPT_RISE_FILE [PATH_TO_OPT_RISE_FILE]"
  exit 1
fi

UNOPT_RISE_SOURCE="$1"
OPT_RISE_SOURCE="${2:-$1}"  # If no optimized file provided, use the unoptimized one

# Create out directory if it doesn't exist
OUT_DIR="out"
mkdir -p "$OUT_DIR"

# Check if the source files exist.
if [ ! -f "$UNOPT_RISE_SOURCE" ]; then
  echo "Error: Unoptimized RISE source file '$UNOPT_RISE_SOURCE' not found."
  exit 1
fi

if [ ! -f "$OPT_RISE_SOURCE" ]; then
  echo "Error: Optimized RISE source file '$OPT_RISE_SOURCE' not found."
  exit 1
fi

# Find the jar file
JAR_FILE="../float-safe-optimizer.jar"
if [ ! -f "$JAR_FILE" ]; then
  # Try alternate location
  JAR_FILE="../../float-safe-optimizer.jar"
  if [ ! -f "$JAR_FILE" ]; then
    echo "Error: Could not find float-safe-optimizer.jar. Please ensure it's in the correct location."
    exit 1
  fi
fi

BASE_NAME=$(basename "$UNOPT_RISE_SOURCE" .rise)

# 1. Generate unoptimized version without MPFR
FUNC_NAME="${BASE_NAME}_unopt"
OUTPUT="${OUT_DIR}/${FUNC_NAME}.c"
echo ""
echo ""
echo "Compiling unoptimized version of '$UNOPT_RISE_SOURCE' to '$OUTPUT'..."
echo ""
java -Xss20m -Xms512m -Xmx4G -jar "$JAR_FILE" "$FUNC_NAME" "$UNOPT_RISE_SOURCE" "$OUTPUT" "false" "true" 2>&1
if [ $? -ne 0 ]; then
  echo "Error: Failed to compile unoptimized version"
  exit 1
fi

# 2. Generate optimized version without MPFR
FUNC_NAME="${BASE_NAME}"
OUTPUT="${OUT_DIR}/${FUNC_NAME}.c"
echo ""
echo ""
echo "Compiling optimized version of '$OPT_RISE_SOURCE' to '$OUTPUT'..."
echo ""
java -Xss20m -Xms512m -Xmx4G -jar "$JAR_FILE" "$FUNC_NAME" "$OPT_RISE_SOURCE" "$OUTPUT" "false" "false" 2>&1
if [ $? -ne 0 ]; then
  echo "Error: Failed to compile optimized version"
  exit 1
fi

# 3. Generate unoptimized version with MPFR
FUNC_NAME="${BASE_NAME}_mpfr_unopt"
OUTPUT="${OUT_DIR}/${FUNC_NAME}.c"
echo ""
echo ""
echo "Compiling unoptimized MPFR version of '$UNOPT_RISE_SOURCE' to '$OUTPUT'..."
echo ""
java -Xss20m -Xms512m -Xmx4G -jar "$JAR_FILE" "$FUNC_NAME" "$UNOPT_RISE_SOURCE" "$OUTPUT" "true" "true" 2>&1
if [ $? -ne 0 ]; then
  echo "Error: Failed to compile unoptimized MPFR version"
  exit 1
fi

echo "Compilation completed successfully."
exit 0

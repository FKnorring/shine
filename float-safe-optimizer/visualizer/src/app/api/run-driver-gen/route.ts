import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';
import fs from 'fs/promises';

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const formData = await req.json();
    const {
      unoptRiseFile,
      optRiseFile,
      dimension,
      iterations,
      precision,
      outputFile,
      floatType,
      prefix,
      includeNegatives,
      metricsFile,
    } = formData;

    // Validate required fields
    if (!unoptRiseFile) {
      return NextResponse.json(
        { error: 'Unoptimized RISE file is required' },
        { status: 400 }
      );
    }

    // Build command - make sure to cd into the driver_generator directory so that the "out" directory is created there
    let command = `cd ../driver_generator && python3 driver_gen.py "../${unoptRiseFile}"`;

    if (optRiseFile) {
      command += ` -o "../${optRiseFile}"`;
    }
    if (dimension) {
      command += ` -d ${dimension}`;
    }
    if (iterations) {
      command += ` -i ${iterations}`;
    }
    if (precision) {
      command += ` -p ${precision}`;
    }
    if (outputFile) {
      command += ` --output "${outputFile}"`;
    }
    if (floatType) {
      command += ` -f ${floatType}`;
    }
    if (prefix) {
      command += ` --prefix "${prefix}"`;
    }
    if (includeNegatives) {
      command += ` --include_negatives`;
    }
    if (metricsFile) {
      command += ` --metrics_file "${metricsFile}"`;
    }

    console.log(`Executing command: ${command}`);

    const { stdout, stderr } = await execAsync(command);
    
    return NextResponse.json({
      success: true,
      stdout,
      stderr,
    });
  } catch (error) {
    console.error('Error running driver generator:', error);
    return NextResponse.json(
      { error: `Failed to run driver generator: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import { DriverGenOptions } from "@/types";
import * as fs from 'fs';

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const data: DriverGenOptions = await req.json();
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
      skipCompilation,
      inputConfig
    } = data;

    console.log(data);
    console.log(inputConfig);

    // Validate required fields
    if (!unoptRiseFile) {
      return NextResponse.json({ error: "Missing required field: unoptRiseFile" });
    }

    // Build the command
    const riseDir = process.cwd() + "/../";
    const driverGenDir = "../driver_generator";
    
    let command = `cd ${driverGenDir} && python3 driver_gen.py "${riseDir}${unoptRiseFile}"`;

    // Add optional arguments
    if (optRiseFile) {
      command += ` -o "${riseDir}${optRiseFile}"`;
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
    
    if (skipCompilation) {
      command += ` --skip_compilation`;
    }

    // Add input configuration if provided
    let tempConfigFile: string | null = null;
    if (inputConfig) {
      // Create a temporary file for the input configuration
      tempConfigFile = `/tmp/input_config_${Date.now()}.json`;
      fs.writeFileSync(tempConfigFile, JSON.stringify(inputConfig));
      command += ` --input_config "${tempConfigFile}"`;
    }

    console.log(`Executing command: ${command}`);

    // Execute the command
    const { stdout, stderr } = await execAsync(command);

    // Clean up temporary file if it was created
    if (tempConfigFile) {
      try {
        fs.unlinkSync(tempConfigFile);
      } catch (error) {
        console.error("Error cleaning up temporary config file:", error);
      }
    }

    return NextResponse.json({ stdout, stderr });
  } catch (error) {
    console.error("Error:", error);
    return NextResponse.json({ 
      error: error instanceof Error ? error.message : "Unknown error" 
    });
  }
} 
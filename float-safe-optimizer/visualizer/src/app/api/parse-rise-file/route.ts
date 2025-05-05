import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { existsSync } from 'fs';
import { execSync } from 'child_process';

interface RiseInput {
  type: string;
  isArray: boolean;
  dimensions: string[];
  size: string;
}

/**
 * Parse a RISE file to extract structure information
 */
export async function POST(request: NextRequest) {
  try {
    const { riseFile } = await request.json();
    
    if (!riseFile) {
      return NextResponse.json({ error: 'No RISE file provided', success: false }, { status: 400 });
    }
    
    // Path to the parser.py script
    const scriptPath = join(process.cwd(), '..', 'driver_generator', 'parser.py');
    
    // Path to the RISE file in the rise directory
    const riseFilePath = join(process.cwd(), '..', riseFile);
    
    // Ensure the script exists
    if (!existsSync(scriptPath)) {
      return NextResponse.json(
        { error: 'parser.py script not found', success: false },
        { status: 500 }
      );
    }
    
    // Execute the parser script to analyze the RISE file
    try {
      // Build command to run the script
      const command = `python3 ${scriptPath} "${riseFilePath}"`;
      
      // Execute the command and get output
      const output = execSync(command, { encoding: 'utf-8' });
      
      // Parse the output to extract structure information
      // Example output:
      // Parsed RISE file information:
      // Dimensions: n
      // Input sizes: n, n
      // Output size: n
      // Single value output: false
      
      let dimensions: string[] = [];
      let inputs: RiseInput[] = [];
      let outputSize = '';
      let isSingleValue = false;
      
      // Extract dimensions
      const dimMatch = output.match(/Dimensions: (.*)/);
      if (dimMatch && dimMatch[1]) {
        dimensions = dimMatch[1].split(', ').map(d => d.trim());
      }
      
      // Extract input sizes
      const inputMatch = output.match(/Input sizes: (.*)/);
      if (inputMatch && inputMatch[1]) {
        const inputSizes = inputMatch[1].split(', ').map(s => s.trim());
        
        // Create input objects for each size
        inputs = inputSizes.map((size) => {
          const isArray = size !== '1';
          return {
            type: 'f32',
            isArray,
            dimensions: isArray ? size.split(' * ') : [],
            size
          };
        });
      }
      
      // Extract output size
      const outputMatch = output.match(/Output size: (.*)/);
      if (outputMatch && outputMatch[1]) {
        outputSize = outputMatch[1].trim();
      }
      
      // Extract single value output info
      const singleValueMatch = output.match(/Single value output: (.*)/);
      if (singleValueMatch && singleValueMatch[1]) {
        isSingleValue = singleValueMatch[1].trim() === 'True';
      }
      
      // Return the structured data
      return NextResponse.json({ 
        success: true,
        fileInfo: {
          dimensions,
          inputs,
          outputSize,
          isSingleValue
        }
      });
    } catch (error) {
      console.error('Error parsing RISE file:', error);
      return NextResponse.json({ 
        error: 'Failed to parse RISE file',
        success: false 
      });
    }
  } catch (error) {
    console.error('Error in parse-rise-file API:', error);
    return NextResponse.json(
      { error: 'Failed to process request', success: false },
      { status: 500 }
    );
  }
} 
import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  try {
    const { driverPath } = await req.json();
    
    if (!driverPath) {
      return NextResponse.json(
        { error: 'Driver path is required' },
        { status: 400 }
      );
    }
    
    // Build command to run the driver, making sure to run it from the driver_generator directory
    // The path will typically be something like "out/driver_compare" without ./ prefix
    const executable = driverPath.startsWith('out/') ? driverPath : `out/${driverPath}`;
    const command = `cd ../driver_generator && ./${executable}`;
    
    console.log(`Executing command: ${command}`);
    
    const { stdout, stderr } = await execAsync(command);
    
    return NextResponse.json({
      success: true,
      stdout,
      stderr,
    });
  } catch (error) {
    console.error('Error running driver:', error);
    return NextResponse.json(
      { error: `Failed to run driver: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
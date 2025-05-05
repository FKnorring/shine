import { NextRequest, NextResponse } from 'next/server';
import { join } from 'path';
import { existsSync } from 'fs';
import { execSync } from 'child_process';

/**
 * Check if compiled C files already exist for a given RISE file
 */
export async function POST(request: NextRequest) {
  try {
    const { riseFile, prefix = '' } = await request.json();
    
    if (!riseFile) {
      return NextResponse.json({ error: 'No RISE file provided' }, { status: 400 });
    }
    
    // Path to the check_c_files.py script
    const scriptPath = join(process.cwd(), '..', 'driver_generator', 'check_c_files.py');
    
    // Path to the out directory
    const outDirPath = join(process.cwd(), '..', 'driver_generator', 'out');
    
    // Path to the RISE file in the rise directory
    const riseFilePath = join(process.cwd(), '..', riseFile);

    console.log(riseFilePath);
    
    // Ensure the script exists
    if (!existsSync(scriptPath)) {
      return NextResponse.json(
        { error: 'check_c_files.py script not found', exist: false },
        { status: 500 }
      );
    }
    
    // Execute the script to check if files exist
    try {
      // Build command to run the script
      const command = `python3 ${scriptPath} "${riseFilePath}" --out-dir "${outDirPath}" ${prefix ? `--prefix "${prefix}"` : ''}`;
      
      // Execute the command, which will return exit code 0 if files exist
      execSync(command);
      
      // If we get here, the command succeeded, meaning the files exist
      return NextResponse.json({ exist: true });
    } catch {
      // Exit code non-zero means files don't exist
      return NextResponse.json({ exist: false });
    }
  } catch (error) {
    console.error('Error checking C files:', error);
    return NextResponse.json(
      { error: 'Failed to check C files', exist: false },
      { status: 500 }
    );
  }
} 
import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function GET() {
  try {
    // Find all .rise files in the examples directory
    const command = `cd .. && find -name "*.rise" | sort`;
    
    const { stdout } = await execAsync(command);
    
    // Parse the output into an array of file paths
    const riseFiles = stdout.trim().split('\n').filter(Boolean);
    
    return NextResponse.json({ riseFiles });
  } catch (error) {
    console.error('Error listing RISE files:', error);
    return NextResponse.json(
      { error: `Failed to list RISE files: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function POST() {
  try {
    // Command to remove all files from the out directory but keep the directory itself
    const command = `cd ../driver_generator && rm -f out/*`;
    
    const { stdout, stderr } = await execAsync(command);
    
    return NextResponse.json({
      success: true,
      message: 'Out directory cleared successfully',
      stdout,
      stderr,
    });
  } catch (error) {
    console.error('Error clearing out directory:', error);
    return NextResponse.json(
      { error: `Failed to clear out directory: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
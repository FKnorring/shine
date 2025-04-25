import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs/promises';
import path from 'path';

const execAsync = promisify(exec);

export async function GET() {
  try {
    // Get the list of files in the out directory
    const command = `cd ../driver_generator && find out -type f | sort`;
    
    const { stdout } = await execAsync(command);
    
    // Parse the output into an array of file paths
    const outFiles = stdout.trim().split('\n').filter(Boolean);
    
    // Get file information
    const filesWithInfo = await Promise.all(
      outFiles.map(async (filePath) => {
        try {
          // Construct the full path to access the file
          const fullPath = path.join(process.cwd(), '..', 'driver_generator', filePath);
          const stats = await fs.stat(fullPath);
          const content = filePath.endsWith('.csv') 
            ? await fs.readFile(fullPath, 'utf-8')
            : null;
          
          return {
            path: filePath,
            name: path.basename(filePath),
            size: stats.size,
            timestamp: stats.mtimeMs,
            isExecutable: !!(stats.mode & 0o111),
            content,
            isMetrics: filePath.endsWith('.csv'),
          };
        } catch (err) {
          console.error(`Error getting info for ${filePath}:`, err);
          return {
            path: filePath,
            name: path.basename(filePath),
            error: 'Could not read file info',
          };
        }
      })
    );
    
    return NextResponse.json({ files: filesWithInfo });
  } catch (error) {
    console.error('Error listing out files:', error);
    return NextResponse.json(
      { error: `Failed to list out files: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
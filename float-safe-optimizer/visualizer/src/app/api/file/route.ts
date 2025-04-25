import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function GET(req: NextRequest) {
  try {
    const url = new URL(req.url);
    const filePath = url.searchParams.get('path');
    
    if (!filePath) {
      return NextResponse.json(
        { error: 'Path parameter is required' },
        { status: 400 }
      );
    }
    
    // Make sure the path is within our project directory - files should be in driver_generator/out now
    const fullPath = path.join(process.cwd(), '..', 'driver_generator', filePath);
    
    // Read the file content
    const content = await fs.readFile(fullPath, 'utf-8');
    
    // Return the file content as plain text
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/plain',
      },
    });
  } catch (error) {
    console.error('Error serving file:', error);
    return NextResponse.json(
      { error: `Failed to read file: ${error instanceof Error ? error.message : String(error)}` },
      { status: 500 }
    );
  }
} 
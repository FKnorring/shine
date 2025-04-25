import React, { useState, useEffect } from 'react';
import { OutFile } from '@/types';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatRelativeTime } from '@/utils/formatTime';

interface OutFilesProps {
  files: OutFile[];
  onRunDriver: (filePath: string) => void;
  isLoading: boolean;
}

export default function OutFiles({ files, onRunDriver, isLoading }: OutFilesProps) {
  // State to trigger re-renders for time updates
  // This state isn't directly referenced but changing it forces re-renders to update timestamps
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [currentTime, setCurrentTime] = useState(Date.now());

  // Update the current time every 5 seconds to refresh timestamps
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  if (files.length === 0) {
    return (
      <div className="p-6 text-center">
        <p className="text-muted-foreground text-sm">No files in the output directory</p>
      </div>
    );
  }

  // Group files by type
  const executableFiles = files.filter(file => file.isExecutable);
  const sourceFiles = files.filter(file => file.name.endsWith('.c') && !file.isExecutable);
  const metricsFiles = files.filter(file => file.isMetrics);
  const otherFiles = files.filter(file => 
    !file.isExecutable && !file.name.endsWith('.c') && !file.isMetrics
  );

  return (
    <div className="overflow-hidden">
      <Table className="px-2">
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Size</TableHead>
            <TableHead>Time</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {executableFiles.length > 0 && (
            <>
              <TableRow className="bg-blue-50/30 hover:bg-blue-50/50">
                <TableCell colSpan={4} className="py-1.5 text-xs font-medium text-blue-800">
                  Executable Files
                </TableCell>
              </TableRow>
              {executableFiles.map((file) => (
                <TableRow key={file.path}>
                  <TableCell className="font-medium text-sm py-1.5">{file.name}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatFileSize(file.size)}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatRelativeTime(file.timestamp, currentTime)}</TableCell>
                  <TableCell className="py-1.5">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => onRunDriver(file.path)}
                      disabled={isLoading}
                      className="h-7 px-2 text-xs"
                    >
                      Run
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </>
          )}
          
          {sourceFiles.length > 0 && (
            <>
              <TableRow className="bg-green-50/30 hover:bg-green-50/50">
                <TableCell colSpan={4} className="py-1.5 text-xs font-medium text-green-800">
                  Source Files
                </TableCell>
              </TableRow>
              {sourceFiles.map((file) => (
                <TableRow key={file.path}>
                  <TableCell className="font-medium text-sm py-1.5">{file.name}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatFileSize(file.size)}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatRelativeTime(file.timestamp, currentTime)}</TableCell>
                  <TableCell className="py-1.5">
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="h-7 px-2 text-xs"
                      asChild
                    >
                      <a 
                        href={`/api/file?path=${encodeURIComponent(file.path)}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        View
                      </a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </>
          )}
          
          {metricsFiles.length > 0 && (
            <>
              <TableRow className="bg-purple-50/30 hover:bg-purple-50/50">
                <TableCell colSpan={4} className="py-1.5 text-xs font-medium text-purple-800">
                  Metrics Files
                </TableCell>
              </TableRow>
              {metricsFiles.map((file) => (
                <TableRow key={file.path}>
                  <TableCell className="font-medium text-sm py-1.5">{file.name}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatFileSize(file.size)}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatRelativeTime(file.timestamp, currentTime)}</TableCell>
                  <TableCell className="py-1.5">
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="h-7 px-2 text-xs"
                      asChild
                    >
                      <a 
                        href={`/api/file?path=${encodeURIComponent(file.path)}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        View
                      </a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </>
          )}
          
          {otherFiles.length > 0 && (
            <>
              <TableRow className="bg-gray-50/30 hover:bg-gray-50/50">
                <TableCell colSpan={4} className="py-1.5 text-xs font-medium text-gray-800">
                  Other Files
                </TableCell>
              </TableRow>
              {otherFiles.map((file) => (
                <TableRow key={file.path}>
                  <TableCell className="font-medium text-sm py-1.5">{file.name}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatFileSize(file.size)}</TableCell>
                  <TableCell className="text-sm py-1.5">{formatRelativeTime(file.timestamp, currentTime)}</TableCell>
                  <TableCell className="py-1.5">
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="h-7 px-2 text-xs"
                      asChild
                    >
                      <a 
                        href={`/api/file?path=${encodeURIComponent(file.path)}`} 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        View
                      </a>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </>
          )}
        </TableBody>
      </Table>
    </div>
  );
}

// Helper function to format file size
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
} 
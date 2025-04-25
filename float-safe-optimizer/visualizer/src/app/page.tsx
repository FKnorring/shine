"use client";

import React, { useState, useEffect } from "react";
import DriverGenForm from "@/components/DriverGenForm";
import CommandOutput from "@/components/CommandOutput";
import OutFiles from "@/components/OutFiles";
import MetricsCharts from "@/components/MetricsCharts";
import {
  DriverGenOptions,
  CommandOutput as CommandOutputType,
  OutFile,
  MetricsData,
} from "@/types";
import { parseMetricsCSV, combineMetricsData } from "@/utils/metricsParser";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [outFiles, setOutFiles] = useState<OutFile[]>([]);
  const [driverGenOutput, setDriverGenOutput] =
    useState<CommandOutputType | null>(null);
  const [driverOutput, setDriverOutput] = useState<CommandOutputType | null>(
    null
  );
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [activeTab, setActiveTab] = useState<string>("metrics");

  // Process metrics files
  const processMetricsFiles = (files: OutFile[]) => {
    // Get main metrics.csv file
    const metricsFile = files.find(
      (file) => file.isMetrics && file.path.endsWith('metrics.csv')
    );
    
    // Get iteration data files
    const optTimingsFile = files.find(
      (file) => file.path.endsWith('metrics_opt_timings.csv')
    );
    
    const unoptTimingsFile = files.find(
      (file) => file.path.endsWith('metrics_unopt_timings.csv')
    );
    
    const optResultsFile = files.find(
      (file) => file.path.endsWith('metrics_opt_results.csv')
    );
    
    if (metricsFile && metricsFile.content) {
      // Parse base metrics
      const baseMetrics = parseMetricsCSV(metricsFile.content);
      
      // Combine with iteration data if available
      const combinedMetrics = combineMetricsData(
        baseMetrics,
        optTimingsFile?.content || undefined,
        unoptTimingsFile?.content || undefined,
        optResultsFile?.content || undefined
      );
      
      setMetricsData(combinedMetrics);
    } else {
      setMetricsData(null);
    }
  };

  // Fetch files in the out directory
  const fetchOutFiles = async () => {
    try {
      const response = await fetch("/api/out-files");
      const data = await response.json();

      if (data.files) {
        setOutFiles(data.files);
        processMetricsFiles(data.files);
      }
    } catch (error) {
      console.error("Failed to fetch out files:", error);
    }
  };

  // Run the driver generator
  const runDriverGen = async (data: DriverGenOptions) => {
    setIsLoading(true);
    setDriverGenOutput(null);
    setDriverOutput(null);

    try {
      const response = await fetch("/api/run-driver-gen", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();
      setDriverGenOutput(result);

      // Refresh the list of files in the out directory
      await fetchOutFiles();
    } catch (error) {
      console.error("Error running driver generator:", error);
      setDriverGenOutput({
        error: `Failed to run driver generator: ${
          error instanceof Error ? error.message : String(error)
        }`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Run the compiled driver
  const runDriver = async (driverPath: string) => {
    setIsLoading(true);
    setDriverOutput(null);

    try {
      const response = await fetch("/api/run-driver", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ driverPath }),
      });

      const result = await response.json();
      setDriverOutput(result);

      // Refresh the list of files to get updated metrics
      await fetchOutFiles();
    } catch (error) {
      console.error("Error running driver:", error);
      setDriverOutput({
        error: `Failed to run driver: ${
          error instanceof Error ? error.message : String(error)
        }`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Clear the out directory
  const clearOutDirectory = async () => {
    setIsLoading(true);

    try {
      await fetch("/api/clear-out", {
        method: "POST",
      });

      // Reset state
      setDriverGenOutput(null);
      setDriverOutput(null);
      setMetricsData(null);

      // Refresh the list of files
      await fetchOutFiles();
    } catch (error) {
      console.error("Error clearing out directory:", error);
      alert("Failed to clear out directory");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Fetch files on component mount
    fetchOutFiles();
  }, []);

  // Check if command outputs are available
  const hasCommandOutput = driverGenOutput || driverOutput;

  return (
    <main className="min-h-screen bg-muted/20">
      <div className="container mx-auto px-4 py-6">
        <header className="mb-3">
          <h1 className="text-3xl font-bold text-foreground">
            Float-Safe Optimizer Visualizer
          </h1>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-1 space-y-6">
            <Card className="shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">Controls</CardTitle>
              </CardHeader>
              <CardContent>
                <DriverGenForm 
                  onSubmit={runDriverGen} 
                  isLoading={isLoading} 
                  onRunDriver={() => {
                    const driverFile = outFiles.find(file => file.path.endsWith('.c'));
                    if (driverFile) {
                      // Remove .c extension to get the executable path
                      const executablePath = driverFile.path.replace(/\.c$/, '');
                      runDriver(executablePath);
                    }
                  }}
                  hasDriver={outFiles.some(file => file.path.endsWith('.c'))}
                />
              </CardContent>
            </Card>

            <Card className="shadow-sm">
              <CardHeader>
                <CardTitle className="text-xl">Output Files</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <Button
                  variant="destructive"
                  onClick={clearOutDirectory}
                  disabled={isLoading}
                  className="ml-4 mb-2"
                >
                  Clear Out Directory
                </Button>
                <OutFiles
                  files={outFiles}
                  onRunDriver={runDriver}
                  isLoading={isLoading}
                />
              </CardContent>
            </Card>
          </div>

          <div className="xl:col-span-2 space-y-6">
            <Card className="shadow-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-xl">Results</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger 
                      value="metrics" 
                      disabled={!metricsData}
                      className={!metricsData ? "cursor-not-allowed opacity-50" : ""}
                    >
                      Metrics
                    </TabsTrigger>
                    <TabsTrigger 
                      value="output" 
                      disabled={!hasCommandOutput}
                      className={!hasCommandOutput ? "cursor-not-allowed opacity-50" : ""}
                    >
                      Command Output
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="output" className="mt-6">
                    {driverGenOutput && (
                      <CommandOutput
                        output={driverGenOutput}
                        title="Driver Generator Output"
                      />
                    )}

                    {driverOutput && (
                      <CommandOutput
                        output={driverOutput}
                        title="Driver Execution Output"
                      />
                    )}

                    {!hasCommandOutput && (
                      <div className="py-8 text-center text-muted-foreground">
                        No command output available yet. Run a command to see output here.
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="metrics" className="mt-6">
                    {metricsData ? (
                      <MetricsCharts 
                        metricsData={metricsData} 
                        timestamp={outFiles.find((f: OutFile) => f.isMetrics && f.path.endsWith('metrics.csv'))?.timestamp} 
                      />
                    ) : (
                      <div className="py-8 text-center text-muted-foreground">
                        No metrics data available yet. Run a command that generates metrics.
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}

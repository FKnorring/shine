import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MetricsData } from "@/types";
import { getIterationTimingData } from "@/utils/metricsParser";
import { MetricCard } from "./MetricCard";
import { formatNumber } from "@/utils/metricsParser";

interface PerformanceDistributionCardProps {
  metricsData: MetricsData;
}

// Helper function to calculate quartiles and detect outliers
function calculateOutliers(data: number[]) {
  const sorted = [...data].sort((a, b) => a - b);
  const q1 = sorted[Math.floor(sorted.length * 0.25)];
  const q3 = sorted[Math.floor(sorted.length * 0.75)];
  const iqr = q3 - q1;
  const lowerBound = q1 - 1.5 * iqr;
  const upperBound = q3 + 1.5 * iqr;
  
  return {
    lowerBound,
    upperBound,
    outliers: data.filter(x => x < lowerBound || x > upperBound),
    nonOutliers: data.filter(x => x >= lowerBound && x <= upperBound)
  };
}

export function PerformanceDistributionCard({ metricsData }: PerformanceDistributionCardProps) {
  const { optData: optIterationsData, unoptData: unoptIterationsData } = getIterationTimingData(metricsData);

  const optTimesStats = {
    min: metricsData.opt_min_time || 0,
    mean: metricsData.opt_mean_time || 0,
    median: metricsData.opt_median_time || 0,
    max: metricsData.opt_max_time || 0,
    stddev: metricsData.opt_time_stddev || 0,
  };

  const unoptTimesStats = {
    min: metricsData.unopt_min_time || 0,
    mean: metricsData.unopt_mean_time || 0,
    median: metricsData.unopt_median_time || 0,
    max: metricsData.unopt_max_time || 0,
    stddev: metricsData.unopt_time_stddev || 0,
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="distribution">
          <TabsList className="mb-4">
            <TabsTrigger value="distribution">Distribution</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="distribution">
            <div className="w-full h-[300px]">
              {(() => {
                const optTimes = optIterationsData.map(d => d.time);
                const unoptTimes = unoptIterationsData.map(d => d.time);
                
                // Calculate outliers for both datasets
                const optOutliers = calculateOutliers(optTimes);
                const unoptOutliers = calculateOutliers(unoptTimes);
                
                // Use non-outlier data for bucketing
                const allNonOutlierTimes = [...optOutliers.nonOutliers, ...unoptOutliers.nonOutliers];
                const min = Math.min(...allNonOutlierTimes);
                const max = Math.max(...allNonOutlierTimes);
                const numBuckets = 20;
                const bucketSize = (max - min) / numBuckets;

                const optBuckets = new Array(numBuckets).fill(0);
                const unoptBuckets = new Array(numBuckets).fill(0);

                // Count non-outliers in buckets
                optOutliers.nonOutliers.forEach(time => {
                  const bucketIndex = Math.min(
                    Math.floor((time - min) / bucketSize),
                    numBuckets - 1
                  );
                  optBuckets[bucketIndex]++;
                });

                unoptOutliers.nonOutliers.forEach(time => {
                  const bucketIndex = Math.min(
                    Math.floor((time - min) / bucketSize),
                    numBuckets - 1
                  );
                  unoptBuckets[bucketIndex]++;
                });

                const distributionData = Array(numBuckets).fill(0).map((_, i) => ({
                  timeRange: min + (i + 0.5) * bucketSize,
                  optimized: optBuckets[i],
                  unoptimized: unoptBuckets[i]
                }));

                return (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={distributionData}
                      margin={{ top: 20, right: 50, left: 20, bottom: 5 }}
                      barSize={20}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="timeRange"
                        type="number"
                        label={{
                          value: "Execution Time (seconds)",
                          position: "insideBottom",
                          offset: -5,
                        }}
                        tickFormatter={(value) => value.toExponential(2)}
                      />
                      <YAxis
                        label={{
                          value: "Frequency",
                          angle: -90,
                          position: "insideLeft",
                          offset: -10,
                        }}
                      />
                      <Tooltip
                        formatter={(value: number, name: string) => [
                          `Count: ${value}`,
                          name
                        ]}
                      />
                      <Legend />
                      <Bar dataKey="optimized" name="Optimized" fill="#8884d8" opacity={0.8} />
                      <Bar dataKey="unoptimized" name="Unoptimized" fill="#82ca9d" opacity={0.8} />
                    </BarChart>
                  </ResponsiveContainer>
                );
              })()}
            </div>
          </TabsContent>

          <TabsContent value="stats">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-lg font-medium mb-2">Optimized</h3>
                <div className="grid grid-cols-2 gap-2">
                  <MetricCard
                    title="Min Time"
                    value={`${formatNumber(optTimesStats.min)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Max Time"
                    value={`${formatNumber(optTimesStats.max)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Mean Time"
                    value={`${formatNumber(optTimesStats.mean)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Median Time"
                    value={`${formatNumber(optTimesStats.median)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="StdDev"
                    value={`${formatNumber(optTimesStats.stddev)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Variance"
                    value={`${formatNumber(metricsData.opt_time_variance || 0)}`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium mb-2">Unoptimized</h3>
                <div className="grid grid-cols-2 gap-2">
                  <MetricCard
                    title="Min Time"
                    value={`${formatNumber(unoptTimesStats.min)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Max Time"
                    value={`${formatNumber(unoptTimesStats.max)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Mean Time"
                    value={`${formatNumber(unoptTimesStats.mean)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Median Time"
                    value={`${formatNumber(unoptTimesStats.median)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="StdDev"
                    value={`${formatNumber(unoptTimesStats.stddev)} s`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                  <MetricCard
                    title="Variance"
                    value={`${formatNumber(metricsData.unopt_time_variance || 0)}`}
                    valueClassName="text-sm font-mono overflow-x-auto"
                  />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
} 
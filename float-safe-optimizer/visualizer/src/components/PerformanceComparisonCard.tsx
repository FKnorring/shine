import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsData } from "@/types";
import { getPerformanceChartData, formatNumber } from "@/utils/metricsParser";
import { MetricCard } from "./MetricCard";

interface ExtendedMetricsData extends MetricsData {
  unopt_mean_time?: number;
  opt_mean_time?: number;
  unopt_time?: number;
  opt_time?: number;
}

interface PerformanceComparisonCardProps {
  metricsData: MetricsData;
}

export function PerformanceComparisonCard({ metricsData }: PerformanceComparisonCardProps) {
  const extendedMetrics = metricsData as ExtendedMetricsData;
  const performanceData = getPerformanceChartData(metricsData);

  // Calculate speedup based on mean times if available, otherwise use single-run times
  const unoptTime = extendedMetrics.unopt_mean_time ?? extendedMetrics.unopt_time ?? 0;
  const optTime = extendedMetrics.opt_mean_time ?? extendedMetrics.opt_time ?? 0;
  const speedup = unoptTime > 0 ? unoptTime / optTime : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Performance Comparison</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={performanceData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis
                label={{
                  value: "Execution Time (seconds)",
                  angle: -90,
                  position: "inside",
                  dx: -40,
                }}
                tickFormatter={(value) => value.toExponential(2)}
              />
              <Tooltip
                formatter={(value: number) => [
                  `${formatNumber(value)} seconds`,
                  "Execution Time",
                ]}
              />
              <Legend />
              <Bar dataKey="time" name="Execution Time" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Unoptimized Time"
            value={`${formatNumber(unoptTime)} s`}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Optimized Time"
            value={`${formatNumber(optTime)} s`}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Speedup Ratio"
            value={`${formatNumber(speedup)}x`}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
        </div>
      </CardContent>
    </Card>
  );
} 
import React from "react";
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsData } from "@/types";
import { getIterationResultData, formatNumber } from "@/utils/metricsParser";
import { MetricCard } from "./MetricCard";

interface ResultStabilityCardProps {
  metricsData: MetricsData;
}

export function ResultStabilityCard({ metricsData }: ResultStabilityCardProps) {
  const optResultsData = getIterationResultData(metricsData);

  const getResultStats = () => {
    if (optResultsData.length === 0)
      return { min: 0, max: 0, mean: 0, consistent: true };

    const values = optResultsData.map((item) => item.result);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const sum = values.reduce((a, b) => a + b, 0);
    const mean = sum / values.length;

    // Check if all results are the same (consistent)
    const consistent = min === max;

    return { min, max, mean, consistent };
  };

  const resultStats = getResultStats();

  if (optResultsData.length === 0) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Result Stability</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          {resultStats.consistent ? (
            <div className="flex h-full flex-col items-center justify-center">
              <div className="text-2xl font-bold text-green-500 mb-4">
                Results are consistent across all iterations
              </div>
              <div className="text-lg text-muted-foreground">
                All {optResultsData.length} iterations produced identical
                results
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 20, right: 30, left: 20, bottom: 10 }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="iteration"
                  name="Iteration"
                  label={{
                    value: "Iteration",
                    position: "insideBottom",
                    offset: -5,
                  }}
                />
                <YAxis
                  dataKey="result"
                  name="Result Value"
                  label={{
                    value: "Result Value",
                    angle: -90,
                    position: "insideLeft",
                  }}
                  domain={["auto", "auto"]}
                  tickFormatter={(value) => value.toExponential(2)}
                />
                <Tooltip
                  formatter={(value: number) => formatNumber(value)}
                  cursor={{ strokeDasharray: "3 3" }}
                />
                <Legend />
                <Scatter
                  name="Result Value"
                  data={optResultsData}
                  fill="#8884d8"
                />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="Min Result"
            value={formatNumber(resultStats.min)}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Max Result"
            value={formatNumber(resultStats.max)}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Mean Result"
            value={formatNumber(resultStats.mean)}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
        </div>
      </CardContent>
    </Card>
  );
} 
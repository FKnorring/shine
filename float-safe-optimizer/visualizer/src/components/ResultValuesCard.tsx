import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsData } from "@/types";
import { MetricCard } from "./MetricCard";
import { getIterationResultData, formatFullNumber } from "@/utils/metricsParser";

interface ResultValuesCardProps {
  metricsData: MetricsData;
}

export function ResultValuesCard({ metricsData }: ResultValuesCardProps) {
  const optResultsData = getIterationResultData(metricsData);
  const meanValue = optResultsData.length > 0 
    ? optResultsData.reduce((sum, item) => sum + item.result, 0) / optResultsData.length
    : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Result Values</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            title="MPFR Reference"
            value={metricsData.mpfr_value !== undefined ? formatFullNumber(metricsData.mpfr_value) : ""}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Unoptimized"
            value={metricsData.unopt_value !== undefined ? formatFullNumber(metricsData.unopt_value) : ""}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
          <MetricCard
            title="Optimized (mean)"
            value={formatFullNumber(meanValue)}
            valueClassName="text-sm font-mono overflow-x-auto"
          />
        </div>
      </CardContent>
    </Card>
  );
} 
import React, { useState, useEffect } from "react";
import { MetricsData } from "@/types";
import { PerformanceComparisonCard } from "./PerformanceComparisonCard";
import { PerformanceDistributionCard } from "./PerformanceDistributionCard";
import { ResultStabilityCard } from "./ResultStabilityCard";
import { AccuracyComparisonCard } from "./AccuracyComparisonCard";
import { ResultValuesCard } from "./ResultValuesCard";
import { RawMetricsDataCard } from "./RawMetricsDataCard";

interface MetricsChartsProps {
  metricsData: MetricsData | null;
  timestamp?: number;
}

export default function MetricsCharts({
  metricsData,
  timestamp,
}: MetricsChartsProps) {
  // State to trigger re-renders for time updates
  const [currentTime, setCurrentTime] = useState(Date.now());

  // Update the current time every 5 seconds to refresh timestamps
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!metricsData) return null;

  return (
    <div className="space-y-8">
      <PerformanceComparisonCard metricsData={metricsData} />
      <PerformanceDistributionCard metricsData={metricsData} />
      <ResultStabilityCard metricsData={metricsData} />
      <AccuracyComparisonCard metricsData={metricsData} />
      <ResultValuesCard metricsData={metricsData} />
      <RawMetricsDataCard 
        metricsData={metricsData} 
        timestamp={timestamp} 
        currentTime={currentTime} 
      />
    </div>
  );
}

import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricsData } from "@/types";
import { getMetricsTableData } from "@/utils/metricsParser";
import { formatRelativeTime } from "@/utils/formatTime";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface RawMetricsDataCardProps {
  metricsData: MetricsData;
  timestamp?: number;
  currentTime?: number;
}

export function RawMetricsDataCard({ metricsData, timestamp, currentTime }: RawMetricsDataCardProps) {
  const tableData = getMetricsTableData(metricsData);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex justify-between items-center">
          <span>Raw Metrics Data</span>
          {timestamp && currentTime && (
            <span className="text-sm text-muted-foreground">
              Generated {formatRelativeTime(timestamp, currentTime)}
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableCaption>Complete metrics data from CSV file</TableCaption>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Value</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tableData.map((row, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{row.metric}</TableCell>
                  <TableCell>{row.value.toString()}</TableCell>
                  <TableCell>{row.description}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
} 
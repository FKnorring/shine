import React from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { MetricsData } from "@/types";
import { formatFullNumber } from "@/utils/metricsParser";

interface AccuracyComparisonCardProps {
  metricsData: MetricsData;
}

export function AccuracyComparisonCard({ metricsData }: AccuracyComparisonCardProps) {
  const relativeErrorData = [
    { 
      name: 'Unoptimized vs MPFR',
      error: metricsData.unopt_rel_error || 0
    },
    { 
      name: 'Optimized vs MPFR',
      error: metricsData.opt_mean_rel_error || 0
    },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Accuracy Comparison</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={relativeErrorData}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis
                label={{
                  value: "Relative Error",
                  angle: -90,
                  position: "inside",
                  dx: -40,
                }}
                tickFormatter={(value) => formatFullNumber(value)}
              />
              <Tooltip
                formatter={(value: number) => [
                  formatFullNumber(value),
                  "Relative Error",
                ]}
              />
              <Legend />
              <Bar dataKey="error" name="Relative Error" fill="#ffc658" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-6">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Metric</TableHead>
                <TableHead>Unoptimized</TableHead>
                <TableHead>Optimized</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Absolute Error</TableCell>
                <TableCell>{formatFullNumber(metricsData.unopt_abs_error || 0)}</TableCell>
                <TableCell>{formatFullNumber(metricsData.opt_mean_abs_error || 0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Relative Error</TableCell>
                <TableCell>{formatFullNumber(metricsData.unopt_rel_error || 0)}</TableCell>
                <TableCell>{formatFullNumber(metricsData.opt_mean_rel_error || 0)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">ULPs</TableCell>
                <TableCell>{formatFullNumber(metricsData.unopt_ulps || 0)}</TableCell>
                <TableCell>{formatFullNumber(metricsData.opt_mean_ulps || 0)}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
} 
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: string | number;
  className?: string;
  valueClassName?: string;
}

export function MetricCard({
  title,
  value,
  className,
  valueClassName,
}: MetricCardProps) {
  return (
    <Card className={cn("gap-2", className)}>
      <CardHeader>
        <CardTitle className="font-medium text-sm text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className={valueClassName || "text-xl"}>{value}</p>
      </CardContent>
    </Card>
  );
} 
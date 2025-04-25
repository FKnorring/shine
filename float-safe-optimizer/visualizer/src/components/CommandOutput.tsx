import React, { useState } from 'react';
import { CommandOutput as CommandOutputType } from '@/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDownIcon, ChevronUpIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CommandOutputProps {
  output: CommandOutputType | null;
  title: string;
}

export default function CommandOutput({ output, title }: CommandOutputProps) {
  const [isOpen, setIsOpen] = useState(true);
  
  if (!output) return null;

  return (
    <Card className="shadow-sm">
      <Collapsible open={isOpen} onOpenChange={setIsOpen} className="w-full">
        <CardHeader className="py-3 flex flex-row items-center justify-between">
          <CardTitle className="text-xl">{title}</CardTitle>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="p-0 h-7 w-7">
              {isOpen ? <ChevronUpIcon className="size-4" /> : <ChevronDownIcon className="size-4" />}
            </Button>
          </CollapsibleTrigger>
        </CardHeader>
        <CollapsibleContent>
          <CardContent className="p-0 max-h-96 overflow-y-auto bg-slate-900">
            {output.error ? (
              <pre className="text-destructive p-4 font-mono whitespace-pre-wrap text-sm">
                {output.error}
              </pre>
            ) : (
              <>
                {output.stdout && (
                  <pre className="text-green-600 p-4 font-mono whitespace-pre-wrap text-sm">
                    {output.stdout}
                  </pre>
                )}
                {output.stderr && (
                  <pre className="text-amber-600 p-4 pt-0 font-mono whitespace-pre-wrap text-sm">
                    {output.stderr}
                  </pre>
                )}
              </>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
} 
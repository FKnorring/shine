import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { DriverGenOptions } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

interface DriverGenFormProps {
  onSubmit: (data: DriverGenOptions) => void;
  isLoading: boolean;
  onRunDriver: () => void;
  hasDriver: boolean;
}

export default function DriverGenForm({ onSubmit, isLoading, onRunDriver, hasDriver }: DriverGenFormProps) {
  const [riseFiles, setRiseFiles] = useState<string[]>([]);
  const form = useForm<DriverGenOptions>({
    defaultValues: {
      dimension: 1048576,
      iterations: 50,
      precision: 256,
      outputFile: 'driver_compare.c',
      floatType: 'normal',
      includeNegatives: false,
      metricsFile: 'metrics.csv'
    }
  });

  // Fetch available RISE files on component mount
  useEffect(() => {
    async function fetchRiseFiles() {
      try {
        const response = await fetch('/api/rise-files');
        const data = await response.json();
        if (data.riseFiles) {
          setRiseFiles(data.riseFiles);
        }
      } catch (error) {
        console.error('Failed to fetch RISE files:', error);
      }
    }

    fetchRiseFiles();
  }, []);

  const multiplyDimension = (factor: number) => {
    const currentValue = form.getValues('dimension') || 0;
    form.setValue('dimension', Math.max(1, Math.round(currentValue * factor)));
  };

  const changeIterations = (delta: number) => {
    const currentValue = form.getValues('iterations') || 0;
    form.setValue('iterations', Math.max(1, currentValue + delta));
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="unoptRiseFile"
            rules={{ required: "This field is required" }}
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Unoptimized RISE File <span className="text-destructive">*</span>
                </FormLabel>
                <Select 
                  disabled={isLoading} 
                  onValueChange={field.onChange} 
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a file" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {riseFiles.map((file) => (
                      <SelectItem key={file} value={file}>
                        {file}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="optRiseFile"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Optimized RISE File (optional)</FormLabel>
                <Select 
                  disabled={isLoading} 
                  onValueChange={field.onChange} 
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a file" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {riseFiles.map((file) => (
                      <SelectItem key={file} value={file}>
                        {file}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Dimension row */}
        <div className="grid grid-cols-1 gap-6">
          <FormField
            control={form.control}
            name="dimension"
            rules={{ 
              required: "This field is required",
              min: { value: 1, message: 'Must be positive' }
            }}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Dimension (Array size)</FormLabel>
                <div className="flex items-center space-x-2">
                  <FormControl>
                    <Input 
                      type="number" 
                      disabled={isLoading} 
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      className="w-full"
                    />
                  </FormControl>
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="icon" 
                    onClick={() => multiplyDimension(0.5)}
                    disabled={isLoading}
                    className="shrink-0 h-9 w-10"
                  >
                    /2
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="icon" 
                    onClick={() => multiplyDimension(2)}
                    disabled={isLoading}
                    className="shrink-0 h-9 w-10"
                  >
                    *2
                  </Button>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Iterations row */}
        <div className="grid grid-cols-1 gap-6">
          <FormField
            control={form.control}
            name="iterations"
            rules={{ 
              required: "This field is required",
              min: { value: 1, message: 'Must be positive' }
            }}
            render={({ field }) => (
              <FormItem>
                <FormLabel>Iterations</FormLabel>
                <div className="flex items-center space-x-2">
                  <FormControl>
                    <Input 
                      type="number" 
                      disabled={isLoading} 
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                      className="w-full"
                    />
                  </FormControl>
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm" 
                    onClick={() => changeIterations(-50)}
                    disabled={isLoading}
                    className="shrink-0 h-9 w-12"
                  >
                    -50
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    size="sm" 
                    onClick={() => changeIterations(50)}
                    disabled={isLoading}
                    className="shrink-0 h-9 w-12"
                  >
                    +50
                  </Button>
                </div>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* MPFR Precision and Output File Name row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="precision"
            rules={{ 
              required: "This field is required",
              min: { value: 2, message: 'Must be at least 2' }
            }}
            render={({ field }) => (
              <FormItem>
                <FormLabel>MPFR Precision (bits)</FormLabel>
                <FormControl>
                  <Input 
                    type="number" 
                    disabled={isLoading} 
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="outputFile"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Output File Name</FormLabel>
                <FormControl>
                  <Input type="text" disabled={isLoading} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Float Type and File Prefix row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="floatType"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Float Type</FormLabel>
                <Select 
                  disabled={isLoading} 
                  onValueChange={field.onChange} 
                  defaultValue={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select float type" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="subnormal">Subnormal</SelectItem>
                    <SelectItem value="mixed">Mixed</SelectItem>
                    <SelectItem value="magnitude">Magnitude</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="prefix"
            render={({ field }) => (
              <FormItem>
                <FormLabel>File Prefix</FormLabel>
                <FormControl>
                  <Input 
                    type="text" 
                    disabled={isLoading} 
                    placeholder="Optional prefix for output files" 
                    {...field} 
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="metricsFile"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Metrics File</FormLabel>
                <FormControl>
                  <Input type="text" disabled={isLoading} {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="includeNegatives"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center space-x-3 space-y-0 rounded-md border p-4">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                    disabled={isLoading}
                  />
                </FormControl>
                <div className="space-y-1 leading-none">
                  <FormLabel>Include negative numbers</FormLabel>
                </div>
              </FormItem>
            )}
          />
        </div>

        <div className="pt-4 flex gap-4">
          <Button type="submit" disabled={isLoading} className="flex-1">
            {isLoading ? 'Running...' : 'Generate & Compile Driver'}
          </Button>
          {hasDriver && (
            <Button 
              type="button" 
              variant="outline" 
              onClick={onRunDriver} 
              disabled={isLoading}
              className="flex-1"
            >
              Run Generated Driver
            </Button>
          )}
        </div>
      </form>
    </Form>
  );
} 
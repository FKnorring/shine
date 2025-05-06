import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { DriverGenOptions, InputConfig, ArrayInputConfig } from '@/types';
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
  FormDescription,
} from "@/components/ui/form";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2 } from "lucide-react";
interface RiseFileInfo {
  dimensions: string[];
  inputs: {
    type: string;
    isArray: boolean;
    dimensions: string[];
    size: string;
  }[];
  outputSize: string;
  isSingleValue: boolean;
}

interface DriverGenFormProps {
  onSubmit: SubmitHandler<DriverGenOptions>;
  isLoading: boolean;
  onRunDriver: () => void;
  hasDriver: boolean;
}

type FormData = DriverGenOptions;

export default function DriverGenForm({ onSubmit, isLoading, onRunDriver, hasDriver }: DriverGenFormProps) {
  const [riseFiles, setRiseFiles] = useState<string[]>([]);
  const [cFilesExist, setCFilesExist] = useState<boolean>(false);
  const [checkingFiles, setCheckingFiles] = useState<boolean>(false);
  const [riseFileInfo, setRiseFileInfo] = useState<RiseFileInfo | null>(null);
  const [parsingFile, setParsingFile] = useState<boolean>(false);
  const [inputConfig, setInputConfig] = useState<InputConfig | null>(null);
  
  const form = useForm<FormData>({
    defaultValues: {
      unoptRiseFile: '',
      dimension: 1048576,
      iterations: 50,
      precision: 256,
      outputFile: 'driver_compare.c',
      floatType: 'normal',
      includeNegatives: false,
      metricsFile: 'metrics.csv',
      skipCompilation: false,
      inputConfig: undefined
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

  // Check if C files exist when a RISE file is selected
  const checkCFilesExist = async (riseFile: string) => {
    if (!riseFile) return;
    
    setCheckingFiles(true);
    try {
      const response = await fetch('/api/check-c-files', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          riseFile,
          prefix: form.getValues('prefix') || ''
        }),
      });
      
      const data = await response.json();
      setCFilesExist(data.exist);
      
      // If files exist, enable skip compilation by default
      if (data.exist) {
        form.setValue('skipCompilation', true);
      }
    } catch (error) {
      console.error('Failed to check C files:', error);
      setCFilesExist(false);
    } finally {
      setCheckingFiles(false);
    }
  };

  // Parse RISE file to get structure information
  const parseRiseFile = async (riseFile: string) => {
    if (!riseFile) return;
    
    setParsingFile(true);
    try {
      const response = await fetch('/api/parse-rise-file', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          riseFile
        }),
      });
      
      const data = await response.json();
      if (data.success) {
        setRiseFileInfo(data.fileInfo);
        
        // Initialize input sizes based on default dimensions, but only for dimensions that exist in the RISE file
        const defaultDimensions: Record<string, number> = {};
        data.fileInfo.dimensions.forEach((dim: string) => {
          defaultDimensions[dim] = 64; // Default size for each dimension
        });
        
        const inputs = data.fileInfo.inputs.map((input: { isArray: boolean; size: string }) => {
          if (!input.isArray) return 0;
          
          const size = input.size.split(' * ').reduce((acc: number, dim: string) => {
            const dimValue = defaultDimensions[dim.trim()];
            return acc * (dimValue || 1);
          }, 1);
          
          return {
            size,
            float_type: 'normal',
            include_negatives: false
          };
        });
        
        updateInputConfig({
          dimensions: defaultDimensions,
          inputs
        });
      } else {
        setRiseFileInfo(null);
      }
    } catch (error) {
      console.error('Failed to parse RISE file:', error);
      setRiseFileInfo(null);
    } finally {
      setParsingFile(false);
    }
  };

  // When unoptimized RISE file changes, check for C files and parse structure
  useEffect(() => {
    const unoptRiseFile = form.watch('unoptRiseFile');
    if (unoptRiseFile) {
      checkCFilesExist(unoptRiseFile);
      parseRiseFile(unoptRiseFile);
    }
  }, [form.watch('unoptRiseFile')]);

  const multiplyDimension = (factor: number) => {
    const currentValue = form.getValues('dimension') || 0;
    form.setValue('dimension', Math.max(1, Math.round(currentValue * factor)));
  };

  const changeIterations = (delta: number) => {
    const currentValue = form.getValues('iterations') || 0;
    form.setValue('iterations', Math.max(1, currentValue + delta));
  };

  const updateInputConfig = (newConfig: Partial<InputConfig>) => {
    setInputConfig(prev => {
      if (!prev) {
        const updated: InputConfig = {
          inputs: [],
          ...newConfig
        };
        form.setValue('inputConfig', updated);
        return updated;
      }
      const updated: InputConfig = {
        ...prev,
        ...newConfig,
        inputs: newConfig.inputs || prev.inputs
      };
      form.setValue('inputConfig', updated);
      return updated;
    });
  };

  const handleDimensionChange = (dimName: string, value: number) => {
    if (!riseFileInfo) return;

    // Only allow changing dimensions that exist in the RISE file
    if (!riseFileInfo.dimensions.includes(dimName)) {
      console.warn(`Dimension ${dimName} not found in RISE file`);
      return;
    }

    const newDimensions = {
      ...inputConfig?.dimensions,
      [dimName]: value
    };

    // Recalculate input sizes based on new dimensions
    const newInputs = riseFileInfo.inputs.map((input, index) => {
      if (!input.isArray) return inputConfig?.inputs[index] || 0;

      const currentInput = inputConfig?.inputs[index];
      if (typeof currentInput === 'number') {
        return currentInput;
      }

      const size = input.size.split(' * ').reduce((acc, dim) => {
        const dimValue = newDimensions[dim.trim()];
        return acc * (dimValue || 1);
      }, 1);

      return {
        ...(currentInput || {}),
        size,
        float_type: (currentInput as ArrayInputConfig)?.float_type || 'normal',
        include_negatives: (currentInput as ArrayInputConfig)?.include_negatives || false
      };
    });

    updateInputConfig({
      dimensions: newDimensions,
      inputs: newInputs
    });
  };

  const handleArrayInputChange = (index: number, field: keyof ArrayInputConfig, value: string | boolean | number | number[]) => {
    if (!riseFileInfo) return;

    const input = riseFileInfo.inputs[index];
    if (!input.isArray) return;

    const newInputs = [...(inputConfig?.inputs || [])];
    while (newInputs.length <= index) {
      newInputs.push({ size: parseInt(input.size) });
    }

    if (typeof newInputs[index] === 'number') {
      newInputs[index] = { size: parseInt(input.size) };
    }

    const currentConfig = newInputs[index] as ArrayInputConfig;
    newInputs[index] = {
      ...currentConfig,
      [field]: value
    };

    // Calculate size based on dimensions if not provided
    if (field === 'size' && value === null && inputConfig?.dimensions) {
      const size = input.size.split(' * ').reduce((acc, dim) => {
        const dimValue = inputConfig?.dimensions?.[dim.trim()];
        return acc * (dimValue || 1);
      }, 1);
      newInputs[index] = {
        ...newInputs[index],
        size
      };
    }

    updateInputConfig({ inputs: newInputs });
  };

  const handleScalarInputChange = (index: number, value: number) => {
    if (!riseFileInfo) return;

    const input = riseFileInfo.inputs[index];
    if (input.isArray) return;

    const newInputs = [...(inputConfig?.inputs || [])];
    newInputs[index] = value;
    updateInputConfig({ inputs: newInputs });
  };

  const handleFormSubmit: SubmitHandler<FormData> = (data) => {
    // Ensure inputConfig is properly structured before submission
    if (inputConfig) {
      data.inputConfig = {
        dimensions: inputConfig.dimensions,
        inputs: inputConfig.inputs.map((input, index) => {
          if (typeof input === 'number') return input;
          return {
            size: input.size,
            float_type: input.float_type || 'normal',
            include_negatives: input.include_negatives || false,
            ...(input.values ? { values: input.values } : {})
          };
        })
      };
    }
    onSubmit(data);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleFormSubmit)} className="space-y-6">
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
                  onValueChange={(value) => {
                    field.onChange(value);
                    checkCFilesExist(value);
                    parseRiseFile(value);
                  }}
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

        {/* Skip compilation checkbox */}
        <FormField
          control={form.control}
          name="skipCompilation"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center space-x-3 space-y-0 rounded-md border p-4">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                  disabled={isLoading || !cFilesExist}
                />
              </FormControl>
              <div className="space-y-1 leading-none flex-1">
                <FormLabel>Skip RISE to C compilation</FormLabel>
                <FormDescription>
                  {checkingFiles 
                    ? <span className="flex items-center">
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> 
                        Checking for existing C files...
                      </span>
                    : cFilesExist 
                      ? "Use existing compiled C files (faster)" 
                      : "Required C files don't exist yet"}
                </FormDescription>
              </div>
            </FormItem>
          )}
        />

        {/* Advanced input configuration if RISE file is parsed */}
        {parsingFile ? (
          <div className="flex items-center text-muted-foreground py-2">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Parsing RISE file...
          </div>
        ) : riseFileInfo ? (
          <Accordion type="single" collapsible className="border rounded-md" defaultChecked={true}>
            <AccordionItem value="advanced-config">
              <AccordionTrigger className="px-4">Advanced Input Configuration</AccordionTrigger>
              <AccordionContent className="px-4 pb-4">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-sm font-medium mb-2">Dimensions:</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {riseFileInfo.dimensions.map((dim, index) => (
                        <FormItem key={index} className="flex flex-col">
                          <FormLabel>{dim}</FormLabel>
                          <div className="flex items-center space-x-2">
                            <Input 
                              type="number" 
                              min="1"
                              placeholder="Dimension size" 
                              disabled={isLoading}
                              value={inputConfig?.dimensions?.[dim] || form.getValues('dimension')}
                              onChange={(e) => handleDimensionChange(dim, parseInt(e.target.value))}
                            />
                            <Button 
                              type="button" 
                              variant="outline" 
                              size="icon" 
                              onClick={() => handleDimensionChange(dim, Math.max(1, Math.round((inputConfig?.dimensions?.[dim] || form.getValues('dimension')) * 0.5)))}
                              disabled={isLoading}
                              className="shrink-0 h-9 w-10"
                            >
                              /2
                            </Button>
                            <Button 
                              type="button" 
                              variant="outline" 
                              size="icon" 
                              onClick={() => handleDimensionChange(dim, (inputConfig?.dimensions?.[dim] || form.getValues('dimension')) * 2)}
                              disabled={isLoading}
                              className="shrink-0 h-9 w-10"
                            >
                              *2
                            </Button>
                          </div>
                        </FormItem>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Input Arrays:</h3>
                    <div className="space-y-4">
                      {riseFileInfo.inputs.map((input, index) => (
                        <div key={index} className="border rounded-md p-3">
                          <h4 className="text-sm font-semibold mb-2">Input {index + 1} {input.isArray ? `(Array - ${input.size})` : '(Scalar)'}</h4>
                          
                          {input.isArray ? (
                            <div className="space-y-3">
                              <div className="flex gap-2">
                                <Select 
                                  disabled={isLoading} 
                                  value={(inputConfig?.inputs[index] as ArrayInputConfig)?.float_type || 'normal'}
                                  onValueChange={(value) => handleArrayInputChange(index, 'float_type', value)}
                                >
                                  <SelectTrigger className="w-full">
                                    <SelectValue placeholder="Float type" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="normal">Normal</SelectItem>
                                    <SelectItem value="subnormal">Subnormal</SelectItem>
                                    <SelectItem value="mixed">Mixed</SelectItem>
                                    <SelectItem value="magnitude">Magnitude</SelectItem>
                                  </SelectContent>
                                </Select>
                                
                                <div className="flex items-center space-x-2">
                                  <Checkbox 
                                    id={`neg-input-${index}`} 
                                    disabled={isLoading} 
                                    checked={(inputConfig?.inputs[index] as ArrayInputConfig)?.include_negatives || false}
                                    onCheckedChange={(checked) => handleArrayInputChange(index, 'include_negatives', checked)}
                                  />
                                  <label htmlFor={`neg-input-${index}`} className="text-sm">Include negatives</label>
                                </div>
                              </div>

                              <div>
                                <FormLabel className="text-sm">Custom Values (comma-separated)</FormLabel>
                                <Input
                                  type="text"
                                  placeholder="1.0, 2.0, 3.0"
                                  disabled={isLoading}
                                  value={(inputConfig?.inputs[index] as ArrayInputConfig)?.values?.join(', ') || ''}
                                  onChange={(e) => {
                                    const values = e.target.value
                                      .split(',')
                                      .map(v => parseFloat(v.trim()))
                                      .filter(v => !isNaN(v));
                                    handleArrayInputChange(index, 'values', values);
                                  }}
                                />
                              </div>
                            </div>
                          ) : (
                            <div>
                              <Input 
                                type="number" 
                                placeholder="Custom value" 
                                disabled={isLoading}
                                value={typeof inputConfig?.inputs[index] === 'number' ? inputConfig.inputs[index] : ''}
                                onChange={(e) => handleScalarInputChange(index, parseFloat(e.target.value))}
                              />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        ) : null}

        {/* Standard configuration options below */}
        {/* Dimension row */}
        <div className="grid grid-cols-1 gap-6 hidden">
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
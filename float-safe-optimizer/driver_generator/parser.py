import re
from typing import Dict, List, Any


class ParsingError(Exception):
    pass


def parse_function_arguments(args_str: str) -> List[Dict[str, str]]:
    args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
    parsed_args = []

    for arg in args:
        tokens = arg.split()
        if len(tokens) < 2:
            raise ParsingError(f"Could not parse argument: {arg}")
        param_name = tokens[-1]
        param_type = " ".join(tokens[:-1])
        parsed_args.append({"name": param_name, "type": param_type})

    return parsed_args


def categorize_arguments(parsed_args: List[Dict[str, str]]) -> Dict[str, Any]:
    output = parsed_args[0]
    dimensions = []
    inputs = []

    for arg in parsed_args[1:]:
        if "*" in arg["type"]:
            inputs.append(arg)
        else:
            dimensions.append(arg)

    return {"output": output, "dimensions": dimensions, "inputs": inputs}


def parse_c_function(c_code: str) -> Dict[str, Any]:
    signature_pattern = r"void\s+(\w+)\s*\(([^)]*)\)"
    match = re.search(signature_pattern, c_code)
    if not match:
        raise ParsingError("Function signature not found in the C code.")

    func_name = match.group(1)
    args_str = match.group(2)

    parsed_args = parse_function_arguments(args_str)
    categorized_args = categorize_arguments(parsed_args)
    
    # Store the original C code for function type detection
    categorized_args["code"] = c_code
    
    # Check if this is a single-value output function
    is_single_value = False
    
    # Look for patterns that suggest a single value output
    # Pattern 1: "output[0] = ..." is the only assignment to output
    output_assignments = re.findall(r"output\[\d+\]\s*=", c_code)
    if len(output_assignments) == 1 and "output[0]" in output_assignments[0]:
        is_single_value = True
    
    # Pattern 2: Contains a final reduction that assigns to output[0]
    if re.search(r"reduceSeq.*output\[0\]", c_code, re.DOTALL):
        is_single_value = True
        
    categorized_args["is_single_value"] = is_single_value

    return {"name": func_name, **categorized_args}


def parse_rise_array_sizes(rise_code: str) -> Dict[str, Any]:
    """Parse the Rise function type to determine array sizes and dimension mapping."""
    # Extract the type signature between the => fun( and ) parts
    type_pattern = r"depFun\(\(([^)]+)\)\s*=>\s*fun\(\s*([^)]+)\s*\)"
    match = re.search(type_pattern, rise_code, re.DOTALL)
    if not match:
        raise ParsingError("Could not find Rise function type signature")

    # Parse dimension declarations
    dim_decls = match.group(1)
    dims = [d.split(":")[0].strip() for d in dim_decls.split(",")]

    type_sig = match.group(2)
    print("Type signature:", type_sig)  # Debug print

    # Split into input and output types
    types = [t.strip() for t in type_sig.split("->:")]
    print("Types:", types)  # Debug print

    # Extract all array types (input and output)
    array_pattern = r"\((\w+)`\.`(\w+)`\.`f32\)"
    array_types = []
    for t in types:
        matches = re.findall(array_pattern, t)
        if matches:
            array_types.extend(matches)
    print("Found array types:", array_types)  # Debug print

    # Parse array dimensions for each type
    sizes = {
        "inputs": [],
        "output": None,
        "dimensions": dims,  # Store the dimension names
    }

    # The last type is the output type
    if array_types:
        sizes["output"] = f"{array_types[-1][0]} * {array_types[-1][1]}"
        # All but the last type are input types
        for dim1, dim2 in array_types[:-1]:
            sizes["inputs"].append(f"{dim1} * {dim2}")

    print("Parsed Rise sizes:", sizes)  # Debug print
    return sizes

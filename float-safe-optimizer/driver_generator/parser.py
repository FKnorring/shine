import re
from typing import Dict, List, Any, Tuple


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


def extract_dimensions(rise_code: str) -> List[str]:
    """Extract dimension declarations from the depFun part."""
    dim_pattern = r"depFun\(\(([^)]+)\)"
    dim_match = re.search(dim_pattern, rise_code)
    if not dim_match:
        raise ParsingError("Could not find dimension declarations")
    
    dim_decls = dim_match.group(1)
    dims = [d.split(":")[0].strip() for d in dim_decls.split(",")]
    print("Found dimensions:", dims)
    return dims


def extract_inputs_and_output(rise_code: str) -> Tuple[List[str], str]:
    """Extract input and output types from the function signature.
    
    Returns:
        Tuple[List[str], str]: A tuple containing (list of input types, output type)
    """
    # Find the start of the function signature
    fun_start = rise_code.find("fun(")
    if fun_start == -1:
        raise ParsingError("Could not find function signature")
    
    # Find the matching closing parenthesis
    start = fun_start + 4  # Skip "fun("
    count = 1
    pos = start
    
    while count > 0 and pos < len(rise_code):
        if rise_code[pos] == '(':
            count += 1
        elif rise_code[pos] == ')':
            count -= 1
        pos += 1
    
    if count != 0:
        raise ParsingError("Unmatched parentheses in function signature")
    
    # Extract the signature
    signature = rise_code[start:pos-1]  # -1 to exclude the closing parenthesis
    print("Found signature:", signature)
    
    # Split the signature by ->: to separate inputs and output
    parts = [p.strip() for p in signature.split("->:")]
    if len(parts) < 2:
        raise ParsingError("Invalid function signature format")
    
    inputs = parts[:-1]
    output = parts[-1]
    
    print("Inputs:", inputs)
    print("Output:", output)
    return inputs, output


def parse_type(type_str: str) -> Dict[str, Any]:
    """Parse a single type string into its components.
    
    Args:
        type_str: The type string to parse (e.g. "(n`.`f32)" or "f32")
    
    Returns:
        Dict containing:
            - is_array: bool indicating if this is an array type
            - dimensions: List[str] of dimension names (empty for scalar)
            - size: str representing the size (e.g. "n" or "n * m")
    """
    # Check if this is a scalar type
    if type_str.strip() == "f32":
        return {
            "is_array": False,
            "dimensions": [],
            "size": "1"
        }
    
    # Parse array type
    array_pattern = r"\((\w+)`\.`f32\)|\((\w+)`\.`(\w+)`\.`f32\)"
    match = re.search(array_pattern, type_str)
    if not match:
        raise ParsingError(f"Could not parse type: {type_str}")
    
    # Check if this is a 1D or 2D array
    if match.group(1) and not match.group(2):  # 1D array
        dim = match.group(1)
        return {
            "is_array": True,
            "dimensions": [dim],
            "size": dim
        }
    else:  # 2D array
        dim1, dim2 = match.group(2), match.group(3)
        return {
            "is_array": True,
            "dimensions": [dim1, dim2],
            "size": f"{dim1} * {dim2}"
        }


def parse_rise_array_sizes(rise_code: str) -> Dict[str, Any]:
    """Parse the Rise function type to determine array sizes and dimension mapping."""
    # Step 1: Extract dimensions
    dimensions = extract_dimensions(rise_code)
    
    # Step 2: Extract inputs and output
    inputs, output = extract_inputs_and_output(rise_code)
    
    # Step 3: Parse each type
    parsed_inputs = [parse_type(inp) for inp in inputs]
    parsed_output = parse_type(output)
    
    # Build the final result
    sizes = {
        "inputs": [inp["size"] for inp in parsed_inputs],
        "output": parsed_output["size"],
        "dimensions": dimensions,
        "is_single_value": not parsed_output["is_array"]
    }
    
    print("Parsed Rise sizes:", sizes)
    return sizes

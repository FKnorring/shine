import os
import subprocess
from typing import Tuple
import re
from utils import ensure_out_dir

def compile_rise_to_c(unopt_rise_file_path: str, opt_rise_file_path: str = None, prefix: str = "") -> Tuple[str, str, str]:
    """
    Compile RISE programs to three C files using the compile.sh script:
    - Unoptimized without MPFR
    - Unoptimized with MPFR
    - Optimized without MPFR
    
    Args:
        unopt_rise_file_path: Path to the unoptimized RISE source file
        opt_rise_file_path: Path to the optimized RISE source file (optional)
        prefix: Optional prefix to add to output files
    
    Returns:
        Tuple of paths to the generated C files: (unopt, unopt_mpfr, opt)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    compile_script = os.path.join(script_dir, "compile.sh")
    out_dir = ensure_out_dir()
    base_name = os.path.basename(unopt_rise_file_path).replace(".rise", "")
    
    # If prefix is provided, use it for the output files
    if prefix:
        prefixed_base_name = f"{prefix}{base_name}"
    else:
        prefixed_base_name = base_name

    try:
        # Make sure the compile script is executable
        os.chmod(compile_script, 0o755)

        # Run the compile script with the original base name
        cmd = [compile_script, unopt_rise_file_path]
        if opt_rise_file_path:
            cmd.append(opt_rise_file_path)
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        print(result.stdout)
        
        # Build the paths to the expected output files
        unopt_file = os.path.join(out_dir, f"{base_name}_unopt.c")
        unopt_mpfr_file = os.path.join(out_dir, f"{base_name}_mpfr_unopt.c")
        opt_file = os.path.join(out_dir, f"{base_name}.c")
        
        # Verify files exist
        for file_path in [unopt_file, unopt_mpfr_file, opt_file]:
            if not os.path.exists(file_path):
                raise RuntimeError(f"C file was not generated at expected path: {file_path}")
        
        # If prefix is provided, rename the files
        if prefix:
            prefixed_unopt_file = os.path.join(out_dir, f"{prefixed_base_name}_unopt.c")
            prefixed_unopt_mpfr_file = os.path.join(out_dir, f"{prefixed_base_name}_mpfr_unopt.c")
            prefixed_opt_file = os.path.join(out_dir, f"{prefixed_base_name}.c")
            
            # Rename the files
            os.rename(unopt_file, prefixed_unopt_file)
            os.rename(unopt_mpfr_file, prefixed_unopt_mpfr_file)
            os.rename(opt_file, prefixed_opt_file)
            
            return prefixed_unopt_file, prefixed_unopt_mpfr_file, prefixed_opt_file
        else:
            return unopt_file, unopt_mpfr_file, opt_file

    except subprocess.CalledProcessError as e:
        print("Error during RISE compilation:")
        print(e.stderr)
        raise
    except Exception as e:
        print(f"Error during RISE compilation: {str(e)}")
        raise
    
def edit_function_names(unopt_file: str, mpfr_file: str, opt_file: str) -> None:
    """
    Edit the function names in the generated C files:
    - Unoptimized: foo -> foo_unopt
    - MPFR: foo -> foo_mpfr 
    - Optimized: foo -> foo_opt
    
    Args:
        unopt_file: Path to unoptimized C file
        mpfr_file: Path to MPFR C file
        opt_file: Path to optimized C file
    """
    # Get the base name from the file names
    base_name = os.path.basename(unopt_file).replace("_unopt.c", "")
    
    # Rename unoptimized function
    try:
        with open(unopt_file, 'r') as f:
            unopt_content = f.read()
        
        # Find function declaration pattern
        unopt_match = re.search(r'void\s+(\w+)\s*\(', unopt_content)
        if not unopt_match:
            raise RuntimeError(f"Could not find function name in {unopt_file}")
        
        unopt_function_name = unopt_match.group(1)
        
        # Replace with foo_unopt
        if unopt_function_name != f"{base_name}_unopt":
            new_unopt_content = unopt_content.replace(f"void {unopt_function_name}(", f"void {base_name}_unopt(")
            with open(unopt_file, 'w') as f:
                f.write(new_unopt_content)
            print(f"Renamed function in {unopt_file} from {unopt_function_name} to {base_name}_unopt")
    except Exception as e:
        print(f"Error editing unoptimized function name: {e}")
        raise
    
    # Rename MPFR function
    try:
        with open(mpfr_file, 'r') as f:
            mpfr_content = f.read()
        
        # Find function declaration pattern
        mpfr_match = re.search(r'void\s+(\w+)\s*\(', mpfr_content)
        if not mpfr_match:
            raise RuntimeError(f"Could not find function name in {mpfr_file}")
        
        mpfr_function_name = mpfr_match.group(1)
        
        # Replace with foo_mpfr
        if mpfr_function_name != f"{base_name}_mpfr":
            new_mpfr_content = mpfr_content.replace(f"void {mpfr_function_name}(", f"void {base_name}_mpfr(")
            with open(mpfr_file, 'w') as f:
                f.write(new_mpfr_content)
            print(f"Renamed function in {mpfr_file} from {mpfr_function_name} to {base_name}_mpfr")
    except Exception as e:
        print(f"Error editing MPFR function name: {e}")
        raise
    
    # Rename optimized function
    try:
        with open(opt_file, 'r') as f:
            opt_content = f.read()
        
        # Find optimized function name
        opt_match = re.search(r'void\s+(\w+)\s*\(', opt_content)
        if not opt_match:
            raise RuntimeError(f"Could not find function name in {opt_file}")
        
        opt_function_name = opt_match.group(1)
        
        # Replace with foo_opt
        if opt_function_name != f"{base_name}_opt":
            new_opt_content = opt_content.replace(f"void {opt_function_name}(", f"void {base_name}_opt(")
            with open(opt_file, 'w') as f:
                f.write(new_opt_content)
            print(f"Renamed function in {opt_file} from {opt_function_name} to {base_name}_opt")
    except Exception as e:
        print(f"Error editing optimized function name: {e}")
        raise
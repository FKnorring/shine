import os

def ensure_out_dir():
    """Create the out directory if it doesn't exist."""
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    return out_dir
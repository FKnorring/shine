
def sign_code(include_negatives: bool) -> str:
    return """
    // Randomly negate values
    if (rand() % 2) {
      val = -val;
    }""" if include_negatives else ""
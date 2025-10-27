def format_data(data):
    # Function to format data for consistency
    return [str(item).strip() for item in data]

def log_message(message):
    # Function to log messages to the console or a file
    print(f"[LOG] {message}")

def extract_keywords(text):
    # Function to extract keywords from a given text
    # Placeholder for actual keyword extraction logic
    return text.split()[:5]  # Example: return first 5 words as keywords

def validate_input(input_data):
    # Function to validate input data
    if not input_data:
        log_message("Input data is empty.")
        return False
    return True
# -------------------------------------------------------------------
# config.py
# -------------------------------------------------------------------

# Default prompt in English
DEFAULT_PROMPT_EN = "Summarize the text concisely and directly without prefatory phrases. Focus on presenting its key points and main ideas, ensuring that essential details are accurately conveyed in a straightforward manner."

# Default values for chunk size and chunk overlap
DEFAULT_CHUNK_SIZE = 10000
DEFAULT_CHUNK_OVERLAP = 3000

# Standard directory for saving summaries
SUMMARY_SAVE_PATH = "/path/to/summaries"

# Supported file formats for saving and loading documents
SUPPORTED_FILE_FORMATS = [".pdf", ".docx", ".rtf", ".txt"]

# Supported languages for translation
SUPPORTED_LANGUAGES = ["en", "nl", "fr", "es"]  

# Default language for translation (if applicable)
DEFAULT_TRANSLATION_LANGUAGE = "en"

# Standard directory for API key
API_KEY_PATH = r'C:\\api_key.txt'

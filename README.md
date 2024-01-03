# Docsum

Docsum is an application designed to automate the summarization of documents. It supports various file formats such as PDF, DOCX, RTF, and TXT, leveraging Natural Language Processing (NLP) and machine learning techniques. The project is structured modularly and incorporates multithreading and asynchronous programming elements.

## Features

- **Multiple File Formats**: Docsum supports PDF, DOCX, RTF, and TXT files.
- **Advanced Text Processing**: Utilizing NLP and machine learning techniques for summarization.
- **Language Detection and Translation**: Automatically detects and translates content based on the document's language.
- **Summarization**: Employs clustering techniques and OpenAI's GPT-3.5 model for generating concise summaries.
- **GUI**: Features a Tkinter-based graphical user interface.
- **Progress Tracking**: Provides visual progress indicators during the summarization process.

### Main Components

- `main.py`: The primary entry point of the application.
- `summarization.py`: Responsible for handling the summarization logic.
- `file_handler.py`: Manages file operations, including reading and writing files.
- `language_processing.py`: Handles various natural language processing tasks.
- `config.py`: Contains configuration settings for the application.

## main.py

### Overview

- main.py features a user-friendly GUI for document selection, prompt customization, and summary saving.
- It seamlessly integrates multiple modules (`file_handler`, `language_processing`, `summarization`) for different functionalities.
- Threading is employed to run the summarization process concurrently without blocking the GUI.
- The application is capable of handling various file types and languages, with a primary focus on English and Dutch.

1. **Imports and Global Variables**:
   - Imports modules such as `file_handler`, `language_processing`, `summarization`, and standard libraries for GUI and threading.
   - Defines global variables for file paths, progress indicators, and configuration settings.

2. **Logging Configuration**:
   - Sets up basic logging with a specified format.

3. **Configuration Usage**:
   - Retrieves default settings from the `config` module.

4. **Helper Functions**:
   - `get_api_key`: Retrieves an API key from a file.
   - `select_file`: Opens a file dialog for selecting a document.
   - `get_summary_prompt`: Generates a prompt for summarization based on the document's language.

5. **Summarization Functions**:
   - `start_summarization_thread`: Starts a new thread for the summarization process.
   - `start_summarization`: Handles the summarization logic, including loading the document, chunking, and calling the summarization module.
   - `update_progress_bar`: Updates the GUI's progress bar.
   - `save_summary_file`: Saves the generated summary to a file.

6. **GUI Code Block (`main_gui`)**:
   - Sets up the GUI using Tkinter, including layout, styles, and interactive elements like buttons and text areas.
   - Implements functionality for file selection and starting the summarization process.

7. **Script Execution Block**:
   - Checks if the script is the main module and runs the GUI function.

## summarization.py

### Overview

- This module is well-structured and modular, with clear separation of functionalities.
- It leverages advanced techniques like text embeddings, clustering, and large language models (LLMs) for summarization.
- Parallel processing is used for efficiency, especially important for handling large documents.
- A progress callback is used for real-time progress bar updates.

1. **Imports and Dependencies**:
   - Imports necessary libraries and modules, including NLP libraries and other project-specific modules.

2. **Summarization Functions**:
   - Contains the core logic for text summarization.
   - Includes functions for breaking down text into manageable chunks, applying summarization algorithms, and compiling the final summary.

2.1. **Text Splitting (`split_text`)**:
   - Splits the input text into smaller chunks using `RecursiveCharacterTextSplitter`.
   - Handles different separators like newlines and tabs.
   - Configurable chunk size and overlap, using values from `config.py`.

2.2. **Text Embedding (`embed_text`)**:
   - Converts text chunks into embeddings using `OpenAIEmbeddings`.
   - Embeddings are likely used for clustering and summarization.

2.3. **Optimal Clusters Determination (`determine_optimal_clusters`)**:
   - Utilizes KMeans clustering and the `KneeLocator` to find the optimal number of clusters in the embeddings.
   - This step is crucial for efficient summarization.

2.4. **Clustering Embeddings (`cluster_embeddings`)**:
   - Clusters the embeddings and identifies key chunks for summarization.

2.5. **Chunk Processing (`process_chunk`)**:
   - Summarizes individual text chunks using a loaded summarization chain.
   - Logs the first 100 characters of each processed chunk.

2.6. **Generating Chunk Summaries (`generate_chunk_summaries`)**:
   - Summarizes selected text chunks in parallel using `ThreadPoolExecutor`.
   - Utilizes `ChatOpenAI` for summarization, with a custom prompt template.
   - Logs summaries and handles errors during summarization.

2.7. **Executing Summary (`execute_summary`)**:
   - Orchestrates the entire summarization process, including text splitting, embedding, clustering, and summarizing.
   - Optionally updates a progress callback.
   - Concatenates and logs the final summary.

3. **Error Handling and Logging**:
   - Robust error handling to manage exceptions during the summarization process.
   - Logging for tracking the process and debugging.

4. **Integration with Other Modules**:
   - Interfaces with `language_processing.py` for language-specific processing.
   - Uses `file_handler.py` for reading input text and writing the summary output.


## file_handler.py

### Overview

- This module abstracts file operations effectively, simplifying the loading and saving of documents in various formats.
- It relies on external libraries such as PyMuPDF, python-docx, striprtf, and ReportLab to handle specific file formats.
- Robust error handling and logging are implemented for debugging and user feedback.

1. **`is_valid_file_path(path)`**:
   - Validates the provided file path using a regular expression pattern.
   - Checks if the file exists at the specified path.
   - Returns `True` if the path is valid and the file exists, and `False` otherwise.

2. **`load_document(file_path)`**:
   - Loads a document from the given file path.
   - Supports various file formats: PDF (using PyMuPDF), DOCX (using python-docx), RTF (using striprtf), and plain text.
   - Extracts and returns the text content of the document.
   - Raises a `ValueError` if the file path is invalid or the file extension is unsupported.

3. **`save_summary(summary, file_path)`**:
   - Saves the summary text to a file.
   - Handles different file formats for saving: TXT, DOCX (using python-docx), and PDF (using ReportLab).
   - Logs the first 500 characters of the summary before saving.
   - Raises a `ValueError` for unsupported file formats and a `RuntimeError` for any errors during the file saving process.

## language_processing.py

### Overview

- This module effectively integrates language detection and translation functionalities, enhancing the application's ability to process documents in different languages.
- It relies on external libraries (`langdetect` and `translate`) for core functionalities.
- The module is designed to gracefully handle failures in language detection and translation, ensuring the application's robustness.

1. **`detect_language(text)`**:
   - Detects the language of the provided text using the `langdetect` library.
   - Returns the detected language code (e.g., 'en' for English).
   - In case of detection failure, it returns 'unknown'.
   - Includes error handling and logging for any issues during language detection.

2. **`translate_prompt(prompt_text, target_language)`**:
   - Translates the given prompt text to the specified target language.
   - Utilizes the `translate` library for translation.
   - Currently supports translation to languages specified in `config.SUPPORTED_LANGUAGES`, primarily Dutch ('nl') and English ('en').
   - Returns the translated text or the original text if translation fails or the target language is not supported.
   - Includes error handling and logging for translation issues.

## config.py

### Overview

- `config.py` centralizes essential settings, making it convenient to manage and modify configuration values without altering the core application code.
- It provides insights into the application's language support, supported file formats, and summarization preferences.

1. **Default Prompt in English (`DEFAULT_PROMPT_EN`)**:
   - A predefined prompt for summarization tasks, particularly for English texts. It instructs the summarization process to prioritize conciseness, directness, and emphasis on key points and main ideas.

2. **Chunk Size and Overlap (`DEFAULT_CHUNK_SIZE`, `DEFAULT_CHUNK_OVERLAP`)**:
   - Default values for chunk size and overlap, likely used in text processing and summarization steps. These settings determine how the text is divided and processed in parts.

3. **Summary Save Path (`SUMMARY_SAVE_PATH`)**:
   - Specifies the default directory path for saving summaries. This path serves as a placeholder and should be configured during setup.

4. **Supported File Formats (`SUPPORTED_FILE_FORMATS`)**:
   - Lists the file formats that the application can handle, including PDF, DOCX, RTF, and TXT. This is crucial for the file handling module to correctly process different document types.

5. **Supported Languages for Translation (`SUPPORTED_LANGUAGES`)**:
   - Defines the languages supported by the application for translation, including English, Dutch, French, and Spanish. This is important for the language processing module to handle multilingual documents.

6. **Default Translation Language (`DEFAULT_TRANSLATION_LANGUAGE`)**:
   - Sets a default translation language, which is English in this case. This setting may be used when the document's language is unsupported or undetectable.

7. **API Key Path (`API_KEY_PATH`)**:
   - Provides the directory path for storing the API key, essential for accessing external services like translation and summarization APIs.


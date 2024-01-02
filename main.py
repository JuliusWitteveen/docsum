import file_handler
import language_processing
import summarization
import logging
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# Global variables
selected_file_path = None
progress = None
custom_prompt_area = None
chunk_size = None
chunk_overlap = None

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set default prompt in English and default values for chunk size and overlap
default_prompt_en = """Summarize the text concisely and directly without prefatory phrases. Focus on presenting its key points and main ideas, ensuring that essential details are accurately conveyed in a straightforward manner."""
DEFAULT_CHUNK_SIZE = 10000
DEFAULT_CHUNK_OVERLAP = 3000

# Helper Functions
def get_api_key(file_path=r'C:\\api_key.txt'):
    logging.info("Retrieving API key.")
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error(f"API key file not found at {file_path}")
        return None
    except IOError as e:
        logging.error(f"Error reading the API key file: {e}")
        return None

def select_file():
    file_path = filedialog.askopenfilename(
        title="Select a Document",
        filetypes=[("PDF Files", "*.pdf"), ("Word Documents", "*.docx"), ("RTF Files", "*.rtf"), ("Text Files", "*.txt")])
    return file_path

def get_summary_prompt(file_path, api_key):
    text = file_handler.load_document(file_path)
    if not text:
        return None

    language = language_processing.detect_language(text)
    if language == "nl":
        translated_prompt = language_processing.translate_prompt(default_prompt_en, language)
        return translated_prompt
    elif language == "en":
        return default_prompt_en

    return default_prompt_en

# Background Summarization Function
def start_summarization_thread(root):
    summarization_thread = threading.Thread(target=start_summarization, args=(root,))
    summarization_thread.start()

def start_summarization(root):
    global selected_file_path, custom_prompt_area, chunk_size, chunk_overlap
    api_key = get_api_key()
    if api_key and selected_file_path:
        try:
            custom_prompt_text = get_summary_prompt(selected_file_path, api_key)
            update_progress_bar(10, root)

            text = file_handler.load_document(selected_file_path)
            update_progress_bar(20, root)

            user_chunk_size = int(chunk_size.get() or DEFAULT_CHUNK_SIZE)
            user_chunk_overlap = int(chunk_overlap.get() or DEFAULT_CHUNK_OVERLAP)

            summary = summarization.generate_summary(
                text, 
                api_key, 
                custom_prompt_text,
                user_chunk_size,
                user_chunk_overlap,
                progress_update_callback=lambda value: update_progress_bar(value, root)
            )

            if summary:
                filename_without_ext = os.path.splitext(os.path.basename(selected_file_path))[0]
                root.after(0, lambda: save_summary_file(summary, filename_without_ext))
                update_progress_bar(100, root)

        except Exception as e:
            logging.error(f"Error in summarization process: {e}")
            messagebox.showerror("Summarization Error", f"An error occurred during summarization: {e}")
            update_progress_bar(0, root)
    else:
        messagebox.showinfo("API Key Missing", "API key is missing or invalid.")
        update_progress_bar(0, root)

def update_progress_bar(value, root):
    def set_progress(value):
        progress['value'] = value
    root.after(0, lambda: set_progress(value))

def save_summary_file(summary, filename_without_ext):
    default_summary_filename = f"{filename_without_ext}_sum"
    file_path = filedialog.asksaveasfilename(
        initialfile=default_summary_filename,
        filetypes=[("Text Files", "*.txt"), ("Word Documents", "*.docx"), ("PDF Files", "*.pdf")],
        defaultextension=".txt"
    )
    if file_path:
        # Log the first 500 characters of the summary being saved
        logging.info(f"Saving Summary (first 500 characters): {summary[:500]}...")

        file_handler.save_summary(summary, file_path)
        messagebox.showinfo("Success", f"Summary saved successfully to {file_path}")
    else:
        messagebox.showerror("Error", "No file path selected.")


# GUI Code Block
def main_gui():
    global selected_file_path, progress, custom_prompt_area, chunk_size, chunk_overlap

    logging.info("Initializing GUI for the Document Summarizer.")
    root = tk.Tk()
    root.title("Document Summarizer")
    root.state('zoomed')  # Full-screen window

    # Define colors, fonts, and styles for the GUI
    primary_color = "#2E3F4F"
    secondary_color = "#4F5D75"
    text_color = "#E0FBFC"
    button_color = "#3F88C5"
    larger_font = ('Helvetica', 12)
    button_font = ('Helvetica', 10, 'bold')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('W.TButton', font=button_font, background=button_color, foreground=text_color)
    style.map('W.TButton', background=[('active', secondary_color)], foreground=[('active', text_color)])

    # Configure layout of the main window
    root.configure(bg=primary_color)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)

    # Progress bar to indicate summarization progress
    progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress.grid(row=0, column=0, pady=10, padx=10, sticky='ew')

    # Customizable prompt box for user input
    prompt_label = tk.Label(root, text="Customize the summarization prompt:", fg=text_color, bg=primary_color, font=larger_font)
    prompt_label.grid(row=1, column=0, pady=(10, 0), sticky='nw')
    custom_prompt_area = tk.Text(root, height=15, width=80, wrap="word", bd=2, font=larger_font)
    custom_prompt_area.grid(row=2, column=0, pady=10, padx=10, sticky='nsew')

    # Chunk Size and Overlap Input Fields
    chunk_size = tk.StringVar(value=str(DEFAULT_CHUNK_SIZE))
    chunk_overlap = tk.StringVar(value=str(DEFAULT_CHUNK_OVERLAP))

    chunk_size_label = tk.Label(root, text="Chunk Size:", fg=text_color, bg=primary_color, font=larger_font)
    chunk_size_label.grid(row=3, column=0, pady=(10, 0), sticky='nw')
    chunk_size_entry = tk.Entry(root, textvariable=chunk_size, bd=2, font=larger_font)
    chunk_size_entry.grid(row=3, column=1, pady=10, padx=10, sticky='nsew')

    chunk_overlap_label = tk.Label(root, text="Chunk Overlap:", fg=text_color, bg=primary_color, font=larger_font)
    chunk_overlap_label.grid(row=4, column=0, pady=(10, 0), sticky='nw')
    chunk_overlap_entry = tk.Entry(root, textvariable=chunk_overlap, bd=2, font=larger_font)
    chunk_overlap_entry.grid(row=4, column=1, pady=10, padx=10, sticky='nsew')

    # Function for file selection
    def file_select():
        global selected_file_path
        selected_file_path = select_file()
        if selected_file_path:
            api_key = get_api_key()
            if api_key:
                try:
                    text = file_handler.load_document(selected_file_path)
                    if text:
                        language = language_processing.detect_language(text)
                        custom_prompt = default_prompt_en  # Use the default English prompt
                        if language == "nl":
                            dutch_prompt = language_processing.translate_prompt(default_prompt_en, "nl")
                            custom_prompt = dutch_prompt if dutch_prompt else default_prompt_en

                        custom_prompt_area.delete("1.0", tk.END)
                        custom_prompt_area.insert(tk.END, custom_prompt)
                        progress['value'] = 0
                        summarize_button['state'] = 'normal'
                    else:
                        messagebox.showerror("Error", "Failed to load document.")
                        summarize_button['state'] = 'disabled'
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load document: {e}")
                    summarize_button['state'] = 'disabled'
            else:
                summarize_button['state'] = 'disabled'
        else:
            summarize_button['state'] = 'disabled'

    # Select file button
    select_button = ttk.Button(root, text="Select Document", command=file_select, style='W.TButton')
    select_button.grid(row=5, column=0, pady=20, padx=10, sticky='ew')

    # Start summarization button
    summarize_button = ttk.Button(root, text="Start Summarization", command=lambda: start_summarization_thread(root), style='W.TButton')
    summarize_button.grid(row=6, column=0, pady=20, padx=10, sticky='ew')

    root.mainloop()  # This line starts the Tkinter event loop

# Script Execution Block
if __name__ == '__main__':
    logging.info("Starting the Document Summarizer application.")
    main_gui()

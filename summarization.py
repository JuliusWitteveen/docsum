import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from sklearn.cluster import KMeans
import numpy as np
from kneed import KneeLocator
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define default values for chunk size and overlap
DEFAULT_CHUNK_SIZE = 10000
DEFAULT_CHUNK_OVERLAP = 3000

def split_text(text, chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP):
    try:
        text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "\t"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.create_documents([text])
        return docs
    except Exception as e:
        logging.error(f"Error during text splitting: {e}")
        raise

def embed_text(docs, openai_api_key):
    try:
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectors = embeddings.embed_documents([x.page_content for x in docs])
        return vectors
    except Exception as e:
        logging.error(f"Error during text embedding: {e}")
        raise

def determine_optimal_clusters(vectors, max_clusters=100):
    try:
        num_samples = len(vectors)
        if num_samples == 0:
            raise ValueError("No data points available for clustering.")

        max_clusters = min(num_samples, max_clusters)
        sse = []
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(vectors)
            sse.append(kmeans.inertia_)

        elbow_point = KneeLocator(range(1, len(sse) + 1), sse, curve='convex', direction='decreasing').elbow
        return elbow_point or 1
    except Exception as e:
        logging.error(f"Error determining optimal clusters: {e}")
        raise

def cluster_embeddings(vectors, num_clusters):
    try:
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10).fit(vectors)
        closest_indices = [np.argmin(np.linalg.norm(vectors - center, axis=1)) for center in kmeans.cluster_centers_]
        return sorted(closest_indices)
    except Exception as e:
        logging.error(f"Error during clustering embeddings: {e}")
        raise

def process_chunk(doc, llm3_turbo, map_prompt_template):
    try:
        summary = load_summarize_chain(llm=llm3_turbo, chain_type="stuff", prompt=map_prompt_template).run([doc])
        # Log the first 100 characters of the processed chunk
        logging.info(f"Processed Chunk (first 100 characters): {summary[:100]}...")
        return summary
    except Exception as e:
        logging.error(f"Error summarizing document chunk: {e}")
        return ""

def generate_chunk_summaries(docs, selected_indices, openai_api_key, custom_prompt, max_workers=10):
    try:
        llm3_turbo = ChatOpenAI(temperature=0, openai_api_key=openai_api_key, max_tokens=4096, model='gpt-3.5-turbo-16k')
        map_prompt_template = PromptTemplate(template=f"```{{text}}```\n{custom_prompt}", input_variables=["text"])
        summary_list = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_doc = {executor.submit(process_chunk, docs[i], llm3_turbo, map_prompt_template): i for i in selected_indices}
            for future in as_completed(future_to_doc):
                index = future_to_doc[future]
                try:
                    chunk_summary = future.result()
                    if not isinstance(chunk_summary, str):
                        chunk_summary = str(chunk_summary)  # Convert to string if not already
                        logging.info(f"Converted chunk {index} summary to string.")
                    logging.info(f"Chunk {index} Summary: {chunk_summary[:100]}...")  # Log first 100 characters of the summary
                    summary_list.append(chunk_summary)
                except Exception as e:
                    logging.error(f"Error summarizing document chunk at index {index}: {e}")

        return summary_list
    except Exception as e:
        logging.error(f"Error in generating chunk summaries: {e}")
        raise

def generate_summary(text, api_key, custom_prompt, chunk_size, chunk_overlap, progress_update_callback=None):
    try:
        # Split the text into chunks
        docs = split_text(text, chunk_size, chunk_overlap)
        if progress_update_callback:
            progress_update_callback(30)

        # Embed the text chunks
        vectors = embed_text(docs, api_key)
        if progress_update_callback:
            progress_update_callback(40)

        # Determine the optimal number of clusters
        num_clusters = determine_optimal_clusters(vectors)
        if progress_update_callback:
            progress_update_callback(50)

        # Generate summaries for each chunk
        summaries = generate_chunk_summaries(docs, range(len(docs)), api_key, custom_prompt)

        # Manually concatenate the summaries
        final_summary = ""
        for summary in summaries:
            final_summary += summary + "\n\n"

        # Trim the last two newline characters
        final_summary = final_summary.rstrip("\n")

        if progress_update_callback:
            progress_update_callback(90)

        # Log the first 500 characters of the final summary
        logging.info(f"Final Summary (first 500 characters): {final_summary[:500]}...")

        return final_summary
    except Exception as e:
        logging.error(f"Error in the summarization process: {e}")
        raise

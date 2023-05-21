
import asyncio
import concurrent.futures
from collections import defaultdict
import os
import sys
import time
import requests
import requests.exceptions
from bs4 import BeautifulSoup
from tqdm import tqdm

class InvertedIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.compressed_index = {}

    def add_document(self, doc_id, document):
        import re
        terms = re.findall(r'\b\w+\b', document.lower())
        terms = [term.replace(" ", "") for term in terms]  # Remove whitespace from terms
        for term in terms:
            self.index[term].append(doc_id)

    def compress_index(self):
        for term, postings in self.index.items():
            self.compressed_index[term] = self.encode(postings)

    @staticmethod
    def encode(postings):
        deltas = [postings[0]]
        for i in range(1, len(postings)):
            deltas.append(postings[i] - postings[i - 1])

        return [InvertedIndex.elias_gamma_encode(delta) for delta in deltas]

    @staticmethod
    def elias_gamma_encode(delta):
        if delta == 0:
            return '0'

        binary_delta = bin(delta)[2:]
        unary_code = '0' * (len(binary_delta) - 1)
        gamma_code = unary_code + binary_delta
        return gamma_code

    @staticmethod
    def elias_gamma_decode(gamma_code):
        offset = gamma_code.find('1')
        binary_delta = '1' + gamma_code[offset + 1:]
        return int(binary_delta, 2)

    
    async def search(self, query):
        terms = query.split()
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            loop = asyncio.get_event_loop()
            tasks = [loop.run_in_executor(executor, self.search_term, term) for term in terms]
            for response in await asyncio.gather(*tasks):
                results.append(response)

        return set.intersection(*results) if results else set()

    def search_term(self, term):
        if term in self.index:
            if term in self.compressed_index:
                return set(self.decode_postings(self.compressed_index[term]))
            else:
                return set(self.index[term])
        return set()


    def decode_postings(self, postings):
        decoded_postings = []
        for gamma_code in postings:
            delta = self.elias_gamma_decode(gamma_code)
            if decoded_postings:
                decoded_postings.append(decoded_postings[-1] + delta)
            else:
                decoded_postings.append(delta)
        return decoded_postings


def extract_text_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text(separator=' ')
        words = text_content.split()  # Split the text content into words
        print(f"Extracted text from {url}: {text_content[:50]}...")
        return ' '.join(words)  # Join the words back into a single string
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema, requests.exceptions.RequestException,  Exception, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects, requests.exceptions.ConnectionError, requests.exceptions.HTTPError, requests.exceptions.URLRequired) as e:
        print(f"Failed to extract content from URL: {url}")
        return ""


def read_documents_from_files(directory_path):
    documents = []
    file_names = os.listdir(directory_path)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        with tqdm(total=len(file_names), desc="Processing files") as pbar:
            futures = []
            for file_name in file_names:
                file_path = os.path.join(directory_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:
                    urls = file.readlines()
                    for url in urls:
                        future = executor.submit(extract_text_content, url.strip())
                        futures.append(future)
                pbar.update(1)  # Update the progress bar

            for future in concurrent.futures.as_completed(futures):
                text_content = future.result()
                documents.append(text_content)

    return documents


# def calculate_index_size(index):
#     classical_size = sum(sys.getsizeof(postings) for postings in index.index.values())

#     compressed_size = sum(
#         sys.getsizeof(gamma_code) for postings in index.index.values() for gamma_code in postings
#     )

#     return classical_size, compressed_size

def calculate_index_size(index):
    classical_size = sum(sys.getsizeof(posting) for postings in index.index.values() for posting in postings)

    compressed_size = sum(
        sys.getsizeof(str(gamma_code)) * len(str(gamma_code)) // 8
        for postings in index.index.values()
        for gamma_code in postings
    )

    return classical_size, compressed_size






def build_index(documents, use_compression=False):
    index = defaultdict(list)
    index_sizes = [0, 0]  # classical, compressed

    for doc_id, document in enumerate(documents):
        terms = document.split()

        if use_compression:
            encoded_terms = [InvertedIndex.elias_gamma_encode(i) for i, _ in enumerate(terms)]
            index_sizes[1] += sum(len(term) for term in encoded_terms)
            terms = encoded_terms
        else:
            index_sizes[0] += sum(sys.getsizeof(term) for term in terms)

        for term in terms:
            index[term].append(doc_id)

    return index, index_sizes


# Set the directory paths where the crawled links are stored
spbgu_directory = 'SBP'
# msu_directory = 'T2'

# Read the crawled links and extract text content from web pages
spbgu_documents = read_documents_from_files(spbgu_directory)
# msu_documents = read_documents_from_files(msu_directory)

# Initialize the inverted indexes
spbgu_index_classical = InvertedIndex()
spbgu_index_compressed = InvertedIndex()

msu_index_classical = InvertedIndex()
msu_index_compressed = InvertedIndex()

# Build the indexes for SPbGU
spbgu_index_classical.index, spbgu_index_sizes_classical = build_index(spbgu_documents, use_compression=False)
spbgu_index_compressed.index, spbgu_index_sizes_compressed = build_index(spbgu_documents, use_compression=True)

# # Build the indexes for MSU
# msu_index_classical.index, msu_index_sizes_classical = build_index(msu_documents, use_compression=False)
# msu_index_compressed.index, msu_index_sizes_compressed = build_index(msu_documents, use_compression=True)

# Calculate and print index sizes
spbgu_classical_size, spbgu_compressed_size = calculate_index_size(spbgu_index_classical), calculate_index_size(spbgu_index_compressed)
msu_classical_size, msu_compressed_size = calculate_index_size(msu_index_classical), calculate_index_size(msu_index_compressed)

print("\nIndex Sizes:")
print(f"SPbGU - Compressed: {spbgu_classical_size[0]} bytes")
print(f"SPbGU - Classical: {spbgu_compressed_size[1]} bytes")
# print(f"MSU - Classical: {msu_classical_size[0]} bytes")
# print(f"MSU - Compressed: {msu_compressed_size[1]} bytes")

async def perform_search(query, index, index_type):
    start_time = time.time()
    results = await index.search(query)
    end_time = time.time()
    search_time = end_time - start_time

    print(f"\nSearch results for '{query}' in {index_type}:")
    print(f"Number of documents where query was found: {len(results)}")
    print(list(results)[:20])  # Convert set to list and show only the first 20 elements
    print(f"\nSearch time for {index_type}: {search_time:.4f} seconds")

# Perform search operations
query_spbgu = "Ректор СПбГУ"
# query_msu = "Ректор МГУ"

# Create event loop
loop = asyncio.get_event_loop()

# Perform SPbGU search using the classical index
spbgu_classical_task = loop.create_task(perform_search(query_spbgu, spbgu_index_classical, "SPbGU "))

# # Perform SPbGU search using the compressed index
# spbgu_compressed_task = loop.create_task(perform_search(query_spbgu, spbgu_index_compressed, "SPbGU (Compressed Index)"))

# # Perform MSU search using the classical index
# msu_classical_task = loop.create_task(perform_search(query_msu, msu_index_classical, "MSU "))

# # Perform MSU search using the compressed index
# msu_compressed_task = loop.create_task(perform_search(query_msu, msu_index_compressed, "MSU (Compressed Index)"))

# Gather search tasks
search_tasks = asyncio.gather(spbgu_classical_task)

# Run the event loop
loop.run_until_complete(search_tasks)
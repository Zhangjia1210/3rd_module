# Test Cases Documentation

This README.md file provides detailed documentation for the test cases implemented in the project.

## Test: `test_compress_index()`

This test case verifies the functionality of the `compress_index()` method in the `InvertedIndex` class. It performs the following steps:
1. Creates an instance of `InvertedIndex`.
2. Adds a sample document using the `add_document()` method.
3. Calls the `compress_index()` method.
4. Asserts that the length of the compressed index is greater than 0.

## Test: `test_encode()`

This test case ensures the correctness of the `encode()` method in the `InvertedIndex` class. It validates the following:
1. Creates an instance of `InvertedIndex`.
2. Defines a list of postings.
3. Calls the `encode()` method to encode the postings.
4. Asserts that the length of the encoded postings is equal to the length of the original postings.

## Test: `test_elias_gamma_encode()`

This test case verifies the correctness of the `elias_gamma_encode()` static method in the `InvertedIndex` class. It checks the encoding of different delta values and their corresponding expected codes. The test data includes:
- Delta value 0 with expected code '0'.
- Delta value 1 with expected code '10'.
- Delta value 2 with expected code '110'.
- Delta value 3 with expected code '1110'.

## Test: `test_search_term()`

This test case validates the functionality of the `search_term()` method in the `InvertedIndex` class. It performs the following steps:
1. Creates an instance of `InvertedIndex`.
2. Adds sample documents using the `add_document()` method.
3. Calls the `search_term()` method with the search term "document".
4. Asserts that the number of search results is equal to the expected count.

## Test: `test_search()`

This test case ensures the correctness of the `search_term()` method in the `InvertedIndex` class. It performs the same steps as `test_search_term()`.

## Test: `test_decode_postings()`

This test case validates the functionality of the `decode_postings()` method in the `InvertedIndex` class. It checks the decoding of a list of encoded postings. The test data includes:
- Encoded postings ['10', '110', '10'].

## Test: `test_extract_text_content()`

This test case verifies the correctness of the `extract_text_content()` function. It performs the following steps:
1. Defines a sample URL.
2. Calls the `extract_text_content()` function with the URL.
3. Asserts that the length of the extracted text content is greater than 0.

## Test: `test_read_documents_from_files()`

This test case validates the functionality of the `read_documents_from_files()` function. It performs the following steps:
1. Creates a temporary directory.
2. Creates a sample file inside the temporary directory with URLs.
3. Calls the `read_documents_from_files()` function with the temporary directory path.
4. Asserts that the number of extracted documents is equal to the expected count.

## Test: `test_calculate_index_size()`

This test case ensures the correctness of the `calculate_index_size()` function. It performs the following steps:
1. Creates an instance of `InvertedIndex`.
2. Adds sample documents using the `add_document()` method.
3. Calls the `calculate_index_size()` function with the index.
4. Asserts that the classical size and compressed size are both greater than 0.

## Test: `test_build_index()`

This test case verifies the correctness of the `build_index()` function. It performs the following steps:
1. Defines a list of sample documents.
2. Calls the `build_index()` function with the documents.
3. Asserts that the length of the index is greater than 0 and the length of the index sizes is equal to the number of documents.


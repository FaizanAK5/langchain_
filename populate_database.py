import argparse
import os
import shutil
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from get_embeddings import get_embedding_function
from langchain_chroma import Chroma
from langchain_core.documents import Document


CHROMA_PATH = "./chroma_hydrogen"
DATA_PATH = "./hydrogen"


def main():

    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    # embeds and stores new chunks in the db, skipping existing ones
    add_to_chroma(chunks)


def load_documents():
    '''reads all files from the data directory and returns a list of Document objects
    Each document has text and metadata (e.g. Filename, page number)
    '''
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, # each document is splitted into chunks of 800-characters
        chunk_overlap=80, # we keep an overlap of 8 characters between chunks to preserve context across them
        length_function=len, # fo character count
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Loads the existing database and uses the embedding function defined.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs. Adds an id field in metadata (e.g. "data/file.pdf:3:1" meaning page 3, chunk 1)
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default. This returns only the ids (excludes metadata and embeddings etc)
    existing_ids = set(existing_items["ids"]) # set makes it efaster to checvk if a chunk already exists. O(1) time complexity instead of O(n) for lists
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB. The loop skips chunks that are already there to avoid duplication
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    # the new chunks found are embedded and stored in the db
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    '''Assigns a unique, human readable id to eaqch chunk based on
        Page Source (file name) : Page Number : Chunk Index
    '''
    # This will create IDs like "data/report.pdf:6:2"

    # to track chunks per page
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}" # creates a page id (e.g. data/report.pdf:4)

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1 # if it's still the same page, we increment the chunk index to make it unique
        else:
            current_chunk_index = 0 # if we're at a new page, we reset the chunk index to 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}" # adds the chunk index to the page id to create a unique chunk id
        last_page_id = current_page_id # the curent page is now the last page, for new page we will have the chunk id starting from 0

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    '''If a Chroma db exists, this function deletes the entire folder (including embeddings + metadata)'''
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    main()

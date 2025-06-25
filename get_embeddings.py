from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    '''Embeds both the content and the question (need to have the same embeddings for them)'''
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    return embeddings

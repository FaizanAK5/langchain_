# # import argparse (for using CLI)
# from langchain_chroma import Chroma
# from langchain.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM

# from get_embeddings import get_embedding_function

# # this is where the vector db will be stored 
# CHROMA_PATH = "./chroma"

# # we define the prompt template. The model will only answer based on the context provided
# PROMPT_TEMPLATE = """
# You are a helpful asistant. Think step by step and answer the question based only on the provided context:
# Provide yout chain of thought (what steps you took and how you arrived at the answer) under the Reasoning heading.
# Breakdown your responses in sections with an appropriate heading fro each section.

# In your answer, also provide a breakdown of:
# - What documents you analysed
# - If you communicated with any AI Agents for the task
# - If you analysed any external sources
# - Yearly comparison
# - General Trends
# - Summary

# {context}

# ---

# Answer the question based on the above context: {question}
# """


# # def main():
# # This can be used to run the program from cli instead of a ui
# #     parser = argparse.ArgumentParser()
# #     parser.add_argument("query_text", type=str, help="The query text.")
# #     args = parser.parse_args()
# #     query_text = args.query_text
# #     query_rag(query_text)


# def query_model(query_text: str):
#     # Prepare the DB.
#     embedding_function = get_embedding_function()
#     # We create the vector database using Chroma which stores the embeddings of our documents.
#     db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

#     # Search the DB (runs similarity search with distance, returns List of Tuples of (doc, similarity_score))
#     # in this case, it searches the top 5 most relevant documents to the query
#     results = db.similarity_search_with_score(query_text, k=5)

#     # joins the extracted document content using line separators  
#     context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
#     # creates the prompt template
#     prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     # replaces the context and question variables in the prrompt with the actual content
#     prompt = prompt_template.format(context=context_text, question=query_text)
#     # print(prompt)

#     # calls the query model
#     model = OllamaLLM(model="deepseek-r1:8b")
#     # we run the prrompt throuh the model and receieve a response
#     response_text = model.invoke(prompt)

#     # the retrieved results contain the document ids where available (in thee metadata). We collect these document IDs
#     sources = [doc.metadata.get("id", None) for doc, _score in results]
#     # combining the response and the sources
#     formatted_response = f"Response: {response_text}" + "\n\n" f"Sources: {sources}"
#     print(formatted_response)
#     return formatted_response

#  -------------------------------------

# import argparse (for using CLI)
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from get_embeddings import get_embedding_function

# this is where the vector db will be stored
CHROMA_PATH = "./chroma_hydrogen"

# We have three different styles of responses: Enhanced, analytical, converstaional
# ENHANCED: Detailed/Comprehensive response
# ANALYTICAL: Technical response
# CONVERSATIONAL: Quick response


# Enhanced prompt template with chain of thought
ENHANCED_PROMPT_TEMPLATE = """
You are an expert assistant analyzing documents for Net Zero TC. Your task is to provide comprehensive, well-structured answers based STRICTLY on the provided context.

INSTRUCTIONS:
1. Think step by step before answering
2. Base your response ONLY on the provided context - do not use external knowledge
3. Structure your response with clear sections and headings
4. Show your reasoning process transparently
5. If information is not available in the context, explicitly state this

RESPONSE FORMAT:
Your response must follow this exact structure:

## Executive Summary
[Provide a brief 2-3 sentence summary of your answer]

## Detailed Analysis
[Break down your answer into logical subsections with appropriate headings. Use markdown formatting.]

## Chain of Thought
### Reasoning Process
[Explain step-by-step how you arrived at your answer]

### Document Analysis
[List and describe each document you analyzed from the context, including:]
- Document name/identifier
- Key information extracted
- Relevance to the query

### Information Synthesis
[Explain how you combined information from different sources to form your answer]

### Confidence Assessment
[Rate your confidence in the answer based on available evidence: High/Medium/Low and explain why]

## Agent Communication Log
[Other AI Agents consulted to complete the task"]

## External Sources Consulted
[other external sources consulted to complete the task]

## Limitations and Gaps
[Identify any information gaps or limitations in your analysis based on the available context]

---

CONTEXT DOCUMENTS:
{context}

---

USER QUERY: {question}

Remember:
- Use ONLY the information provided in the context
- Be explicit about what you can and cannot determine from the available information
- Structure your response clearly with the sections above
- Show your reasoning transparently
"""

# Analytical prompt for technical queries
ANALYTICAL_PROMPT_TEMPLATE = """
You are a specialized document analysis AI for Net Zero Technology Centre. Analyze the provided context documents and respond to the user's query with rigorous methodology.

ANALYSIS FRAMEWORK:
Follow this systematic approach:

1. QUERY DECOMPOSITION: Break down the user's question into sub-components
2. CONTEXT MAPPING: Map available information to each sub-component
3. EVIDENCE SYNTHESIS: Combine relevant information logically
4. GAP IDENTIFICATION: Identify missing information
5. CONCLUSION FORMATION: Draw conclusions based on available evidence

RESPONSE STRUCTURE:

# Response to: "{question}"

## 📋 Executive Summary
[2-3 sentence overview of findings]

## 🔍 Detailed Findings

### [Create relevant headings based on the query]
[Detailed analysis with supporting evidence from the context]

## 🧠 Analytical Process

### Query Breakdown
1. [First component of the question]
2. [Second component of the question]
[Continue as needed]

### Document Analysis
**Documents processed:**
[List each document found in the context and its relevance]

### Evidence Chain
**Step 1:** [First reasoning step with evidence]
- Supporting evidence: [Quote or reference from context]
- Source: [Document identifier if available]

**Step 2:** [Second reasoning step]
- Supporting evidence: [Quote or reference from context]  
- Source: [Document identifier if available]

[Continue for each logical step]

### Information Synthesis
[Explain how you combined different pieces of information to reach your conclusion]

## 🤖 Process Transparency

### AI Agent Collaboration
- **Other AI agents consulted**: [Any other AI Agnets consulted] - [brief explanation]

### External Research
- **External sources checked**: [Any external sources checked] - [brief explanation]

### Confidence Assessment
- **Overall Confidence:** [High/Medium/Low]
- **Evidence Quality:** [Strong/Moderate/Weak]
- **Coverage Completeness:** [Complete/Partial/Limited]
- **Rationale:** [Brief explanation of confidence assessment]

## ⚠️ Analysis Limitations

### Information Gaps
[List any missing information that would improve the analysis]

### Scope Boundaries  
[Clarify what aspects of the query could/could not be addressed]

---

CONTEXT FOR ANALYSIS:
{context}

INSTRUCTIONS: Analyze the above context to answer the user's query. Follow the structured format exactly and base your response solely on the provided information.
"""

# Conversational prompt for general queries
CONVERSATIONAL_PROMPT_TEMPLATE = """
You are a helpful AI assistant for Net Zero TC. Answer the user's question based on the provided documents, thinking through your response step by step.

Please structure your response as follows:

## Answer
[Provide a clear, direct answer to the user's question]

## Supporting Details
[Break down your answer with relevant details from the documents, organized with clear headings]

## How I Found This Information
**Documents I analyzed:**
[List the documents you used and what information you found in each]

**My reasoning process:**
1. [Step 1 of your thinking process]
2. [Step 2 of your thinking process]
3. [Continue as needed]

**What I couldn't determine:**
[Mention any information that wasn't available in the provided documents]

## Research Notes
- **Other AI agents consulted: [Any other AI Agnets consulted] - [brief explanation]**
- **External sources checked: [Any external sources checked] - [brief explanation]**
- **Confidence level:** [High/Medium/Low] - [brief explanation]

---

Here are the documents I have access to:
{context}

---

Question: {question}

Please answer based only on the information in the documents above.
"""

def query_model(query_text: str, prompt_style: str = "enhanced"):
    """
    Query the model with enhanced prompting
   
    Args:
        query_text (str): The user's question
        prompt_style (str): Style of prompt to use - "enhanced", "analytical", or "conversational"
    """
    # Prepare the DB.
    embedding_function = get_embedding_function()
    # WE create the vector database using Chroma DB which stores the embeddings of the documents.
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB (runs similarity search with distance, returns list of tuples of (doc, similarity_score))
    # in this case, it searches the top 5 most relevant documents to query
    results = db.similarity_search_with_score(query_text, k=5)

    # Create context with document information
    context_parts = []
    for i, (doc, score) in enumerate(results):
        doc_id = doc.metadata.get("id", f"Document_{i+1}")
        context_parts.append(f"=== {doc_id} ===\n{doc.page_content}")
   
    context_text = "\n\n".join(context_parts)

    # Select prompt template (from the three different styles defined above)
    if prompt_style == "analytical":
        template = ANALYTICAL_PROMPT_TEMPLATE
    elif prompt_style == "conversational":
        template = CONVERSATIONAL_PROMPT_TEMPLATE
    else:
        template = ENHANCED_PROMPT_TEMPLATE

    # Create and format prompt
    prompt_template = ChatPromptTemplate.from_template(template)
    # We replace the context and question variables in our promp templates with the actual information
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Call the model (Curently using Deepseek R1 for reasoning. Others downloaded include Llama and Mistral)
    model = OllamaLLM(model="deepseek-r1:8b")
    # invoke the model with th prompt to receieve a response
    response_text = model.invoke(prompt)

    # Collect sources
    sources = [doc.metadata.get("id", None) for doc, _score in results]
   
    # For backward compatibility, return formatted response
    formatted_response = f"Response: {response_text}\n\nSources: {sources}"
    print(formatted_response)
    return formatted_response

def query_model_with_style(query_text: str, style: str = "enhanced"):
    """
    Enhanced query function that allows prompt style selection
    """
    return query_model(query_text, prompt_style=style)

# Keep original function for backward compatibility
def query_model_original(query_text: str):
    """Original query model function"""
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_score(query_text, k=5)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
   
    # Original simple prompt
    ORIGINAL_PROMPT = """
    You are a helpful assistant. Answer the question based only on the provided context:
    {context}
    ---
    Answer the question based on the above context: {question}
    """
   
    prompt_template = ChatPromptTemplate.from_template(ORIGINAL_PROMPT)
    prompt = prompt_template.format(context=context_text, question=query_text)
   
    model = OllamaLLM(model="deepseek-r1:8b")
    response_text = model.invoke(prompt)
    sources = [doc.metadata.get("id", None) for doc, _score in results]
   
    return f"Response: {response_text}\n\nSources: {sources}"
# import streamlit as st
# from llm import query_model

# st.set_page_config(page_title="NZTC Assistant", layout='wide')

# with st.sidebar:
#     st.markdown("Options")
#     st.markdown("[View the System Architecture](https://faizanabbas5.github.io/Agent-Architcture/)")
#     st.markdown("---")
#     st.markdown("Developed by NZTC")

# st.sidebar.image("logo.jpg", width=50)
# st.markdown(
#     """
#     <h1 style='text-align: center; margin-bottom: 0'>Net Zero TC Agent</h1>
    
#     """,
#     unsafe_allow_html=True
# )

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])


# if prompt := st.chat_input("Ask me about NZTC's annual review data..."):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     st.chat_message("user").markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Thinking..."):
#             try:
#                 reply = query_model(prompt)
#             except Exception as e:
#                 reply = f"Error {str(e)}"

#         st.markdown(reply)
#     st.session_state.messages.append({"role": "assistant", "content": reply})

# # while True:
# #     print("\n\n-------------------------------")
# #     question = input("Ask your question (q to quit): ")
# #     print("\n\n")
# #     if question == "q":
# #         break

# #     print(query_model(question))


# ------------------------------------

import streamlit as st
import os
from langchain_.agent import query_model_with_style

DATA_PATH = "./hydrogen"

st.set_page_config(page_title="NZTC Assistant", layout='wide')

# We parse the sources (the documents used to respond to the query)
def parse_sources(sources):
    """Parse source strings to extract file path, page, and chunk info
    Sources are of the format: Page Source (file name):Page Number:Chunk Index
    e.g. data/report.pdf:5:3
    """
    parsed_sources = []
    for source in sources:
        if source:
            parts = source.split(':')
            if len(parts) >= 3:
                file_path = parts[0] # data/report.pdf
                page_num = parts[1] # 5
                chunk_num = parts[2] # 3
                filename = os.path.basename(file_path) # report.pdf
               
                parsed_sources.append({
                    'full_path': file_path,
                    'filename': filename,
                    'page': page_num,
                    'chunk': chunk_num,
                    'display_text': f"{filename} (Page {page_num}, Chunk {chunk_num})"
                })
    return parsed_sources

def display_sources_with_links(sources, message_id=None):
    """Display sources as clickable elements"""
    if not sources or all(s is None for s in sources):
        return
   
    st.markdown("### 📚 Sources Referenced:")
   
    parsed_sources = parse_sources(sources)
   
    if not parsed_sources:
        st.markdown("*No valid sources found.*")
        return
    
    # Added message id as without it, the key can sometimes throw an eorro. The message id makes each source key unique, so subsequent queries will provide the source crrectly even if a source is repeated from the previous query 
    if message_id is None:
        message_id=len(st.session_state.messages)
   
    # Create columns for better layout
    cols = st.columns(min(len(parsed_sources), 3))
   
    for idx, source in enumerate(parsed_sources):
        col_idx = idx % 3
        with cols[col_idx]:
            st.markdown(f"**{source['display_text']}**")
           
            if os.path.exists(source['full_path']):
                with open(source['full_path'], "rb") as file:
                    st.download_button(
                        label="📥 Download PDF",
                        data=file.read(),
                        file_name=source['filename'],
                        mime="application/pdf",
                        key=f"download_{message_id}_{idx}_{source['filename']}"
                    )
               
                if st.button(f"📂 Show File Path", key=f"path_{message_id}_{idx}"):
                    st.code(os.path.abspath(source['full_path']))
            else:
                st.error(f"File not found: {source['full_path']}")
           
            st.markdown("---")

def query_model_enhanced(query_text: str, style: str = "enhanced"):
    """Enhanced version that returns response and sources separately"""
    full_response = query_model_with_style(query_text, style)
   
    if "Sources:" in full_response:
        response_part, sources_part = full_response.split("Sources:", 1)
        response_text = response_part.replace("Response:", "").strip()
       
        sources_str = sources_part.strip()
        sources_clean = sources_str.strip("[]'\"").replace("'", "").replace('"', '')
        sources_list = [s.strip() for s in sources_clean.split(',') if s.strip()]
       
        return response_text, sources_list
    else:
        return full_response, []

# Sidebar configuration
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
   
    # Prompt style selector
    prompt_style = st.selectbox(
        "Response Style:",
        options=["enhanced", "analytical", "conversational"],
        index=0,
        help="""
        • Enhanced: Structured response with detailed chain of thought\n
        • Analytical: Technical analysis with evidence tables\n
        • Conversational: Friendly, easy-to-read format
        """
    )
   
    st.markdown("---")
   
    # Style descriptions
    with st.expander("ℹ️ Response Style Details"):
        st.markdown("""
        **Enhanced Style:**
        - Executive summary
        - Detailed analysis with sections
        - Complete chain of thought
        - Confidence assessment
        - Limitation analysis
       
        **Analytical Style:**
        - Query decomposition
        - Evidence tables
        - Step-by-step reasoning
        - Rigorous methodology
        - Technical format
       
        **Conversational Style:**
        - Direct answers
        - Simple explanations
        - Easy to read
        - Less formal structure
        """)
   
    st.markdown("---")
    st.markdown("[View System Architecture](https://faizanabbas5.github.io/Agent-Architcture/)")
   
    # File browser
    st.markdown("### 📁 Document Library")
    data_dir = DATA_PATH
    with st.expander("📚 Digital"):
        if os.path.exists(data_dir):
            pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
            if pdf_files:
                for pdf_file in pdf_files:
                    file_path = os.path.join(data_dir, pdf_file)
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"📄 {pdf_file}",
                            data=file.read(),
                            file_name=pdf_file,
                            mime="application/pdf",
                            key=f"sidebar_{pdf_file}"
                        )
            else:
                st.info("No PDF files found in data directory")
        else:
            st.warning("Data directory not found")

    st.markdown("---")
    st.markdown("**[Developed by NZTC](https://www.netzerotc.com/)**")

# Logo
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", width=50)

# Main title
st.markdown(
    """
    <h1 style='text-align: center; margin-bottom: 0'>Net Zero TC Agent</h1>
    <p style='text-align: center; color: #666; margin-top: 0'>Intelligent Document Analysis Assistant</p>
    """,
    unsafe_allow_html=True
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg_idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "sources" in msg:
            st.markdown(msg["content"])
            display_sources_with_links(msg["sources"], message_id=msg_idx)
        else:
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me about NZTC's annual review data..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner(f"Analyzing documents using {prompt_style} style..."):
            try:
                response_text, sources_list = query_model_enhanced(prompt, prompt_style)
               
                # Display response
                st.markdown(response_text)
               
                # Display sources
                if sources_list:
                    current_msg_id = len(st.session_state.messages)
                    display_sources_with_links(sources_list, message_id=current_msg_id)
                   
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
                response_text = f"I apologize, but I encountered an error while processing your request: {str(e)}"
                sources_list = []
   
    # Store response in session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "sources": sources_list
    })

# Usage tips
with st.expander("💡 Usage Tips"):
    st.markdown("""
    **For best results:**
    - Ask specific questions about the documents
    - Use the **Enhanced** style for comprehensive analysis
    - Use the **Analytical** style for technical queries
    - Use the **Conversational** style for quick answers
   
    **Example queries:**
    - "What were the key achievements in 2021?"
    - "Compare the performance metrics across different years"
    - "What challenges were identified in the reports?"
    - "Summarize the latest advancements in the di"
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #999; font-size: 12px;'>Net Zero TC Document Analysis Assistant • Powered by AI</p>",
    unsafe_allow_html=True
)
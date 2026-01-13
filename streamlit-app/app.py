"""Streamlit demo app for Sentio+ RAG chatbot."""

import streamlit as st
import requests
from typing import Optional

# Page config
st.set_page_config(
    page_title="Sentio+ RAG Demo",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000"

# Sidebar
with st.sidebar:
    st.title("📊 Sentio+ RAG")
    st.markdown("---")
    
    # API Configuration
    st.subheader("🔌 API Configuration")
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="Base URL for the FastAPI backend (e.g., http://localhost:8000)"
    )
    st.session_state.api_base_url = api_url.rstrip("/")
    
    st.markdown("---")
    
    # Stats
    st.subheader("📈 Collection Stats")
    try:
        response = requests.get(f"{st.session_state.api_base_url}/ingest/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            st.metric("Total Documents", f"{stats.get('total_documents', 0):,}")
            st.metric("Unique Apps", stats.get('unique_apps', 0))
            st.metric("Categories", stats.get('unique_categories', 0))
            
            categories = stats.get('categories', [])
            if isinstance(categories, list):
                st.markdown("**Categories:**")
                for cat in categories[:10]:
                    st.text(f"  • {cat}")
                if len(categories) > 10:
                    st.text(f"  ... and {len(categories) - 10} more")
        else:
            st.warning(f"Could not load stats: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.warning(f"Could not connect to API: {e}")
    
    st.markdown("---")
    
    # Settings
    st.subheader("⚙️ Query Settings")
    filter_by_source = st.checkbox("Filter by App Name", value=True, help="Use LLM to pre-filter relevant apps")
    
    st.markdown("---")
    
    # Model Info
    st.subheader("🤖 Model Info")
    try:
        model_response = requests.get(f"{st.session_state.api_base_url}/query/model", timeout=2)
        if model_response.status_code == 200:
            model_data = model_response.json()
            st.caption(f"**Provider:** {model_data.get('provider', 'Unknown')}")
            st.caption(f"**Model:** {model_data.get('model', 'Unknown')}")
            st.caption(f"**Temperature:** {model_data.get('temperature', 'N/A')}")
        else:
            st.caption("Model info unavailable")
    except requests.exceptions.RequestException:
        st.caption("Model info unavailable")
    
    st.markdown("---")
    
    # Health check
    try:
        health_response = requests.get(f"{st.session_state.api_base_url}/health", timeout=2)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ API Connected")
            st.caption(f"**Service:** {health_data.get('service', 'Unknown')}")
            st.caption(f"**Documents:** {health_data.get('documents', 0):,}")
        else:
            st.error("❌ API Health Check Failed")
    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to API")

# Main content
st.title("💬 Sentio+ RAG Chatbot")
st.markdown("Ask questions about app reviews using semantic search and AI-powered insights.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize auto-submit flag
if "auto_submit" not in st.session_state:
    st.session_state.auto_submit = False

# Example queries
st.markdown("### 💡 Example Queries")
example_col1, example_col2, example_col3, example_col4 = st.columns(4)
with example_col1:
    if st.button("👍 What do people like?", use_container_width=True):
        st.session_state.query = "What do people like about apps?"
        st.session_state.auto_submit = True
        st.rerun()
with example_col2:
    if st.button("👎 Common complaints?", use_container_width=True):
        st.session_state.query = "What are common complaints?"
        st.session_state.auto_submit = True
        st.rerun()
with example_col3:
    if st.button("⭐ Best reviewed apps?", use_container_width=True):
        st.session_state.query = "Which apps have the best reviews?"
        st.session_state.auto_submit = True
        st.rerun()
with example_col4:
    if st.button("🔍 Navigation apps?", use_container_width=True):
        st.session_state.query = "What do people think about navigation apps?"
        st.session_state.auto_submit = True
        st.rerun()

# Query input
query = st.text_input(
    "Ask a question:",
    value=st.session_state.get("query", ""),
    placeholder="e.g., What do people think about navigation apps?",
    key="query_input"
)

# Query button
col1, col2 = st.columns([1, 10])
with col1:
    submit_button = st.button("🔍 Search", type="primary", use_container_width=True)

# Process query (either from button or auto-submit)
should_process = (submit_button and query) or (st.session_state.auto_submit and query)

if should_process:
    # Clear auto-submit flag
    st.session_state.auto_submit = False
    
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": query})
    
    with st.spinner("Searching reviews and generating answer..."):
        try:
            # Query API
            response = requests.post(
                f"{st.session_state.api_base_url}/query",
                json={
                    "question": query,
                    "filter_by_source": filter_by_source,
                },
                timeout=60,
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Add assistant response to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["answer"],
                    "sources": result.get("sources", []),
                    "num_docs": result.get("num_docs", 0),
                    "selected_sources": result.get("selected_sources"),
                })
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg, "error": True})
                st.error(error_msg)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "error": True})
            st.error(error_msg)
        except Exception as e:
            error_msg = f"Error processing query: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "error": True})
            st.error(error_msg)
            st.exception(e)

elif submit_button and not query:
    st.warning("Please enter a query first.")
elif st.session_state.auto_submit:
    # Clear auto-submit if no query
    st.session_state.auto_submit = False

# Display chat history
if st.session_state.messages:
    st.markdown("### 💬 Conversation History")
    
    for i, msg in enumerate(reversed(st.session_state.messages[-10:])):  # Show last 10 messages
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
            # Show metadata for assistant messages
            if msg["role"] == "assistant" and not msg.get("error"):
                with st.expander(f"🔍 Details for message {len(st.session_state.messages) - i}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Documents Retrieved", msg.get("num_docs", 0))
                    with col2:
                        sources = msg.get("sources", [])
                        if sources:
                            st.text(f"Apps: {', '.join(sources)}")
                    
                    selected = msg.get("selected_sources")
                    if selected:
                        st.caption(f"Selected sources: {', '.join(selected)}")
    
    # Clear history button
    if st.button("🗑️ Clear History"):
        st.session_state.messages = []
        st.rerun()

# Additional info section
st.markdown("---")
st.markdown("### 📖 How It Works")
st.markdown("""
1. **Semantic Search**: Your question is converted to a vector and matched against review embeddings
2. **Retrieval**: The most relevant review chunks are retrieved from ChromaDB
3. **Generation**: An LLM (Claude via AWS Bedrock) synthesizes an answer from the retrieved reviews
4. **Sources**: The answer includes which apps were referenced
""")

# Footer
st.markdown("---")
st.caption("Sentio+ RAG Demo | Powered by ChromaDB + AWS Bedrock")

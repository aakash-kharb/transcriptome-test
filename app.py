"""
Main entry point for the Gene Expression Analysis multi-page Streamlit application.
"""

import streamlit as st
import data_loader

# Page configuration
st.set_page_config(
    page_title="Gene Expression Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables used across pages."""
    if 'cold_ca_ids' not in st.session_state:
        st.session_state.cold_ca_ids = set()
    
    if 'drought_ca_ids' not in st.session_state:
        st.session_state.drought_ca_ids = set()
    
    if 'heat_ca_ids' not in st.session_state:
        st.session_state.heat_ca_ids = set()
    
    if 'salinity_ca_ids' not in st.session_state:
        st.session_state.salinity_ca_ids = set()
    
    # Store filter results for each page
    if 'cold_last_query' not in st.session_state:
        st.session_state.cold_last_query = None
    
    if 'drought_last_query' not in st.session_state:
        st.session_state.drought_last_query = None
    
    if 'heat_last_query' not in st.session_state:
        st.session_state.heat_last_query = None
    
    if 'salinity_last_query' not in st.session_state:
        st.session_state.salinity_last_query = None


# Initialize session state
init_session_state()

# Ensure data is available (download from Google Drive if needed)
if not data_loader.ensure_data_available():
    st.stop()

# Main page content
st.title("🧬 Gene Expression Analysis Platform")

st.markdown("""
### Welcome to the Gene Expression Analysis Platform

This application allows you to analyze gene expression data across different stress conditions.

#### Available Pages:

1. **Cold Stress** - Analysis of cold stress response data
2. **Drought Stress** - Analysis of drought stress response across multiple datasets
3. **Heat Stress** - Analysis of heat stress response across different cultivars
4. **Salinity Stress** - Analysis of salinity stress response data
5. **Arena** - Compare and combine Ca IDs from different stress types

#### How to Use:

1. Navigate to a stress type page using the sidebar
2. View the raw data at the top of each page
3. Use the filtering options to query specific genes:
   - Filter by log2FC threshold
   - Filter by tissue type (Root/Shoot/Leaf)
   - For multi-file pages, combine results using AND/OR operations
4. Choose to view only Ca IDs or full data
5. Download filtered results as CSV
6. Send filtered Ca IDs to Arena for cross-stress analysis

#### Navigation:

Use the sidebar to switch between different pages.

---
""")

# Quick stats display
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Cold Ca IDs in Arena", len(st.session_state.cold_ca_ids))

with col2:
    st.metric("Drought Ca IDs in Arena", len(st.session_state.drought_ca_ids))

with col3:
    st.metric("Heat Ca IDs in Arena", len(st.session_state.heat_ca_ids))

with col4:
    st.metric("Salinity Ca IDs in Arena", len(st.session_state.salinity_ca_ids))

st.info("👈 Select a stress type from the sidebar to begin analysis")

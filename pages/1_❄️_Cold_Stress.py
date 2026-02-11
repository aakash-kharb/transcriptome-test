"""
Cold Stress Analysis Page
Displays and filters Cold_Top.csv data
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend

st.set_page_config(page_title="Cold Stress Analysis", page_icon="❄️", layout="wide")

st.title("❄️ Cold Stress Analysis")

# File path
FILE_PATH = "data/Cold_Top.csv"

# Load data
@st.cache_data
def load_cold_data():
    """Load cold stress data."""
    try:
        df = pd.read_csv(FILE_PATH)
        return df
    except Exception as e:
        st.error(f"Error loading {FILE_PATH}: {e}")
        return None

c_df = load_cold_data()

if c_df is not None:
    # Display raw data
    st.header("Raw Data - Cold_Top.csv")
    st.dataframe(c_df, use_container_width=True, height=300)
    
    st.markdown("---")
    
    # Detect Ca ID column
    ca_id_col = backend.detect_ca_id_column(c_df)
    
    if ca_id_col:
        st.header("🔍 Filter Options")
        
        # Detect number of tissues
        num_tissues = backend.get_tissue_count(c_df, ca_id_col)
        
        # Create filtering mode selection
        st.subheader("1. Select Filtering Mode")
        filter_mode = st.radio(
            "Choose how to filter genes:",
            options=["View All Data", "Filter by Specific Tissue", "Filter by Multi-Tissue Response"],
            key="cold_filter_mode",
            horizontal=False
        )
        
        st.markdown("---")
        
        # Initialize variables
        use_log2fc_filter = False
        log2fc_threshold = 1.5
        selected_tissue = "Both"
        min_tissue_count = 1
        
        # Mode-specific options
        if filter_mode == "Filter by Specific Tissue":
            st.subheader("2. Tissue & Threshold Settings")
            col1, col2 = st.columns(2)
            
            with col1:
                tissue_options = ["Both", "Root", "Shoot"]
                selected_tissue = st.selectbox(
                    "Select tissue type:",
                    tissue_options,
                    key="cold_tissue"
                )
            
            with col2:
                use_log2fc_filter = st.checkbox(
                    "Apply log2FC threshold",
                    value=True,
                    key="cold_log2fc_enable"
                )
                
                if use_log2fc_filter:
                    log2fc_threshold = st.number_input(
                        "log2FC threshold (|log2FC| ≥)",
                        min_value=0.5,
                        max_value=10.0,
                        value=1.5,
                        step=0.1,
                        key="cold_log2fc"
                    )
        
        elif filter_mode == "Filter by Multi-Tissue Response":
            st.subheader("2. Multi-Tissue Response Settings")
            
            st.info(f"📊 This dataset contains **{num_tissues} tissue types**: Root, Shoot")
            
            col1, col2 = st.columns(2)
            
            with col1:
                min_tissue_count = st.number_input(
                    f"Minimum number of tissues gene must be responsive in:",
                    min_value=1,
                    max_value=num_tissues,
                    value=min(2, num_tissues),
                    step=1,
                    key="cold_min_tissues"
                )
                st.caption(f"Gene must pass threshold in at least {min_tissue_count} tissue(s)")
            
            with col2:
                log2fc_threshold = st.number_input(
                    "log2FC threshold (|log2FC| ≥)",
                    min_value=0.5,
                    max_value=10.0,
                    value=1.5,
                    step=0.1,
                    key="cold_multi_log2fc"
                )
                st.caption(f"Applied to each tissue independently")
            
            use_log2fc_filter = True
        
        st.markdown("---")
        
        # Output options
        st.subheader("3. Output Options")
        show_only_ids = st.checkbox(
            "Show only Ca IDs (hide expression values)",
            value=False,
            key="cold_show_ids"
        )
        
        st.markdown("---")
        
        # Apply filters button
        if st.button("🚀 Apply Filters", type="primary", key="cold_apply", use_container_width=True):
            filtered_df = c_df.copy()
            
            # Apply filtering based on mode
            if filter_mode == "View All Data":
                # No filtering, show all data
                pass
            
            elif filter_mode == "Filter by Specific Tissue":
                # Apply tissue filter first
                if selected_tissue != "Both" and use_log2fc_filter:
                    # Filter by tissue AND log2FC
                    tissue_cols = [col for col in filtered_df.columns if selected_tissue in col]
                    if tissue_cols:
                        cols_to_keep = [ca_id_col] + tissue_cols
                        filtered_df = filtered_df[cols_to_keep]
                    
                    # Apply log2FC threshold
                    control_cols = [col for col in filtered_df.columns if 'Control' in col]
                    stress_cols = [col for col in filtered_df.columns if '-CS' in col]
                    
                    if control_cols and stress_cols:
                        filtered_df = backend.filter_by_log2fc_threshold(
                            filtered_df,
                            ca_id_col,
                            control_cols,
                            stress_cols,
                            log2fc_threshold,
                            use_abs=True
                        )
                elif selected_tissue != "Both":
                    # Filter by tissue only (no log2FC)
                    tissue_cols = [col for col in filtered_df.columns if selected_tissue in col]
                    if tissue_cols:
                        cols_to_keep = [ca_id_col] + tissue_cols
                        filtered_df = filtered_df[cols_to_keep]
                elif use_log2fc_filter:
                    # Filter by log2FC only (keep all tissues)
                    control_cols = [col for col in filtered_df.columns if 'Control' in col]
                    stress_cols = [col for col in filtered_df.columns if '-CS' in col]
                    
                    if control_cols and stress_cols:
                        filtered_df = backend.filter_by_log2fc_threshold(
                            filtered_df,
                            ca_id_col,
                            control_cols,
                            stress_cols,
                            log2fc_threshold,
                            use_abs=True
                        )
            
            elif filter_mode == "Filter by Multi-Tissue Response":
                # Use the new multi-tissue filtering function
                filtered_df = backend.filter_by_minimum_tissues(
                    filtered_df,
                    ca_id_col,
                    log2fc_threshold,
                    min_tissue_count,
                    control_suffix='Control',
                    stress_suffixes=['CS']
                )
            
            
            # Detect duplicates in filtered results
            total_genes, unique_genes, duplicate_df = backend.detect_duplicates(filtered_df, ca_id_col)
            
            # Show results with clear metrics
            st.markdown("---")
            st.markdown("### 📊 Results")
            
            result_col1, result_col2, result_col3 = st.columns(3)
            with result_col1:
                st.metric("Total Genes", total_genes)
            with result_col2:
                st.metric("Unique Ca IDs", unique_genes)
            with result_col3:
                duplicate_count = total_genes - unique_genes
                st.metric("Duplicates", duplicate_count, 
                         delta=None if duplicate_count == 0 else f"-{duplicate_count} redundant")
            
            # Show filtering summary
            if filter_mode == "Filter by Multi-Tissue Response":
                st.info(f"✓ Showing genes responsive in **≥{min_tissue_count} tissues** with |log2FC| ≥ {log2fc_threshold}")
            elif filter_mode == "Filter by Specific Tissue":
                tissue_desc = selected_tissue if selected_tissue != "Both" else "all tissues"
                if use_log2fc_filter:
                    st.info(f"✓ Showing {tissue_desc} with |log2FC| ≥ {log2fc_threshold}")
                else:
                    st.info(f"✓ Showing {tissue_desc} (no threshold applied)")
            else:
                st.info("✓ Showing all data (no filters applied)")
            
            
            # Show duplicate warning if present
            if duplicate_count > 0:
                st.warning(f"⚠️ Found {duplicate_count} duplicate Ca ID entries in the results")
                with st.expander(f"View {duplicate_count} Duplicate Entries"):
                    st.dataframe(duplicate_df, use_container_width=True)
                    st.info("These Ca IDs appear multiple times in the dataset. Only unique IDs will be stored for combined analysis.")
            else:
                if total_genes > 0:
                    st.success(f"✓ All {total_genes} genes have unique Ca IDs")
                else:
                    st.warning("⚠️ No genes match the selected criteria. Try adjusting your filters.")
            
            # Show only IDs if requested
            if show_only_ids:
                filtered_df = filtered_df[[ca_id_col]]
            
            # Store in session state
            st.session_state.cold_last_query = filtered_df
            
            # Display results
            if len(filtered_df) > 0:
                st.markdown("---")
                st.markdown("### 📋 Filtered Data")
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Get Ca IDs
                ca_ids = backend.get_ca_ids_from_df(filtered_df, ca_id_col)
                
                # Action buttons
                st.markdown("---")
                st.markdown("### 💾 Actions")
                col_act1, col_act2 = st.columns(2)
                
                with col_act1:
                    # Download button
                    csv_data = backend.create_download_csv(filtered_df)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv_data,
                        file_name="cold_filtered_results.csv",
                        mime="text/csv",
                        key="cold_download",
                        use_container_width=True
                    )
                
                with col_act2:
                    # Send to Arena button
                    if st.button("🎯 Send to Arena", key="cold_send_arena", use_container_width=True):
                        st.session_state.cold_ca_ids = ca_ids
                        st.success(f"✓ Sent {len(ca_ids)} unique Ca IDs to Arena")
                        st.info("Navigate to Arena page to perform cross-stress analysis")
            
        
        # Show current Arena status
        st.markdown("---")
        st.subheader("Current Arena Status")
        col7, col8, col9, col10 = st.columns(4)
        
        with col7:
            st.metric("Cold Ca IDs", len(st.session_state.get('cold_ca_ids', set())))
        with col8:
            st.metric("Drought Ca IDs", len(st.session_state.get('drought_ca_ids', set())))
        with col9:
            st.metric("Heat Ca IDs", len(st.session_state.get('heat_ca_ids', set())))
        with col10:
            st.metric("Salinity Ca IDs", len(st.session_state.get('salinity_ca_ids', set())))
    
    else:
        st.error("Could not detect Ca ID column in the data")
else:
    st.error(f"Failed to load data from {FILE_PATH}")

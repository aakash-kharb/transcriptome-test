"""
Salinity Stress Analysis Page
Displays and filters multiple salinity stress datasets
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend

st.set_page_config(page_title="Salinity Stress Analysis", page_icon="🧂", layout="wide")

st.title("🧂 Salinity Stress Analysis")

# File paths
FILES = {
    "SalinityRootShoot53711": "data/SalinityRootShoot53711_Top.csv",
    "SalinityGSE70377": "data/SalinityGSE70377_Top.csv",
    "Salinity_ICCV_JG": "data/Salinity_ICCV_JG_Top.csv",
    "SalinityICCV2-JG62": "data/SalinityICCV2-JG62_Top.csv"
}

# Load data
@st.cache_data
def load_salinity_data():
    """Load all salinity stress data files."""
    dataframes = {}
    for name, filepath in FILES.items():
        try:
            df = pd.read_csv(filepath)
            dataframes[name] = df
        except Exception as e:
            st.warning(f"Could not load {filepath}: {e}")
            dataframes[name] = None
    return dataframes

# Load all dataframes
data_dict = load_salinity_data()
s1_df = data_dict["SalinityRootShoot53711"]
s2_df = data_dict["SalinityGSE70377"]
s3_df = data_dict["Salinity_ICCV_JG"]
s4_df = data_dict["SalinityICCV2-JG62"]

# Display all raw data
st.header("Raw Data - Salinity Stress Datasets")

if s1_df is not None:
    st.subheader("SalinityRootShoot53711_Top.csv")
    st.dataframe(s1_df, use_container_width=True, height=250)
    st.markdown("---")

if s2_df is not None:
    st.subheader("SalinityGSE70377_Top.csv")
    st.dataframe(s2_df, use_container_width=True, height=250)
    st.markdown("---")

if s3_df is not None:
    st.subheader("Salinity_ICCV_JG_Top.csv")
    st.dataframe(s3_df, use_container_width=True, height=250)
    st.markdown("---")

if s4_df is not None:
    st.subheader("SalinityICCV2-JG62_Top.csv")
    st.dataframe(s4_df, use_container_width=True, height=250)

st.markdown("---")

# Filtering section
st.header("Filter Options")

st.info("""
**Column Nomenclature:**

**GSE70377 file:**
- **Stol**: Tolerant genotype, **Ssen**: Sensitive genotype
- **veg**: Vegetative stage, **rep**: Reproductive stage
- **CT**: Control, **SS**: Stress

**ICCV_JG file:**
- Multiple genotypes with Control/Stress conditions and different developmental stages
""")

# Tab for different filtering modes
tab1, tab2 = st.tabs(["Individual File Filtering", "Combined Filtering"])

with tab1:
    st.subheader("Filter Each Dataset Individually")
    
    # Select which file to filter
    file_options = [name for name, df in data_dict.items() if df is not None]
    selected_file = st.selectbox("Select dataset to filter", file_options, key="salinity_file_select")
    
    if selected_file:
        working_df = data_dict[selected_file]
        ca_id_col = backend.detect_ca_id_column(working_df)
        
        if ca_id_col:
            # Detect number of tissues
            num_tissues = backend.get_tissue_count(working_df, ca_id_col, 
                                                   stress_suffixes=['SS', 'Stress', '-S', '-SS'])
            
            st.markdown("---")
            st.subheader("1. Select Filtering Mode")
            
            # Different modes based on file type
            if "RootShoot53711" in selected_file and num_tissues > 1:
                filter_mode = st.radio(
                    "Choose how to filter genes:",
                    options=["View All Data", "Filter by Specific Tissue", "Filter by Multi-Tissue Response"],
                    key=f"salinity_{selected_file}_mode",
                    horizontal=False
                )
            else:
                filter_mode = st.radio(
                    "Choose how to filter genes:",
                    options=["View All Data", "Filter by Threshold"],
                    key=f"salinity_{selected_file}_mode",
                    horizontal=False
                )
            
            st.markdown("---")
            
            # Initialize variables
            use_log2fc = False
            log2fc_threshold = 1.5
            selected_tissue = "Both"
            selected_genotype = "All"
            selected_stage = "Both"
            selected_condition = "All"
            min_tissue_count = 1
            
            # Mode-specific options
            if filter_mode == "Filter by Specific Tissue" and "RootShoot53711" in selected_file:
                st.subheader("2. Tissue & Threshold Settings")
                col1, col2 = st.columns(2)
                
                with col1:
                    tissue_options = ["Both", "Root", "Shoot"]
                    selected_tissue = st.selectbox(
                        "Select tissue type:",
                        tissue_options,
                        key=f"salinity_{selected_file}_tissue"
                    )
                
                with col2:
                    use_log2fc = st.checkbox(
                        "Apply log2FC threshold",
                        value=True,
                        key=f"salinity_{selected_file}_log2fc_enable"
                    )
                    
                    if use_log2fc:
                        log2fc_threshold = st.number_input(
                            "log2FC threshold (|log2FC| ≥)",
                            min_value=0.5,
                            max_value=10.0,
                            value=1.5,
                            step=0.1,
                            key=f"salinity_{selected_file}_log2fc"
                        )
            
            elif filter_mode == "Filter by Multi-Tissue Response" and "RootShoot53711" in selected_file:
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
                        key=f"salinity_{selected_file}_min_tissues"
                    )
                    st.caption(f"Gene must pass threshold in at least {min_tissue_count} tissue(s)")
                
                with col2:
                    log2fc_threshold = st.number_input(
                        "log2FC threshold (|log2FC| ≥)",
                        min_value=0.5,
                        max_value=10.0,
                        value=1.5,
                        step=0.1,
                        key=f"salinity_{selected_file}_multi_log2fc"
                    )
                    st.caption(f"Applied to each tissue independently")
                
                use_log2fc = True
            
            elif filter_mode == "Filter by Threshold":
                st.subheader("2. Filter & Threshold Settings")
                
                # File-specific filter options
                if "GSE70377" in selected_file:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        genotype_options = ["All", "Stol (Tolerant)", "Ssen (Sensitive)"]
                        selected_genotype = st.selectbox(
                            "Select genotype:",
                            genotype_options,
                            key=f"salinity_{selected_file}_genotype"
                        )
                    
                    with col2:
                        stage_options = ["Both", "Vegetative (veg)", "Reproductive (rep)"]
                        selected_stage = st.selectbox(
                            "Select stage:",
                            stage_options,
                            key=f"salinity_{selected_file}_stage"
                        )
                
                elif "ICCV_JG" in selected_file and "JG62" not in selected_file:
                    genotype_options = ["All", "ICCV", "JG"]
                    selected_genotype = st.selectbox(
                        "Select genotype:",
                        genotype_options,
                        key=f"salinity_{selected_file}_genotype"
                    )
                
                elif "JG62" in selected_file:
                    condition_options = ["All", "SS (Shoot)", "ST (Root)"]
                    selected_condition = st.selectbox(
                        "Select tissue:",
                        condition_options,
                        key=f"salinity_{selected_file}_condition"
                    )
                
                # Threshold settings
                st.markdown("**Threshold Settings:**")
                col_t1, col_t2 = st.columns(2)
                
                with col_t1:
                    use_log2fc = st.checkbox("Apply log2FC threshold", value=True,
                                            key=f"salinity_{selected_file}_log2fc_enable2")
                
                with col_t2:
                    if use_log2fc:
                        log2fc_threshold = st.number_input(
                            "log2FC threshold (|log2FC| ≥)",
                            min_value=0.5,
                            max_value=10.0,
                            value=1.5,
                            step=0.1,
                            key=f"salinity_{selected_file}_log2fc2"
                        )
            
            st.markdown("---")
            
            # Output options
            st.subheader("3. Output Options")
            show_only_ids = st.checkbox(
                "Show only Ca IDs (hide expression values)",
                value=False,
                key=f"salinity_{selected_file}_show_ids"
            )
            
            st.markdown("---")
            
            if st.button("🚀 Apply Filters", type="primary", key=f"salinity_{selected_file}_apply", use_container_width=True):
                filtered_df = working_df.copy()
                
                # Apply filtering based on mode and file type
                if filter_mode == "View All Data":
                    # No filtering, show all data
                    pass
                
                elif filter_mode == "Filter by Specific Tissue" and "RootShoot53711" in selected_file:
                    # Apply tissue filter for RootShoot53711 dataset
                    if selected_tissue != "Both" and use_log2fc:
                        filtered_df = backend.filter_by_tissue_simple(
                            filtered_df, ca_id_col, selected_tissue, log2fc_threshold
                        )
                    elif selected_tissue != "Both":
                        tissue_cols = [col for col in filtered_df.columns if selected_tissue in col]
                        if tissue_cols:
                            cols_to_keep = [ca_id_col] + tissue_cols
                            filtered_df = filtered_df[cols_to_keep]
                    elif use_log2fc:
                        control_cols = [col for col in filtered_df.columns if 'Control' in col]
                        stress_cols = [col for col in filtered_df.columns if '-SS' in col]
                        if control_cols and stress_cols:
                            filtered_df = backend.filter_by_log2fc_threshold(
                                filtered_df, ca_id_col, control_cols, stress_cols,
                                log2fc_threshold, use_abs=True
                            )
                
                elif filter_mode == "Filter by Multi-Tissue Response" and "RootShoot53711" in selected_file:
                    # Use multi-tissue filtering for RootShoot53711 dataset
                    filtered_df = backend.filter_by_minimum_tissues(
                        filtered_df,
                        ca_id_col,
                        log2fc_threshold,
                        min_tissue_count,
                        control_suffix='Control',
                        stress_suffixes=['SS']
                    )
                
                elif filter_mode == "Filter by Threshold":
                    # Apply filtering based on file type
                    if "RootShoot53711" in selected_file:
                        # This shouldn't normally happen as RootShoot has the multi-tissue option
                        # But handle it just in case
                        if use_log2fc:
                            control_cols = [col for col in filtered_df.columns if 'Control' in col]
                            stress_cols = [col for col in filtered_df.columns if '-SS' in col]
                            if control_cols and stress_cols:
                                filtered_df = backend.filter_by_log2fc_threshold(
                                    filtered_df, ca_id_col, control_cols, stress_cols,
                                    log2fc_threshold, use_abs=True
                                )
                    
                    elif "GSE70377" in selected_file:
                        # Filter by genotype and stage
                        genotype = None
                        if "Stol" in selected_genotype:
                            genotype = "Stol"
                        elif "Ssen" in selected_genotype:
                            genotype = "Ssen"
                        
                        stage = None
                        if "Vegetative" in selected_stage:
                            stage = "Vegetative"
                        elif "Reproductive" in selected_stage:
                            stage = "Reproductive"
                        
                        if genotype or stage:
                            filtered_df = backend.filter_by_genotype_salinity(
                                filtered_df, ca_id_col, genotype, stage,
                                log2fc_threshold if use_log2fc else None
                            )
                        elif use_log2fc:
                            control_cols = [col for col in filtered_df.columns if 'CT' in col]
                            stress_cols = [col for col in filtered_df.columns if 'SS' in col]
                            if control_cols and stress_cols:
                                filtered_df = backend.filter_by_log2fc_threshold(
                                    filtered_df, ca_id_col, control_cols, stress_cols,
                                    log2fc_threshold, use_abs=True
                                )
                    
                    elif "ICCV_JG" in selected_file and "JG62" not in selected_file:
                        if selected_genotype != "All":
                            genotype_cols = [col for col in filtered_df.columns if selected_genotype in col]
                            if genotype_cols:
                                cols_to_keep = [ca_id_col] + genotype_cols
                                filtered_df = filtered_df[cols_to_keep]
                        
                        if use_log2fc:
                            control_cols = [col for col in filtered_df.columns if 'Control' in col]
                            stress_cols = [col for col in filtered_df.columns if 'Stress' in col]
                            if control_cols and stress_cols:
                                filtered_df = backend.filter_by_log2fc_threshold(
                                    filtered_df, ca_id_col, control_cols, stress_cols,
                                    log2fc_threshold, use_abs=True
                                )
                    
                    elif "JG62" in selected_file:
                        if selected_condition != "All":
                            condition_key = "SS" if "Shoot" in selected_condition else "ST"
                            condition_cols = [col for col in filtered_df.columns if condition_key in col]
                            if condition_cols:
                                cols_to_keep = [ca_id_col] + condition_cols
                                filtered_df = filtered_df[cols_to_keep]
                        
                        if use_log2fc:
                            control_cols = [col for col in filtered_df.columns if '-C' in col]
                            stress_cols = [col for col in filtered_df.columns if '-S' in col and '-C' not in col]
                            if control_cols and stress_cols:
                                filtered_df = backend.filter_by_log2fc_threshold(
                                    filtered_df, ca_id_col, control_cols, stress_cols,
                                    log2fc_threshold, use_abs=True
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
                    if use_log2fc:
                        st.info(f"✓ Showing {tissue_desc} with |log2FC| ≥ {log2fc_threshold}")
                    else:
                        st.info(f"✓ Showing {tissue_desc} (no threshold applied)")
                elif filter_mode == "Filter by Threshold":
                    if use_log2fc:
                        st.info(f"✓ Showing genes with |log2FC| ≥ {log2fc_threshold}")
                    else:
                        st.info("✓ Showing all data (no filters applied)")
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
                
                # Display filtered results
                if len(filtered_df) > 0:
                    st.markdown("---")
                    st.markdown("### 📋 Filtered Data")
                    st.dataframe(filtered_df, use_container_width=True, height=400)
                    
                    # Download and save options
                    st.markdown("---")
                    st.markdown("### 💾 Actions")
                    col_act1, col_act2 = st.columns(2)
                    
                    with col_act1:
                        csv_data = backend.create_download_csv(filtered_df)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv_data,
                            file_name=f"salinity_{selected_file}_filtered.csv",
                            mime="text/csv",
                            key=f"salinity_{selected_file}_download",
                            use_container_width=True
                        )
                    
                    # Store for combined analysis
                    ca_ids = backend.get_ca_ids_from_df(filtered_df, ca_id_col)
                    if f'salinity_{selected_file}_filtered_ids' not in st.session_state:
                        st.session_state[f'salinity_{selected_file}_filtered_ids'] = set()
                    st.session_state[f'salinity_{selected_file}_filtered_ids'] = ca_ids
                    st.info(f"💾 Stored {len(ca_ids)} unique Ca IDs for combined analysis")

with tab2:
    st.subheader("Combine Results from Multiple Datasets")
    
    st.write("Select which filtered results to combine:")
    
    # Check which files have been filtered
    available_results = {}
    for name in file_options:
        key = f'salinity_{name}_filtered_ids'
        if key in st.session_state and len(st.session_state[key]) > 0:
            available_results[name] = st.session_state[key]
    
    if len(available_results) == 0:
        st.info("First filter individual files in the 'Individual File Filtering' tab to enable combined analysis")
    else:
        st.markdown("**Available filtered results:**")
        for name, ca_ids in available_results.items():
            st.write(f"• {name}: {len(ca_ids)} Ca IDs")
        
        # Select which results to combine
        selected_for_combine = st.multiselect(
            "Select datasets to combine",
            list(available_results.keys()),
            default=list(available_results.keys()),
            key="salinity_combine_select"
        )
        
        if len(selected_for_combine) > 0:
            # Choose operation
            operation = st.radio(
                "Set operation",
                ["OR (Union)", "AND (Intersection)"],
                key="salinity_operation",
                horizontal=True
            )
            
            operation_type = "OR" if "OR" in operation else "AND"
            
            if st.button("Combine Results", type="primary", key="salinity_combine"):
                ca_id_sets = [available_results[name] for name in selected_for_combine]
                combined_ids = backend.perform_set_operation(ca_id_sets, operation_type)
                
                st.success(f"Combined {len(selected_for_combine)} datasets using {operation_type} operation")
                st.metric("Resulting Ca IDs", len(combined_ids))
                
                # Display the IDs
                st.markdown("**Combined Ca IDs**")
                combined_df = pd.DataFrame(sorted(list(combined_ids)), columns=['Ca_ID'])
                st.dataframe(combined_df, use_container_width=True)
                
                # Action buttons
                col6, col7 = st.columns(2)
                
                with col6:
                    csv_data = backend.create_download_csv(combined_df)
                    st.download_button(
                        label="Download Combined Results",
                        data=csv_data,
                        file_name="salinity_combined_results.csv",
                        mime="text/csv",
                        key="salinity_combined_download"
                    )
                
                with col7:
                    if st.button("Send to Arena", key="salinity_send_arena"):
                        st.session_state.salinity_ca_ids = combined_ids
                        st.success(f"Sent {len(combined_ids)} Ca IDs to Arena")
                        st.info("Navigate to Arena page to perform cross-stress analysis")

# Show current Arena status
st.markdown("---")
st.subheader("Current Arena Status")
col8, col9, col10, col11 = st.columns(4)

with col8:
    st.metric("Cold Ca IDs", len(st.session_state.get('cold_ca_ids', set())))
with col9:
    st.metric("Drought Ca IDs", len(st.session_state.get('drought_ca_ids', set())))
with col10:
    st.metric("Heat Ca IDs", len(st.session_state.get('heat_ca_ids', set())))
with col11:
    st.metric("Salinity Ca IDs", len(st.session_state.get('salinity_ca_ids', set())))

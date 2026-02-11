"""
Heat Stress Analysis Page
Displays and filters multiple cultivar heat stress datasets
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend

st.set_page_config(page_title="Heat Stress Analysis", page_icon="🌡️", layout="wide")

st.title("🌡️ Heat Stress Analysis")

# File paths
FILES = {
    "Cultivar_92944": "data/Cultivar_92944_filtered.csv",
    "Cultivar_15614": "data/Cultivar_15614_filtered.csv",
    "Cultivar_10685": "data/Cultivar_10685_filtered.csv",
    "Cultivar_5912": "data/Cultivar_5912_filtered.csv",
    "Cultivar_4567": "data/Cultivar_4567_filtered.csv",
    "Cultivar_1356": "data/Cultivar_1356_filtered.csv"
}

# Load data
@st.cache_data
def load_heat_data():
    """Load all heat stress cultivar data files."""
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
data_dict = load_heat_data()
h1_df = data_dict["Cultivar_92944"]
h2_df = data_dict["Cultivar_15614"]
h3_df = data_dict["Cultivar_10685"]
h4_df = data_dict["Cultivar_5912"]
h5_df = data_dict["Cultivar_4567"]
h6_df = data_dict["Cultivar_1356"]

# Display all raw data
st.header("Raw Data - Heat Stress Cultivar Datasets")

display_names = {
    "Cultivar_92944": "ICC 92944 (ICCV 92944)",
    "Cultivar_15614": "ICC 15614",
    "Cultivar_10685": "ICC 10685",
    "Cultivar_5912": "ICC 5912",
    "Cultivar_4567": "ICC 4567",
    "Cultivar_1356": "ICC 1356"
}

for name, display_name in display_names.items():
    df = data_dict[name]
    if df is not None:
        st.subheader(f"{display_name} - {FILES[name]}")
        st.dataframe(df, use_container_width=True, height=250)
        st.markdown("---")

# Filtering section
st.header("Filter Options")

st.info("""
**Column Nomenclature:**
- **AFL**: Leaf - Reproductive stage
- **AFR**: Root - Reproductive stage
- **BFL**: Leaf - Vegetative stage
- **BFR**: Root - Vegetative stage
- **_C**: Control condition
- **_S**: Stress condition
""")

# Tab for different filtering modes
tab1, tab2 = st.tabs(["Individual File Filtering", "Combined Filtering"])

with tab1:
    st.subheader("Filter Each Cultivar Individually")
    
    # Select which file to filter
    file_options = [(name, display_names[name]) for name, df in data_dict.items() if df is not None]
    selected_file_tuple = st.selectbox(
        "Select cultivar to filter",
        file_options,
        format_func=lambda x: x[1],
        key="heat_file_select"
    )
    
    if selected_file_tuple:
        selected_file = selected_file_tuple[0]
        working_df = data_dict[selected_file]
        ca_id_col = backend.detect_ca_id_column(working_df)
        
        if ca_id_col:
            # Detect number of tissue-stage combinations
            num_tissues = backend.get_tissue_count(working_df, ca_id_col, 
                                                   control_suffix='_C',
                                                   stress_suffixes=['_S'])
            
            st.markdown("---")
            st.subheader("1. Select Filtering Mode")
            
            if num_tissues > 1:
                filter_mode = st.radio(
                    "Choose how to filter genes:",
                    options=["View All Data", "Filter by Tissue/Stage", "Filter by Multi-Tissue Response"],
                    key=f"heat_{selected_file}_mode",
                    horizontal=False
                )
            else:
                filter_mode = st.radio(
                    "Choose how to filter genes:",
                    options=["View All Data", "Filter by Threshold"],
                    key=f"heat_{selected_file}_mode",
                    horizontal=False
                )
            
            st.markdown("---")
            
            # Initialize variables
            use_log2fc = False
            log2fc_threshold = 1.5
            selected_tissue = "Both"
            selected_stage = "Both"
            min_tissue_count = 1
            
            # Mode-specific options
            if filter_mode == "Filter by Tissue/Stage":
                st.subheader("2. Tissue, Stage & Threshold Settings")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    tissue_options = ["Both", "Leaf", "Root"]
                    selected_tissue = st.selectbox(
                        "Select tissue type:",
                        tissue_options,
                        key=f"heat_{selected_file}_tissue"
                    )
                
                with col2:
                    stage_options = ["Both", "Reproductive (AF)", "Vegetative (BF)"]
                    selected_stage = st.selectbox(
                        "Select development stage:",
                        stage_options,
                        key=f"heat_{selected_file}_stage"
                    )
                
                with col3:
                    use_log2fc = st.checkbox(
                        "Apply log2FC threshold",
                        value=True,
                        key=f"heat_{selected_file}_log2fc_enable"
                    )
                    
                    if use_log2fc:
                        log2fc_threshold = st.number_input(
                            "log2FC threshold (|log2FC| ≥)",
                            min_value=0.5,
                            max_value=10.0,
                            value=1.5,
                            step=0.1,
                            key=f"heat_{selected_file}_log2fc"
                        )
            
            elif filter_mode == "Filter by Multi-Tissue Response":
                st.subheader("2. Multi-Tissue Response Settings")
                st.info(f"📊 This dataset contains **{num_tissues} tissue-stage combinations** (Leaf/Root × Reproductive/Vegetative)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    min_tissue_count = st.number_input(
                        f"Minimum number of tissue-stage combinations:",
                        min_value=1,
                        max_value=num_tissues,
                        value=min(2, num_tissues),
                        step=1,
                        key=f"heat_{selected_file}_min_tissues"
                    )
                    st.caption(f"Gene must pass threshold in at least {min_tissue_count} combination(s)")
                
                with col2:
                    log2fc_threshold = st.number_input(
                        "log2FC threshold (|log2FC| ≥)",
                        min_value=0.5,
                        max_value=10.0,
                        value=1.5,
                        step=0.1,
                        key=f"heat_{selected_file}_multi_log2fc"
                    )
                    st.caption(f"Applied to each tissue-stage combination")
                
                use_log2fc = True
            
            elif filter_mode == "Filter by Threshold":
                st.subheader("2. Threshold Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    use_log2fc = st.checkbox("Apply log2FC threshold", value=True,
                                            key=f"heat_{selected_file}_log2fc_enable2")
                
                with col2:
                    if use_log2fc:
                        log2fc_threshold = st.number_input(
                            "log2FC threshold (|log2FC| ≥)",
                            min_value=0.5,
                            max_value=10.0,
                            value=1.5,
                            step=0.1,
                            key=f"heat_{selected_file}_log2fc2"
                        )
            
            st.markdown("---")
            
            # Output options
            st.subheader("3. Output Options")
            show_only_ids = st.checkbox(
                "Show only Ca IDs (hide expression values)",
                value=False,
                key=f"heat_{selected_file}_show_ids"
            )
            
            st.markdown("---")
            
            if st.button("🚀 Apply Filters", type="primary", key=f"heat_{selected_file}_apply", use_container_width=True):
                filtered_df = working_df.copy()
                
                # Apply filtering based on mode
                if filter_mode == "View All Data":
                    # No filtering, show all data
                    pass
                
                elif filter_mode == "Filter by Tissue/Stage":
                    # Build filter pattern
                    tissue_letter = None
                    if selected_tissue == "Leaf":
                        tissue_letter = "L"
                    elif selected_tissue == "Root":
                        tissue_letter = "R"
                    
                    stage_prefix = None
                    if "Reproductive" in selected_stage:
                        stage_prefix = "AF"
                    elif "Vegetative" in selected_stage:
                        stage_prefix = "BF"
                    
                    # Apply tissue/stage filters
                    if stage_prefix or tissue_letter:
                        if stage_prefix and tissue_letter:
                            pattern = f"{stage_prefix}{tissue_letter}"
                        elif tissue_letter:
                            pattern = f"F{tissue_letter}"
                        elif stage_prefix:
                            pattern = stage_prefix
                        else:
                            pattern = None
                        
                        if pattern:
                            # Filter columns
                            matching_cols = [col for col in filtered_df.columns if pattern in col]
                            if matching_cols:
                                cols_to_keep = [ca_id_col] + matching_cols
                                filtered_df = filtered_df[cols_to_keep]
                    
                    # Apply log2FC threshold
                    if use_log2fc:
                        abs_log2fc_cols = [col for col in filtered_df.columns if 'abs_log2FC' in col]
                        
                        if abs_log2fc_cols:
                            mask = (filtered_df[abs_log2fc_cols] >= log2fc_threshold).any(axis=1)
                            filtered_df = filtered_df[mask]
                        else:
                            control_cols = [col for col in filtered_df.columns if '_C' in col and 'log2FC' not in col]
                            stress_cols = [col for col in filtered_df.columns if '_S' in col and 'log2FC' not in col]
                            
                            if control_cols and stress_cols:
                                filtered_df = backend.filter_by_log2fc_threshold(
                                    filtered_df, ca_id_col, control_cols, stress_cols,
                                    log2fc_threshold, use_abs=True
                                )
                
                elif filter_mode == "Filter by Multi-Tissue Response":
                    # Use multi-tissue filtering
                    filtered_df = backend.filter_by_minimum_tissues(
                        filtered_df,
                        ca_id_col,
                        log2fc_threshold,
                        min_tissue_count,
                        control_suffix='_C',
                        stress_suffixes=['_S']
                    )
                
                elif filter_mode == "Filter by Threshold":
                    # Apply log2FC threshold to all columns
                    if use_log2fc:
                        abs_log2fc_cols = [col for col in filtered_df.columns if 'abs_log2FC' in col]
                        
                        if abs_log2fc_cols:
                            mask = (filtered_df[abs_log2fc_cols] >= log2fc_threshold).any(axis=1)
                            filtered_df = filtered_df[mask]
                        else:
                            control_cols = [col for col in filtered_df.columns if '_C' in col and 'log2FC' not in col]
                            stress_cols = [col for col in filtered_df.columns if '_S' in col and 'log2FC' not in col]
                            
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
                    st.info(f"✓ Showing genes responsive in **≥{min_tissue_count} tissue-stage combinations** with |log2FC| ≥ {log2fc_threshold}")
                elif filter_mode == "Filter by Tissue/Stage":
                    tissue_desc = selected_tissue if selected_tissue != "Both" else "all tissues"
                    stage_desc = selected_stage if selected_stage != "Both" else "all stages"
                    if use_log2fc:
                        st.info(f"✓ Showing {tissue_desc}, {stage_desc} with |log2FC| ≥ {log2fc_threshold}")
                    else:
                        st.info(f"✓ Showing {tissue_desc}, {stage_desc} (no threshold applied)")
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
                            file_name=f"heat_{selected_file}_filtered.csv",
                            mime="text/csv",
                            key=f"heat_{selected_file}_download",
                            use_container_width=True
                        )
                    
                    # Store for combined analysis
                    ca_ids = backend.get_ca_ids_from_df(filtered_df, ca_id_col)
                    if f'heat_{selected_file}_filtered_ids' not in st.session_state:
                        st.session_state[f'heat_{selected_file}_filtered_ids'] = set()
                    st.session_state[f'heat_{selected_file}_filtered_ids'] = ca_ids
                    st.info(f"💾 Stored {len(ca_ids)} unique Ca IDs for combined analysis")

with tab2:
    st.subheader("Combine Results from Multiple Cultivars")
    
    st.write("Select which filtered results to combine:")
    
    # Check which files have been filtered
    available_results = {}
    for name in [f[0] for f in file_options]:
        key = f'heat_{name}_filtered_ids'
        if key in st.session_state and len(st.session_state[key]) > 0:
            available_results[name] = st.session_state[key]
    
    if len(available_results) == 0:
        st.info("First filter individual cultivars in the 'Individual File Filtering' tab to enable combined analysis")
    else:
        st.markdown("**Available filtered results:**")
        for name, ca_ids in available_results.items():
            st.write(f"• {display_names[name]}: {len(ca_ids)} Ca IDs")
        
        # Select which results to combine
        selected_for_combine = st.multiselect(
            "Select cultivars to combine",
            list(available_results.keys()),
            format_func=lambda x: display_names[x],
            default=list(available_results.keys()),
            key="heat_combine_select"
        )
        
        if len(selected_for_combine) > 0:
            # Choose operation
            operation = st.radio(
                "Set operation",
                ["OR (Union)", "AND (Intersection)"],
                key="heat_operation",
                horizontal=True
            )
            
            operation_type = "OR" if "OR" in operation else "AND"
            
            if st.button("Combine Results", type="primary", key="heat_combine"):
                ca_id_sets = [available_results[name] for name in selected_for_combine]
                combined_ids = backend.perform_set_operation(ca_id_sets, operation_type)
                
                st.success(f"Combined {len(selected_for_combine)} cultivars using {operation_type} operation")
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
                        file_name="heat_combined_results.csv",
                        mime="text/csv",
                        key="heat_combined_download"
                    )
                
                with col7:
                    if st.button("Send to Arena", key="heat_send_arena"):
                        st.session_state.heat_ca_ids = combined_ids
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

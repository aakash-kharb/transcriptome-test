"""
Overall Results Page
Shows Ca IDs across all stress conditions
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import backend

# Page config
st.set_page_config(page_title="Overall Results", page_icon="📊", layout="wide")

st.title("📊 Overall Results")
st.markdown("### Comprehensive analysis of Ca IDs across all stress conditions")

# Define file groups
DATA_DIR = Path(__file__).parent.parent / "data"

FILE_GROUPS = {
    "Cold": [
        "Cold_Top.csv"
    ],
    "Drought": [
        "Drought_53711_Top.csv",
        "DroughtICC4958-1882_Top.csv",
        "Drought_ICC2861-283_Top.csv"
    ],
    "Heat": [
        "Cultivar_10685_filtered.csv",
        "Cultivar_1356_filtered.csv",
        "Cultivar_15614_filtered.csv",
        "Cultivar_4567_filtered.csv",
        "Cultivar_5912_filtered.csv",
        "Cultivar_92944_filtered.csv"
    ],
    "Salinity": [
        "SalinityGSE70377_Top.csv",
        "SalinityICCV2-JG62_Top.csv",
        "SalinityRootShoot53711_Top.csv",
        "Salinity_ICCV_JG_Top.csv"
    ]
}

# Threshold settings: minimum number of files a Ca ID must appear in
THRESHOLDS = {
    "Cold": 1,      # Single file, so 1 out of 1
    "Drought": 2,   # At least 2 out of 3 files
    "Heat": 6,      # 6 out of 6 files (change this variable as needed)
    "Salinity": 3   # At least 3 out of 4 files
}

@st.cache_data
def load_ca_ids_from_file(filepath):
    """Load Ca IDs from a single file."""
    try:
        df = pd.read_csv(filepath)
        ca_id_col = backend.detect_ca_id_column(df)
        
        if ca_id_col:
            # Get unique Ca IDs
            ca_ids = set(df[ca_id_col].dropna().astype(str).unique())
            return ca_ids
        return set()
    except Exception as e:
        st.error(f"Error loading {filepath.name}: {e}")
        return set()

@st.cache_data
def get_ca_ids_for_stress_type(stress_type, files, threshold):
    """Get Ca IDs for a stress type based on threshold."""
    all_sets = []
    file_details = []
    
    for filename in files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            ca_ids = load_ca_ids_from_file(filepath)
            all_sets.append(ca_ids)
            file_details.append({
                'filename': filename,
                'count': len(ca_ids)
            })
    
    if not all_sets:
        return set(), [], file_details, 0
    
    # Count how many files each Ca ID appears in
    from collections import Counter
    ca_id_counter = Counter()
    for ca_set in all_sets:
        for ca_id in ca_set:
            ca_id_counter[ca_id] += 1
    
    # Filter Ca IDs that appear in at least 'threshold' files
    result_ids = {ca_id for ca_id, count in ca_id_counter.items() if count >= threshold}
    
    return result_ids, all_sets, file_details, threshold

# Main content
st.markdown("---")

# Process each stress type
for stress_type, files in FILE_GROUPS.items():
    st.header(f"{stress_type} Stress")
    
    threshold = THRESHOLDS[stress_type]
    result_ids, all_sets, file_details, _ = get_ca_ids_for_stress_type(stress_type, files, threshold)
    
    # Display file information
    with st.expander(f"📁 Files Included ({len(files)} files)", expanded=False):
        for detail in file_details:
            st.write(f"• {detail['filename']}: {detail['count']:,} Ca IDs")
    
    # Display results
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.metric("Files Analyzed", len(file_details))
    
    with col2:
        st.metric(f"Ca IDs (in ≥{threshold}/{len(files)} files)", len(result_ids))
    
    with col3:
        if len(all_sets) > 1:
            # Calculate union (IDs in ANY file)
            union_ids = set.union(*all_sets)
            st.metric("Ca IDs in ANY file", len(union_ids))
    
    # Display Ca IDs
    if result_ids:
        with st.expander(f"📋 View Ca IDs ({len(result_ids)} IDs)", expanded=False):
            # Convert to sorted list for display
            sorted_ids = sorted(result_ids, key=lambda x: int(x.replace('Ca_', '')) if 'Ca_' in x else 0)
            
            # Create dataframe for better display
            display_df = pd.DataFrame({'Ca_ID': sorted_ids})
            display_df.index = display_df.index + 1  # Start index from 1
            
            st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label=f"⬇️ Download {stress_type} Ca IDs",
                data=csv,
                file_name=f"{stress_type}_Ca_IDs.csv",
                mime="text/csv"
            )
    else:
        st.warning(f"No Ca IDs found for {stress_type} stress.")
    
    st.markdown("---")

# Summary section
st.header("📈 Summary Across All Stress Types")

summary_data = []
for stress_type, files in FILE_GROUPS.items():
    threshold = THRESHOLDS[stress_type]
    result_ids, all_sets, file_details, _ = get_ca_ids_for_stress_type(stress_type, files, threshold)
    
    summary_data.append({
        'Stress Type': stress_type,
        'Files': len(file_details),
        'Threshold': f"{threshold}/{len(file_details)}",
        'Ca IDs': len(result_ids),
        'Description': f'Present in ≥{threshold} file(s)'
    })

summary_df = pd.DataFrame(summary_data)
st.dataframe(summary_df, use_container_width=True, hide_index=True)

# Overall statistics
total_unique_ca_ids = set()
for stress_type, files in FILE_GROUPS.items():
    threshold = THRESHOLDS[stress_type]
    result_ids, _, _, _ = get_ca_ids_for_stress_type(stress_type, files, threshold)
    total_unique_ca_ids.update(result_ids)

st.info(f"**Total unique Ca IDs across all stress conditions:** {len(total_unique_ca_ids):,}")

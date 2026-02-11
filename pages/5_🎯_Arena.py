"""
Arena Page - Cross-Stress Analysis
Perform AND/OR operations on Ca IDs from different stress types
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import backend

st.set_page_config(page_title="Arena - Cross-Stress Analysis", page_icon="🎯", layout="wide")

st.title("🎯 Arena - Cross-Stress Analysis")

st.markdown("""
Welcome to the **Arena**! This is where you can perform cross-stress analysis by combining 
Ca IDs from different stress types using AND/OR operations.

### How to use Arena:
1. First, filter genes on individual stress pages (Cold, Drought, Heat, Salinity)
2. Send filtered Ca IDs to Arena using the "Send to Arena" button
3. Select which stress types to combine
4. Choose AND (intersection) or OR (union) operation
5. View and download the combined results
""")

st.markdown("---")

# Display current Arena status
st.header("📊 Current Arena Status")

col1, col2, col3, col4 = st.columns(4)

cold_ids = st.session_state.get('cold_ca_ids', set())
drought_ids = st.session_state.get('drought_ca_ids', set())
heat_ids = st.session_state.get('heat_ca_ids', set())
salinity_ids = st.session_state.get('salinity_ca_ids', set())

with col1:
    st.metric("❄️ Cold Stress", len(cold_ids))
    if len(cold_ids) > 0:
        with st.expander("View Ca IDs"):
            st.write(sorted(list(cold_ids))[:20])  # Show first 20
            if len(cold_ids) > 20:
                st.write(f"... and {len(cold_ids) - 20} more")

with col2:
    st.metric("🌵 Drought Stress", len(drought_ids))
    if len(drought_ids) > 0:
        with st.expander("View Ca IDs"):
            st.write(sorted(list(drought_ids))[:20])
            if len(drought_ids) > 20:
                st.write(f"... and {len(drought_ids) - 20} more")

with col3:
    st.metric("🌡️ Heat Stress", len(heat_ids))
    if len(heat_ids) > 0:
        with st.expander("View Ca IDs"):
            st.write(sorted(list(heat_ids))[:20])
            if len(heat_ids) > 20:
                st.write(f"... and {len(heat_ids) - 20} more")

with col4:
    st.metric("🧂 Salinity Stress", len(salinity_ids))
    if len(salinity_ids) > 0:
        with st.expander("View Ca IDs"):
            st.write(sorted(list(salinity_ids))[:20])
            if len(salinity_ids) > 20:
                st.write(f"... and {len(salinity_ids) - 20} more")

st.markdown("---")

# Check if any stress types have Ca IDs
available_stress_types = {}
if len(cold_ids) > 0:
    available_stress_types["❄️ Cold Stress"] = cold_ids
if len(drought_ids) > 0:
    available_stress_types["🌵 Drought Stress"] = drought_ids
if len(heat_ids) > 0:
    available_stress_types["🌡️ Heat Stress"] = heat_ids
if len(salinity_ids) > 0:
    available_stress_types["🧂 Salinity Stress"] = salinity_ids

if len(available_stress_types) == 0:
    st.warning("""
    ⚠️ No Ca IDs available in Arena yet!
    
    Please navigate to stress type pages and send filtered Ca IDs to Arena.
    """)
else:
    # Cross-stress analysis section
    st.header("🔬 Cross-Stress Analysis")
    
    col5, col6 = st.columns([2, 1])
    
    with col5:
        st.subheader("Select Stress Types to Combine")
        selected_stresses = st.multiselect(
            "Choose 2 or more stress types",
            list(available_stress_types.keys()),
            default=list(available_stress_types.keys()) if len(available_stress_types) >= 2 else None,
            key="arena_stress_select"
        )
    
    with col6:
        st.subheader("Set Operation")
        operation = st.radio(
            "Select operation",
            ["AND (Intersection)", "OR (Union)"],
            key="arena_operation",
            help="AND: Genes present in ALL selected stress types\nOR: Genes present in ANY selected stress type"
        )
    
    if len(selected_stresses) < 2:
        st.info("ℹ️ Please select at least 2 stress types to perform analysis")
    else:
        st.markdown("---")
        
        # Show summary before combining
        st.subheader("📋 Selected Stress Types Summary")
        summary_data = []
        for stress in selected_stresses:
            summary_data.append({
                "Stress Type": stress,
                "Number of Ca IDs": len(available_stress_types[stress])
            })
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        # Perform analysis button
        if st.button("🔗 Perform Cross-Stress Analysis", type="primary", key="arena_analyze"):
            operation_type = "AND" if "AND" in operation else "OR"
            
            # Get selected Ca ID sets
            selected_sets = [available_stress_types[stress] for stress in selected_stresses]
            
            # Perform operation
            result_ids = backend.perform_set_operation(selected_sets, operation_type)
            
            st.success(f"✅ Analysis complete using {operation_type} operation")
            
            # Display results
            st.markdown("---")
            st.header("📈 Analysis Results")
            
            col7, col8 = st.columns(2)
            
            with col7:
                st.metric("Resulting Ca IDs", len(result_ids))
            
            with col8:
                if operation_type == "AND":
                    st.info("These genes are present in ALL selected stress types")
                else:
                    st.info("These genes are present in at least ONE of the selected stress types")
            
            # Create result dataframe
            if len(result_ids) > 0:
                result_df = pd.DataFrame(sorted(list(result_ids)), columns=['Ca_ID'])
                
                st.subheader("📊 Ca IDs Result Table")
                st.dataframe(result_df, use_container_width=True, height=400)
                
                # Download options
                st.markdown("---")
                st.subheader("💾 Download Results")
                
                col9, col10 = st.columns(2)
                
                with col9:
                    csv_data = backend.create_download_csv(result_df)
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=csv_data,
                        file_name=f"arena_{operation_type}_results.csv",
                        mime="text/csv",
                        key="arena_download"
                    )
                
                with col10:
                    # Create detailed report
                    report_data = []
                    for ca_id in sorted(list(result_ids)):
                        presence = []
                        for stress_name, stress_set in available_stress_types.items():
                            if ca_id in stress_set:
                                presence.append(stress_name)
                        
                        report_data.append({
                            'Ca_ID': ca_id,
                            'Present_in': ', '.join(presence),
                            'Number_of_stresses': len(presence)
                        })
                    
                    report_df = pd.DataFrame(report_data)
                    report_csv = backend.create_download_csv(report_df)
                    
                    st.download_button(
                        label="⬇️ Download Detailed Report",
                        data=report_csv,
                        file_name=f"arena_{operation_type}_detailed_report.csv",
                        mime="text/csv",
                        key="arena_report_download"
                    )
                
                # Visualization - Stress type presence distribution
                st.markdown("---")
                st.subheader("📊 Distribution by Stress Type Presence")
                
                if operation_type == "OR":
                    stress_count_dist = {}
                    for ca_id in result_ids:
                        count = sum(1 for stress_set in available_stress_types.values() if ca_id in stress_set)
                        if count not in stress_count_dist:
                            stress_count_dist[count] = 0
                        stress_count_dist[count] += 1
                    
                    dist_df = pd.DataFrame([
                        {"Number of Stress Types": k, "Number of Genes": v}
                        for k, v in sorted(stress_count_dist.items())
                    ])
                    
                    st.dataframe(dist_df, use_container_width=True, hide_index=True)
                    
                    # Show genes unique to single stress
                    if 1 in stress_count_dist:
                        with st.expander(f"View genes unique to single stress type ({stress_count_dist[1]} genes)"):
                            unique_genes = []
                            for ca_id in result_ids:
                                count = sum(1 for stress_set in available_stress_types.values() if ca_id in stress_set)
                                if count == 1:
                                    for stress_name, stress_set in available_stress_types.items():
                                        if ca_id in stress_set:
                                            unique_genes.append({'Ca_ID': ca_id, 'Stress_Type': stress_name})
                                            break
                            unique_df = pd.DataFrame(unique_genes)
                            st.dataframe(unique_df, use_container_width=True, hide_index=True)
                    
                    # Show genes common to all stresses
                    max_count = max(stress_count_dist.keys())
                    if max_count == len(selected_stresses) and len(selected_stresses) > 1:
                        with st.expander(f"View genes common to ALL stress types ({stress_count_dist[max_count]} genes)"):
                            common_genes = []
                            for ca_id in result_ids:
                                count = sum(1 for stress_set in available_stress_types.values() if ca_id in stress_set)
                                if count == max_count:
                                    common_genes.append({'Ca_ID': ca_id})
                            common_df = pd.DataFrame(common_genes)
                            st.dataframe(common_df, use_container_width=True, hide_index=True)
                
            else:
                st.warning(f"⚠️ No common genes found using {operation_type} operation")
                st.info("Try using OR operation to find genes present in any of the selected stress types")

# Management section
st.markdown("---")
st.header("🗑️ Manage Arena Data")

col11, col12, col13 = st.columns(3)

with col11:
    if st.button("Clear All Arena Data", key="arena_clear_all"):
        st.session_state.cold_ca_ids = set()
        st.session_state.drought_ca_ids = set()
        st.session_state.heat_ca_ids = set()
        st.session_state.salinity_ca_ids = set()
        st.success("✅ All Arena data cleared!")
        st.rerun()

with col12:
    stress_to_clear = st.selectbox(
        "Select stress type to clear",
        ["Cold", "Drought", "Heat", "Salinity"],
        key="arena_stress_clear_select"
    )
    
    if st.button(f"Clear {stress_to_clear} Data", key="arena_clear_single"):
        if stress_to_clear == "Cold":
            st.session_state.cold_ca_ids = set()
        elif stress_to_clear == "Drought":
            st.session_state.drought_ca_ids = set()
        elif stress_to_clear == "Heat":
            st.session_state.heat_ca_ids = set()
        elif stress_to_clear == "Salinity":
            st.session_state.salinity_ca_ids = set()
        st.success(f"✅ {stress_to_clear} data cleared!")
        st.rerun()

with col13:
    st.markdown("### Quick Stats")
    total_unique_genes = len(cold_ids | drought_ids | heat_ids | salinity_ids)
    st.metric("Total Unique Ca IDs", total_unique_genes)

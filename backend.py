"""
Backend functions for filtering and analyzing gene expression data.
Handles log2FC calculations, tissue filtering, and set operations on Ca IDs.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Optional, Tuple


def calculate_log2fc(control_val: float, stress_val: float) -> float:
    """Calculate log2 fold change between stress and control values."""
    if control_val == 0:
        return np.inf if stress_val > 0 else 0
    return np.log2(stress_val / control_val)


def filter_by_log2fc_threshold(df: pd.DataFrame, ca_id_col: str, 
                                 control_cols: List[str], stress_cols: List[str],
                                 threshold: float, use_abs: bool = True) -> pd.DataFrame:
    """
    Filter dataframe by log2FC threshold.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        control_cols: List of control column names
        stress_cols: List of stress column names
        threshold: log2FC threshold value
        use_abs: If True, use absolute value of log2FC
    
    Returns:
        Filtered dataframe
    """
    result_df = df.copy()
    
    # Check if log2FC columns already exist
    has_log2fc = any('log2FC' in col or 'log2fc' in col.lower() for col in df.columns)
    
    if has_log2fc:
        # Use existing log2FC columns
        log2fc_cols = [col for col in df.columns if 'log2FC' in col or 'log2fc' in col.lower()]
        
        if use_abs:
            # Check if abs columns exist
            abs_cols = [col for col in df.columns if 'abs_log2FC' in col or 'abs_log2fc' in col.lower()]
            if abs_cols:
                mask = (result_df[abs_cols] >= threshold).any(axis=1)
            else:
                mask = (result_df[log2fc_cols].abs() >= threshold).any(axis=1)
        else:
            mask = (result_df[log2fc_cols] >= threshold).any(axis=1)
    else:
        # Calculate log2FC on the fly
        log2fc_values = []
        for ctrl_col, stress_col in zip(control_cols, stress_cols):
            if ctrl_col in df.columns and stress_col in df.columns:
                log2fc = df.apply(lambda row: calculate_log2fc(row[ctrl_col], row[stress_col]), axis=1)
                log2fc_values.append(log2fc.abs() if use_abs else log2fc)
        
        if log2fc_values:
            log2fc_df = pd.concat(log2fc_values, axis=1)
            mask = (log2fc_df >= threshold).any(axis=1)
        else:
            mask = pd.Series([False] * len(df))
    
    return result_df[mask]


def filter_by_tissue_simple(df: pd.DataFrame, ca_id_col: str, 
                            tissue_keyword: str, threshold: float = None) -> pd.DataFrame:
    """
    Filter by tissue type for simple files (like Cold, Drought_53711).
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        tissue_keyword: 'Root' or 'Shoot'
        threshold: Optional log2FC threshold
    
    Returns:
        Filtered dataframe
    """
    # Find columns matching the tissue type
    tissue_cols = [col for col in df.columns if tissue_keyword in col]
    
    if not tissue_cols:
        return df
    
    # Select only Ca ID and tissue-related columns
    cols_to_keep = [ca_id_col] + tissue_cols
    result_df = df[cols_to_keep].copy()
    
    # If threshold provided, filter by log2FC
    if threshold is not None:
        control_cols = [col for col in tissue_cols if 'Control' in col]
        stress_cols = [col for col in tissue_cols if any(s in col for s in ['Stress', 'CS', 'DS', 'SS'])]
        
        if control_cols and stress_cols:
            result_df = filter_by_log2fc_threshold(result_df, ca_id_col, control_cols, 
                                                    stress_cols, threshold, use_abs=True)
    
    return result_df


def filter_by_tissue_cultivar(df: pd.DataFrame, ca_id_col: str,
                               tissue_keyword: str, stage: str = None,
                               threshold: float = None) -> pd.DataFrame:
    """
    Filter by tissue type for cultivar files (Heat stress).
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        tissue_keyword: 'Root' or 'Leaf'
        stage: 'Reproductive' (AF) or 'Vegetative' (BF), or None for both
        threshold: Optional log2FC threshold based on abs_log2FC columns
    
    Returns:
        Filtered dataframe
    """
    # Determine stage prefix
    stage_prefix = None
    if stage == 'Reproductive':
        stage_prefix = 'AF'
    elif stage == 'Vegetative':
        stage_prefix = 'BF'
    
    # Find matching columns
    if tissue_keyword == 'Root':
        tissue_letter = 'R'
    elif tissue_keyword == 'Leaf':
        tissue_letter = 'L'
    else:
        tissue_letter = None
    
    # Build column filter
    if stage_prefix and tissue_letter:
        pattern = f'{stage_prefix}{tissue_letter}'
    elif tissue_letter:
        pattern = f'F{tissue_letter}'
    else:
        pattern = None
    
    if pattern:
        matching_cols = [col for col in df.columns if pattern in col]
    else:
        matching_cols = [col for col in df.columns if ca_id_col not in col]
    
    cols_to_keep = [ca_id_col] + matching_cols
    result_df = df[[col for col in cols_to_keep if col in df.columns]].copy()
    
    # Filter by threshold if provided
    if threshold is not None and pattern:
        log2fc_col = f'abs_log2FC_{pattern}'
        if log2fc_col in df.columns:
            result_df = df[df[log2fc_col] >= threshold].copy()
        else:
            # Fallback: use any abs_log2FC columns with the pattern
            abs_cols = [col for col in df.columns if 'abs_log2FC' in col and pattern in col]
            if abs_cols:
                mask = (df[abs_cols] >= threshold).any(axis=1)
                result_df = df[mask].copy()
    
    return result_df


def filter_by_genotype_salinity(df: pd.DataFrame, ca_id_col: str,
                                genotype: str = None, stage: str = None,
                                threshold: float = None) -> pd.DataFrame:
    """
    Filter salinity data by genotype and stage.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        genotype: Genotype name (e.g., 'ICCV', 'JG', 'Stol', 'Ssen')
        stage: 'Vegetative' (veg) or 'Reproductive' (rep) for GSE files
        threshold: Optional log2FC threshold
    
    Returns:
        Filtered dataframe
    """
    if genotype:
        # Find columns matching genotype
        genotype_cols = [col for col in df.columns if genotype in col]
    else:
        genotype_cols = [col for col in df.columns if ca_id_col not in col]
    
    if stage and stage in ['Vegetative', 'Reproductive']:
        stage_key = 'veg' if stage == 'Vegetative' else 'rep'
        genotype_cols = [col for col in genotype_cols if stage_key in col]
    
    cols_to_keep = [ca_id_col] + genotype_cols
    result_df = df[[col for col in cols_to_keep if col in df.columns]].copy()
    
    # Apply threshold if provided
    if threshold is not None:
        control_cols = [col for col in genotype_cols if any(c in col for c in ['Control', 'CT', '-C'])]
        stress_cols = [col for col in genotype_cols if any(s in col for s in ['Stress', 'SS', '-S', '-D'])]
        
        if control_cols and stress_cols:
            result_df = filter_by_log2fc_threshold(result_df, ca_id_col, control_cols,
                                                    stress_cols, threshold, use_abs=True)
    
    return result_df


def filter_by_minimum_tissues(df: pd.DataFrame, ca_id_col: str, 
                              threshold: float, min_tissue_count: int,
                              control_suffix: str = 'Control',
                              stress_suffixes: List[str] = None) -> pd.DataFrame:
    """
    Filter genes that pass |log2FC| threshold in at least N tissues.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        threshold: log2FC threshold value (|log2FC| >= threshold)
        min_tissue_count: Minimum number of tissues where gene must be responsive
        control_suffix: Suffix identifying control columns (default: 'Control')
        stress_suffixes: List of suffixes identifying stress columns (default: ['CS', 'DS', 'SS', 'Stress'])
    
    Returns:
        Filtered dataframe with genes meeting the minimum tissue count criterion
    """
    if stress_suffixes is None:
        stress_suffixes = ['CS', 'DS', 'SS', 'Stress', '-S', '-D']
    
    # Identify tissue types by extracting prefixes
    # For Cold: Root-Control, Root-CS -> tissue = Root
    # For Drought: Shoot-Control, Shoot-DS -> tissue = Shoot
    tissue_map = {}
    
    for col in df.columns:
        if col == ca_id_col:
            continue
            
        # Extract tissue name (part before the hyphen or underscore)
        if '-' in col:
            tissue_name = col.split('-')[0]
        elif '_' in col:
            tissue_name = col.split('_')[0]
        else:
            continue
            
        if tissue_name not in tissue_map:
            tissue_map[tissue_name] = {'control': None, 'stress': []}
        
        # Classify as control or stress
        if control_suffix in col:
            tissue_map[tissue_name]['control'] = col
        elif any(suffix in col for suffix in stress_suffixes):
            tissue_map[tissue_name]['stress'].append(col)
    
    # Remove tissues without both control and stress
    valid_tissues = {k: v for k, v in tissue_map.items() 
                     if v['control'] is not None and len(v['stress']) > 0}
    
    if not valid_tissues:
        return pd.DataFrame()
    
    # For each gene, count tissues where |log2FC| >= threshold
    def count_responsive_tissues(row):
        count = 0
        for tissue_name, cols in valid_tissues.items():
            control_col = cols['control']
            stress_col = cols['stress'][0]  # Use first stress column
            
            control_val = row[control_col]
            stress_val = row[stress_col]
            
            # Calculate log2FC
            if control_val > 0:
                log2fc = calculate_log2fc(control_val, stress_val)
                if abs(log2fc) >= threshold:
                    count += 1
            elif stress_val > 0:  # Control is 0, stress is not
                count += 1
        
        return count
    
    # Apply filter
    df_copy = df.copy()
    df_copy['_tissue_count'] = df_copy.apply(count_responsive_tissues, axis=1)
    filtered_df = df_copy[df_copy['_tissue_count'] >= min_tissue_count].copy()
    
    # Remove helper column
    if '_tissue_count' in filtered_df.columns:
        filtered_df = filtered_df.drop(columns=['_tissue_count'])
    
    return filtered_df


def get_tissue_count(df: pd.DataFrame, ca_id_col: str,
                    control_suffix: str = 'Control',
                    stress_suffixes: List[str] = None) -> int:
    """
    Count the number of distinct tissues in the dataframe.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        control_suffix: Suffix identifying control columns
        stress_suffixes: List of suffixes identifying stress columns
    
    Returns:
        Number of distinct tissues
    """
    if stress_suffixes is None:
        stress_suffixes = ['CS', 'DS', 'SS', 'Stress', '-S', '-D']
    
    tissues = set()
    for col in df.columns:
        if col == ca_id_col:
            continue
        
        if '-' in col:
            tissue_name = col.split('-')[0]
        elif '_' in col:
            tissue_name = col.split('_')[0]
        else:
            continue
        
        # Only count if it's a control or stress column
        if control_suffix in col or any(suffix in col for suffix in stress_suffixes):
            tissues.add(tissue_name)
    
    return len(tissues)


def get_ca_ids_from_df(df: pd.DataFrame, ca_id_col: str) -> Set[str]:
    """Extract unique Ca IDs from dataframe."""
    if ca_id_col in df.columns:
        return set(df[ca_id_col].dropna().astype(str).tolist())
    return set()


def detect_duplicates(df: pd.DataFrame, ca_id_col: str) -> tuple:
    """
    Detect duplicate Ca IDs in a dataframe.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
    
    Returns:
        Tuple of (total_count, unique_count, duplicate_df)
        - total_count: Total number of rows
        - unique_count: Number of unique Ca IDs
        - duplicate_df: DataFrame containing only duplicate entries with occurrence counts
    """
    if ca_id_col not in df.columns:
        return 0, 0, pd.DataFrame()
    
    total_count = len(df)
    unique_count = df[ca_id_col].nunique()
    
    # Find duplicates
    duplicates = df[df.duplicated(subset=[ca_id_col], keep=False)]
    
    if len(duplicates) > 0:
        # Get count of each duplicate
        duplicate_counts = duplicates[ca_id_col].value_counts().reset_index()
        duplicate_counts.columns = [ca_id_col, 'Occurrence_Count']
        
        # Merge to get full duplicate rows with counts
        duplicate_df = duplicates.merge(duplicate_counts, on=ca_id_col)
        duplicate_df = duplicate_df.sort_values([ca_id_col, 'Occurrence_Count'], ascending=[True, False])
    else:
        duplicate_df = pd.DataFrame()
    
    return total_count, unique_count, duplicate_df


def perform_set_operation(ca_id_sets: List[Set[str]], operation: str) -> Set[str]:
    """
    Perform AND or OR operation on multiple sets of Ca IDs.
    
    Args:
        ca_id_sets: List of sets containing Ca IDs
        operation: 'AND' or 'OR'
    
    Returns:
        Resulting set of Ca IDs
    """
    if not ca_id_sets:
        return set()
    
    if operation == 'AND':
        result = ca_id_sets[0]
        for ca_set in ca_id_sets[1:]:
            result = result.intersection(ca_set)
        return result
    elif operation == 'OR':
        result = set()
        for ca_set in ca_id_sets:
            result = result.union(ca_set)
        return result
    else:
        raise ValueError(f"Invalid operation: {operation}. Use 'AND' or 'OR'.")


def filter_df_by_ca_ids(df: pd.DataFrame, ca_id_col: str, 
                         ca_ids: Set[str], show_only_ids: bool = False) -> pd.DataFrame:
    """
    Filter dataframe to only include specified Ca IDs.
    
    Args:
        df: Input dataframe
        ca_id_col: Name of the Ca ID column
        ca_ids: Set of Ca IDs to include
        show_only_ids: If True, return only Ca ID column
    
    Returns:
        Filtered dataframe
    """
    if ca_id_col not in df.columns:
        return pd.DataFrame()
    
    filtered_df = df[df[ca_id_col].isin(ca_ids)].copy()
    
    if show_only_ids:
        return filtered_df[[ca_id_col]]
    
    return filtered_df


def get_column_identifier(file_type: str) -> str:
    """Get the Ca ID column name based on file type."""
    file_type_lower = file_type.lower()
    
    if 'cultivar' in file_type_lower or 'heat' in file_type_lower:
        return 'Ca_ID'
    elif 'cold' in file_type_lower or 'drought_53711' in file_type_lower:
        return 'Gene_identifier'
    elif 'drought_icc2861' in file_type_lower:
        return 'Ca ids'
    elif 'drought_icc4958' in file_type_lower or 'salinity_iccv2' in file_type_lower:
        return 'Ca_ID' if 'Ca_ID' in file_type else 'gene'
    elif 'salinity' in file_type_lower:
        if 'gse' in file_type_lower:
            return 'Ca IDS' if 'Ca IDS' in file_type else 'Ca_ID'
        elif 'iccv_jg' in file_type_lower:
            return 'Ca IDS'
        elif 'rootshoot' in file_type_lower:
            return 'Gene_identifier'
    
    # Default fallback
    return 'Ca_ID'


def detect_ca_id_column(df: pd.DataFrame) -> Optional[str]:
    """Automatically detect the Ca ID column in a dataframe."""
    possible_names = ['Ca_ID', 'Ca IDS', 'Ca ids', 'Gene_identifier', 'gene', 'Gene', 'Ref_gene_id', 'Ca_id']
    
    for col in df.columns:
        if col in possible_names:
            return col
        # Check if column contains Ca_ pattern
        if 'Ca' in col and df[col].astype(str).str.contains('Ca_', na=False).any():
            return col
    
    return None


def get_user_friendly_column_names() -> Dict[str, str]:
    """
    Return mapping of technical column names to user-friendly names.
    """
    return {
        # Root/Shoot nomenclature
        'Root-Control': 'Root Control',
        'Root-CS': 'Root Cold Stress',
        'Root-DS': 'Root Drought Stress',
        'Root-SS': 'Root Salinity Stress',
        'Shoot-Control': 'Shoot Control',
        'Shoot-CS': 'Shoot Cold Stress',
        'Shoot-DS': 'Shoot Drought Stress',
        'Shoot-SS': 'Shoot Salinity Stress',
        
        # Cultivar nomenclature (Heat)
        'AFL': 'Leaf-Reproductive',
        'AFR': 'Root-Reproductive',
        'BFL': 'Leaf-Vegetative',
        'BFR': 'Root-Vegetative',
        
        # GSE nomenclature (Salinity)
        'Stol-veg-CT': 'Tolerant-Vegetative-Control',
        'Stol-veg-SS': 'Tolerant-Vegetative-Stress',
        'Ssen-veg-CT': 'Sensitive-Vegetative-Control',
        'Ssen-veg-SS': 'Sensitive-Vegetative-Stress',
        'Stol-rep-CT': 'Tolerant-Reproductive-Control',
        'Stol-rep-SS': 'Tolerant-Reproductive-Stress',
        'Ssen-rep-CT': 'Sensitive-Reproductive-Control',
        'Ssen-rep-SS': 'Sensitive-Reproductive-Stress',
        
        # Drought nomenclature
        'FPKM-DS-C': 'Shoot-Control',
        'FPKM-DS-D': 'Shoot-Drought',
        'FPKM-DT-C': 'Root-Control',
        'FPKM-DT-D': 'Root-Drought',
    }


def create_download_csv(df: pd.DataFrame) -> str:
    """Convert dataframe to CSV string for download."""
    return df.to_csv(index=False)

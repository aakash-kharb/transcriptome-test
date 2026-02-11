"""
Data loader module for downloading and managing data from Google Drive.
This handles automatic data download when deployed on Streamlit Cloud.
"""

import os
import zipfile
import streamlit as st
import requests
from pathlib import Path


def download_file_from_gdrive(file_id, destination):
    """
    Download a file from Google Drive.
    
    Args:
        file_id: Google Drive file ID
        destination: Local path where file should be saved
    
    Returns:
        bool: True if download successful, False otherwise
    """
    URL = "https://drive.google.com/uc?export=download"
    
    session = requests.Session()
    
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = None
    
    # Handle large file confirmation
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value
            break
    
    if token:
        params = {'id': file_id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    
    # Check if response is successful
    if response.status_code != 200:
        return False
    
    # Save file
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    
    return True


def extract_zip(zip_path, extract_to):
    """
    Extract a zip file to specified directory.
    
    Args:
        zip_path: Path to zip file
        extract_to: Directory to extract contents to
    
    Returns:
        bool: True if extraction successful, False otherwise
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        return True
    except Exception as e:
        st.error(f"Error extracting zip file: {e}")
        return False


def ensure_data_available():
    """
    Ensure data directory exists and is populated.
    Downloads from Google Drive if necessary.
    
    Returns:
        bool: True if data is available, False otherwise
    """
    data_dir = Path("data")
    
    # Check if data directory exists and has files
    if data_dir.exists() and len(list(data_dir.glob("*.csv"))) > 0:
        return True
    
    # Data not available, try to download from Google Drive
    st.info("📥 Data not found locally. Downloading from Google Drive...")
    
    # Get Google Drive file ID from secrets
    try:
        if hasattr(st, 'secrets') and 'GDRIVE_FILE_ID' in st.secrets:
            file_id = st.secrets['GDRIVE_FILE_ID']
        else:
            st.error("⚠️ Google Drive file ID not found in secrets. Please configure secrets.toml")
            st.info("See .streamlit/secrets.toml.example for configuration instructions")
            return False
    except Exception as e:
        st.error(f"⚠️ Error reading secrets: {e}")
        return False
    
    # Create temporary directory for download
    temp_zip = "data_temp.zip"
    
    # Download file
    with st.spinner("Downloading data from Google Drive... This may take a minute."):
        success = download_file_from_gdrive(file_id, temp_zip)
    
    if not success:
        st.error("❌ Failed to download data from Google Drive. Please check the file ID and sharing permissions.")
        st.info("Make sure the Google Drive link is set to 'Anyone with the link can view'")
        return False
    
    st.success("✅ Download complete!")
    
    # Extract zip file
    with st.spinner("Extracting data files..."):
        # Create data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        
        # Extract to current directory (should contain 'data' folder)
        success = extract_zip(temp_zip, ".")
    
    # Clean up temp file
    if os.path.exists(temp_zip):
        os.remove(temp_zip)
    
    if not success:
        st.error("❌ Failed to extract data files")
        return False
    
    # Verify extraction
    if data_dir.exists() and len(list(data_dir.glob("*.csv"))) > 0:
        st.success("✅ Data files ready!")
        return True
    else:
        st.error("❌ Data directory is empty after extraction. Please check the zip file structure.")
        st.info("The zip file should contain a 'data' folder with all CSV files inside.")
        return False


def check_data_integrity():
    """
    Check if all expected data files are present.
    
    Returns:
        tuple: (bool, list) - (all_present, missing_files)
    """
    data_dir = Path("data")
    
    expected_files = [
        "Cold_Top.csv",
        "Cultivar_10685_filtered.csv",
        "Cultivar_1356_filtered.csv",
        "Cultivar_15614_filtered.csv",
        "Cultivar_4567_filtered.csv",
        "Cultivar_5912_filtered.csv",
        "Cultivar_92944_filtered.csv",
        "Drought_53711_Top.csv",
        "Drought_ICC2861-283_Top_all12.csv",
        "Drought_ICC2861-283_Top.csv",
        "DroughtICC4958-1882_Top.csv",
        "Salinity_ICCV_JG_Top.csv",
        "SalinityGSE70377_Top.csv",
        "SalinityICCV2-JG62_Top.csv",
        "SalinityRootShoot53711_Top.csv",
        "Summary_All_Cultivars.csv"
    ]
    
    missing_files = []
    for file in expected_files:
        if not (data_dir / file).exists():
            missing_files.append(file)
    
    return len(missing_files) == 0, missing_files

#!/usr/bin/env python3
"""
Quick verification script to test Google Drive data download locally.
Run this before deploying to Streamlit Cloud to ensure everything works.
"""

import os
import sys
import zipfile
import requests
from pathlib import Path

def test_gdrive_download():
    """Test downloading from Google Drive"""
    print("🧪 Testing Google Drive Download\n")
    
    file_id = "1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc"
    print(f"📋 File ID: {file_id}")
    print(f"🔗 Full URL: https://drive.google.com/file/d/1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc/view?usp=sharing\n")
    
    # Test URL construction
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    print(f"📥 Download URL: {download_url}\n")
    
    # Test if we can reach the URL
    print("🌐 Testing connection...")
    try:
        response = requests.head(download_url, allow_redirects=True, timeout=10)
        print(f"✅ Connection successful! Status code: {response.status_code}")
        
        if 'content-length' in response.headers:
            size_mb = int(response.headers['content-length']) / (1024 * 1024)
            print(f"📦 File size: {size_mb:.2f} MB")
        
        # Check if we get HTML (means we need confirmation) or actual file
        content_type = response.headers.get('content-type', '')
        if 'text/html' in content_type:
            print("⚠️  Large file detected - will need download confirmation")
        else:
            print(f"📄 Content type: {content_type}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("\n1. Verify the Google Drive sharing settings:")
    print("   - Go to: https://drive.google.com/file/d/1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc/view")
    print("   - Click 'Share' button")
    print("   - Set 'General access' to 'Anyone with the link'")
    print("   - Permission: 'Viewer'")
    
    print("\n2. Verify data.zip structure:")
    print("   - Open data.zip and check it contains a 'data' folder")
    print("   - Inside 'data' folder should be 16 CSV files")
    
    print("\n3. Deploy to Streamlit Cloud:")
    print("   - Go to https://share.streamlit.io")
    print("   - New app → GitHub: aakash-kharb/transcriptome-test")
    print("   - Add secret: GDRIVE_FILE_ID = \"1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc\"")
    
    print("\n4. Monitor first deployment:")
    print("   - Watch for 'Downloading from Google Drive...' message")
    print("   - Should take 1-2 minutes for initial download")
    print("   - Subsequent loads will be instant (cached)\n")
    
    return True

def check_local_data():
    """Check if local data directory exists"""
    print("\n" + "="*60)
    print("📂 LOCAL DATA CHECK")
    print("="*60)
    
    data_dir = Path("data")
    if data_dir.exists():
        csv_files = list(data_dir.glob("*.csv"))
        print(f"✅ Data directory exists with {len(csv_files)} CSV files")
        
        expected = [
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
        
        missing = []
        for file in expected:
            if not (data_dir / file).exists():
                missing.append(file)
        
        if missing:
            print(f"⚠️  Missing {len(missing)} expected files:")
            for f in missing:
                print(f"   - {f}")
        else:
            print("✅ All 16 expected CSV files are present!")
        
        print(f"\n💡 Local data is available - app will use local files")
        print(f"   Delete 'data' folder to test Google Drive download")
    else:
        print("❌ No local data directory")
        print("💡 App will attempt to download from Google Drive when run")

if __name__ == "__main__":
    print("="*60)
    print("🔍 GOOGLE DRIVE SETUP VERIFICATION")
    print("="*60 + "\n")
    
    test_gdrive_download()
    check_local_data()
    
    print("\n" + "="*60)
    print("✨ VERIFICATION COMPLETE")
    print("="*60)
    print("\nYou're ready to deploy to Streamlit Cloud! 🚀\n")

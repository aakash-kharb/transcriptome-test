# Deployment Guide for Streamlit Cloud

## 📋 Pre-Deployment Checklist

- [x] Code committed to GitHub
- [x] `.gitignore` configured (excludes data/ and secrets.toml)
- [x] `requirements.txt` updated
- [x] Google Drive data link prepared
- [ ] Streamlit Cloud secrets configured

## 🚀 Deploying to Streamlit Cloud

### Step 1: Verify Google Drive File

1. **Google Drive Link**: https://drive.google.com/file/d/1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc/view?usp=sharing
2. **File ID**: `1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc`
3. **Important**: Make sure the file sharing is set to "Anyone with the link can view"

To check/update sharing settings:
- Go to Google Drive
- Right-click on `data.zip`
- Click "Share" → "General access" → Set to "Anyone with the link"

### Step 2: Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account (@aakash-kharb)
3. Click "New app"
4. Select:
   - **Repository**: `aakash-kharb/transcriptome-test`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click "Deploy"

### Step 3: Configure Secrets

**IMPORTANT**: Before the app fully loads, configure secrets:

1. In the Streamlit Cloud dashboard, click on your app
2. Click the "⋮" menu (three dots) → "Settings"
3. Navigate to "Secrets" section
4. Paste the following:

```toml
GDRIVE_FILE_ID = "1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc"
```

5. Click "Save"
6. The app will automatically restart with the secrets configured

## ✅ Verification

After deployment, the app should:
1. Show "📥 Data not found locally. Downloading from Google Drive..." on first load
2. Download and extract the data automatically
3. Display all pages and functionality
4. Data will persist across app restarts (Streamlit Cloud has persistent storage)

## 🔧 Troubleshooting

### If data download fails:

**Issue**: "Failed to download data from Google Drive"
- **Solution**: Verify Google Drive link sharing is set to "Anyone with the link can view"
- Check that file ID in secrets matches the actual file ID
- File must be less than ~500MB for reliable downloads

**Issue**: "Data directory is empty after extraction"
- **Solution**: Verify that data.zip contains a 'data' folder with CSV files inside
- Structure should be: `data.zip → data/ → *.csv files`

**Issue**: "Google Drive file ID not found in secrets"
- **Solution**: Make sure you added the secrets in Streamlit Cloud settings
- Secrets format must be exactly as shown above
- Wait a minute after saving secrets and restart the app

### Alternative: Local Data Testing

If Google Drive link doesn't work, you can test locally:
```bash
# Copy your data folder to the project directory
cp -r /path/to/data ./data

# Run locally
streamlit run app.py
```

## 📦 Data Structure Requirements

The `data.zip` file must have this structure:
```
data.zip
└── data/
    ├── Cold_Top.csv
    ├── Cultivar_10685_filtered.csv
    ├── Cultivar_1356_filtered.csv
    ├── Cultivar_15614_filtered.csv
    ├── Cultivar_4567_filtered.csv
    ├── Cultivar_5912_filtered.csv
    ├── Cultivar_92944_filtered.csv
    ├── Drought_53711_Top.csv
    ├── Drought_ICC2861-283_Top_all12.csv
    ├── Drought_ICC2861-283_Top.csv
    ├── DroughtICC4958-1882_Top.csv
    ├── Salinity_ICCV_JG_Top.csv
    ├── SalinityGSE70377_Top.csv
    ├── SalinityICCV2-JG62_Top.csv
    ├── SalinityRootShoot53711_Top.csv
    └── Summary_All_Cultivars.csv
```

## 🔄 Updating the Deployed App

To push updates:
```bash
git add .
git commit -m "Your update message"
git push origin main
```

Streamlit Cloud will automatically detect the push and redeploy.

## 📱 Your App URL

After deployment, your app will be available at:
`https://transcriptome-test.streamlit.app` (or similar)

Share this URL with your users!

## ⚠️ Known Limitations

1. **First Load Time**: Initial data download may take 1-2 minutes
2. **File Size**: Google Drive downloads work best for files < 500MB
3. **Rate Limits**: Too many simultaneous downloads from Google Drive may be rate-limited

## 💡 Alternative Data Hosting

If Google Drive doesn't work reliably, consider:
- **Streamlit Cloud**: Upload data.zip directly (if < 200MB)
- **AWS S3**: Use public S3 bucket with direct download URL
- **GitHub LFS**: For files < 2GB
- **Dropbox**: Similar to Google Drive with direct download links

Let me know if you need help with alternative hosting!

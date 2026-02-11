# 🧬 Gene Expression Analysis Platform

A Streamlit-based web application for analyzing gene expression data across different stress conditions (Cold, Drought, Heat, and Salinity).

## 🌟 Features

- **Multi-Stress Analysis**: Analyze gene expression data for Cold, Drought, Heat, and Salinity stress conditions
- **Smart Filtering**: 
  - Filter by specific tissues/genotypes
  - Filter by log2FC thresholds
  - **Multi-tissue response filtering**: Find genes responsive in multiple tissues simultaneously
- **Data Export**: Download filtered results as CSV files
- **Cross-Stress Comparison**: Compare Ca IDs across different stress types in the Arena
- **Interactive UI**: Clean, organized interface with step-by-step filtering workflow

## 🚀 Deployment

This app is deployed on [Streamlit Cloud](https://streamlit.io/cloud).

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/aakash-kharb/transcriptome-test.git
cd transcriptome-test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up secrets (for data download):
```bash
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your Google Drive file ID
```

4. Run the app:
```bash
streamlit run app.py
```

## 📊 Data

The application uses gene expression data stored in CSV format. Data is automatically downloaded from Google Drive when the app is deployed or when running locally without the data directory.

### Data Structure

```
data/
├── Cold_Top.csv
├── Cultivar_*_filtered.csv (6 files)
├── Drought_*.csv (4 files)
├── Salinity*.csv (4 files)
└── Summary_All_Cultivars.csv
```

## 🔧 Configuration

### Streamlit Secrets

Create a `.streamlit/secrets.toml` file with the following content:

```toml
GDRIVE_FILE_ID = "your-google-drive-file-id"
```

**For Streamlit Cloud deployment:**
1. Go to your app settings on Streamlit Cloud
2. Navigate to "Secrets"
3. Add the following:
```toml
GDRIVE_FILE_ID = "1ob81k5GyZhZzpirVliPpo3Koh8pKI2Hc"
```

## 📁 Project Structure

```
transcriptome-test/
├── app.py                          # Main application file
├── backend.py                      # Backend filtering functions
├── data_loader.py                  # Google Drive data loader
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── pages/
│   ├── 1_❄️_Cold_Stress.py
│   ├── 2_🌵_Drought_Stress.py
│   ├── 3_🌡️_Heat_Stress.py
│   ├── 4_🧂_Salinity_Stress.py
│   ├── 5_🎯_Arena.py
│   └── 6_📊_Overall_Results.py
└── .streamlit/
    └── secrets.toml.example       # Example secrets file
```

## 💡 Usage

### Filtering Workflow

1. **Select a stress type** from the sidebar (Cold, Drought, Heat, or Salinity)
2. **Choose filtering mode**:
   - View All Data
   - Filter by Specific Tissue
   - Filter by Multi-Tissue Response (find genes responsive in multiple tissues)
3. **Configure filters** (threshold, tissue selection, etc.)
4. **View results** and download or send to Arena for cross-stress analysis

### Multi-Tissue Response Filtering

This powerful feature allows you to find genes that are responsive in a minimum number of tissues:
- Example: Find genes with |log2FC| ≥ 1.5 in **both** Root and Shoot tissues
- Works for datasets with multiple tissues (Cold, Drought_53711, Heat, SalinityRootShoot53711)

## 🛠️ Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Requests**: HTTP library for downloading data

## 👤 Author

**Aakash Kharb** - [@aakash-kharb](https://github.com/aakash-kharb)

## 📝 License

This project is open source and available for academic and research purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 🙏 Acknowledgments

- Gene expression data from chickpea stress response studies
- Streamlit community for the excellent framework

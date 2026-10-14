# Property Price Estimation Dashboard (Python + Streamlit)

An interactive dashboard to explore Indian residential property records and estimate a property's price using city, locality, area, BHK, bathrooms, property type, age, furnishing and amenities.

## What is included

- **Overview:** KPI cards, city comparison, and year-wise trend charts.
- **Estimate Price:** Random Forest model and an approximate price range. Changing the city refreshes available localities immediately.
- **Readable controls:** buttons expand or wrap long labels instead of clipping their words; primary button text has stronger contrast.
- **Market Insights:** area-vs-price, BHK comparisons and trend charts.
- **Raw Data & Sources:** filters, table view, CSV export, public listing sample, source manifest.
- **Indian currency:** prices are formatted as ₹, lakh and crore.
- **Offline-ready demo data:** 1,400 reproducible example rows across 10 Indian cities.
- **Public data downloader:** optionally downloads complete Mumbai and Delhi CSVs from public GitHub URLs into `data/raw/external/`.

## Important data note

The bundled `india_property_sample.csv` is **synthetic educational demo data**. It is not real sale history. It gives the app historical-year fields so charts and the model can run immediately without relying on a network connection.

The bundled `public_listings_extract.csv` is a small extract of public asking-price listings from the linked Mumbai and Delhi source files. Asking prices are **not necessarily completed sale prices**, and those source files do not provide sale years for the sampled rows. The dashboard keeps these public listings separate from the synthetic training data to avoid mixing incompatible fields or implying they are verified sale transactions.

For real-world use, replace the training dataset with licensed, dated and verified local transaction records matching the schema below. Model output is an educational estimate and is not professional valuation advice.

## Project structure

```text
property_price_estimation_dashboard/
├── app.py
├── run_dashboard.command       # double-click launcher for macOS
├── download_data.py
├── create_demo_data.py
├── requirements.txt
├── README.md
├── .gitignore
└── data/
    └── raw/
        ├── india_property_sample.csv
        ├── public_listings_extract.csv
        ├── sources.csv
        └── external/              # populated by download_data.py
```


## Easiest way to run on MacBook (macOS)

1. Download and extract the ZIP.
2. Open the extracted `property_price_estimation_dashboard` folder in Finder.
3. Double-click `run_dashboard.command`. On the first run it creates `.venv` and installs the dependencies (internet is required).
4. If macOS blocks the file, open Terminal and run `cd `, drag the project folder into Terminal, press Enter, then run `bash run_dashboard.command`.
5. Wait for the address `http://localhost:8501` in the Terminal window and open it in Safari or Chrome. Keep Terminal open while you use the dashboard.

### If the interface does not appear

- Make sure the final command in Terminal is `streamlit run app.py` (or `python -m streamlit run app.py`) and that Terminal's current folder is this project folder.
- Open `http://localhost:8501` manually in your browser.
- If Terminal says `No module named streamlit`, activate the environment with `source .venv/bin/activate` and run `pip install -r requirements.txt`.
- If port 8501 is already in use, run `python -m streamlit run app.py --server.port 8502` and open `http://localhost:8502`.
- To stop the server, click Terminal and press `Control + C`. To refresh the browser, press `Command + R`.
- If button text is clipped or the old layout remains visible, stop the old server with `Control + C`, open the newly extracted project folder, run `bash run_dashboard.command` again, then hard-refresh the page with `Command + Shift + R`.
- On the Estimate Price page, the City dropdown is reactive: selecting a different city updates the Locality choices before you click Estimate.
- If a control does nothing, check that you are viewing `http://localhost:8501` from the currently running project and that Terminal has no red error message. Send the last 10–20 Terminal lines if there is an error.

## 1. Install Python

Use Python 3.10–3.12 if available. Confirm installation in Terminal / Command Prompt:

```bash
python --version
```

If `python` is not recognized on Windows, try `py --version` and replace `python` with `py` in commands.

## 2. Open the project folder

Download and extract the ZIP, then open a terminal inside the extracted `property_price_estimation_dashboard` folder.

### Windows Command Prompt

```bat
cd path\to\property_price_estimation_dashboard
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux Terminal

```bash
cd /path/to/property_price_estimation_dashboard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open that URL in your browser. Keep the terminal window running while using the dashboard. Stop it with `Ctrl+C`.

## 3. Download the full public raw listing CSVs (optional)

Internet access is required for this step. The dashboard works without it.

```bash
python download_data.py
```

The complete files are saved to `data/raw/external/Mumbai.csv`, `Delhi.csv` and `Bengaluru_House_RawData.csv`. The downloader preserves the source files without silently modifying their columns. Check each source and its terms before republishing or using for commercial purposes.

## Dataset schema used by the model

The bundled demo CSV contains these model columns:

| Column | Meaning |
|---|---|
| `city`, `locality` | City and locality |
| `property_type` | Apartment, house, villa or builder floor |
| `area_sqft` | Built-up area in square feet |
| `bhk`, `bathrooms` | Bedroom and bathroom count |
| `age_years` | Approximate property age |
| `furnishing_status` | Furnished, semi-furnished or unfurnished |
| `parking`, `lift`, `gated_community`, `gym`, `swimming_pool` | Amenity flags (0/1) |
| `sale_year` | Demo historical-year marker |
| `price_lakhs` | Target price in ₹ lakh |

The displayed holdout MAE and R² are measured only on this synthetic dataset; they should not be interpreted as real market accuracy.

## 4. Push to GitHub

1. Create a new **empty** repository on GitHub (for example, `property-price-estimation-dashboard`). Do not add a README on GitHub if you already have one here.
2. In your terminal, from this project's root folder, run:

```bash
git init
git add .
git commit -m "Build Streamlit property price estimation dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/property-price-estimation-dashboard.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Git may ask you to sign in or authorize in a browser. If the project is already a Git repository, skip `git init`; if `origin` already exists, update it with:

```bash
git remote set-url origin https://github.com/YOUR-USERNAME/property-price-estimation-dashboard.git
```

### Future updates

After changing files:

```bash
git add .
git commit -m "Update dashboard"
git push
```

## Sources

- Public Mumbai and Delhi listing CSVs in the `happygoluckycodeeditor/pricepredictionmodel` repository: [GitHub repository](https://github.com/happygoluckycodeeditor/pricepredictionmodel) · [Mumbai.csv](https://github.com/happygoluckycodeeditor/pricepredictionmodel/blob/main/Mumbai.csv) · [Delhi.csv](https://github.com/happygoluckycodeeditor/pricepredictionmodel/blob/main/Delhi.csv).
- Public Bengaluru House Price Dataset extract: [Bengaluru_House_RawData.csv](https://github.com/Anamikaa-MK/Bengaluru-House-Price-Analysis/blob/main/Data/Bengaluru_House_RawData.csv). It has location, area, BHK, bathrooms and price, but does not establish a completed-sale date.
- [Indian Urban House Price Prediction (Kaggle)](https://www.kaggle.com/competitions/indian-urban-house-price-prediction/data): describes a synthetic multi-city educational dataset; not used as a real transaction source in this app.
- [Indian Housing Datasets project](https://github.com/Rvbaghel/india_housing_datasets): repository explicitly describes its standardized city datasets as synthetically generated for educational use.

## License and attribution

Code in this project is provided for educational use. Public listing data remains subject to its original source terms and licenses. Keep source attribution when redistributing downloaded files.

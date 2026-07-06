# Airbnb Listings Data Analysis - Edinburgh

Analysis of 6,258 Edinburgh Airbnb listings (Inside Airbnb `listings.csv`), covering data cleaning, exploratory analysis, review activity, and an interactive dashboard.

## Project Structure
```
├── Airbnb_Edinburgh_EDA.ipynb   # Full EDA notebook (cleaning, 23 charts, insights, conclusion)
├── Airbnb_Edinburgh_Analysis.pptx  # Slide deck summarizing findings & recommendations
├── app.py                       # Streamlit interactive dashboard
├── requirements.txt             # Python dependencies
├── data/
│   ├── listings.csv             # Raw listings data (Inside Airbnb)
│   └── reviews.csv              # Review dates (compact version, no comment text)
└── README.md
```

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the Notebook
```bash
jupyter notebook Airbnb_Edinburgh_EDA.ipynb
```

## Run the Dashboard
```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).

## Data Source
[Inside Airbnb](https://insideairbnb.com/get-the-data/) - Edinburgh listings and reviews.

## Notes & Limitations
- `reviews.csv` used here is the **compact** version (`listing_id`, `date` only) - it does not include review comment text, so true sentiment analysis was not possible. The notebook covers **review activity/volume trends** instead. If the detailed reviews file (with a `comments` column) is obtained later, sentiment scoring (e.g. via TextBlob) can be added using the same merge logic already in the notebook.
- Prices above the 95th percentile are flagged (not removed) as outliers throughout the analysis.

## Key Findings (summary)
- **Room type** is the strongest price driver - Entire home/apt (median £261) prices roughly 2x Private room (median £130).
- **Location** sets a price ceiling - city-centre neighbourhoods (New Town, Old Town) command the highest prices.
- **Price has almost no correlation** with number of reviews (-0.03) or availability (+0.05) - undercutting price is not an effective way to drive demand.
- Review activity shows healthy long-term growth with an expected COVID-era dip and full recovery.

See the notebook and slide deck for full detail and business recommendations.

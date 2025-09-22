# CORD-19 COVID-19 Research Data Explorer

This project is an interactive Streamlit dashboard for exploring the CORD-19 dataset, which contains metadata about COVID-19 research papers. The dashboard allows users to filter, visualize, and analyze publication trends, top journals, word frequencies, and more.

---

## Features

- **Filter papers** by publication year and journal
- **Visualize** publication trends, top journals, and word frequencies
- **Interactive word clouds** for titles and abstracts
- **Summary statistics** and data sample views

---

## Project Structure

```
Python-Week-8-Assignment/
├── app.py                # Main Streamlit app
├── analysis.py           # Data analysis and visualization logic
├── .gitignore            # Specifies files/folders to ignore in git
├── data/
│   └── metadata.csv      # CORD-19 dataset (not included in repo)
└── README.md             # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/JSIMBA11/Python-Week-8-Assignment.git

```

### 2. Install Required Python Packages

You need Python 3.7+ installed.  
Install dependencies with:

```sh
pip install streamlit pandas matplotlib seaborn plotly wordcloud
```

**Add-ons installed for visualization:**
- `streamlit` (for the dashboard)
- `pandas` (for data manipulation)
- `matplotlib` and `seaborn` (for plotting)
- `plotly` (for interactive charts)
- `wordcloud` (for word cloud visualizations)

### 3. Download the Data

Due to file size limits, the dataset is **not included** in this repository.

- Download `metadata.csv` from the [official CORD-19 source](https://www.semanticscholar.org/cord19/download).
- Place it in the `data` folder:
  ```
  data/metadata.csv
  ```

### 4. Run the App

```sh
streamlit run app.py
```
or, if `streamlit` is not recognized:
```sh
python -m streamlit run app.py
```

Open your browser and go to [http://localhost:8501](http://localhost:8501) to use the dashboard.

---

## Notes

- The file `data/metadata.csv` is **ignored** by git (see `.gitignore`) and must be downloaded separately.
- If you add new dependencies, update the `requirements.txt` with:
  ```
  pip freeze > requirements.txt
  ```

---

## Troubleshooting

- If you see `ModuleNotFoundError`, ensure all required packages are installed.
- If `streamlit` is not recognized, use the full command: `python -m streamlit run app.py`
- If the app says "Error loading data," make sure `metadata.csv` is in the `data` folder.

---

## License

Assignment


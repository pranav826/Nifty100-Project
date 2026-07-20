from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

RAW_PATH = BASE_DIR / "data" / "raw"
SUPPORTING_PATH = RAW_PATH / "supporting datasets"

CORE_FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
}

SUPPORTING_FILES = {
    "financial_ratios": "financial_ratios.xlsx",
    "market_cap": "market_cap.xlsx",
    "peer_groups": "peer_groups.xlsx",
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
}


def load_all_datasets():

    datasets = {}

    print("RAW PATH:", RAW_PATH)
    print("SUPPORTING PATH:", SUPPORTING_PATH)

    for name, file in CORE_FILES.items():
        datasets[name] = pd.read_excel(RAW_PATH / file, header=1)

    for name, file in SUPPORTING_FILES.items():
        datasets[name] = pd.read_excel(SUPPORTING_PATH / file)

    return datasets
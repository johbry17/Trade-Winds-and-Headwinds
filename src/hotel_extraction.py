"""
src/hotel_extraction.py

"""

from pathlib import Path

import pandas as pd


DATA_DIR = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "USVIBER-Hotel"
)

OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "processed"
    / "usviber_hotel_annual.csv"
)


def build_hotel_annual():
    """Merge manually curated hotel CSVs and save the annual dataset."""

    files = {
        "available": "raw_available.csv",
        "occupied": "raw_occupied.csv",
        "occupancy": "raw_occupancy.csv",
    }

    frames = {}

    for measure, filename in files.items():
        df = pd.read_csv(DATA_DIR / filename)

        if df["year"].duplicated().any():
            raise ValueError(f"Duplicate years in {filename}")

        df["year"] = pd.to_numeric(df["year"], errors="raise").astype(int)

        rename = {
            "filename": f"{measure}_filename",
            "prev_year_value": f"{measure}_prev_year_value",
            "value": {
                "available": "nights_available_k",
                "occupied": "nights_occupied_k",
                "occupancy": "occupancy_pct",
            }[measure],
        }

        frames[measure] = df.rename(columns=rename)[
            [
                "year",
                f"{measure}_filename",
                f"{measure}_prev_year_value",
                rename["value"],
            ]
        ]

    hotel = frames["available"]

    for measure in ("occupied", "occupancy"):
        hotel = hotel.merge(
            frames[measure],
            on="year",
            how="outer",
            validate="one_to_one",
        )

    hotel["occ_calculated"] = (
        hotel["nights_occupied_k"] / hotel["nights_available_k"] * 100
    ).round(1)

    hotel = hotel.sort_values("year").reset_index(drop=True)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    hotel.to_csv(OUTPUT_PATH, index=False)

    return hotel


def load_hotel_annual():
    """Load the processed annual hotel dataset."""

    if not OUTPUT_PATH.exists():
        raise FileNotFoundError(
            f"{OUTPUT_PATH} not found. Run build_hotel_annual() first."
        )

    return pd.read_csv(OUTPUT_PATH)
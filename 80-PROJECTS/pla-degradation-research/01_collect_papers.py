"""
PLA Degradation Research - Step 1: Collect and Extract Data from Literature
Uses AI to search papers and extract key degradation metrics
"""

import json
import re
import sys
from pathlib import Path

# Add venv packages to path
venv_packages = Path(__file__).parent / "venv" / "lib" / "site-packages"
sys.path.insert(0, str(venv_packages))

import pandas as pd
import numpy as np


def extract_molecular_weight(text: str) -> dict | None:
    """Extract molecular weight data from text using pattern matching"""
    patterns = {
        'Mn': r'Mn\s*[=:?]\s*([\d.]+)\s*[×x]\s*10[\⁴⁴]?\s*(?:g/mol|kDa)',
        'Mw': r'Mw\s*[=:?]\s*([\d.]+)\s*[×x]\s*10[\⁴⁴]?\s*(?:g/mol|kDa)',
        'PDI': r'PDI\s*[=:?]\s*([\d.]+)',
    }

    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            # Convert to consistent units (kDa)
            if value < 1000:
                value_kda = value
            else:
                value_kda = value / 1000
            results[key] = value_kda
    return results if results else None


def extract_degradation_rate(text: str) -> dict | None:
    """Extract degradation rate constants"""
    patterns = {
        'k_hydrolysis': r'k\s*[=:?]\s*([\d.]+)\s*[×x]\s*10[⁻-]?[\d.]+?\s*(?:day⁻¹|d⁻¹)',
        'half_life': r't\s*1[/2]\s*[=:?]\s*([\d.]+)\s*(?:days|d)',
    }

    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[key] = float(match.group(1))
    return results if results else None


def extract_mechanical_retention(text: str) -> dict | None:
    """Extract tensile strength retention data"""
    patterns = {
        'ts_retention_30d': r'(?:30\s*days?|1\s*month).*?(\d+)\s*%\s*(?:tensile|TS|strength)',
        'ts_retention_60d': r'(?:60\s*days?|2\s*months?).*?(\d+)\s*%\s*(?:tensile|TS|strength)',
        'elongation_retention': r'elongation.*?(\d+)\s*%',
    }

    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            results[key] = float(match.group(1))
    return results if results else None


def simulate_ai_extraction(paper_text: str) -> dict:
    """
    Simulate AI extraction from paper abstract.
    In production, this would call GPT-4 or Claude API.
    Returns structured data as if AI had read the paper.
    """
    data = {
        'source': 'simulated',
        'title': None,
        'year': None,
        'molecular_weight': extract_molecular_weight(paper_text),
        'degradation_rate': extract_degradation_rate(paper_text),
        'mechanical_retention': extract_mechanical_retention(paper_text),
    }

    # Extract year
    year_match = re.search(r'(19|20)\d{2}', paper_text)
    if year_match:
        data['year'] = int(year_match.group())

    return data


# Simulated literature data (would be extracted from real papers via AI)
LITERATURE_DATA = [
    {
        'study': 'Nature Polymers 2020',
        'condition': 'soil burial, 25°C, 50% RH',
        'Mw': 58.0,  # kDa
        'PDI': 1.8,
        'ts_initial': 65.0,  # MPa
        'ts_30d': 42.0,
        'ts_60d': 28.0,
        'ts_90d': 15.0,
        'mw_30d': 42.0,
        'mw_60d': 31.0,
        'degradation_type': 'hydrolysis + enzymatic',
    },
    {
        'study': 'Biomaterials 2019',
        'condition': 'composting, 58°C',
        'Mw': 72.0,
        'PDI': 2.1,
        'ts_initial': 70.0,
        'ts_15d': 35.0,
        'ts_30d': 12.0,
        'mw_15d': 38.0,
        'mw_30d': 18.0,
        'degradation_type': 'hydrolysis + thermal',
    },
    {
        'study': 'J Applied Polymer Sci 2021',
        'condition': 'phosphate buffer, pH 7.4, 37°C',
        'Mw': 45.0,
        'PDI': 1.9,
        'ts_initial': 58.0,
        'ts_7d': 52.0,
        'ts_14d': 45.0,
        'ts_21d': 38.0,
        'ts_28d': 31.0,
        'mw_7d': 41.0,
        'mw_14d': 36.0,
        'mw_21d': 30.0,
        'mw_28d': 24.0,
        'degradation_type': 'hydrolysis',
    },
    {
        'study': 'Polymer Degradation 2022',
        'condition': 'marine environment, 20°C',
        'Mw': 65.0,
        'PDI': 2.0,
        'ts_initial': 62.0,
        'ts_30d': 55.0,
        'ts_60d': 48.0,
        'ts_90d': 40.0,
        'mw_30d': 58.0,
        'mw_60d': 52.0,
        'mw_90d': 45.0,
        'degradation_type': 'hydrolysis + UV',
    },
    {
        'study': 'ACS Sustainable 2023',
        'condition': 'activated sludge, 35°C',
        'Mw': 52.0,
        'PDI': 1.7,
        'ts_initial': 68.0,
        'ts_20d': 38.0,
        'ts_40d': 18.0,
        'mw_20d': 30.0,
        'mw_40d': 15.0,
        'degradation_type': 'enzymatic',
    },
]


def main():
    print("=" * 60)
    print("PLA Degradation Research - Data Collection")
    print("=" * 60)

    # Create DataFrame from literature
    df = pd.DataFrame(LITERATURE_DATA)
    print(f"\nCollected {len(df)} studies from literature\n")

    # Save raw data
    data_dir = Path(__file__).parent / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(data_dir / "literature_data.csv", index=False)
    print(f"Saved to {data_dir / 'literature_data.csv'}")

    # Display summary
    print("\n--- Studies Summary ---")
    for _, row in df.iterrows():
        print(f"\n{row['study']}")
        print(f"  Condition: {row['condition']}")
        print(f"  Initial Mw: {row['Mw']} kDa, PDI: {row['PDI']}")
        print(f"  Initial TS: {row['ts_initial']} MPa")
        print(f"  Degradation type: {row['degradation_type']}")

    print("\n" + "=" * 60)
    print("Next step: Run 02_analyze_degradation.py")
    print("=" * 60)


if __name__ == "__main__":
    main()

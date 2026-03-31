"""
PLA Degradation Research - Step 2: Degradation Kinetics Analysis
Analyzes molecular weight loss and mechanical property changes over time
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

venv_packages = Path(__file__).parent / "venv" / "lib" / "site-packages"
sys.path.insert(0, str(venv_packages))

import pandas as pd
from scipy.stats import linregress


def main():
    print("=" * 60)
    print("PLA Degradation Research - Kinetics Analysis")
    print("=" * 60)

    # Load data
    data_path = Path(__file__).parent / "data" / "raw" / "literature_data.csv"
    df = pd.read_csv(data_path)

    results = []

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Process each study
    for idx, row in df.iterrows():
        study_name = row['study']
        print(f"\nAnalyzing: {study_name}")
        print(f"  Condition: {row['condition']}")

        # Find all mw_ and ts_ columns (time series)
        mw_cols = sorted([c for c in df.columns if c.startswith('mw_')],
                        key=lambda x: int(x.split('_')[1].replace('d', '')))
        ts_cols = sorted([c for c in df.columns if c.startswith('ts_') and c != 'ts_initial'],
                         key=lambda x: int(x.split('_')[1].replace('d', '')))

        initial_mw = row['Mw']
        initial_ts = row['ts_initial']

        # Extract MW time series for this study
        mw_times, mw_values, mw_retention = [], [], []
        for c in mw_cols:
            if pd.notna(row[c]):
                t = int(c.split('_')[1].replace('d', ''))
                mw_times.append(t)
                mw_values.append(row[c])
                mw_retention.append((row[c] / initial_mw) * 100)

        # Extract TS time series
        ts_times, ts_values, ts_retention = [], [], []
        for c in ts_cols:
            if pd.notna(row[c]):
                t = int(c.split('_')[1].replace('d', ''))
                ts_times.append(t)
                ts_values.append(row[c])
                ts_retention.append((row[c] / initial_ts) * 100)

        # Calculate degradation rate (first-order)
        if len(mw_times) >= 2:
            k = -np.log(mw_values[-1] / initial_mw) / mw_times[-1]
            half_life = np.log(2) / k
            print(f"  Degradation rate (k): {k:.4f} day⁻¹")
            print(f"  Half-life: {half_life:.1f} days")
        else:
            k, half_life = None, None

        results.append({
            'study': study_name,
            'condition': row['condition'],
            'initial_Mw': initial_mw,
            'k': k,
            'half_life_days': half_life,
            'degradation_type': row['degradation_type'],
        })

        # Plot MW retention
        axes[0, 0].plot(mw_times, mw_retention, 'o-', label=study_name.split()[0])
        axes[0, 1].plot(ts_times, ts_retention, 's-', label=study_name.split()[0])

    # Finish plots
    axes[0, 0].set_xlabel('Time (days)')
    axes[0, 0].set_ylabel('MW Retention (%)')
    axes[0, 0].set_title('Molecular Weight Retention')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].set_xlabel('Time (days)')
    axes[0, 1].set_ylabel('TS Retention (%)')
    axes[0, 1].set_title('Tensile Strength Retention')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Bar chart of half-lives
    results_df = pd.DataFrame(results)
    valid_results = results_df.dropna(subset=['half_life_days'])
    axes[1, 0].bar(range(len(valid_results)), valid_results['half_life_days'])
    axes[1, 0].set_xticks(range(len(valid_results)))
    axes[1, 0].set_xticklabels([s.split()[0] for s in valid_results['study']], rotation=45)
    axes[1, 0].set_ylabel('Half-life (days)')
    axes[1, 0].set_title('MW Half-life by Study')
    axes[1, 0].grid(True, alpha=0.3)

    # Temperature effect
    temps = {'Nature Polymers 2020': 25, 'Biomaterials 2019': 58,
             'J Applied Polymer Sci 2021': 37, 'Polymer Degradation 2022': 20,
             'ACS Sustainable 2023': 35}
    study_temps = [temps.get(r['study'], 30) for _, r in valid_results.iterrows()]
    rates = valid_results['k'].values

    axes[1, 1].scatter(study_temps, rates, s=100, c='steelblue')
    axes[1, 1].set_xlabel('Temperature (°C)')
    axes[1, 1].set_ylabel('Degradation Rate (day⁻¹)')
    axes[1, 1].set_title('Temperature Effect on Degradation')
    axes[1, 1].grid(True, alpha=0.3)

    if len(study_temps) >= 3:
        slope, intercept, r, _, _ = linregress(study_temps, rates)
        x_line = np.linspace(min(study_temps), max(study_temps), 100)
        axes[1, 1].plot(x_line, slope * x_line + intercept, '--', alpha=0.5)
        print(f"\n  Temperature trend: slope = {slope:.5f}")

    plt.tight_layout()
    plot_path = Path(__file__).parent / "data" / "processed" / "degradation_analysis.png"
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved plot to {plot_path}")

    # Save results
    results_path = Path(__file__).parent / "data" / "processed" / "kinetics_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"Saved kinetics to {results_path}")

    # Key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    fastest_idx = results_df['k'].idxmax()
    slowest_idx = results_df['k'].idxmin()

    print(f"\nFastest degradation: {results_df.loc[fastest_idx, 'study']}")
    print(f"  Condition: {results_df.loc[fastest_idx, 'condition']}")
    print(f"  Half-life: {results_df.loc[fastest_idx, 'half_life_days']:.1f} days")

    print(f"\nSlowest degradation: {results_df.loc[slowest_idx, 'study']}")
    print(f"  Condition: {results_df.loc[slowest_idx, 'condition']}")
    print(f"  Half-life: {results_df.loc[slowest_idx, 'half_life_days']:.1f} days")

    print("\n" + "=" * 60)
    print("Next step: Run 03_write_report.py to generate summary")
    print("=" * 60)


if __name__ == "__main__":
    main()

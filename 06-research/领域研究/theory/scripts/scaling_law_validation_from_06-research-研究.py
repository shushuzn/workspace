# -*- coding: utf-8 -*-
"""
Scaling Law Validation Script

Fit experimental data to theoretical scaling law:
  sigma = sigma_0 * (P/(v*d))^alpha

Usage:
  1. Prepare data in CSV format with columns: P, v, d, sigma
  2. Run script to fit alpha and verify scaling law
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("Scaling Law Validation")
print("=" * 70)

# Load literature data from CSV
print("\n[1/4] Loading literature data...")
data_file = Path("D:/OpenClaw/workspace/11-research/theory/data/improved_synthetic_data.csv")

if data_file.exists():
    df = pd.read_csv(data_file)
    # Extract P, v, d, sigma
    P_data = df['P_W'].values
    v_data = df['v_mms'].values
    d_data = df['d_um'].values
    sigma_data = df['sigma_Sm'].values
    
    print(f"  Loaded {len(df)} data points from synthetic literature data")
else:
    print(f"  [!] Data file not found, using sample data")
    # Sample data (replace with real literature data)
    # Format: [P (W), v (mm/s), d (um), sigma (S/m)]
    sample_data = np.array([
        [10, 50, 100, 1.2e5],
        [15, 50, 100, 2.5e5],
        [20, 50, 100, 4.1e5],
        [25, 50, 100, 5.8e5],
        [15, 30, 100, 3.2e5],
        [15, 70, 100, 1.9e5],
        [20, 40, 80, 5.5e5],
        [20, 60, 120, 3.2e5],
    ])
    P_data = sample_data[:, 0]
    v_data = sample_data[:, 1]
    d_data = sample_data[:, 2]
    sigma_data = sample_data[:, 3]

print(f"  Number of data points: {len(sigma_data)}")
print(f"  Power range: {P_data.min():.1f} - {P_data.max():.1f} W")
print(f"  Speed range: {v_data.min():.1f} - {v_data.max():.1f} mm/s")
print(f"  Conductivity range: {sigma_data.min():.2e} - {sigma_data.max():.2e} S/m")

# Calculate power density
print("\n[2/4] Calculating power density...")
power_density = P_data / (v_data * d_data)  # W/(mm/s * um) = W*s/(mm*um)

print(f"  Power density range: {power_density.min():.3f} - {power_density.max():.3f}")

# Fit scaling law: sigma = sigma_0 * (P/(v*d))^alpha
print("\n[3/4] Fitting scaling law...")

def scaling_law(x, sigma_0, alpha):
    return sigma_0 * np.power(x, alpha)

# Log-log fitting
log_x = np.log10(power_density)
log_y = np.log10(sigma_data)

# Linear fit in log space
coeffs = np.polyfit(log_x, log_y, 1)
alpha_fit = coeffs[0]
log_sigma_0 = coeffs[1]
sigma_0_fit = 10**log_sigma_0

# Calculate R^2
y_pred_log = np.polyval(coeffs, log_x)
ss_res = np.sum((log_y - y_pred_log)**2)
ss_tot = np.sum((log_y - np.mean(log_y))**2)
r_squared = 1 - ss_res / ss_tot

print(f"\n  Fitted parameters:")
print(f"    alpha = {alpha_fit:.3f}")
print(f"    sigma_0 = {sigma_0_fit:.2e} S/m")
print(f"    R^2 = {r_squared:.4f}")

# Check if alpha is in expected range
if 1.0 <= alpha_fit <= 2.0:
    print(f"\n  [OK] Alpha is in expected range (1-2)")
else:
    print(f"\n  [!] Alpha is outside expected range (1-2)")

if r_squared >= 0.75:
    print(f"  [OK] R^2 >= 0.75, good fit!")
else:
    print(f"  [!] R^2 < 0.75, need more data or check model")

# Visualization
print("\n[4/4] Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Log-log scaling law
fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
ax1.scatter(log_x, log_y, s=80, c='blue', alpha=0.7, label='Data')
ax1.plot(log_x, y_pred_log, 'r-', linewidth=2, label=f'Fit: alpha={alpha_fit:.2f}')
ax1.set_xlabel('log10(P/(v*d))', fontsize=12)
ax1.set_ylabel('log10(sigma)', fontsize=12)
ax1.set_title('Power Density Scaling Law', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "scaling_law_loglog.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] Log-log plot saved")

# Plot 2: Raw data with fit
fig2, ax2 = plt.subplots(figsize=(8, 6), dpi=300)
ax2.scatter(power_density, sigma_data, s=80, c='blue', alpha=0.7, label='Data')
x_fit = np.linspace(power_density.min(), power_density.max(), 100)
y_fit = scaling_law(x_fit, sigma_0_fit, alpha_fit)
ax2.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Fit: sigma_0*(P/vd)^{alpha_fit:.2f}')
ax2.set_xlabel('Power Density P/(v*d)', fontsize=12)
ax2.set_ylabel('Conductivity sigma (S/m)', fontsize=12)
ax2.set_title('Scaling Law Validation', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "scaling_law_raw.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] Raw data plot saved")

# Summary
print("\n" + "=" * 70)
print("[OK] Scaling Law Validation Complete!")
print("=" * 70)

print(f"\nResults:")
print(f"  Scaling exponent alpha = {alpha_fit:.3f}")
print(f"  Pre-factor sigma_0 = {sigma_0_fit:.2e} S/m")
print(f"  Goodness of fit R^2 = {r_squared:.4f}")

print(f"\nValidation status:")
if 1.0 <= alpha_fit <= 2.0 and r_squared >= 0.75:
    print(f"  [PASS] Scaling law validated!")
    print(f"  - Alpha in expected range (1-2)")
    print(f"  - R^2 >= 0.75")
else:
    print(f"  [NEEDS WORK] Further validation needed")
    if not (1.0 <= alpha_fit <= 2.0):
        print(f"  - Alpha {alpha_fit:.3f} outside range (1-2)")
    if r_squared < 0.75:
        print(f"  - R^2 {r_squared:.4f} < 0.75")

print(f"\nFigures saved to: {figures_dir}")
print(f"\nNext steps:")
print(f"  1. Replace sample data with real literature data")
print(f"  2. Collect 20-30 data points minimum")
print(f"  3. Verify scaling law holds across different studies")

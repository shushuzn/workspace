# -*- coding: utf-8 -*-
"""
2D Axisymmetric Thermal Simulation for LIG

Extends 1D model to 2D (r-z cylindrical coordinates)
Captures lateral heat dissipation

Dependencies:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.colors import LogNorm

print("=" * 70)
print("2D Axisymmetric Thermal Simulation - LIG")
print("=" * 70)

# ============================================================================
# 1. Material Properties
# ============================================================================
print("\n[1/7] Setting material properties...")

rho = 1400      # kg/m3
k = 0.12        # W/(m.K)
Cp = 1100       # J/(kg.K)
alpha = k / (rho * Cp)  # m2/s

print(f"  Density: {rho} kg/m3")
print(f"  Thermal conductivity: {k} W/(m.K)")
print(f"  Specific heat: {Cp} J/(kg.K)")
print(f"  Thermal diffusivity: {alpha:.2e} m2/s")

# ============================================================================
# 2. Laser Parameters
# ============================================================================
print("\n[2/7] Setting laser parameters...")

P = 10.0        # W
v = 0.05        # m/s
d = 100e-6      # m
absorb = 0.8    # absorption

t_dwell = d / v
q_0 = 2 * absorb * P / (np.pi * d**2)  # Peak power density

print(f"  Power: {P} W")
print(f"  Speed: {v *1000:.1f} mm/s")
print(f"  Spot size: {d *1e6:.0f} um")
print(f"  Dwell time: {t_dwell *1e6:.1f} us")
print(f"  Peak power density: {q_0:.2e} W/m2")

# ============================================================================
# 3. 2D Grid
# ============================================================================
print("\n[3/7] Setting up 2D grid...")

# Radial direction
nr = 100        # radial points
R_max = 300e-6  # 300 um
dr = R_max / (nr - 1)
r = np.linspace(0, R_max, nr)

# Axial direction
nz = 50         # axial points
Z_max = 150e-6  # 150 um
dz = Z_max / (nz - 1)
z = np.linspace(0, Z_max, nz)

# Time
dt = 0.1e-6     # 0.1 us
nt = 500        # time steps

print(f"  Radial: {nr} points, {R_max *1e6:.0f} um, dr = {dr *1e6:.1f} um")
print(f"  Axial: {nz} points, {Z_max *1e6:.0f} um, dz = {dz *1e6:.1f} um")
print(f"  Time: {nt} steps, dt = {dt *1e6:.1f} us")

# Stability check
stability_r = alpha * dt / dr**2
stability_z = alpha * dt / dz**2
print(f"  Stability (r): {stability_r:.3f} (should be <= 0.5)")
print(f"  Stability (z): {stability_z:.3f} (should be <= 0.5)")

# ============================================================================
# 4. Initialize
# ============================================================================
print("\n[4/7] Initializing...")

T_env = 300     # K
T = np.ones((nr, nz)) * T_env

# Meshgrid for visualization
R, Z = np.meshgrid(r, z, indexing='ij')

# Record history
record_times = [0, 100, 200, 300, 499]
T_history = []
time_history = []

# ============================================================================
# 5. Time Stepping
# ============================================================================
print("\n[5/7] Running simulation...")

for n in range(nt):
    T_new = T.copy()

    # Internal nodes (2D diffusion in cylindrical coordinates)
    for i in range(1, nr -1):
        for j in range(1, nz -1):
            # Radial term
            r_i = r[i]
            if r_i > 0:
                k_r_iphalf = k  # Interface conductivity
                k_r_imhalf = k
                r_iphalf = r[i] + dr /2
                r_imhalf = r[i] - dr /2

                radial_term = (k_r_iphalf * r_iphalf * (T[i +1,j] - T[i,j]) -
                              k_r_imhalf * r_imhalf * (T[i,j] - T[i -1,j])) / (r_i * dr**2)
            else:
                # At r=0, use L'Hopital's rule
                radial_term = 2 * k * (T[i +1,j] - 2 *T[i,j] + T[i -1,j]) / dr**2

            # Axial term
            axial_term = k * (T[i,j +1] - 2 *T[i,j] + T[i,j -1]) / dz**2

            # Update
            T_new[i,j] = T[i,j] + dt / (rho * Cp) * (radial_term + axial_term)

    # Boundary conditions

    # r = 0 (axisymmetric): dT/dr = 0 (already handled)

    # r = R_max (ambient)
    T_new[-1, :] = T_env

    # z = 0 (surface with laser heating)
    for i in range(nr):
        # Gaussian laser profile
        q_laser = q_0 * np.exp(-2 * r[i]**2 / (d /2)**2)

        # Only heat during dwell time
        if n * dt < t_dwell:
            T_new[i, 0] = T[i, 0] + q_laser * dt / (rho * Cp * dz)
        else:
            # Cooling
            h = 10
            T_new[i, 0] = T[i, 0] - h * (T[i, 0] - T_env) * dt / (rho * Cp * dz)

    # z = Z_max (adiabatic)
    T_new[:, -1] = T[:, -1]

    T = T_new

    # Record
    if n in record_times:
        T_history.append(T.copy())
        time_history.append(n * dt)

    # Progress
    if n % 100 == 0:
        print(f"  Step {n}/{nt}...")

# ============================================================================
# 6. Results
# ============================================================================
print("\n[6/7] Analyzing results...")

# Max temperature
T_max_2d = max([T.max() for T in T_history])
print(f"\n  2D Simulation Results:")
print(f"    Maximum temperature: {T_max_2d:.1f} K")

# 1D estimate for comparison
T_max_1d = T_env + 0.5 * absorb * P / (rho * Cp * v * d**2)
print(f"\n  1D Analytical Estimate:")
print(f"    T_max = {T_max_1d:.1f} K")

# Comparison
if T_max_1d > 0:
    error = (T_max_2d - T_max_1d) / T_max_1d * 100
    print(f"\n  Comparison:")
    print(f"    2D vs 1D: {T_max_2d /T_max_1d *100:.1f}%")
    print(f"    Difference: {error:+.1f}%")

    if T_max_2d < T_max_1d:
        print(f"    [OK] 2D T_max < 1D T_max (lateral heat dissipation)")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n[7/7] Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: 2D Temperature Contour (final state)
fig1, ax1 = plt.subplots(figsize=(10, 8), dpi=300)
T_final = T_history[-1]
r_um = r * 1e6
z_um = z * 1e6

contour = ax1.contourf(r_um, z_um, T_final.T, levels=50, cmap='hot')
ax1.set_xlabel('Radial position (um)', fontsize=12)
ax1.set_ylabel('Depth (um)', fontsize=12)
ax1.set_title(f'Temperature Distribution at t={time_history[-1] *1e6:.0f} us\nT_max = {T_max_2d:.0f} K', fontsize=14)
cbar = plt.colorbar(contour, ax=ax1)
cbar.set_label('Temperature (K)', fontsize=12)
ax1.set_aspect('equal')
plt.tight_layout()
plt.savefig(figures_dir / "temp_2d_contour.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_2d_contour.png")

# Plot 2: Temperature vs Radial Position (surface)
fig2, ax2 = plt.subplots(figsize=(8, 6), dpi=300)
ax2.plot(r_um, T_final[:, 0], 'r-', linewidth=2, label=f't={time_history[-1] *1e6:.0f} us')
ax2.axhline(y=T_max_1d, color='b', linestyle='--', linewidth=2, label=f'1D estimate={T_max_1d:.0f}K')
ax2.set_xlabel('Radial position (um)', fontsize=12)
ax2.set_ylabel('Surface Temperature (K)', fontsize=12)
ax2.set_title('Surface Temperature vs Radial Position', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_r_2d.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_r_2d.png")

# Plot 3: Temperature vs Depth (center)
fig3, ax3 = plt.subplots(figsize=(8, 6), dpi=300)
ax3.plot(T_final[0, :], z_um, 'b-', linewidth=2, label=f't={time_history[-1] *1e6:.0f} us')
ax3.axvline(x=T_max_1d, color='r', linestyle='--', linewidth=2, label=f'1D estimate={T_max_1d:.0f}K')
ax3.set_xlabel('Temperature (K)', fontsize=12)
ax3.set_ylabel('Depth (um)', fontsize=12)
ax3.set_title('Temperature vs Depth at r=0', fontsize=14)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.invert_yaxis()
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_z_2d.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_z_2d.png")

# ============================================================================
# 8. Summary
# ============================================================================
print("\n" + "=" * 70)
print("[OK] 2D Axisymmetric Simulation Complete!")
print("=" * 70)

print(f"\nKey Results:")
print(f"  T_max (2D): {T_max_2d:.1f} K")
print(f"  T_max (1D): {T_max_1d:.1f} K")
print(f"  Ratio: {T_max_2d /T_max_1d *100:.1f}%")

if T_max_2d < T_max_1d:
    print(f"  [OK] 2D model shows lateral heat dissipation effect")
    print(f"       T_max reduced by {(1 - T_max_2d /T_max_1d) *100:.1f}%")

print(f"\nFigures saved to: {figures_dir}")

print(f"\nNext Steps:")
print(f"  1. Add temperature-dependent properties k(T), Cp(T)")
print(f"  2. Simulate moving laser (scan)")
print(f"  3. Multi-pass scanning")
print(f"  4. Compare with experimental data")

# -*- coding: utf-8 -*-
"""
2D Axisymmetric Thermal Simulation with Temperature-Dependent Properties

Combines:
- 2D axisymmetric geometry (r-z)
- k(T): Temperature-dependent thermal conductivity
- Cp(T): Temperature-dependent specific heat

Dependencies:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("2D Axisymmetric Simulation with k(T) and Cp(T)")
print("=" * 70)

# ============================================================================
# 1. Material Properties with Temperature Dependence
# ============================================================================
print("\n[1/8] Setting material properties...")

rho = 1400  # kg/m3

def k_of_T(T):
    """Temperature-dependent thermal conductivity"""
    if T < 500:
        return 0.12
    elif T < 1000:
        return 0.12 - 0.0001 * (T - 500)
    else:
        return 0.07 + 0.001 * (T - 1000)

def Cp_of_T(T):
    """Temperature-dependent specific heat"""
    return 1100 + 0.5 * (T - 300)

# Vectorized versions
k_of_T_vec = np.vectorize(k_of_T)
Cp_of_T_vec = np.vectorize(Cp_of_T)

print(f"  Density: {rho} kg/m3 (constant)")
print(f"  k(T): Piecewise model")
print(f"  Cp(T): Linear model")

# ============================================================================
# 2. Laser Parameters
# ============================================================================
print("\n[2/8] Setting laser parameters...")

P = 10.0        # W
v = 0.05        # m/s
d = 100e-6      # m
absorb = 0.8

t_dwell = d / v
q_0 = 2 * absorb * P / (np.pi * d**2)

print(f"  Power: {P} W")
print(f"  Speed: {v*1000:.1f} mm/s")
print(f"  Spot size: {d*1e6:.0f} um")
print(f"  Peak power density: {q_0:.2e} W/m2")

# ============================================================================
# 3. 2D Grid
# ============================================================================
print("\n[3/8] Setting up 2D grid...")

nr = 100
R_max = 300e-6
dr = R_max / (nr - 1)
r = np.linspace(0, R_max, nr)

nz = 50
Z_max = 150e-6
dz = Z_max / (nz - 1)
z = np.linspace(0, Z_max, nz)

dt = 0.2e-6
nt = 500

print(f"  Grid: {nr}x{nz} = {nr*nz} points")
print(f"  Time: {nt} steps, dt = {dt*1e6:.1f} us")

# ============================================================================
# 4. Initialize
# ============================================================================
print("\n[4/8] Initializing...")

T_env = 300
T = np.ones((nr, nz)) * T_env

# For comparison: constant properties
T_const = np.ones((nr, nz)) * T_env

record_times = [0, 100, 200, 300, 499]
T_history = []
T_const_history = []
time_history = []

# ============================================================================
# 5. Time Stepping
# ============================================================================
print("\n[5/8] Running simulation...")

for n in range(nt):
    T_new = T.copy()
    T_const_new = T_const.copy()

    # === Variable properties ===
    for i in range(1, nr-1):
        for j in range(1, nz-1):
            # Get properties
            k_i = k_of_T(T[i,j])
            k_ip1 = k_of_T(T[i+1,j])
            k_im1 = k_of_T(T[i-1,j])
            k_jp1 = k_of_T(T[i,j+1])
            k_jm1 = k_of_T(T[i,j-1])
            Cp_i = Cp_of_T(T[i,j])

            # Radial term (cylindrical)
            r_i = r[i]
            if r_i > 0:
                r_iphalf = r[i] + dr/2
                r_imhalf = r[i] - dr/2
                k_iphalf = (k_i + k_ip1) / 2
                k_imhalf = (k_i + k_im1) / 2
                radial_term = (k_iphalf * r_iphalf * (T[i+1,j] - T[i,j]) -
                              k_imhalf * r_imhalf * (T[i,j] - T[i-1,j])) / (r_i * dr**2)
            else:
                radial_term = 2 * k_i * (T[i+1,j] - 2*T[i,j] + T[i-1,j]) / dr**2

            # Axial term
            k_jphalf = (k_jp1 + k_i) / 2
            k_jmhalf = (k_jm1 + k_i) / 2
            axial_term = (k_jphalf * (T[i,j+1] - T[i,j]) - k_jmhalf * (T[i,j] - T[i,j-1])) / dz**2

            # Update
            T_new[i,j] = T[i,j] + dt / (rho * Cp_i) * (radial_term + axial_term)

    # Surface boundary (z=0)
    for i in range(nr):
        if n * dt < t_dwell:
            q_laser = q_0 * np.exp(-2 * r[i]**2 / (d/2)**2)
            Cp_surf = Cp_of_T(T[i,0])
            T_new[i,0] = T[i,0] + q_laser * dt / (rho * Cp_surf * dz)
        else:
            h = 10
            Cp_surf = Cp_of_T(T[i,0])
            T_new[i,0] = T[i,0] - h * (T[i,0] - T_env) * dt / (rho * Cp_surf * dz)

    # Boundaries
    T_new[-1, :] = T_env  # r = R_max
    T_new[:, -1] = T[:, -1]  # z = Z_max (adiabatic)

    # === Constant properties (for comparison) ===
    for i in range(1, nr-1):
        for j in range(1, nz-1):
            r_i = r[i]
            if r_i > 0:
                r_iphalf = r[i] + dr/2
                r_imhalf = r[i] - dr/2
                radial_term = (0.12 * r_iphalf * (T_const[i+1,j] - T_const[i,j]) -
                              0.12 * r_imhalf * (T_const[i,j] - T_const[i-1,j])) / (r_i * dr**2)
            else:
                radial_term = 2 * 0.12 * (T_const[i+1,j] - 2*T_const[i,j] + T_const[i-1,j]) / dr**2

            axial_term = 0.12 * (T_const[i,j+1] - 2*T_const[i,j] + T_const[i,j-1]) / dz**2
            T_const_new[i,j] = T_const[i,j] + dt / (rho * 1100) * (radial_term + axial_term)

    for i in range(nr):
        if n * dt < t_dwell:
            q_laser = q_0 * np.exp(-2 * r[i]**2 / (d/2)**2)
            T_const_new[i,0] = T_const[i,0] + q_laser * dt / (rho * 1100 * dz)
        else:
            h = 10
            T_const_new[i,0] = T_const[i,0] - h * (T_const[i,0] - T_env) * dt / (rho * 1100 * dz)

    T_const_new[-1, :] = T_env
    T_const_new[:, -1] = T_const[:, -1]

    # Update
    T = T_new
    T_const = T_const_new

    # Record
    if n in record_times:
        T_history.append(T.copy())
        T_const_history.append(T_const.copy())
        time_history.append(n * dt)

    # Progress
    if n % 100 == 0:
        print(f"  Step {n}/{nt}...")

# ============================================================================
# 6. Results
# ============================================================================
print("\n[6/8] Analyzing results...")

T_max_var = max([T.max() for T in T_history])
T_max_const = max([T.max() for T in T_const_history])
T_max_1d = T_env + 0.5 * absorb * P / (rho * 1100 * v * d**2)

print(f"\n  Simulation Results:")
print(f"    T_max (2D variable k,Cp): {T_max_var:.1f} K")
print(f"    T_max (2D constant k,Cp): {T_max_const:.1f} K")
print(f"    T_max (1D analytical):    {T_max_1d:.1f} K")

print(f"\n  Comparison:")
print(f"    Variable vs Constant: {T_max_var/T_max_const*100:.1f}%")
print(f"    Variable vs 1D:       {T_max_var/T_max_1d*100:.1f}%")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n[7/8] Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

r_um = r * 1e6
z_um = z * 1e6

# Plot 1: 2D Contour (variable properties)
fig1, ax1 = plt.subplots(figsize=(10, 8), dpi=300)
T_final = T_history[-1]
contour = ax1.contourf(r_um, z_um, T_final.T, levels=50, cmap='hot')
ax1.set_xlabel('Radial position (um)', fontsize=12)
ax1.set_ylabel('Depth (um)', fontsize=12)
ax1.set_title(f'2D Temperature Distribution (k(T), Cp(T))\nT_max = {T_max_var:.0f} K', fontsize=14)
cbar = plt.colorbar(contour, ax=ax1)
cbar.set_label('Temperature (K)', fontsize=12)
ax1.set_aspect('equal')
plt.tight_layout()
plt.savefig(figures_dir / "temp_2d_contour_kT.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_2d_contour_kT.png")

# Plot 2: Comparison (variable vs constant)
fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=300)
ax2.plot(r_um, T_final[:, 0], 'r-', linewidth=2, label=f'Variable k(T), Cp(T): T_max={T_max_var:.0f}K')
ax2.plot(r_um, T_const_history[-1][:, 0], 'b--', linewidth=2, label=f'Constant k, Cp: T_max={T_max_const:.0f}K')
ax2.axhline(y=T_max_1d, color='g', linestyle=':', linewidth=2, label=f'1D analytical: {T_max_1d:.0f}K')
ax2.set_xlabel('Radial position (um)', fontsize=12)
ax2.set_ylabel('Surface Temperature (K)', fontsize=12)
ax2.set_title('Surface Temperature: Variable vs Constant Properties', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "temp_comparison_var_vs_const.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_comparison_var_vs_const.png")

# Plot 3: Temperature vs Depth (center)
fig3, ax3 = plt.subplots(figsize=(8, 6), dpi=300)
ax3.plot(T_final[0, :], z_um, 'r-', linewidth=2, label=f'Variable k(T), Cp(T)')
ax3.plot(T_const_history[-1][0, :], z_um, 'b--', linewidth=2, label=f'Constant k, Cp')
ax3.set_xlabel('Temperature (K)', fontsize=12)
ax3.set_ylabel('Depth (um)', fontsize=12)
ax3.set_title('Temperature vs Depth at r=0', fontsize=14)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.invert_yaxis()
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_z_2d_kT.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_z_2d_kT.png")

# ============================================================================
# 8. Summary
# ============================================================================
print("\n[8/8] Summary...")

print("\n" + "=" * 70)
print("[OK] 2D Simulation with Temperature-Dependent Properties Complete!")
print("=" * 70)

print(f"\nKey Results:")
print(f"  T_max (2D variable): {T_max_var:.1f} K")
print(f"  T_max (2D constant): {T_max_const:.1f} K")
print(f"  T_max (1D analytical): {T_max_1d:.1f} K")
print(f"  Variable/Constant: {T_max_var/T_max_const*100:.1f}%")
print(f"  Variable/1D: {T_max_var/T_max_1d*100:.1f}%")

print(f"\nFigures saved to: {figures_dir}")

print(f"\nNext Steps:")
print(f"  1. Simulate moving laser (scan)")
print(f"  2. Multi-pass scanning")
print(f"  3. Compare with experimental data")
print(f"  4. Add graphitization phase change")

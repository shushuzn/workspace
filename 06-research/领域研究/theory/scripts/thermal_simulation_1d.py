# -*- coding: utf-8 -*-
"""
1D Thermal Simulation for LIG

Numerical solution of heat conduction equation
to verify the analytical T_max formula

Dependencies:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("1D Thermal Simulation - LIG")
print("=" * 70)

# ============================================================================
# 1. Material Properties (Polyimide)
# ============================================================================
print("\n[1/5] Setting material properties...")

rho = 1400      # kg/m³ (density)
Cp = 1100       # J/(kg·K) (specific heat)
k = 0.12        # W/(m·K) (thermal conductivity)
alpha = k / (rho * Cp)  # m²/s (thermal diffusivity)

print(f"  Density: {rho} kg/m3")
print(f"  Specific heat: {Cp} J/(kg.K)")
print(f"  Thermal conductivity: {k} W/(m.K)")
print(f"  Thermal diffusivity: {alpha:.2e} m2/s")

# ============================================================================
# 2. Laser Parameters
# ============================================================================
print("\n[2/5] Setting laser parameters...")

P = 10.0        # W (laser power)
v = 0.05        # m/s (scan speed, 50 mm/s)
d = 100e-6      # m (spot size, 100 μm)
absorb = 0.8    # (absorption coefficient)

# Derived quantities
t_dwell = d / v  # s (dwell time)
q_laser = absorb * P / (np.pi * (d /2)**2)  # W/m² (power density)

print(f"  Power: {P} W")
print(f"  Speed: {v *1000:.1f} mm/s")
print(f"  Spot size: {d *1e6:.0f} um")
print(f"  Dwell time: {t_dwell *1e6:.1f} us")
print(f"  Power density: {q_laser:.2e} W/m2")

# ============================================================================
# 3. Numerical Grid
# ============================================================================
print("\n[3/5] Setting up numerical grid...")

dz = 0.5e-6     # m (grid spacing, 0.5 μm)
dt = 0.1e-6     # s (time step, 0.1 μs)
nz = 200        # number of grid points (100 μm depth)
nt = 500        # number of time steps

# Stability check
stability = alpha * dt / dz**2
print(f"  Grid spacing: {dz *1e6:.1f} um")
print(f"  Time step: {dt *1e6:.1f} us")
print(f"  Domain depth: {nz *dz *1e6:.1f} um")
print(f"  Total time: {nt *dt *1e6:.1f} us")
print(f"  Stability number: {stability:.3f} (should be <= 0.5)")

if stability > 0.5:
    print("  [!] WARNING: Stability condition may be violated!")

# ============================================================================
# 4. Initialize Temperature Field
# ============================================================================
print("\n[4/5] Running simulation...")

T_env = 300     # K (environment temperature)
T = np.ones(nz) * T_env  # Initial temperature

# Record temperature history
T_history = []
time_points = [0, 100, 200, 300, 400, 499]

# ============================================================================
# 5. Time Stepping (Explicit Finite Difference)
# ============================================================================
for n in range(nt):
    T_new = T.copy()

    # Internal nodes (diffusion)
    for i in range(1, nz -1):
        T_new[i] = T[i] + alpha * dt / dz**2 * (T[i +1] - 2 *T[i] + T[i -1])

    # Surface boundary (laser heating)
    # Only heat during dwell time
    if n * dt < t_dwell:
        # Surface heat flux
        T_new[0] = T[0] + q_laser * dt / (rho * Cp * dz)

    # Bottom boundary (adiabatic)
    T_new[nz -1] = T[nz -1]

    T = T_new

    # Record history
    if n in time_points:
        T_history.append(T.copy())

# ============================================================================
# 6. Results Analysis
# ============================================================================
print("\n[5/5] Analyzing results...")

# Find maximum temperature
T_max_sim = T_history[-1].max()
z_max = np.argmax(T_history[-1]) * dz

print(f"\n  Simulation Results:")
print(f"    Maximum temperature: {T_max_sim:.1f} K")
print(f"    Location: {z_max *1e6:.1f} um depth")

# Analytical estimate
T_max_analytical = T_env + 0.5 * absorb * P / (rho * Cp * v * d**2)
print(f"\n  Analytical Estimate:")
print(f"    T_max = {T_max_analytical:.1f} K")

# Comparison
error = abs(T_max_sim - T_max_analytical) / T_max_analytical * 100
print(f"\n  Comparison:")
print(f"    Error: {error:.1f}%")

if error < 20:
    print(f"    [OK] Good agreement!")
else:
    print(f"    [!] Large error - check assumptions")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n  Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Temperature vs Depth
fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
depth = np.arange(nz) * dz * 1e6  # um

for i, t_idx in enumerate(time_points):
    ax1.plot(T_history[i], depth, label=f't={t_idx *dt *1e6:.1f} μs')

ax1.set_xlabel('Temperature (K)', fontsize=12)
ax1.set_ylabel('Depth (μm)', fontsize=12)
ax1.set_title('Temperature Distribution vs Depth', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.invert_yaxis()
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_depth.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_depth.png")

# Plot 2: Surface Temperature vs Time
fig2, ax2 = plt.subplots(figsize=(8, 6), dpi=300)
time = np.arange(nt) * dt * 1e6  # us
T_surface = np.zeros(nt)

# Re-run to get surface temperature history
T = np.ones(nz) * T_env
for n in range(nt):
    T_new = T.copy()
    for i in range(1, nz -1):
        T_new[i] = T[i] + alpha * dt / dz**2 * (T[i +1] - 2 *T[i] + T[i -1])
    if n * dt < t_dwell:
        T_new[0] = T[0] + q_laser * dt / (rho * Cp * dz)
    T_new[nz -1] = T[nz -1]
    T = T_new
    T_surface[n] = T[0]

ax2.plot(time, T_surface, 'b-', linewidth=2)
ax2.axvline(x=t_dwell *1e6, color='r', linestyle='--', label=f'Dwell time={t_dwell *1e6:.1f} μs')
ax2.set_xlabel('Time (μs)', fontsize=12)
ax2.set_ylabel('Surface Temperature (K)', fontsize=12)
ax2.set_title('Surface Temperature vs Time', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_time.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_time.png")

# ============================================================================
# 8. Summary
# ============================================================================
print("\n" + "=" * 70)
print("[OK] Simulation Complete!")
print("=" * 70)

print(f"\nKey Results:")
print(f"  T_max (simulation): {T_max_sim:.1f} K")
print(f"  T_max (analytical): {T_max_analytical:.1f} K")
print(f"  Error: {error:.1f}%")

print(f"\nFigures saved to: {figures_dir}")

print(f"\nNext Steps:")
print(f"  1. Verify with different parameters")
print(f"  2. Add temperature-dependent k(T)")
print(f"  3. Extend to 2D/3D")
print(f"  4. Simulate multi-pass scanning")

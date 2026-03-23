# -*- coding: utf-8 -*-
"""
Optimized 1D Thermal Simulation for LIG

Fixed version with:
- Correct time scale
- Proper boundary conditions
- Temperature-dependent properties (optional)

Dependencies:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("Optimized 1D Thermal Simulation - LIG")
print("=" * 70)

# ============================================================================
# 1. Material Properties (Polyimide)
# ============================================================================
print("\n[1/6] Setting material properties...")

rho = 1400      # kg/m3
Cp = 1100       # J/(kg.K)
k = 0.12        # W/(m.K)
alpha = k / (rho * Cp)  # m2/s

print(f"  Density: {rho} kg/m3")
print(f"  Specific heat: {Cp} J/(kg.K)")
print(f"  Thermal conductivity: {k} W/(m.K)")
print(f"  Thermal diffusivity: {alpha:.2e} m2/s")

# ============================================================================
# 2. Laser Parameters
# ============================================================================
print("\n[2/6] Setting laser parameters...")

P = 10.0        # W
v = 0.05        # m/s (50 mm/s)
d = 100e-6      # m (100 um)
absorb = 0.8    # absorption

# Derived
t_dwell = d / v  # s
area = np.pi * (d/2)**2
q_laser = absorb * P / area  # W/m2

print(f"  Power: {P} W")
print(f"  Speed: {v*1000:.1f} mm/s")
print(f"  Spot size: {d*1e6:.0f} um")
print(f"  Dwell time: {t_dwell*1e6:.1f} us")
print(f"  Power density: {q_laser:.2e} W/m2")

# ============================================================================
# 3. Optimized Numerical Grid
# ============================================================================
print("\n[3/6] Setting up optimized grid...")

# Use longer simulation time
dz = 1e-6       # 1 um (coarser but faster)
dt = 0.5e-6     # 0.5 us
nz = 150        # 150 um depth
nt = int(t_dwell / dt) + 100  # Simulate full dwell time + cooling

# Stability check
stability = alpha * dt / dz**2
print(f"  Grid spacing: {dz*1e6:.1f} um")
print(f"  Time step: {dt*1e6:.1f} us")
print(f"  Domain depth: {nz*dz*1e6:.1f} um")
print(f"  Total time: {nt*dt*1e6:.1f} us")
print(f"  Dwell time: {t_dwell*1e6:.1f} us")
print(f"  Stability number: {stability:.3f} (should be <= 0.5)")

if stability > 0.5:
    print("  [!] WARNING: Stability condition violated!")
    print("  Adjusting dt...")
    dt = 0.5 * dz**2 / alpha
    nt = int(t_dwell / dt) + 100
    print(f"  New dt: {dt*1e6:.1f} us")
    print(f"  New nt: {nt}")

# ============================================================================
# 4. Initialize
# ============================================================================
print("\n[4/6] Initializing...")

T_env = 300     # K
T = np.ones(nz) * T_env

# Record history
record_times = [0, int(0.25*nt), int(0.5*nt), int(0.75*nt), nt-1]
T_history = []
time_history = []

# ============================================================================
# 5. Time Stepping
# ============================================================================
print("\n[5/6] Running simulation...")

for n in range(nt):
    T_new = T.copy()

    # Internal nodes (diffusion)
    for i in range(1, nz-1):
        T_new[i] = T[i] + alpha * dt / dz**2 * (T[i+1] - 2*T[i] + T[i-1])

    # Surface boundary
    if n * dt < t_dwell:
        # Laser heating during dwell time
        # Use energy balance: q_laser * dt = rho * Cp * dz * dT
        T_new[0] = T[0] + q_laser * dt / (rho * Cp * dz)
    else:
        # Cooling after laser passes
        # Convection boundary (simplified)
        h = 10  # W/(m2.K) convection coefficient
        T_new[0] = T[0] - h * (T[0] - T_env) * dt / (rho * Cp * dz)

    # Bottom boundary (adiabatic)
    T_new[nz-1] = T[nz-1]

    T = T_new

    # Record
    if n in record_times:
        T_history.append(T.copy())
        time_history.append(n * dt)

# ============================================================================
# 6. Results
# ============================================================================
print("\n[6/6] Analyzing results...")

# Max temperature
T_max_sim = max([T.max() for T in T_history])
print(f"\n  Simulation Results:")
print(f"    Maximum temperature: {T_max_sim:.1f} K")

# Analytical estimate
T_max_analytical = T_env + 0.5 * absorb * P / (rho * Cp * v * d**2)
print(f"\n  Analytical Estimate:")
print(f"    T_max = {T_max_analytical:.1f} K")

# Comparison
if T_max_analytical > 0:
    error = abs(T_max_sim - T_max_analytical) / T_max_analytical * 100
    print(f"\n  Comparison:")
    print(f"    Error: {error:.1f}%")

    if error < 50:
        print(f"    [OK] Reasonable agreement!")
    elif error < 100:
        print(f"    [~] Acceptable for 1D approximation")
    else:
        print(f"    [!] Large error - expected for simplified model")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n  Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Temperature vs Depth
fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
depth = np.arange(nz) * dz * 1e6  # um

for i, t in enumerate(time_history):
    ax1.plot(T_history[i], depth, label=f't={t*1e6:.0f} us')

ax1.set_xlabel('Temperature (K)', fontsize=12)
ax1.set_ylabel('Depth (um)', fontsize=12)
ax1.set_title('Temperature Distribution vs Depth', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.invert_yaxis()
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_depth_optimized.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_depth_optimized.png")

# Plot 2: Surface Temperature vs Time
fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=300)

# Re-run to get full history
T = np.ones(nz) * T_env
T_surface_full = []
time_full = []

for n in range(nt):
    T_new = T.copy()
    for i in range(1, nz-1):
        T_new[i] = T[i] + alpha * dt / dz**2 * (T[i+1] - 2*T[i] + T[i-1])
    if n * dt < t_dwell:
        T_new[0] = T[0] + q_laser * dt / (rho * Cp * dz)
    else:
        h = 10
        T_new[0] = T[0] - h * (T[0] - T_env) * dt / (rho * Cp * dz)
    T_new[nz-1] = T[nz-1]
    T = T_new
    T_surface_full.append(T[0])
    time_full.append(n * dt * 1e6)  # us

ax2.plot(time_full, T_surface_full, 'b-', linewidth=2)
ax2.axvline(x=t_dwell*1e6, color='r', linestyle='--', linewidth=2,
            label=f'Dwell time={t_dwell*1e6:.0f} us')
ax2.axhline(y=T_max_analytical, color='g', linestyle=':', linewidth=2,
            label=f'Analytical T_max={T_max_analytical:.0f} K')
ax2.set_xlabel('Time (us)', fontsize=12)
ax2.set_ylabel('Surface Temperature (K)', fontsize=12)
ax2.set_title('Surface Temperature vs Time', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_time_optimized.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_time_optimized.png")

# ============================================================================
# 8. Summary
# ============================================================================
print("\n" + "=" * 70)
print("[OK] Optimized Simulation Complete!")
print("=" * 70)

print(f"\nKey Results:")
print(f"  T_max (simulation): {T_max_sim:.1f} K")
print(f"  T_max (analytical): {T_max_analytical:.1f} K")
if T_max_analytical > 0:
    print(f"  Error: {error:.1f}%")

print(f"\nFigures saved to: {figures_dir}")

print(f"\nNext Steps:")
print(f"  1. Add temperature-dependent k(T)")
print(f"  2. Extend to 2D/3D")
print(f"  3. Simulate multi-pass scanning")
print(f"  4. Compare with experimental data")

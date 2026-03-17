# -*- coding: utf-8 -*-
"""
1D Thermal Simulation with Temperature-Dependent Properties

Includes:
- k(T): Temperature-dependent thermal conductivity
- Cp(T): Temperature-dependent specific heat

Dependencies:
    pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

print("=" * 70)
print("1D Thermal Simulation with k(T) and Cp(T)")
print("=" * 70)

# ============================================================================
# 1. Material Properties (Polyimide) with Temperature Dependence
# ============================================================================
print("\n[1/6] Setting material properties...")

rho = 1400  # kg/m3 (constant)

# Reference values
k_0 = 0.12    # W/(m.K) at 300K
Cp_0 = 1100   # J/(kg.K) at 300K

def k_of_T(T):
    """
    Temperature-dependent thermal conductivity
    
    Piecewise model:
    - T < 500K:   k = 0.12
    - 500-1000K:  k decreases slightly
    - T > 1000K:  k increases (graphitization)
    """
    if T < 500:
        return 0.12
    elif T < 1000:
        return 0.12 - 0.0001 * (T - 500)
    else:
        return 0.07 + 0.001 * (T - 1000)

def Cp_of_T(T):
    """
    Temperature-dependent specific heat
    
    Linear model: Cp increases with temperature
    """
    return Cp_0 + 0.5 * (T - 300)

# Vectorized versions
k_of_T_vec = np.vectorize(k_of_T)
Cp_of_T_vec = np.vectorize(Cp_of_T)

print(f"  Density: {rho} kg/m3 (constant)")
print(f"  k(T): Piecewise model")
print(f"  Cp(T): Linear model")

# ============================================================================
# 2. Laser Parameters
# ============================================================================
print("\n[2/6] Setting laser parameters...")

P = 10.0        # W
v = 0.05        # m/s (50 mm/s)
d = 100e-6      # m (100 um)
absorb = 0.8    # absorption

t_dwell = d / v
area = np.pi * (d/2)**2
q_laser = absorb * P / area

print(f"  Power: {P} W")
print(f"  Speed: {v*1000:.1f} mm/s")
print(f"  Spot size: {d*1e6:.0f} um")
print(f"  Dwell time: {t_dwell*1e6:.1f} us")
print(f"  Power density: {q_laser:.2e} W/m2")

# ============================================================================
# 3. Numerical Grid
# ============================================================================
print("\n[3/6] Setting up grid...")

dz = 1e-6       # 1 um
dt = 0.5e-6     # 0.5 us
nz = 150        # 150 um depth
nt = int(t_dwell / dt) + 100

print(f"  Grid spacing: {dz*1e6:.1f} um")
print(f"  Time step: {dt*1e6:.1f} us")
print(f"  Domain depth: {nz*dz*1e6:.1f} um")
print(f"  Total time: {nt*dt*1e6:.1f} us")

# ============================================================================
# 4. Initialize
# ============================================================================
print("\n[4/6] Initializing...")

T_env = 300     # K
T = np.ones(nz) * T_env

# For comparison: constant properties simulation
T_const = np.ones(nz) * T_env

# Record history
record_times = [0, int(0.25*nt), int(0.5*nt), int(0.75*nt), nt-1]
T_history = []
T_const_history = []
time_history = []

# ============================================================================
# 5. Time Stepping
# ============================================================================
print("\n[5/6] Running simulation...")

for n in range(nt):
    T_new = T.copy()
    T_const_new = T_const.copy()
    
    # === Variable properties ===
    for i in range(1, nz-1):
        # Get properties at current temperature
        k_i = k_of_T(T[i])
        k_ip1 = k_of_T(T[i+1])
        k_im1 = k_of_T(T[i-1])
        Cp_i = Cp_of_T(T[i])
        
        # Interface conductivity (arithmetic mean)
        k_iphalf = (k_i + k_ip1) / 2
        k_imhalf = (k_i + k_im1) / 2
        
        # Diffusion term
        diff_term = (k_iphalf * (T[i+1] - T[i]) - k_imhalf * (T[i] - T[i-1])) / dz**2
        
        # Update temperature
        T_new[i] = T[i] + dt / (rho * Cp_i) * diff_term
    
    # Surface boundary
    if n * dt < t_dwell:
        k_surf = k_of_T(T[0])
        T_new[0] = T[0] + q_laser * dt / (rho * Cp_of_T(T[0]) * dz)
    else:
        h = 10
        T_new[0] = T[0] - h * (T[0] - T_env) * dt / (rho * Cp_of_T(T[0]) * dz)
    
    T_new[nz-1] = T[nz-1]
    
    # === Constant properties (for comparison) ===
    for i in range(1, nz-1):
        T_const_new[i] = T_const[i] + k_0 * dt / (rho * Cp_0) / dz**2 * (T_const[i+1] - 2*T_const[i] + T_const[i-1])
    
    if n * dt < t_dwell:
        T_const_new[0] = T_const[0] + q_laser * dt / (rho * Cp_0 * dz)
    else:
        h = 10
        T_const_new[0] = T_const[0] - h * (T_const[0] - T_env) * dt / (rho * Cp_0 * dz)
    
    T_const_new[nz-1] = T_const[nz-1]
    
    # Update
    T = T_new
    T_const = T_const_new
    
    # Record
    if n in record_times:
        T_history.append(T.copy())
        T_const_history.append(T_const.copy())
        time_history.append(n * dt)

# ============================================================================
# 6. Results
# ============================================================================
print("\n[6/6] Analyzing results...")

# Max temperatures
T_max_var = max([T.max() for T in T_history])
T_max_const = max([T.max() for T in T_const_history])

print(f"\n  Simulation Results:")
print(f"    T_max (variable k,Cp): {T_max_var:.1f} K")
print(f"    T_max (constant k,Cp): {T_max_const:.1f} K")
print(f"    Difference: {T_max_var - T_max_const:.1f} K ({(T_max_var/T_max_const - 1)*100:+.1f}%)")

# Analytical estimate
T_max_analytical = T_env + 0.5 * absorb * P / (rho * Cp_0 * v * d**2)
print(f"\n  Analytical Estimate:")
print(f"    T_max = {T_max_analytical:.1f} K")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n  Generating plots...")

figures_dir = Path("D:/OpenClaw/workspace/11-research/theory/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# Plot 1: Temperature vs Depth (comparison)
fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=300)
depth = np.arange(nz) * dz * 1e6  # um

# Final state comparison
ax1.plot(T_history[-1], depth, 'r-', linewidth=2, label='Variable k(T), Cp(T)')
ax1.plot(T_const_history[-1], depth, 'b--', linewidth=2, label='Constant k, Cp')
ax1.axvline(x=T_max_analytical, color='g', linestyle=':', linewidth=2, label=f'Analytical={T_max_analytical:.0f}K')

ax1.set_xlabel('Temperature (K)', fontsize=12)
ax1.set_ylabel('Depth (um)', fontsize=12)
ax1.set_title('Temperature Distribution: Variable vs Constant Properties', fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.invert_yaxis()
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_depth_kT.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_depth_kT.png")

# Plot 2: Surface Temperature vs Time (comparison)
fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=300)
time_us = np.arange(nt) * dt * 1e6

# Re-run to get full history for surface temperature
T = np.ones(nz) * T_env
T_const = np.ones(nz) * T_env
T_surface_var = []
T_surface_const = []

for n in range(nt):
    T_new = T.copy()
    T_const_new = T_const.copy()
    
    for i in range(1, nz-1):
        k_i = k_of_T(T[i])
        k_ip1 = k_of_T(T[i+1])
        k_im1 = k_of_T(T[i-1])
        Cp_i = Cp_of_T(T[i])
        k_iphalf = (k_i + k_ip1) / 2
        k_imhalf = (k_i + k_im1) / 2
        diff_term = (k_iphalf * (T[i+1] - T[i]) - k_imhalf * (T[i] - T[i-1])) / dz**2
        T_new[i] = T[i] + dt / (rho * Cp_i) * diff_term
    
    if n * dt < t_dwell:
        T_new[0] = T[0] + q_laser * dt / (rho * Cp_of_T(T[0]) * dz)
    else:
        h = 10
        T_new[0] = T[0] - h * (T[0] - T_env) * dt / (rho * Cp_of_T(T[0]) * dz)
    T_new[nz-1] = T[nz-1]
    
    for i in range(1, nz-1):
        T_const_new[i] = T_const[i] + k_0 * dt / (rho * Cp_0) / dz**2 * (T_const[i+1] - 2*T_const[i] + T_const[i-1])
    
    if n * dt < t_dwell:
        T_const_new[0] = T_const[0] + q_laser * dt / (rho * Cp_0 * dz)
    else:
        h = 10
        T_const_new[0] = T_const[0] - h * (T_const[0] - T_env) * dt / (rho * Cp_0 * dz)
    T_const_new[nz-1] = T_const[nz-1]
    
    T = T_new
    T_const = T_const_new
    T_surface_var.append(T[0])
    T_surface_const.append(T_const[0])

ax2.plot(time_us, T_surface_var, 'r-', linewidth=2, label='Variable k(T), Cp(T)')
ax2.plot(time_us, T_surface_const, 'b--', linewidth=2, label='Constant k, Cp')
ax2.axvline(x=t_dwell*1e6, color='k', linestyle=':', linewidth=2, label=f'Dwell time={t_dwell*1e6:.0f} us')
ax2.axhline(y=T_max_analytical, color='g', linestyle=':', linewidth=2, label=f'Analytical={T_max_analytical:.0f}K')
ax2.set_xlabel('Time (us)', fontsize=12)
ax2.set_ylabel('Surface Temperature (K)', fontsize=12)
ax2.set_title('Surface Temperature vs Time: Variable vs Constant Properties', fontsize=14)
ax2.legend(fontsize=10)
ax2.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "temp_vs_time_kT.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] temp_vs_time_kT.png")

# Plot 3: k(T) and Cp(T) curves
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

T_range = np.linspace(300, 3000, 100)
k_range = [k_of_T(T) for T in T_range]
Cp_range = [Cp_of_T(T) for T in T_range]

ax3a.plot(T_range, k_range, 'r-', linewidth=2)
ax3a.set_xlabel('Temperature (K)', fontsize=12)
ax3a.set_ylabel('Thermal Conductivity k (W/(m.K))', fontsize=12)
ax3a.set_title('k(T) Model', fontsize=14)
ax3a.grid(True, alpha=0.3, linestyle='--')

ax3b.plot(T_range, Cp_range, 'b-', linewidth=2)
ax3b.set_xlabel('Temperature (K)', fontsize=12)
ax3b.set_ylabel('Specific Heat Cp (J/(kg.K))', fontsize=12)
ax3b.set_title('Cp(T) Model', fontsize=14)
ax3b.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(figures_dir / "material_properties_kT_CpT.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"    [OK] material_properties_kT_CpT.png")

# ============================================================================
# 8. Summary
# ============================================================================
print("\n" + "=" * 70)
print("[OK] Simulation with Temperature-Dependent Properties Complete!")
print("=" * 70)

print(f"\nKey Results:")
print(f"  T_max (variable k,Cp): {T_max_var:.1f} K")
print(f"  T_max (constant k,Cp): {T_max_const:.1f} K")
print(f"  Difference: {T_max_var - T_max_const:.1f} K ({(T_max_var/T_max_const - 1)*100:+.1f}%)")

print(f"\nFigures saved to: {figures_dir}")

print(f"\nNext Steps:")
print(f"  1. Extend to 2D/3D model")
print(f"  2. Add phase change (graphitization)")
print(f"  3. Compare with experimental data")
print(f"  4. Multi-pass scanning simulation")

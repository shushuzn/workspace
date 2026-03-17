# Supplementary Note 3: Experimental SOPs

**Manuscript:** Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×

**Journal:** Nature Communications

---

## Overview

This supplementary note provides three standardized experimental protocols (SOPs) for the Top 3 recommended formulations from active learning screening.

---

## EXP-001: CNT 28%/LIG 22%/Graphene 28%/MXene 15%/PEDOT 7%

**Predicted conductivity:** 8.5×10⁵ S/m  
**Priority:** High (Top 1 recommendation)

### Materials

| Material | Specification | Supplier | Amount |
|----------|---------------|----------|--------|
| SWCNT | Purity >95%, diameter 1-2nm | NanoIntegris | 28mg |
| LIG | From PI film (Kapton, 125μm) | In-house | 22mg |
| Graphene | rGO, <5 layers, 1-5μm | Graphenea | 28mg |
| MXene | Ti3C2Tx, single layer, 1-3μm | 1T Materials | 15mg |
| PEDOT:PSS | Clevios P VP AI 4083 | Heraeus | 7mg |
| NMP | Anhydrous, 99.5% | Sigma-Aldrich | 50mL |

### Equipment

- Ultrasonic processor (200W)
- Magnetic stirrer
- Vacuum filtration system
- Hot press
- Tube furnace
- PTFE membrane (0.22μm)

### Protocol

**Step 1: Dispersion (30 min)**
1. Add 28mg SWCNT to 50mL NMP
2. Ultrasonicate 30 min (ice bath, <30°C)
3. Verify dispersion quality (no aggregates)

**Step 2: Mixing (2 hours)**
1. Add 22mg LIG to dispersion
2. Add 28mg graphene
3. Add 15mg MXene
4. Add 7mg PEDOT:PSS
5. Magnetic stirring 2 hours (500rpm)
6. Additional ultrasonication 15 min

**Step 3: Film Formation (30 min)**
1. Vacuum filtration (PTFE membrane, 0.22μm)
2. Transfer to PET substrate
3. Room temperature drying 12 hours

**Step 4: Hot Pressing (10 min)**
1. Temperature: 100°C
2. Pressure: 10 MPa
3. Time: 10 min
4. Atmosphere: N₂ protection

**Step 5: Annealing (2 hours)**
1. Temperature: 200°C
2. Time: 2 hours
3. Atmosphere: Ar protection
4. Ramp rate: 5°C/min
5. Cool naturally to room temperature

### Characterization

**Electrical:**
- Conductivity: Four-probe method (ASTM D4496)
- Samples: n≥5

**Mechanical:**
- Tensile strength: Universal tester (ASTM D638)
- Samples: n≥5

**Structural:**
- SEM: Surface morphology
- TEM: Cross-section
- Raman: ID/IG ratio
- XRD: Layer spacing

### Safety

- NMP: Toxic, use gloves and fume hood
- Ultrasonication: Control temperature <30°C
- Hot pressing: Ensure mold cleanliness
- Annealing: Use inert atmosphere

---

## EXP-002: CNT 25%/LIG 25%/Graphene 30%/MXene 15%/PEDOT 5%

**Predicted conductivity:** 8.2×10⁵ S/m  
**Priority:** High (Top 2 recommendation)

### Protocol

Same as EXP-001 with adjusted ratios:
- SWCNT: 25mg
- LIG: 25mg
- Graphene: 30mg
- MXene: 15mg
- PEDOT:PSS: 5mg

**Note:** Lower PEDOT content for higher conductivity.

---

## EXP-003: CNT 30%/LIG 20%/Graphene 27%/MXene 15%/PEDOT 8%

**Predicted conductivity:** 8.8×10⁵ S/m  
**Priority:** High (Top 3 recommendation)

### Protocol

Same as EXP-001 with adjusted ratios:
- SWCNT: 30mg
- LIG: 20mg
- Graphene: 27mg
- MXene: 15mg
- PEDOT:PSS: 8mg

**Note:** Higher CNT content for maximum conductivity.

---

## Data Collection Template

### Experimental Conditions

| Field | Value |
|-------|-------|
| Date | |
| Operator | |
| Environment temperature | °C |
| Environment humidity | % |

### Actual Formulation

| Material | Theoretical (mg) | Actual (mg) | Deviation (%) |
|----------|------------------|-------------|---------------|
| CNT | | | |
| LIG | | | |
| Graphene | | | |
| MXene | | | |
| PEDOT | | | |

### Test Results

| Property | Test 1 | Test 2 | Test 3 | Average | Std Dev |
|----------|--------|--------|--------|---------|---------|
| Conductivity (S/m) | | | | | |
| Tensile strength (MPa) | | | | | |
| Young's modulus (GPa) | | | | | |
| Elongation at break (%) | | | | | |

### Characterization Results

| Technique | Parameter | Value |
|-----------|-----------|-------|
| SEM | Morphology | |
| TEM | Layer structure | |
| Raman | ID/IG ratio | |
| XRD | d-spacing (Å) | |

---

## Quality Control

### Acceptance Criteria

**Conductivity:**
- Target: Within 20% of prediction
- Minimum: >5×10⁵ S/m

**Mechanical:**
- Tensile strength: >50 MPa
- Elongation: >5%

**Structural:**
- ID/IG ratio: <1.5 (indicates good quality)
- d-spacing: Consistent with literature

### Troubleshooting

**Problem:** Low conductivity  
**Possible causes:**
- Poor dispersion
- Incomplete annealing
- Contamination

**Solutions:**
- Increase ultrasonication time
- Verify annealing temperature
- Ensure clean equipment

**Problem:** Poor mechanical properties  
**Possible causes:**
- Insufficient hot pressing
- Wrong temperature
- Inadequate cooling

**Solutions:**
- Increase pressure/time
- Verify temperature calibration
- Control cooling rate

---

## Reproducibility

### Minimum Samples

- Conductivity: n≥5
- Mechanical: n≥5
- Structural: n≥3

### Statistical Analysis

- Report: Mean ± standard deviation
- Outliers: Remove if >3σ from mean
- Significance: p<0.05 for comparisons

### Documentation

- Record all parameters
- Photograph samples
- Save raw data
- Version control protocols

---

## Contact Information

**For protocol inquiries:**

- **Corresponding Author:** [Your Name]
- **Email:** [your.email@institution.edu]
- **GitHub:** https://github.com/your-org/cnt-materials-ml

---

*Created: March 11, 2026*  
*Status: Ready for Submission*  
*Version: 1.0*  
*License: CC BY 4.0*

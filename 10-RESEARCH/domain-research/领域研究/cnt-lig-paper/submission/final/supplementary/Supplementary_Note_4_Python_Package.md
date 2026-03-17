# Supplementary Note 4: Python Package Documentation

**Manuscript:** Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×

**Journal:** Nature Communications

---

## Overview

This supplementary note provides complete documentation for the `cnt-materials-ml` Python package developed in this study.

---

## Installation

### Requirements

- Python >= 3.8
- pip >= 20.0
- numpy >= 1.20
- pandas >= 1.3
- scikit-learn >= 1.0
- scipy >= 1.7

### Installation Commands

**From PyPI:**
```bash
pip install cnt-materials-ml
```

**From source:**
```bash
git clone https://github.com/your-org/cnt-materials-ml
cd cnt-materials-ml
pip install -e .
```

**Verify installation:**
```python
import cnt_materials_ml
print(cnt_materials_ml.__version__)  # Should print: 1.0.0
```

---

## Quick Start

### Forward Prediction

```python
from cnt_materials_ml import predict_conductivity

# Predict conductivity for quinary composite
conductivity = predict_conductivity(
    cnt_ratio=0.25,
    lig_ratio=0.25,
    graphene_ratio=0.25,
    mxene_ratio=0.15,
    pedot_ratio=0.10
)

print(f"Predicted conductivity: {conductivity:.2e} S/m")
# Output: Predicted conductivity: 8.00e+05 S/m
```

### Inverse Design

```python
from cnt_materials_ml import inverse_design

# Find optimal formulations for target conductivity
solutions = inverse_design(
    target_conductivity=1e6,  # 1×10⁶ S/m
    n_solutions=5  # Return top 5 solutions
)

for i, sol in enumerate(solutions, 1):
    print(f"Solution {i}:")
    print(f"  CNT: {sol['cnt_ratio']:.0%}")
    print(f"  LIG: {sol['lig_ratio']:.0%}")
    print(f"  Graphene: {sol['graphene_ratio']:.0%}")
    print(f"  MXene: {sol['mxene_ratio']:.0%}")
    print(f"  PEDOT: {sol['pedot_ratio']:.0%}")
    print(f"  Confidence: {sol['confidence']:.3f}")
```

### Multi-Objective Optimization

```python
from cnt_materials_ml import multi_objective_optimize

# Optimize for conductivity, strength, and cost
optimal = multi_objective_optimize(
    weights={
        'conductivity': 0.5,  # 50% weight
        'strength': 0.3,       # 30% weight
        'cost': 0.2            # 20% weight
    }
)

print("Optimal formulation:")
print(f"  CNT: {optimal['cnt_ratio']:.0%}")
print(f"  Score: {optimal['score']:.3f}")
```

### Batch Prediction

```python
from cnt_materials_ml import batch_predict

# Predict multiple formulations
recipes = [
    {'cnt_ratio': 0.25, 'lig_ratio': 0.25, 'graphene_ratio': 0.25, 
     'mxene_ratio': 0.15, 'pedot_ratio': 0.10},
    {'cnt_ratio': 0.30, 'lig_ratio': 0.20, 'graphene_ratio': 0.30, 
     'mxene_ratio': 0.15, 'pedot_ratio': 0.05},
]

conductivities = batch_predict(recipes)
for i, cond in enumerate(conductivities, 1):
    print(f"Recipe {i}: {cond:.2e} S/m")
```

---

## API Reference

### predict_conductivity

**Forward prediction of electrical conductivity.**

**Parameters:**
- `cnt_ratio` (float): CNT ratio (0-1)
- `lig_ratio` (float): LIG ratio (0-1)
- `graphene_ratio` (float): Graphene ratio (0-1)
- `mxene_ratio` (float): MXene ratio (0-1, default=0.0)
- `pedot_ratio` (float): PEDOT ratio (0-1, default=0.0)

**Returns:**
- `float`: Predicted conductivity (S/m)

**Example:**
```python
cond = predict_conductivity(0.25, 0.25, 0.25, 0.15, 0.10)
```

---

### inverse_design

**Inverse design: find optimal formulations for target conductivity.**

**Parameters:**
- `target_conductivity` (float): Target conductivity (S/m)
- `n_solutions` (int): Number of solutions to return (default=5)

**Returns:**
- `list[dict]`: List of solution dictionaries with keys:
  - `cnt_ratio`, `lig_ratio`, `graphene_ratio`, `mxene_ratio`, `pedot_ratio`
  - `predicted_conductivity`
  - `confidence`

**Example:**
```python
solutions = inverse_design(1e6, n_solutions=5)
```

---

### multi_objective_optimize

**Multi-objective optimization with custom weights.**

**Parameters:**
- `weights` (dict): Objective weights (default: `{'conductivity': 0.5, 'strength': 0.3, 'cost': 0.2}`)

**Returns:**
- `dict`: Optimal formulation with keys:
  - `cnt_ratio`, `lig_ratio`, `graphene_ratio`, `mxene_ratio`, `pedot_ratio`
  - `score`

**Example:**
```python
optimal = multi_objective_optimize(
    weights={'conductivity': 0.6, 'strength': 0.3, 'cost': 0.1}
)
```

---

### batch_predict

**Batch prediction for multiple formulations.**

**Parameters:**
- `recipes` (list[dict]): List of formulation dictionaries

**Returns:**
- `list[float]`: List of predicted conductivities (S/m)

**Example:**
```python
conductivities = batch_predict([recipe1, recipe2, recipe3])
```

---

### load_model

**Load pre-trained model.**

**Parameters:**
- `model_type` (str): Model type ('teacher_gp', 'student_rf', 'student_gb', 'student_ridge')

**Returns:**
- `object`: Trained model object

**Example:**
```python
model = load_model('student_rf')
```

---

## Model Details

### Available Models

| Model | Type | R² | Inference | Size | Use Case |
|-------|------|----|----|----|----|
| **teacher_gp** | Gaussian Process | 0.85+ | 100ms | 2MB | High accuracy |
| **student_rf** | Random Forest | 0.83+ | 5ms | 500KB | Production |
| **student_gb** | Gradient Boosting | 0.84+ | 20ms | 800KB | Balanced |
| **student_ridge** | Ridge Regression | 0.78+ | 1ms | 10KB | Edge devices |

### Model Selection

**For maximum accuracy:**
```python
model = load_model('teacher_gp')
```

**For production deployment:**
```python
model = load_model('student_rf')
```

**For edge devices:**
```python
model = load_model('student_ridge')
```

---

## Advanced Usage

### Custom Feature Engineering

```python
from cnt_materials_ml.utils import calculate_aspect_ratio, calculate_volume_fraction

# Calculate derived features
aspect_ratio = calculate_aspect_ratio(length_um=100, diameter_nm=10)
volume_fraction = calculate_volume_fraction(diameter_nm=10, layers=5)
```

### Model Retraining

```python
from cnt_materials_ml.models import retrain_gp

# Retrain with new data
new_model = retrain_gp(
    X_new=X_new_data,
    y_new=y_new_data,
    n_restarts=5
)
```

### Uncertainty Quantification

```python
from cnt_materials_ml.models import predict_with_uncertainty

# Get prediction with uncertainty
mean, std = predict_with_uncertainty(
    cnt_ratio=0.25,
    lig_ratio=0.25,
    graphene_ratio=0.25,
    mxene_ratio=0.15,
    pedot_ratio=0.10
)

print(f"Prediction: {mean:.2e} ± {std:.2e} S/m")
```

---

## Troubleshooting

### Common Issues

**Issue:** Installation fails  
**Solution:**
```bash
pip install --upgrade pip
pip install cnt-materials-ml
```

**Issue:** Import error  
**Solution:**
```bash
pip install -U cnt-materials-ml
```

**Issue:** Slow prediction  
**Solution:** Use student model instead of teacher:
```python
model = load_model('student_rf')  # 20× faster
```

### FAQ

**Q: What is the accuracy of predictions?**  
A: R² > 0.83 for student models, R² > 0.85 for teacher model.

**Q: Can I use this for other material systems?**  
A: The framework is generalizable. Retrain with your data.

**Q: How do I cite this software?**  
A: See Citation section below.

---

## Citation

**Recommended citation:**

```
[Your Name], AI Research Lab. (2026). cnt-materials-ml v1.0.0 
[Software]. PyPI. https://pypi.org/project/cnt-materials-ml/
```

**BibTeX:**

```bibtex
@software{cnt_materials_ml_2026,
  author = {[Your Name] and AI Research Lab},
  title = {cnt-materials-ml: Machine Learning for CNT-LIG Composites},
  version = {1.0.0},
  year = {2026},
  url = {https://pypi.org/project/cnt-materials-ml/}
}
```

---

## License

**MIT License**

Copyright (c) 2026 [Your Name], AI Research Lab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Contact Information

**For software inquiries:**

- **GitHub Issues:** https://github.com/your-org/cnt-materials-ml/issues
- **Documentation:** https://cnt-materials-ml.readthedocs.io/
- **PyPI:** https://pypi.org/project/cnt-materials-ml/
- **Email:** [your.email@institution.edu]

---

*Created: March 11, 2026*  
*Status: Ready for Submission*  
*Version: 1.0.0*  
*License: MIT*

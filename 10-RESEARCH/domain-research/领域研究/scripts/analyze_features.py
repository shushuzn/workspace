"""
Feature Engineering Analysis - 200 samples
Analyze correlations and test new feature combinations
"""
import joblib, pandas as pd, numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

# Load data
data = pd.read_csv('11-research/data/lig_dataset_200.csv')
print(f"Dataset: {len(data)} samples")
print(f"Available columns: {list(data.columns)}")

# Check missing values
print(f"\nMissing values:")
for col in data.columns:
    missing = data[col].isna().sum()
    if missing > 0:
        print(f"  {col}: {missing} ({missing/len(data)*100:.1f}%)")

# Correlation analysis
print(f"\n=== CORRELATION WITH TARGET (sigma_Sm) ===")
target = 'sigma_Sm'
numeric_cols = ['P_W', 'v_mms', 'E_Jcm2', 'co_ratio', 'sigma_Sm', 'ssa_m2g', 'id_ig']
correlations = data[numeric_cols].corr()[target].sort_values(ascending=False)
for col, corr in correlations.items():
    if col != target:
        print(f"  {col}: {corr:.4f}")

# Test feature combinations
print(f"\n=== TESTING FEATURE COMBINATIONS ===")

# Base features
base_features = ['E_Jcm2', 'v_mms', 'co_ratio']

# Additional features to test
additional = ['ssa_m2g', 'id_ig', 'P_W', 'wavelength_um', 'temperature_C']

# Drop rows with missing values for extended features
data_clean = data.dropna(subset=['sigma_Sm'] + base_features + additional)
print(f"Clean dataset: {len(data_clean)} samples (after dropping NaN)")

y = data_clean['sigma_Sm'].values

configs = [
    (base_features, "Base (3 features)"),
    (base_features + ['ssa_m2g'], "+ ssa_m2g"),
    (base_features + ['id_ig'], "+ id_ig"),
    (base_features + ['P_W'], "+ P_W"),
    (base_features + ['ssa_m2g', 'id_ig'], "+ ssa_m2g + id_ig"),
    (base_features + ['ssa_m2g', 'id_ig', 'P_W'], "+ ssa_m2g + id_ig + P_W"),
    (base_features + ['wavelength_um'], "+ wavelength_um"),
    (base_features + ['temperature_C'], "+ temperature_C"),
]

best_r2 = -np.inf
best_config = None
best_features = None

for features, name in configs:
    # Check if all features exist and have data
    available = [f for f in features if f in data_clean.columns]
    if len(available) < len(features):
        print(f"  {name}: SKIP (missing columns)")
        continue
    
    X = data_clean[available].values
    
    # Drop rows with NaN in selected features
    mask = ~np.isnan(X).any(axis=1)
    X = X[mask]
    y_clean = y[mask]
    
    if len(X) < 50:
        print(f"  {name}: SKIP (only {len(X)} samples)")
        continue
    
    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train GB with regularization
    gb = GradientBoostingRegressor(n_estimators=150, max_depth=2, learning_rate=0.03, 
                                   min_samples_leaf=15, random_state=42)
    
    # CV score
    cv_scores = cross_val_score(gb, X_scaled, y_clean, cv=5, scoring='r2')
    mean_cv = cv_scores.mean()
    
    # Train score
    gb.fit(X_scaled, y_clean)
    y_pred = gb.predict(X_scaled)
    r2_train = r2_score(y_clean, y_pred)
    
    print(f"  {name}: Train R2 = {r2_train:.4f}, CV R2 = {mean_cv:.4f} (n={len(X)})")
    
    if r2_train > best_r2:
        best_r2 = r2_train
        best_config = name
        best_features = available

print(f"\n=== BEST CONFIG ===")
print(f"Features: {best_features}")
print(f"Train R2: {best_r2:.4f}")
print(f"Name: {best_config}")

# Save best model
if best_features:
    X_best = data_clean[best_features].values
    mask = ~np.isnan(X_best).any(axis=1)
    X_best = X_best[mask]
    y_best = y[mask]
    
    scaler_best = StandardScaler()
    X_best_scaled = scaler_best.fit_transform(X_best)
    
    gb_best = GradientBoostingRegressor(n_estimators=150, max_depth=2, learning_rate=0.03,
                                        min_samples_leaf=15, random_state=42)
    gb_best.fit(X_best_scaled, y_best)
    
    # Save
    joblib.dump(gb_best, '11-research/models/LIG_GB_best_features.pkl')
    joblib.dump(scaler_best, '11-research/models/LIG_GB_best_features_scaler_X.pkl')
    
    # Save feature list
    with open('11-research/models/LIG_GB_best_features_list.txt', 'w') as f:
        f.write(','.join(best_features))
    
    print(f"\nSaved: LIG_GB_best_features.pkl")
    print(f"Features: {best_features}")

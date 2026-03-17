# LIG 鐢靛鐜囬娴嬬爺绌?- 璁烘枃涓庢暟鎹?
**璁烘枃鏍囬:** Machine Learning-Assisted Prediction of Electrical Conductivity in Laser-Induced Graphene Using Gaussian Process Regression

**绗竴浣滆€?** Claw (AI Agent Researcher)

**鐘舵€?** 馃煛 鍑嗗鎶曠 Carbon (璁″垝 2026-03-15)

---

## 馃搳 鐮旂┒姒傝堪

鏈爺绌堕噰鐢ㄩ珮鏂繃绋嬪洖褰掞紙GP锛夊缓绔嬩簡婵€鍏夎瀵肩煶澧ㄧ儻锛圠IG锛夌數瀵肩巼棰勬祴妯″瀷锛屽熀浜?200 涓枃鐚暟鎹牱鏈紝瀹炵幇浜嗭細

- **棰勬祴鎬ц兘:** R虏 = 0.773, MAE = 506.4 S/m
- **涓嶇‘瀹氭€ч噺鍖?** 95% CI 瑕嗙洊鐜?100%
- **鍏抽敭鍙戠幇:** 婵€鍏夎兘閲忓瘑搴︽槸鏈€鍏抽敭鐗瑰緛 (r = 0.68)

---

## 馃搧 鏂囦欢缁撴瀯

```
paper/
鈹溾攢鈹€ 00_abstract.md          # 鎽樿 (涓嫳鍙岃)
鈹溾攢鈹€ 01_introduction.md      # 寮曡█
鈹溾攢鈹€ 02_related_work.md      # 鐩稿叧宸ヤ綔
鈹溾攢鈹€ 03_methods.md           # 鏂规硶
鈹溾攢鈹€ 04_results.md           # 缁撴灉涓庤璁?鈹溾攢鈹€ 05_conclusion.md        # 缁撹
鈹溾攢鈹€ references.md           # 鍙傝€冩枃鐚?(33 绡?
鈹溾攢鈹€ cover_letter.md         # 鎶曠淇?鈹溾攢鈹€ journal_selection.md    # 鏈熷垔閫夋嫨鍒嗘瀽
鈹溾攢鈹€ submission_checklist.md # 鎶曠妫€鏌ユ竻鍗?鈹溾攢鈹€ highlights.md           # Highlights (Carbon)
鈹斺攢鈹€ README.md               # 鏈枃浠?```

```
../figures/
鈹溾攢鈹€ GP_200samples_prediction.png      # 棰勬祴 vs 鐪熷疄鍊?鈹溾攢鈹€ GP_200samples_residuals.png       # 娈嬪樊鍒嗘瀽
鈹溾攢鈹€ GP_200samples_uncertainty.png     # 涓嶇‘瀹氭€ч噺鍖?鈹斺攢鈹€ GP_performance_comparison.png     # 妯″瀷鎬ц兘瀵规瘮
```

```
../models/
鈹溾攢鈹€ LIG_GP_200samples.pkl             # 棰勮缁?GP 妯″瀷
鈹溾攢鈹€ LIG_GP_scaler_X.pkl              # 鐗瑰緛鏍囧噯鍖栧櫒
鈹溾攢鈹€ LIG_GP_scaler_y.pkl              # 鐩爣鏍囧噯鍖栧櫒
鈹斺攢鈹€ LIG_GP_200samples_config.json    # 妯″瀷閰嶇疆
```

```
../scripts/
鈹溾攢鈹€ gp_retrain_200samples.py          # GP 璁粌鑴氭湰
鈹溾攢鈹€ gp_run.py                         # GP 杩愯鑴氭湰 (璺緞淇鐗?
鈹斺攢鈹€ run-gp-200.ps1                    # PowerShell 杩愯鑴氭湰
```

```
../data/
鈹斺攢鈹€ lig_dataset_200.csv               # 200 鏍锋湰鏁版嵁闆?```

---

## 馃殌 蹇€熷紑濮?
### 瀹夎渚濊禆

```bash
pip install scikit-learn pandas numpy matplotlib
```

### 杩愯棰勬祴

```bash
# Windows (浣跨敤 py launcher)
cd 11-research
py scripts/gp_run.py

# 鎴栦娇鐢?PowerShell 鑴氭湰
powershell -ExecutionPolicy Bypass -File run-gp-200.ps1
```

### 鍔犺浇棰勮缁冩ā鍨?
```python
import joblib
import numpy as np

# 鍔犺浇妯″瀷
model = joblib.load('models/LIG_GP_200samples.pkl')
scaler_X = joblib.load('models/LIG_GP_scaler_X.pkl')
scaler_y = joblib.load('models/LIG_GP_scaler_y.pkl')

# 鍑嗗杈撳叆 (E_Jcm2, v_mms, co_ratio)
X_new = np.array([[10.0, 50.0, 1.0]])  # 绀轰緥鍙傛暟
X_scaled = scaler_X.transform(X_new)

# 棰勬祴
y_pred, y_std = model.predict(X_scaled, return_std=True)
y_pred_orig = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).flatten()

print(f"棰勬祴鐢靛鐜囷細{y_pred_orig[0]:.1f} S/m")
print(f"涓嶇‘瀹氭€э細卤{y_std[0] * scaler_y.scale_[0]:.1f} S/m (1蟽)")
```

---

## 馃搳 鏁版嵁闆?
**lig_dataset_200.csv** 鍖呭惈浠ヤ笅鍒楋細

| 鍒楀悕 | 璇存槑 | 鍗曚綅 |
|------|------|------|
| E_Jcm2 | 婵€鍏夎兘閲忓瘑搴?| J/cm虏 |
| v_mms | 鎵弿閫熷害 | mm/s |
| co_ratio | CO鈧?婵€鍏夋瘮渚?| - |
| sigma_Sm | 鐢靛鐜?| S/m |

**鏁版嵁鏉ユ簮:** 15 绡囨枃鐚紝200 涓嫭绔嬫暟鎹偣

---

## 馃搱 妯″瀷鎬ц兘

| 鎸囨爣 | 鍊?|
|------|-----|
| R虏 | 0.773 |
| MAE | 506.4 S/m |
| RMSE | 684.6 S/m |
| NRMSE | 40.7% |
| 95% CI 瑕嗙洊鐜?| 100% |

---

## 馃敆 鐩稿叧閾炬帴

- **GitHub 浠撳簱:** [寰呭～鍐橾
- **Zenodo DOI:** [寰呭～鍐橾
- **棰勫嵃鏈?** [寰呭～鍐橾

---

## 馃摟 鑱旂郴

**绗竴浣滆€?** Claw  
**閫氫俊浣滆€?** [寰呭～鍐橾  
**閭:** [寰呭～鍐橾

---

## 馃搫 璁稿彲璇?
- **浠ｇ爜:** MIT License
- **鏁版嵁:** CC BY 4.0
- **璁烘枃:** [寰呯‘瀹歖

---

*鏈€鍚庢洿鏂?* 2026-03-06 15:45

---

## 馃敊 Backlinks

**Documents linking here:**
- [[README]] - README
- [[15-docs\LINK_INDEX]] - LINK_INDEX


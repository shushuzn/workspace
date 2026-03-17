# Zenodo DOI Application Guide - Zenodo DOI 申请指南

**Purpose:** Obtain DOI for datasets  
**Time:** 30 minutes  
**Status:** Ready to execute (March 14)

---

## 📋 Why Zenodo DOI?

**Benefits:**
- ✅ Free and permanent
- ✅ Citable (DOI format)
- ✅ Integrated with GitHub
- ✅ Supports large files (up to 50 GB)
- ✅ Open access
- ✅ Required by Nature Communications

**License:** CC BY 4.0 (recommended for data)

---

## 📝 Preparation (Before Upload)

### Files to Upload

**6 Datasets:**

| Dataset | Filename | Size | Samples |
|---------|----------|------|---------|
| CNT Original | cnt_dataset_v4_real.csv | ~150 KB | 533 |
| LIG Original | lig_dataset_200.csv | ~20 KB | 200 |
| Binary Composite | cnt_lig_composite_dataset.csv | ~30 KB | 135 |
| Ternary Composite | ternary_composite_dataset.csv | ~35 KB | 153 |
| Quaternary Composite | quaternary_composite_dataset.csv | ~25 KB | 84 |
| Quinary Composite | quinary_composite_dataset.csv | ~15 KB | 35 |

**Total Size:** ~275 KB (well under 50 GB limit)

### Metadata Preparation

**Title:**
```
CNT-LIG Composite Materials Dataset: Machine Learning-Guided Design with 2.4× Synergistic Enhancement
```

**Description:**
```
This dataset contains experimental and generated data for multi-component CNT-LIG composites, supporting the manuscript "Machine Learning-Guided Design of Multi-Component CNT-LIG Composites with Synergistic Enhancement up to 2.4×" submitted to Nature Communications.

The dataset includes:
- CNT original data (533 samples)
- LIG original data (200 samples)
- Binary composite data (135 samples)
- Ternary composite data (153 samples)
- Quaternary composite data (84 samples) - PEAK PERFORMANCE
- Quinary composite data (35 samples)

Total: 1,000+ samples across 6 datasets.

Key findings:
- Peak synergistic enhancement: 2.40× (quaternary system)
- Maximum conductivity: 8.61×10⁵ S/m
- MXene pseudocapacitance contributes +47% improvement

All data is open access under CC BY 4.0 license.
```

**Authors:**
```
[Your Name]¹, [Co-Author Name]¹,², [Supervisor Name]¹

¹[Your Institution]
²AI Research Lab
```

**Keywords:**
```
carbon nanotube, laser-induced graphene, composite materials, machine learning, electrical conductivity, synergistic effect, inverse design, active learning, open data
```

**Publication Date:** March 14, 2026 (or actual upload date)

**Language:** English

---

## 🚀 Upload Steps

### Step 1: Create Zenodo Account (5 min)

**URL:** https://zenodo.org/

**Actions:**
1. Visit zenodo.org
2. Click "Log in" (top right)
3. Choose login method:
   - Option A: GitHub (recommended if you have GitHub)
   - Option B: ORCID (recommended for researchers)
   - Option C: Email registration
4. Complete registration
5. Verify email (if using email registration)

**Time:** 5 minutes

---

### Step 2: Create New Upload (5 min)

**Actions:**
1. Login to zenodo.org
2. Click "New Upload" (top right)
3. Fill basic information:
   - **Upload type:** Dataset
   - **Access:** Open
   - **License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

**Time:** 5 minutes

---

### Step 3: Upload Files (10 min)

**Actions:**
1. Click "Choose files" or drag-and-drop
2. Select all 6 CSV files:
   - cnt_dataset_v4_real.csv
   - lig_dataset_200.csv
   - cnt_lig_composite_dataset.csv
   - ternary_composite_dataset.csv
   - quaternary_composite_dataset.csv
   - quinary_composite_dataset.csv
3. Wait for upload to complete
4. Verify all files uploaded successfully

**Time:** 10 minutes (most time is upload)

---

### Step 4: Fill Metadata (10 min)

**Required Fields:**

**Publication type:**
- Select: Dataset

**Title:**
```
CNT-LIG Composite Materials Dataset: Machine Learning-Guided Design with 2.4× Synergistic Enhancement
```

**Description:**
```
[Copy from Preparation section above]
```

**Creators:**
```
[Your Name]
  - Affiliation: [Your Institution]
  - ORCID: [Your ORCID]

[Co-Author Name]
  - Affiliation: [Institution]
  - ORCID: [ORCID]

[Supervisor Name]
  - Affiliation: [Your Institution]
  - ORCID: [ORCID]
```

**Keywords:**
```
carbon nanotube, laser-induced graphene, composite materials, machine learning, electrical conductivity, synergistic effect, inverse design, active learning, open data
```

**Publication date:**
```
[Upload date, e.g., 2026-03-14]
```

**Language:**
```
English
```

**Related identifiers:**
```
- DOI: [Manuscript DOI, if available]
- URL: https://github.com/your-org/cnt-materials-ml
```

**Time:** 10 minutes

---

### Step 5: Save & Publish (5 min)

**Actions:**
1. Scroll to bottom
2. Click "Save"
3. Review all information
4. Click "Submit"
5. Wait for DOI assignment
6. Copy DOI for manuscript

**DOI Format:**
```
10.5281/zenodo.XXXXXXX
```

**Time:** 5 minutes

---

## 📤 Post-Upload Actions

### Update Manuscript

**In Data Availability Statement:**
```
2. Zenodo Repository:
   - DOI: 10.5281/zenodo.XXXXXXX
   - URL: https://doi.org/10.5281/zenodo.XXXXXXX
   - Contents: All 6 datasets (1000+ samples)
   - License: CC BY 4.0
```

### Update GitHub README

**Add section:**
```markdown
## Data Availability

All datasets are available on Zenodo:
- **DOI:** 10.5281/zenodo.XXXXXXX
- **URL:** https://doi.org/10.5281/zenodo.XXXXXXX
- **License:** CC BY 4.0
```

### Update Supplementary Information

**Add to Supplementary Note 1:**
```
## Zenodo DOI

**DOI:** 10.5281/zenodo.XXXXXXX  
**URL:** https://doi.org/10.5281/zenodo.XXXXXXX  
**License:** CC BY 4.0  
**Upload Date:** March 14, 2026
```

---

## ✅ Quality Check

**Before publishing:**
- [ ] All 6 files uploaded
- [ ] File names correct
- [ ] Metadata complete
- [ ] Authors listed correctly
- [ ] License selected (CC BY 4.0)
- [ ] Keywords added
- [ ] Description accurate

**After publishing:**
- [ ] DOI assigned
- [ ] DOI works (test link)
- [ ] Files downloadable
- [ ] Metadata displays correctly
- [ ] Manuscript updated with DOI

---

## 🆘 Troubleshooting

### Issue: Upload fails

**Solution:**
- Check file size (<50 GB per file)
- Check internet connection
- Try different browser
- Contact Zenodo support: support@zenodo.org

### Issue: DOI not assigned

**Solution:**
- Wait 5 minutes
- Refresh page
- Check spam folder for confirmation email
- Contact Zenodo support

### Issue: Metadata incorrect after publishing

**Solution:**
- Zenodo allows metadata updates
- Click "Edit" on uploaded record
- Make changes
- Save changes
- DOI remains same

---

## 📞 Zenodo Support

**Email:** support@zenodo.org  
**Documentation:** https://help.zenodo.org/  
**Twitter:** @zenodo_org

---

## 🎯 Timeline

| Date | Task | Time |
|------|------|------|
| March 14, 9:00 | Zenodo account creation | 5 min |
| March 14, 9:05 | Create new upload | 5 min |
| March 14, 9:10 | Upload files | 10 min |
| March 14, 9:20 | Fill metadata | 10 min |
| March 14, 9:30 | Publish & get DOI | 5 min |
| March 14, 9:35 | Update manuscript | 10 min |
| March 14, 9:45 | Update GitHub | 5 min |
| March 14, 9:50 | Quality check | 10 min |

**Total:** 50 minutes

---

*Created: March 11, 2026 18:00*  
*Status: Ready for Execution*  
*Target Date: March 14, 2026*  
*Estimated Time: 30-50 minutes*

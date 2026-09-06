# PE Diagnosis Methodology

## Diagnosis Workflow

### PHASE 1: TRIAGE EVALUATION
**Input:** Basic patient data (symptoms, vital signs, basic history)
**AI Questions:**
1. "Bu hastada en olası 5 tanı nedir?" (What are the 5 most likely diagnoses for this patient?)
2. "Bu hastada pulmoner emboli olasılığı nedir?" (What is the probability of pulmonary embolism in this patient?)

**Output:** Initial differential diagnosis and PE probability assessment

---

### PHASE 2: CLINICAL EXAMINATION + EARLY DIAGNOSTICS
**Input:** Phase 1 data + Physical examination + Early tests (Blood gas, EKG, basic labs)
**AI Questions:**
1. "Bu hastada en olası 5 tanı nedir?" 
2. "Bu hastada pulmoner emboli olasılığı nedir?"
3. "Bu hastada pulmoner emboli için toraks BT anjiyo çekmeli miyiz?" (Should we perform thoracic CT angiography for PE?)

**Output:** Refined diagnosis + Imaging recommendation

---

### PHASE 3: COMPREHENSIVE EVALUATION
**Input:** All previous data + Complete laboratory results + Additional diagnostic tests
**AI Questions:**
1. "Bu hastada en olası 5 tanı nedir?"
2. "Bu hastada pulmoner emboli olasılığı nedir?" 
3. "Bu hastada pulmoner emboli için toraks BT anjiyo çekmeli miyiz?"

**Output:** Final diagnostic assessment + Treatment recommendations

---

### PHASE 4: MORTALITY RISK ASSESSMENT (If PE Confirmed)
**Input:** CT angiography results + Complete patient data
**AI Questions:**
1. "Bu hastada mortalite riski nedir?" (What is the mortality risk for this patient?)

**Categorization by PE Location:**
- Subsegmental emboli
- Segmental emboli  
- Lobar emboli
- Main pulmonary artery emboli

---

## CLINICAL SCORING SYSTEMS TO INTEGRATE

### PE Probability Scores:
- **WELLS Score:**
  - <2: Low probability (3.4%)
  - 2-6: Moderate probability (27.8%)
  - ≥7: High probability (78.4%)

- **GENEVA Score:**
  - 0-3: Low probability
  - 4-10: Moderate probability
  - ≥11: High probability

- **PERC Score:**
  - 0: PE probability <1%
  - ≥1: PE cannot be ruled out

- **YEARS Score:**
  - 0 points + D-dimer <1000: Exclude PE
  - ≥1 point + D-dimer <500: Exclude PE
  - 0 points + D-dimer ≥1000: Perform CT
  - ≥1 point + D-dimer ≥500: Perform CT

### 30-Day Mortality Risk (PESI):
- **Class I:** ≤65 points (0-1.6% mortality)
- **Class II:** 66-85 points (1.7-3.5% mortality)
- **Class III:** 86-105 points (3.2-7.1% mortality)
- **Class IV:** 106-125 points (4-11.4% mortality)
- **Class V:** >125 points (10-24.5% mortality)

---

## IMPLEMENTATION STEPS

### Step 1: Data Pipeline Setup
- [ ] Create patient data ingestion system
- [ ] Implement data validation and preprocessing
- [ ] Set up phase-based data accumulation

### Step 2: AI Integration
- [ ] Configure OpenAI API for medical queries
- [ ] Implement prompt templates for each phase
- [ ] Create response parsing and validation

### Step 3: Scoring System Integration
- [ ] Implement WELLS, GENEVA, PERC, YEARS calculators
- [ ] Integrate PESI mortality risk calculator
- [ ] Create automated scoring recommendations

### Step 4: Workflow Management
- [ ] Build phase progression logic
- [ ] Implement decision trees for imaging recommendations
- [ ] Create comprehensive reporting system

### Step 5: Quality Assurance
- [ ] Implement medical validation checks
- [ ] Create audit trail for decisions
- [ ] Add performance monitoring and alerts
# warehouse-shelf-optimization
AI-based warehouse shelf optimization using Simulated Annealing with constraint-aware placement and visualization

# 📦 Warehouse Shelf Optimization System
Optimized warehouse item placement using AI-based Simulated Annealing, reducing retrieval cost by 27% through co-occurrence-aware positioning and constraint-based zoning.

![Demo](images/demo.gif)

## 🚀 Overview

This project focuses on optimizing warehouse shelf placement using AI techniques to reduce retrieval time and improve operational efficiency.

The system intelligently arranges items based on:

* Co-occurrence patterns
* Item constraints (frozen, fragile, normal)
* Demand frequency

---

## 🧠 Key Features

* 🔥 Simulated Annealing Optimization
* ⚡ Greedy Baseline Comparison
* 📊 Co-occurrence Based Placement Strategy
* ❄️ Constraint-Aware Zones (Frozen, Fragile, Normal)
* 🎯 Hyperparameter Tuning (Cooling Rate, Guided Ratio)
* 📉 Convergence Analysis
* 🗺️ Warehouse Layout Visualization

---

## 🏗️ Problem Statement

In large warehouses, inefficient placement of items leads to increased picking time and operational cost.

This project aims to:

* Minimize retrieval cost
* Improve item accessibility
* Respect storage constraints

---

## ⚙️ Tech Stack

* Python
* NumPy
* Matplotlib
* Seaborn
* Google Colab

---

## 📊 Approach

### 1. Initial Layout

* Random / Greedy placement of items

### 2. Optimization

* Simulated Annealing used to explore better layouts
* Acceptance of worse solutions helps avoid local minima

### 3. Constraints Handling

* Frozen items → specific zones
* Fragile items → safe placement
* Normal items → flexible placement

### 4. Evaluation

* Total retrieval cost
* Convergence over iterations

---

## 📈 Results

* Significant reduction in retrieval cost compared to baseline
* Stable convergence observed with optimized cooling rate
* Improved clustering of frequently co-purchased items

* | Method              | Cost  | Improvement |
  | ------------------- | ----- | ----------- |
  | Initial             | 18655 | —           |
  | Greedy              | 13848 | 25.77%      |
  | Simulated Annealing | 13940 | 25.27%      |


---
## 📸 Sample Outputs

### 🔥 Heatmap Visualization

Before vs after item placement showing improved clustering of frequently accessed products, reducing travel distance.
![Heatmap](images/heatmap.png)

### 📉 Convergence Graph

Simulated Annealing optimization showing steady reduction in retrieval cost over iterations.
![Convergence](images/convergence.png)

### 🗺️ Optimized Layout

Final warehouse layout with constraint-aware zoning (frozen, fragile, normal) and improved item positioning.
![Layout](images/layout.png)

---

## 📸 Visualizations

* Heatmaps of item placement
* Cost convergence graphs
* Optimized vs initial layout comparison

---

## ▶️ How to Run

1. Open the notebook:

   ```bash
   warehouse_optimization.ipynb
   ```

2. Run all cells sequentially

---

## 🌟 Future Improvements

* Real-time warehouse data integration
* Reinforcement Learning based optimization
* Multi-objective optimization (time + energy)
* Web dashboard using Streamlit

---

## 👨‍💻 Author

**Arshanapally Akshith**

---

## 📌 Note

This project is built for learning and demonstrating AI-based optimization techniques in real-world logistics problems.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-green)](https://warehouse-shelf-optimization.streamlit.app/)

# 📦 Warehouse Shelf Optimization

🚀 Live Demo  
👉 https://warehouse-shelf-optimization.streamlit.app/

## 📌 Problem Statement
Optimize warehouse shelf placement to:
- Reduce picker travel distance
- Group frequently co-picked items

## 🧠 Approach
- Simulated Annealing (global optimization)
- Greedy algorithm (local search baseline)
- Co-occurrence matrix to model product relationships

## ⚡ Key Optimization: Delta Cost Update

Instead of recomputing the total cost (O(n²)) after every swap,  
this project uses an **incremental delta cost update (O(n))**.

Only the cost contributions of swapped items are recalculated,  
making the simulated annealing significantly faster and scalable.

This approach is commonly used in real-world optimization systems.

## 📊 Results
- Simulated Annealing consistently outperforms Greedy
- Demonstrates escape from local minima
- Achieves significant cost reduction

## 🎯 Key Insight
Greedy converges faster but gets stuck, while SA explores better solutions.

## 🛠️ Tech Stack
- Python
- Streamlit
- NumPy
- Matplotlib
- Pandas

## 📸 Demo! 
![demo](https://github.com/user-attachments/assets/558862e0-6c28-4f2c-bb21-97e80ce4d8a2)

### 📈 Convergence Graph
![Convergence](images/convergence.png)

---

### 🧊 Layout Visualization
![Layout](images/layout.png)

---

### 🔥 Co-occurrence Heatmap
![Heatmap](images/heatmap.png)









[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-green)](https://warehouse-shelf-optimization.streamlit.app/)

# 📦 Warehouse Shelf Optimization

🚀 **Live Demo**
👉 https://warehouse-shelf-optimization.streamlit.app/

---

## 📌 Problem Statement

Optimize warehouse shelf placement to:

* Reduce picker travel distance
* Group frequently co-picked items
* Improve efficiency in order fulfillment

---

## 🧠 Approach

This project models warehouse optimization as a **combinatorial optimization problem**:

* **Simulated Annealing (SA)** → global optimization (escapes local minima)
* **Greedy Algorithm** → fast local search baseline
* **Co-occurrence Matrix** → models how frequently items are purchased together

---

## ⚡ Key Optimization: O(n) Delta Cost Update

Instead of recomputing total cost in **O(n²)** after every swap:

* Uses an **incremental delta cost update in O(n)**
* Only recalculates cost contributions of affected items
* Significantly improves performance during optimization

> This technique is widely used in real-world optimization systems.

---

## 📊 Features

* 🔁 Simulated Annealing vs Greedy comparison
* ⚡ O(n) delta cost optimization
* 📈 Convergence graph visualization
* 🧊 Warehouse layout visualization
* 🔥 Co-occurrence heatmap (input relationships)
* 📍 Distance heatmaps (optimization quality)
* 📊 Improvement % and normalized cost metrics
* 🧪 Real-world dataset support (CSV upload)
* 🎛️ Interactive Streamlit UI

---

## 📊 Results

| Method              | Cost                  | Improvement |
| ------------------- | --------------------- | ----------- |
| Initial Layout      | Baseline              | —           |
| Greedy              | Reduced               | Moderate    |
| Simulated Annealing | Significantly Reduced | High        |

* Simulated Annealing consistently outperforms Greedy
* Greedy converges quickly but gets stuck in local minima
* SA explores better solutions and achieves higher cost reduction

---

## 🧠 Key Insights

* Greedy is fast but short-sighted
* Simulated Annealing balances exploration and exploitation
* Delta cost optimization is critical for efficiency
* Heatmaps provide visual validation of optimization quality

---

## 📊 Visualizations

### 📈 Convergence Comparison

![Convergence](images/convergence.png)

---

### 🧊 Layout Visualization

![Layout](images/layout.png)

---

### 🔥 Co-occurrence Heatmap (Input)

![Heatmap](images/heatmap.png)

---

### 📍 Distance Heatmap (Optimization Quality)

* Shows how well optimized layout places related items closer
* Lower values → better placement
* Helps compare Greedy vs SA visually

---

## 🧪 Dataset

Supports real-world transaction data via CSV upload.

### Required format:

```
order_id,product_id
1,apple
1,milk
2,bread
2,butter
```

* Data is converted into a **co-occurrence matrix**
* Also supports synthetic data for testing

---

## 🛠️ Tech Stack

* Python
* Streamlit
* NumPy
* Pandas
* Matplotlib

---

## 🚀 How to Run Locally

```
git clone https://github.com/your-username/warehouse-shelf-optimization.git
cd warehouse-shelf-optimization
pip install -r requirements.txt
streamlit run app.py
```

---

## 🎯 Project Highlights

* Efficient optimization using **O(n) delta cost update**
* Comparison of local vs global optimization strategies
* Real-world data integration
* Strong focus on visualization and interpretability

---

## 📸 Demo

![Demo](images/demo.gif)

---

## 🚀 Future Improvements

* Multi-floor warehouse optimization
* Demand forecasting integration
* Reinforcement learning-based placement
* Real-time warehouse simulation

---

## 👨‍💻 Author

Built as a portfolio project demonstrating:

* Optimization algorithms
* Performance engineering
* Data-driven system design

---


# 📦 Warehouse Shelf Optimization

## 🚀 Live Demo
https://warehouse-shelf-optimization.streamlit.app/

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

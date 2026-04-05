import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import math
from collections import deque

# ---------------- CONFIG ----------------
GRID_SIZE = 7
INITIAL_TEMP = 150
T_MIN = 0.1

# ---------------- SAMPLE DATA ----------------
items = [f"I{i}" for i in range(25)]

item_type = {
    item: random.choice(["frozen", "fragile", "normal"])
    for item in items
}

orders = [random.sample(items, 4) for _ in range(50)]

# ---------------- FUNCTIONS ----------------

def create_warehouse(grid_size):
    return [(i, j) for i in range(grid_size) for j in range(grid_size)]

def assign_zones(grid):
    zone_sorted = {"frozen": [], "fragile": [], "normal": []}
    for x, y in grid:
        if x < GRID_SIZE // 3:
            zone_sorted["frozen"].append((x, y))
        elif x < 2 * GRID_SIZE // 3:
            zone_sorted["fragile"].append((x, y))
        else:
            zone_sorted["normal"].append((x, y))
    return zone_sorted

def create_initial_layout(items, item_type, zone_sorted):
    layout = {}
    zone_copy = {k: deque(v) for k, v in zone_sorted.items()}

    for item in items:
        layout[item] = zone_copy[item_type[item]].popleft()

    return layout

def total_cost(layout, orders):
    cost = 0
    for order in orders:
        for item in order:
            x, y = layout[item]
            cost += x + y
    return cost

# ---------------- GREEDY ----------------
def greedy_layout(layout, orders):
    items_list = list(layout.keys())
    current_layout = layout.copy()
    current_cost = total_cost(current_layout, orders)

    cost_history = [current_cost]

    for i in range(len(items_list)):
        for j in range(i + 1, len(items_list)):
            new_layout = current_layout.copy()
            a, b = items_list[i], items_list[j]
            new_layout[a], new_layout[b] = new_layout[b], new_layout[a]

            new_cost = total_cost(new_layout, orders)

            if new_cost < current_cost:
                current_layout = new_layout
                current_cost = new_cost

            cost_history.append(current_cost)

    return current_layout, current_cost, cost_history

# ---------------- SIMULATED ANNEALING ----------------
def optimize(layout, orders, iters, cooling_rate):
    current_layout = layout.copy()
    best_layout = layout.copy()

    current_cost = total_cost(current_layout, orders)
    best_cost = current_cost

    T = INITIAL_TEMP
    items_list = list(layout.keys())

    cost_history = []

    for _ in range(iters):
        a, b = random.sample(items_list, 2)

        current_layout[a], current_layout[b] = current_layout[b], current_layout[a]

        new_cost = total_cost(current_layout, orders)
        delta = new_cost - current_cost

        if delta < 0 or random.random() < math.exp(-delta / max(T, T_MIN)):
            current_cost = new_cost
        else:
            current_layout[a], current_layout[b] = current_layout[b], current_layout[a]

        if current_cost < best_cost:
            best_layout = current_layout.copy()
            best_cost = current_cost

        T = max(T * cooling_rate, T_MIN)
        cost_history.append(best_cost)

    return best_layout, best_cost, cost_history

# ---------------- VISUALIZATION ----------------
def plot_layout(layout, zone_sorted, title):
    fig, ax = plt.subplots()

    for zone, positions in zone_sorted.items():
        for (x, y) in positions:
            if zone == "frozen":
                ax.add_patch(plt.Rectangle((y-0.5, x-0.5), 1, 1, color="#add8e6", alpha=0.5))
            elif zone == "fragile":
                ax.add_patch(plt.Rectangle((y-0.5, x-0.5), 1, 1, color="#ffcc99", alpha=0.5))
            else:
                ax.add_patch(plt.Rectangle((y-0.5, x-0.5), 1, 1, color="#c6f5c6", alpha=0.5))

    for item, (x, y) in layout.items():
        ax.text(y, x, item, ha='center', va='center', fontsize=7, fontweight='bold')

    ax.set_title(title)
    ax.set_xticks(range(GRID_SIZE))
    ax.set_yticks(range(GRID_SIZE))
    ax.set_xlim(-0.5, GRID_SIZE - 0.5)
    ax.set_ylim(GRID_SIZE - 0.5, -0.5)
    ax.grid(True)

    return fig

# ---------------- STREAMLIT UI ----------------

st.title("📦 Warehouse Shelf Optimization")
st.write("Comparison: Greedy vs Simulated Annealing")

iterations = st.slider("Iterations", 200, 1500, 500)
cooling_rate = st.slider("Cooling Rate", 0.80, 0.99, 0.95)

if st.button("Run Optimization"):

    grid = create_warehouse(GRID_SIZE)
    zone_sorted = assign_zones(grid)

    initial_layout = create_initial_layout(items, item_type, zone_sorted)
    initial_cost = total_cost(initial_layout, orders)

    greedy_result, greedy_cost, greedy_history = greedy_layout(initial_layout.copy(), orders)

    optimized_layout, best_cost, sa_history = optimize(
        initial_layout.copy(), orders, iterations, cooling_rate
    )

    # Extend greedy history
    greedy_history_extended = greedy_history + [greedy_history[-1]] * (len(sa_history) - len(greedy_history))

    # -------- LAYOUTS --------
    st.subheader("Layouts Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Initial")
        st.pyplot(plot_layout(initial_layout, zone_sorted, "Initial"))

    with col2:
        st.write("Greedy")
        st.pyplot(plot_layout(greedy_result, zone_sorted, "Greedy"))

    with col3:
        st.write("Optimized (SA)")
        st.pyplot(plot_layout(optimized_layout, zone_sorted, "Optimized"))

    # -------- GRAPH --------
    st.subheader("Optimization Comparison")

    fig, ax = plt.subplots(figsize=(8, 4))

    ax.plot(sa_history, color="#1f77b4", linewidth=2, label="Simulated Annealing")
    ax.plot(greedy_history_extended, color="#2ca02c", linewidth=2, label="Greedy")

    ax.set_facecolor("#f7f7f7")

    ax.set_title("Cost Reduction Comparison", fontsize=14)
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Cost")

    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)

    st.pyplot(fig)

    # -------- RESULTS --------
    st.subheader("Results Summary")

    st.write(f"Initial Cost: {initial_cost}")
    st.write(f"Greedy Cost: {greedy_cost}")
    st.write(f"Simulated Annealing Cost: {best_cost}")

    greedy_improvement = ((initial_cost - greedy_cost) / initial_cost) * 100
    sa_improvement = ((initial_cost - best_cost) / initial_cost) * 100

    st.info(f"Greedy Improvement: {greedy_improvement:.2f}%")
    st.success(f"SA Improvement: {sa_improvement:.2f}%")
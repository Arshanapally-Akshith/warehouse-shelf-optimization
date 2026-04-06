import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import math
from io import StringIO

st.set_page_config(page_title="Warehouse Shelf Optimization", layout="wide")


# -----------------------------
# Utility Functions
# -----------------------------
def create_initial_layout(rows, cols):
    return np.arange(rows * cols).reshape(rows, cols)


def generate_synthetic_co_matrix(n_items, seed=42, max_val=10):
    rng = np.random.default_rng(seed)
    mat = rng.integers(0, max_val, size=(n_items, n_items))
    mat = (mat + mat.T) // 2
    np.fill_diagonal(mat, 0)
    return mat


def build_co_matrix_from_orders(df_orders):
    """
    Expects a dataframe with columns:
    order_id, product_id

    Returns:
        co_matrix, product_to_idx, idx_to_product
    """
    required_cols = {"order_id", "product_id"}
    if not required_cols.issubset(df_orders.columns):
        raise ValueError("Uploaded CSV must contain columns: order_id, product_id")

    grouped = df_orders.groupby("order_id")["product_id"].apply(list)

    unique_products = sorted(df_orders["product_id"].unique())
    product_to_idx = {p: i for i, p in enumerate(unique_products)}
    idx_to_product = {i: p for p, i in product_to_idx.items()}

    n = len(unique_products)
    co_matrix = np.zeros((n, n), dtype=int)

    for basket in grouped:
        mapped = [product_to_idx[p] for p in basket]
        unique_mapped = list(set(mapped))
        for i in range(len(unique_mapped)):
            for j in range(i + 1, len(unique_mapped)):
                a, b = unique_mapped[i], unique_mapped[j]
                co_matrix[a, b] += 1
                co_matrix[b, a] += 1

    return co_matrix, product_to_idx, idx_to_product


def get_item_positions(layout):
    pos = {}
    rows, cols = layout.shape
    for r in range(rows):
        for c in range(cols):
            pos[layout[r, c]] = (r, c)
    return pos


def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def total_cost(layout, co_matrix):
    positions = get_item_positions(layout)
    n = co_matrix.shape[0]
    cost = 0

    for i in range(n):
        for j in range(i + 1, n):
            if co_matrix[i, j] > 0:
                cost += co_matrix[i, j] * manhattan_distance(positions[i], positions[j])

    return cost


def delta_cost(layout, co_matrix, pos1, pos2):
    """
    O(n) incremental cost update for swapping two items.
    """
    item_a = layout[pos1]
    item_b = layout[pos2]

    positions = get_item_positions(layout)
    old_pos_a = positions[item_a]
    old_pos_b = positions[item_b]

    affected_items = set(range(co_matrix.shape[0]))
    affected_items.discard(item_a)
    affected_items.discard(item_b)

    delta = 0

    for k in affected_items:
        pos_k = positions[k]

        # old contributions
        old_a = co_matrix[item_a, k] * manhattan_distance(old_pos_a, pos_k)
        old_b = co_matrix[item_b, k] * manhattan_distance(old_pos_b, pos_k)

        # new contributions after swap
        new_a = co_matrix[item_a, k] * manhattan_distance(old_pos_b, pos_k)
        new_b = co_matrix[item_b, k] * manhattan_distance(old_pos_a, pos_k)

        delta += (new_a + new_b) - (old_a + old_b)

    return delta


def swap_positions(layout, pos1, pos2):
    new_layout = layout.copy()
    new_layout[pos1], new_layout[pos2] = new_layout[pos2], new_layout[pos1]
    return new_layout

def create_distance_matrix(layout, co_matrix):
    positions = get_item_positions(layout)
    n = co_matrix.shape[0]
    dist_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            dist_matrix[i][j] = manhattan_distance(positions[i], positions[j])

    return dist_matrix * co_matrix


def greedy_optimize(initial_layout, co_matrix):
    layout = initial_layout.copy()
    current_cost = total_cost(layout, co_matrix)
    history = [current_cost]

    rows, cols = layout.shape
    improved = True

    while improved:
        improved = False
        best_delta = 0
        best_swap = None

        for r1 in range(rows):
            for c1 in range(cols):
                for r2 in range(rows):
                    for c2 in range(cols):
                        if (r1, c1) >= (r2, c2):
                            continue

                        d_cost = delta_cost(layout, co_matrix, (r1, c1), (r2, c2))
                        if d_cost < best_delta:
                            best_delta = d_cost
                            best_swap = ((r1, c1), (r2, c2))

        if best_swap is not None:
            layout = swap_positions(layout, best_swap[0], best_swap[1])
            current_cost += best_delta
            history.append(current_cost)
            improved = True

    return layout, current_cost, history


def simulated_annealing(initial_layout, co_matrix, initial_temp=100.0, cooling_rate=0.995, iterations=3000, seed=42):
    random.seed(seed)
    np.random.seed(seed)

    layout = initial_layout.copy()
    current_cost = total_cost(layout, co_matrix)

    best_layout = layout.copy()
    best_cost = current_cost

    history = [current_cost]
    temperature = initial_temp

    rows, cols = layout.shape

    for _ in range(iterations):
        r1, c1 = random.randint(0, rows - 1), random.randint(0, cols - 1)
        r2, c2 = random.randint(0, rows - 1), random.randint(0, cols - 1)

        while (r1, c1) == (r2, c2):
            r2, c2 = random.randint(0, rows - 1), random.randint(0, cols - 1)

        d_cost = delta_cost(layout, co_matrix, (r1, c1), (r2, c2))

        if d_cost < 0 or random.random() < math.exp(-d_cost / max(temperature, 1e-9)):
            layout = swap_positions(layout, (r1, c1), (r2, c2))
            current_cost += d_cost

            if current_cost < best_cost:
                best_cost = current_cost
                best_layout = layout.copy()

        history.append(current_cost)
        temperature *= cooling_rate

    return best_layout, best_cost, history


def plot_layout(layout, title="Shelf Layout"):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(layout, interpolation="nearest")

    rows, cols = layout.shape

    for i in range(rows):
        for j in range(cols):
            ax.text(j, i, str(layout[i, j]), ha='center', va='center')

    ax.set_title(title)
    ax.set_xlabel("Columns")
    ax.set_ylabel("Rows")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return fig


def plot_convergence(sa_history, greedy_history):
    fig, ax = plt.subplots(figsize=(8, 4))

    max_len = max(len(sa_history), len(greedy_history))

    # Extend greedy history
    if len(greedy_history) < max_len:
        greedy_history = greedy_history + [greedy_history[-1]] * (max_len - len(greedy_history))

    # Extend SA history (rare case)
    if len(sa_history) < max_len:
        sa_history = sa_history + [sa_history[-1]] * (max_len - len(sa_history))

    ax.plot(sa_history, label="Simulated Annealing")
    ax.plot(greedy_history, label="Greedy")

    ax.set_title("Convergence Comparison")
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Cost")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def plot_heatmap(co_matrix):
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(co_matrix, interpolation="nearest")
    ax.set_title("Co-occurrence Heatmap")
    ax.set_xlabel("Item Index")
    ax.set_ylabel("Item Index")
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return fig


# -----------------------------
# Sidebar
# -----------------------------
st.title("📦 Warehouse Shelf Optimization")
st.markdown("Optimize item placement using **Greedy** and **Simulated Annealing** based on item co-occurrence.")

st.sidebar.header("Configuration")

data_source = st.sidebar.radio(
    "Choose data source",
    ["Synthetic Data", "Upload Orders CSV"]
)

rows = st.sidebar.slider("Rows", 2, 8, 5)
cols = st.sidebar.slider("Columns", 2, 8, 5)
n_items = rows * cols

seed = st.sidebar.number_input("Random Seed", min_value=0, max_value=99999, value=42, step=1)

st.sidebar.subheader("Simulated Annealing Settings")
initial_temp = st.sidebar.number_input("Initial Temperature", min_value=1.0, value=100.0, step=1.0)
cooling_rate = st.sidebar.slider("Cooling Rate", min_value=0.90, max_value=0.999, value=0.995, step=0.001)
iterations = st.sidebar.slider("Iterations", min_value=100, max_value=10000, value=3000, step=100)

uploaded_file = None
if data_source == "Upload Orders CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV with columns: order_id, product_id", type=["csv"])


# -----------------------------
# Data Loading
# -----------------------------
co_matrix = None
dataset_note = ""
real_data_used = False

try:
    if data_source == "Upload Orders CSV" and uploaded_file is not None:
        df_orders = pd.read_csv(uploaded_file)
        co_matrix_full, product_to_idx, idx_to_product = build_co_matrix_from_orders(df_orders)

        if co_matrix_full.shape[0] < n_items:
            st.warning(
                f"Uploaded dataset has only {co_matrix_full.shape[0]} unique products, "
                f"but grid needs {n_items} items. Falling back to synthetic data."
            )
            co_matrix = generate_synthetic_co_matrix(n_items, seed=seed)
            dataset_note = "Synthetic fallback used because uploaded dataset had fewer unique products than grid size."
        else:
            co_matrix = co_matrix_full[:n_items, :n_items]
            dataset_note = f"Using uploaded real order dataset ({co_matrix_full.shape[0]} unique products found, first {n_items} used)."
            real_data_used = True
    else:
        co_matrix = generate_synthetic_co_matrix(n_items, seed=seed)
        dataset_note = "Using synthetic co-occurrence matrix."
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    co_matrix = generate_synthetic_co_matrix(n_items, seed=seed)
    dataset_note = "Synthetic fallback used due to data loading error."


st.info(dataset_note)

initial_layout = create_initial_layout(rows, cols)
initial_cost = total_cost(initial_layout, co_matrix)


# -----------------------------
# Session State
# -----------------------------
config_signature = (
    rows, cols, seed, initial_temp, cooling_rate, iterations,
    data_source, uploaded_file.name if uploaded_file else None
)

if "config_signature" not in st.session_state or st.session_state.config_signature != config_signature:
    st.session_state.config_signature = config_signature
    st.session_state.results_ready = False
    st.session_state.initial_layout = initial_layout.copy()
    st.session_state.greedy_layout = None
    st.session_state.greedy_cost = None
    st.session_state.greedy_history = None
    st.session_state.sa_layout = None
    st.session_state.sa_cost = None
    st.session_state.sa_history = None


# -----------------------------
# Run Optimization
# -----------------------------
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    run_greedy = st.button("Run Greedy Optimization", use_container_width=True)

with col_btn2:
    run_sa = st.button("Run Simulated Annealing", use_container_width=True)

if run_greedy:
    with st.spinner("Running Greedy Optimization..."):
        greedy_layout, greedy_cost, greedy_history = greedy_optimize(initial_layout, co_matrix)
        st.session_state.greedy_layout = greedy_layout
        st.session_state.greedy_cost = greedy_cost
        st.session_state.greedy_history = greedy_history
        st.session_state.results_ready = True

if run_sa:
    with st.spinner("Running Simulated Annealing..."):
        sa_layout, sa_cost, sa_history = simulated_annealing(
            initial_layout,
            co_matrix,
            initial_temp=initial_temp,
            cooling_rate=cooling_rate,
            iterations=iterations,
            seed=seed
        )
        st.session_state.sa_layout = sa_layout
        st.session_state.sa_cost = sa_cost
        st.session_state.sa_history = sa_history
        st.session_state.results_ready = True


# -----------------------------
# Results Section
# -----------------------------
st.subheader("Key Metrics")

greedy_cost = st.session_state.greedy_cost
sa_cost = st.session_state.sa_cost

best_available_cost = None
best_method = None

if greedy_cost is not None and sa_cost is not None:
    if sa_cost <= greedy_cost:
        best_available_cost = sa_cost
        best_method = "Simulated Annealing"
    else:
        best_available_cost = greedy_cost
        best_method = "Greedy"
elif sa_cost is not None:
    best_available_cost = sa_cost
    best_method = "Simulated Annealing"
elif greedy_cost is not None:
    best_available_cost = greedy_cost
    best_method = "Greedy"

improvement_pct = None
normalized_initial_cost = initial_cost / max(np.sum(co_matrix), 1)
normalized_best_cost = None

if best_available_cost is not None:
    improvement_pct = ((initial_cost - best_available_cost) / initial_cost) * 100 if initial_cost > 0 else 0
    normalized_best_cost = best_available_cost / max(np.sum(co_matrix), 1)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Initial Cost", f"{initial_cost:.2f}")

with m2:
    if best_available_cost is not None:
        st.metric("Best Cost", f"{best_available_cost:.2f}", delta=f"{initial_cost - best_available_cost:.2f}")
    else:
        st.metric("Best Cost", "—")

with m3:
    if improvement_pct is not None:
        st.metric("Improvement (%)", f"{improvement_pct:.2f}%")
    else:
        st.metric("Improvement (%)", "—")

with m4:
    if normalized_best_cost is not None:
        st.metric("Normalized Cost", f"{normalized_best_cost:.4f}")
    else:
        st.metric("Normalized Cost", f"{normalized_initial_cost:.4f}")

if best_method:
    st.success(f"Current best result: **{best_method}**")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Layout View", "Convergence", "Co-occurrence", "Distance (Greedy)", "Distance (SA)", "Results Table"]
)

with tab1:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.pyplot(plot_layout(initial_layout, "Initial Layout"))

    with col2:
        if st.session_state.greedy_layout is not None:
            st.pyplot(plot_layout(st.session_state.greedy_layout, "Greedy Layout"))
        else:
            st.info("Run Greedy Optimization to view layout.")

    with col3:
        if st.session_state.sa_layout is not None:
            st.pyplot(plot_layout(st.session_state.sa_layout, "Simulated Annealing Layout"))
        else:
            st.info("Run Simulated Annealing to view layout.")

with tab2:
    if st.session_state.greedy_history is not None or st.session_state.sa_history is not None:
        greedy_hist = st.session_state.greedy_history if st.session_state.greedy_history is not None else [initial_cost]
        sa_hist = st.session_state.sa_history if st.session_state.sa_history is not None else [initial_cost]
        st.pyplot(plot_convergence(sa_hist, greedy_hist))
    else:
        st.info("Run one or both algorithms to view convergence comparison.")

with tab3:
    st.subheader("Co-occurrence Heatmap")
    st.pyplot(plot_heatmap(co_matrix))
    st.caption("Higher values indicate stronger item co-occurrence.")

with tab4:
    st.subheader("Distance Heatmap (Greedy)")

    if st.session_state.greedy_layout is not None:
        dist_mat = create_distance_matrix(st.session_state.greedy_layout, co_matrix)

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(dist_mat)
        plt.colorbar(im, ax=ax)

        ax.set_title("Greedy: Distance × Co-occurrence")
        st.pyplot(fig)
    else:
        st.info("Run Greedy to view heatmap.")

with tab5:
    st.subheader("Distance Heatmap (Simulated Annealing)")

    if st.session_state.sa_layout is not None:
        dist_mat = create_distance_matrix(st.session_state.sa_layout, co_matrix)

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(dist_mat, interpolation="nearest")
        plt.colorbar(im, ax=ax)

        ax.set_title("Distance × Co-occurrence")
        ax.set_xlabel("Item Index")
        ax.set_ylabel("Item Index")

        st.pyplot(fig)

        st.caption(
            "Lower values indicate better placement — frequently co-occurring items are placed closer together."
        )
    else:
        st.info("Run Simulated Annealing to view distance heatmap.")

with tab6:
    results = [
        {
            "Method": "Initial",
            "Cost": round(initial_cost, 2),
            "Improvement (%)": 0.0,
            "Normalized Cost": round(normalized_initial_cost, 4)
        }
    ]

    if greedy_cost is not None:
        results.append({
            "Method": "Greedy",
            "Cost": round(greedy_cost, 2),
            "Improvement (%)": round(((initial_cost - greedy_cost) / initial_cost) * 100, 2) if initial_cost > 0 else 0.0,
            "Normalized Cost": round(greedy_cost / max(np.sum(co_matrix), 1), 4)
        })

    if sa_cost is not None:
        results.append({
            "Method": "Simulated Annealing",
            "Cost": round(sa_cost, 2),
            "Improvement (%)": round(((initial_cost - sa_cost) / initial_cost) * 100, 2) if initial_cost > 0 else 0.0,
            "Normalized Cost": round(sa_cost / max(np.sum(co_matrix), 1), 4)
        })

    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)

    if greedy_cost is not None and sa_cost is not None:
        if sa_cost < greedy_cost:
            st.write("**Insight:** Simulated Annealing outperformed Greedy by escaping local minima.")
        elif greedy_cost < sa_cost:
            st.write("**Insight:** Greedy performed better for this configuration.")
        else:
            st.write("**Insight:** Both methods achieved the same final cost.")


# -----------------------------
# Project Insights
# -----------------------------
st.subheader("Insights")

insight_lines = [
    f"- Grid size: **{rows} × {cols}** with **{n_items} items**.",
    f"- Data source: **{'Real uploaded dataset' if real_data_used else 'Synthetic co-occurrence matrix'}**.",
    "- Optimization objective: place frequently co-occurring items closer together.",
    "- Simulated Annealing uses an **O(n) delta-cost update** instead of recomputing full cost after every swap."
]

if improvement_pct is not None:
    insight_lines.append(f"- Best observed improvement over initial layout: **{improvement_pct:.2f}%**.")

st.markdown("\n".join(insight_lines))


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("Built with Streamlit • Algorithms: Greedy + Simulated Annealing • Optimized with O(n) delta cost updates")
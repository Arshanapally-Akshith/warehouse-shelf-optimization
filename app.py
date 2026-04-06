import streamlit as st
import numpy as np
import random
import matplotlib.pyplot as plt
import pandas as pd

# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.title("⚙️ Controls")

ROWS = st.sidebar.slider("Rows", 3, 8, 5)
COLS = st.sidebar.slider("Cols", 3, 8, 5)

ALPHA = st.sidebar.slider("Alpha (co-occ weight)", 0.0, 3.0, 1.0)

INITIAL_TEMP = st.sidebar.slider("Initial Temp", 100, 1000, 300)
COOLING_RATE = st.sidebar.slider("Cooling Rate", 0.90, 0.999, 0.98)
ITER_PER_TEMP = st.sidebar.slider("Iterations / Temp", 10, 200, 30)

np.random.seed(42)
random.seed(42)

num_products = ROWS * COLS

# -----------------------------
# CO-OCCURRENCE MATRIX
# -----------------------------
@st.cache_data
def generate_co_matrix(n):
    mat = np.random.randint(0, 10, size=(n, n))
    mat = (mat + mat.T) / 2
    np.fill_diagonal(mat, 0)
    return mat

co_matrix = generate_co_matrix(num_products)

# -----------------------------
# HELPERS
# -----------------------------
def manhattan(p1, p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])

def create_layout():
    arr = list(range(num_products))
    random.shuffle(arr)
    return np.array(arr).reshape(ROWS, COLS)

def get_positions(layout):
    pos = {}
    for i in range(ROWS):
        for j in range(COLS):
            pos[layout[i, j]] = (i, j)
    return pos

def total_cost(layout):
    pos = get_positions(layout)
    cost = 0
    for i in range(num_products):
        for j in range(i+1, num_products):
            d = manhattan(pos[i], pos[j])
            cost += d + ALPHA * co_matrix[i][j] * d
    return cost

# -----------------------------
# DELTA COST
# -----------------------------
def delta_cost(layout, pos, a, b):
    (r1, c1), (r2, c2) = a, b
    p1 = layout[r1, c1]
    p2 = layout[r2, c2]

    delta = 0

    for other in range(num_products):
        if other == p1 or other == p2:
            continue

        r_o, c_o = pos[other]

        d1_old = manhattan((r1, c1), (r_o, c_o))
        d2_old = manhattan((r2, c2), (r_o, c_o))

        d1_new = manhattan((r2, c2), (r_o, c_o))
        d2_new = manhattan((r1, c1), (r_o, c_o))

        delta += (d1_new - d1_old) + (d2_new - d2_old)

        delta += ALPHA * (
            co_matrix[p1][other] * (d1_new - d1_old) +
            co_matrix[p2][other] * (d2_new - d2_old)
        )

    return delta

# -----------------------------
# SA
# -----------------------------
def optimize_sa(layout):
    current = layout.copy()
    pos = get_positions(current)
    current_cost = total_cost(current)

    best = current.copy()
    best_cost = current_cost

    T = INITIAL_TEMP
    history = []

    steps = 0
    max_steps = 2000

    while T > 0.5 and steps < max_steps:
        steps += 1

        for _ in range(ITER_PER_TEMP):
            r1, c1 = random.randint(0, ROWS-1), random.randint(0, COLS-1)
            r2, c2 = random.randint(0, ROWS-1), random.randint(0, COLS-1)

            if (r1, c1) == (r2, c2):
                continue

            d = delta_cost(current, pos, (r1, c1), (r2, c2))

            if d < 0 or random.random() < np.exp(-d / T):
                p1, p2 = current[r1, c1], current[r2, c2]

                current[r1, c1], current[r2, c2] = p2, p1

                pos[p1] = (r2, c2)
                pos[p2] = (r1, c1)

                current_cost += d

                if current_cost < best_cost:
                    best = current.copy()
                    best_cost = current_cost

        history.append(best_cost)
        T *= COOLING_RATE

    return best, best_cost, history

# -----------------------------
# GREEDY
# -----------------------------
def optimize_greedy(layout):
    current = layout.copy()
    best_cost = total_cost(current)

    history = [best_cost]

    improved = True
    max_iters = 200
    iters = 0

    while improved and iters < max_iters:
        improved = False
        iters += 1

        for i1 in range(ROWS):
            for j1 in range(COLS):
                for i2 in range(ROWS):
                    for j2 in range(COLS):

                        if (i1, j1) == (i2, j2):
                            continue

                        new_layout = current.copy()
                        new_layout[i1, j1], new_layout[i2, j2] = new_layout[i2, j2], new_layout[i1, j1]

                        new_cost = total_cost(new_layout)

                        if new_cost < best_cost:
                            current = new_layout
                            best_cost = new_cost
                            history.append(best_cost)
                            improved = True

    return current, best_cost, history

# -----------------------------
# VISUAL
# -----------------------------
def plot_layout(layout, title):
    fig, ax = plt.subplots()
    ax.imshow(layout)

    for i in range(ROWS):
        for j in range(COLS):
            ax.text(j, i, layout[i, j], ha='center', va='center')

    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

# -----------------------------
# SESSION STATE FIX
# -----------------------------
if "layout" not in st.session_state:
    st.session_state.layout = create_layout()

layout = st.session_state.layout

# -----------------------------
# UI
# -----------------------------
st.title("📦 Warehouse Optimization Dashboard")

st.subheader("Initial Layout")
st.pyplot(plot_layout(layout, "Initial Layout"))

initial_cost = total_cost(layout)
st.write("Initial Cost:", initial_cost)

# -----------------------------
# RUN
# -----------------------------
if st.button("Run Optimization"):

    sa_layout, sa_cost, sa_hist = optimize_sa(layout)

    with st.spinner("Running Greedy Optimization..."):
        gr_layout, gr_cost, gr_hist = optimize_greedy(layout)

    # -----------------------------
    # CONVERGENCE
    # -----------------------------
    if len(gr_hist) < len(sa_hist):
        gr_hist.extend([gr_hist[-1]] * (len(sa_hist) - len(gr_hist)))

    st.subheader("📈 Convergence Comparison")

    fig, ax = plt.subplots()
    ax.plot(sa_hist, label="Simulated Annealing")
    ax.plot(gr_hist, label="Greedy")
    ax.legend()
    ax.set_xlabel("Iterations")
    ax.set_ylabel("Cost")

    st.pyplot(fig)

    # -----------------------------
    # INSIGHT
    # -----------------------------
    st.markdown("""
    ### 📊 Insight
    - Greedy converges fast but gets stuck in local minima  
    - Simulated Annealing explores more and finds better solutions  
    """)

    st.info("Tip: Increase alpha to prioritize grouping frequently co-picked items.")

    # -----------------------------
    # LAYOUTS
    # -----------------------------
    st.subheader("🎨 Final Layouts")

    col1, col2 = st.columns(2)

    with col1:
        st.pyplot(plot_layout(sa_layout, "SA Layout"))

    with col2:
        st.pyplot(plot_layout(gr_layout, "Greedy Layout"))

    # -----------------------------
    # FINAL RESULTS
    # -----------------------------
    st.subheader("📊 Final Results")

    st.write("Initial Cost:", initial_cost)

    col1, col2 = st.columns(2)

    col1.metric(
        "SA Final Cost",
        round(sa_cost, 2),
        delta=round(initial_cost - sa_cost, 2)
    )

    col2.metric(
        "Greedy Final Cost",
        round(gr_cost, 2),
        delta=round(initial_cost - gr_cost, 2)
    ) 

    # -----------------------------
    # RESULTS TABLE
    # -----------------------------
    results_df = pd.DataFrame({
        "Algorithm": ["Initial", "Simulated Annealing", "Greedy"],
        "Cost": [
            round(initial_cost, 2),
            round(sa_cost, 2),
            round(gr_cost, 2)
        ]
    })

    st.write("### 📋 Detailed Results Table")
    st.dataframe(results_df)
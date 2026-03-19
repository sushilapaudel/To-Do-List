import sqlite3
import streamlit as st
import random

# ----------------------------
# Database setup
# ----------------------------
conn = sqlite3.connect("tasks.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    task TEXT,
    priority TEXT,
    pinned INTEGER,
    completed INTEGER
)
""")
conn.commit()

# Add user_name column to older databases if missing
try:
    c.execute("ALTER TABLE tasks ADD COLUMN user_name TEXT")
    conn.commit()
except sqlite3.OperationalError:
    pass

st.set_page_config(page_title="✨ My Pretty To-Do List ✨", page_icon="🌸", layout="wide")

# ----------------------------
# Session state
# ----------------------------
if "deleted_count" not in st.session_state:
    st.session_state.deleted_count = 0

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# ----------------------------
# Helper functions
# ----------------------------
def get_message(name):
    messages = [
        f"🌸 Hi {name}, you're blooming today!",
        f"💕 Hi {name}, you've got this! ✨",
        f"🦋 Hi {name}, one sweet task at a time...",
        f"🧁 Hi {name}, you're as sweet as a cupcake!",
        f"💖 Hi {name}, today is full of possibilities!",
        f"☕️ Hi {name}, coffee & tasks - perfect combo!",
        f"🍭 Hi {name}, make today colorful!",
        f"🌟 Hi {name}, you're a star!",
        f"🎀 Hi {name}, pretty tasks for a pretty day!"
    ]
    return random.choice(messages)

def priority_symbol(priority):
    if priority == "High":
        return "🔴"
    elif priority == "Medium":
        return "🟡"
    return "🟢"

def priority_color(priority):
    colors = {
        "High": "#ffb3b3",  # soft pink-red
        "Medium": "#fff2b3",  # soft yellow
        "Low": "#b3e0b3"  # soft green
    }
    return colors.get(priority, "#ffffff")

def sort_tasks(tasks):
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(
        tasks,
        key=lambda x: (
            not x["pinned"],
            x["completed"],
            priority_order[x["priority"]]
        )
    )

def load_tasks(user_name):
    c.execute(
        "SELECT id, user_name, task, priority, pinned, completed FROM tasks WHERE user_name = ?",
        (user_name,)
    )
    rows = c.fetchall()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "user_name": row[1],
            "task": row[2],
            "priority": row[3],
            "pinned": bool(row[4]),
            "completed": bool(row[5])
        })
    return tasks

# ----------------------------
# Custom CSS - Girly Edition
# ----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #fff5f7 0%, #ffe4e9 100%);
    font-family: 'Quicksand', sans-serif;
}

.main-title {
    font-size: 54px;
    font-weight: 700;
    color: #d44e6c;  /* Vibrant pink that stands out */
    margin-bottom: 30px;
    text-align: center;
    text-shadow: 3px 3px 6px rgba(255, 255, 255, 0.8);
    letter-spacing: 1px;
    background: none;
    -webkit-text-fill-color: initial;
}

.greet-box {
    background: linear-gradient(135deg, #ffd1dc 0%, #ffe4e1 100%);
    color: #b45f6b;
    padding: 25px 35px;
    border-radius: 50px;
    font-size: 24px;
    margin-bottom: 35px;
    font-weight: 500;
    text-align: center;
    border: 2px solid #ffb6c1;
    box-shadow: 0 8px 15px rgba(255, 182, 193, 0.3);
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
    100% { transform: translateY(0px); }
}

.metric-pill {
    display: block;
    padding: 15px 20px;
    border-radius: 40px;
    font-size: 20px;
    font-weight: 600;
    border: 2px solid white;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s;
    width: 100%;
    min-width: 120px;
    line-height: 1.4;
    text-align: center;
}

.metric-pill:hover {
    transform: scale(1.02);
}

.pending-pill {
    background: linear-gradient(135deg, #ffe5b4 0%, #ffd700 100%);
    color: #8b4513;
}

.completed-pill {
    background: linear-gradient(135deg, #c1e1c1 0%, #98fb98 100%);
    color: #2e7d32;
}

.deleted-pill {
    background: linear-gradient(135deg, #fbc4c4 0%, #ffb6b6 100%);
    color: #c41e3a;
}

.task-card {
    background: white;
    border-radius: 40px;
    padding: 25px 30px;
    margin-bottom: 20px;
    font-size: 20px;
    color: #4a4a4a;
    border: 2px solid #ffb6c1;
    box-shadow: 0 8px 15px rgba(255, 182, 193, 0.2);
    transition: all 0.3s ease;
}

.task-card:hover {
    transform: translateX(10px);
    box-shadow: 0 12px 20px rgba(255, 182, 193, 0.4);
}

.pinned-task {
    background: linear-gradient(135deg, #fff9e6 0%, #fff2d7 100%);
    border: 3px solid #ffd700;
    box-shadow: 0 8px 20px rgba(255, 215, 0, 0.2);
}

.task-text {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #5e5e5e;
}

.small-text {
    font-size: 16px;
    color: #888;
    font-weight: 400;
}

.stTextInput > div > div > input {
    border-radius: 30px !important;
    border: 2px solid #ffb6c1 !important;
    padding: 15px 20px !important;
    font-size: 18px !important;
    background-color: white !important;
    font-family: 'Quicksand', sans-serif !important;
}

.stSelectbox > div > div > select {
    border-radius: 30px !important;
    border: 2px solid #ffb6c1 !important;
    padding: 15px 20px !important;
    font-size: 16px !important;
    background-color: white !important;
    font-family: 'Quicksand', sans-serif !important;
}

.stCheckbox {
    font-size: 18px !important;
    color: #b45f6b !important;
    padding-top: 10px !important;
}

.stButton > button {
    border-radius: 30px !important;
    border: none !important;
    padding: 12px 25px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    background: linear-gradient(135deg, #ffb6c1 0%, #ff9eb5 100%) !important;
    color: white !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 10px rgba(255, 182, 193, 0.4) !important;
    font-family: 'Quicksand', sans-serif !important;
    border: 2px solid white !important;
}

.stButton > button:hover {
    transform: scale(1.05) !important;
    background: linear-gradient(135deg, #ff9eb5 0%, #ff8da1 100%) !important;
    box-shadow: 0 6px 15px rgba(255, 182, 193, 0.6) !important;
}

/* Special style for add button */
div[data-testid="column"]:nth-of-type(4) .stButton > button {
    background: linear-gradient(135deg, #98fb98 0%, #7ccd7c 100%) !important;
    padding: 15px 20px !important;
    font-size: 18px !important;
    margin-top: 0px !important;
}

.add-task-container {
    background: linear-gradient(135deg, #ffe4e9 0%, #ffd9e0 100%);
    border-radius: 60px;
    padding: 30px;
    margin-bottom: 30px;
    border: 2px solid #ffb6c1;
    box-shadow: 0 8px 20px rgba(255, 182, 193, 0.3);
}

.section-title {
    font-size: 32px;
    font-weight: 600;
    color: #b45f6b;
    margin-bottom: 20px;
    padding-left: 15px;
    text-shadow: 1px 1px 2px rgba(255, 182, 193, 0.3);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: #ffe4e9;
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #ffb6c1 0%, #ff9eb5 100%);
    border-radius: 10px;
    border: 2px solid white;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #ff9eb5 0%, #ff8da1 100%);
}

/* Priority badges */
.priority-badge {
    display: inline-block;
    padding: 5px 15px;
    border-radius: 30px;
    font-size: 14px;
    font-weight: 600;
    margin-left: 10px;
    color: #4a4a4a;
}

/* Emoji decorations */
.flower-decoration {
    text-align: center;
    font-size: 24px;
    margin: 10px 0;
    opacity: 0.7;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Decorative elements
# ----------------------------
st.markdown('<div class="flower-decoration">🌸 🌸 🌸</div>', unsafe_allow_html=True)

# ----------------------------
# Title
# ----------------------------
st.markdown('<div class="main-title">✨🌸 My Pretty To-Do List 🌸✨</div>', unsafe_allow_html=True)

st.markdown('<div class="flower-decoration">🦋 ✨ 🦋</div>', unsafe_allow_html=True)

# ----------------------------
# User name
# ----------------------------
col_name, col_spacer = st.columns([2, 1])
with col_name:
    name = st.text_input("💕 What's your name, beautiful? 💕", 
                        value=st.session_state.user_name, 
                        placeholder="Type your name here...",
                        key="name_input")
st.session_state.user_name = name.strip()

if st.session_state.user_name:
    st.markdown(
        f'<div class="greet-box">{get_message(st.session_state.user_name)}</div>',
        unsafe_allow_html=True
    )

# ----------------------------
# Add new task - Fixed alignment
# ----------------------------
if st.session_state.user_name:
    st.markdown('<div class="section-title">✨ Add a New Task ✨</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="add-task-container">', unsafe_allow_html=True)
        
        # Fixed column ratios for better alignment
        col1, col2, col3, col4 = st.columns([3, 1.2, 1, 0.8])
        
        with col1:
            task_input = st.text_input("📝 What needs to be done?", 
                                      placeholder="e.g., attend meeting, finish proposal...", 
                                      key="task_input",
                                      label_visibility="collapsed")
        
        with col2:
            priority = st.selectbox("🎯 Priority", 
                                   ["High", "Medium", "Low"], 
                                   key="priority_input",
                                   label_visibility="collapsed")
        
        with col3:
            pinned = st.checkbox("📌 Pin this task", key="pin_input")
        
        with col4:
            # Add button aligned with inputs
            st.write("")  # Spacing for alignment
            add_clicked = st.button("➕ Add", use_container_width=True, key="add_button")
        
        st.markdown('</div>', unsafe_allow_html=True)

    if add_clicked:
        if task_input.strip():
            c.execute(
                "INSERT INTO tasks (user_name, task, priority, pinned, completed) VALUES (?, ?, ?, ?, ?)",
                (st.session_state.user_name, task_input.strip(), priority, int(pinned), 0)
            )
            conn.commit()
            st.rerun()
            st.balloons()
        else:
            st.warning("💫 Please write your task first!")

# ----------------------------
# Load tasks for current user
# ----------------------------
tasks = load_tasks(st.session_state.user_name) if st.session_state.user_name else []

# ----------------------------
# Counts with cute icons - Fixed alignment
# ----------------------------
if st.session_state.user_name:
    pending_count = sum(1 for t in tasks if not t["completed"])
    completed_count = sum(1 for t in tasks if t["completed"])
    deleted_count = st.session_state.deleted_count

    # Use columns for better alignment
    col_stats1, col_stats2, col_stats3, col_stats4 = st.columns([1, 1, 1, 3])
    
    with col_stats1:
        st.markdown(
            f'<div class="metric-pill pending-pill">⏳ Pending<br>{pending_count}</div>',
            unsafe_allow_html=True
        )
    
    with col_stats2:
        st.markdown(
            f'<div class="metric-pill completed-pill">✅ Completed<br>{completed_count}</div>',
            unsafe_allow_html=True
        )
    
    with col_stats3:
        st.markdown(
            f'<div class="metric-pill deleted-pill">🗑️ Deleted<br>{deleted_count}</div>',
            unsafe_allow_html=True
        )
    
    with col_stats4:
        st.write("")  # Empty column for spacing

    st.markdown('<div class="flower-decoration">💫 ✨ 💫</div>', unsafe_allow_html=True)

    # ----------------------------
    # Show tasks
    # ----------------------------
    st.markdown('<div class="section-title">📋 Your Tasks</div>', unsafe_allow_html=True)
    
    if tasks:
        sorted_tasks = sort_tasks(tasks)

        for task in sorted_tasks:
            task_id = task["id"]

            card_class = "task-card pinned-task" if task["pinned"] else "task-card"
            pin_mark = "📌 " if task["pinned"] else ""
            priority_mark = priority_symbol(task["priority"])
            
            status_emoji = "✅" if task["completed"] else "⏳"
            status_text = "Completed" if task["completed"] else "Pending"

            st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)

            col_a, col_b, col_c, col_d = st.columns([5, 1.2, 1.2, 1.2])

            with col_a:
                task_style = "text-decoration: line-through; opacity: 0.7;" if task["completed"] else ""
                st.markdown(
                    f"""
                    <div class="task-text" style="{task_style}">
                        {pin_mark}{priority_mark} {task['task']}
                        <span class="priority-badge" style="background-color: {priority_color(task['priority'])}">
                            {task['priority']}
                        </span>
                    </div>
                    <div class="small-text">
                        {status_emoji} {status_text}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_b:
                if not task["completed"]:
                    if st.button("✅ Done", key=f"complete_{task_id}", use_container_width=True):
                        c.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
                        conn.commit()
                        st.balloons()
                        st.rerun()
                else:
                    if st.button("↩️ Undo", key=f"undo_{task_id}", use_container_width=True):
                        c.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
                        conn.commit()
                        st.rerun()

            with col_c:
                pin_icon = "📍 Unpin" if task["pinned"] else "📌 Pin"
                if st.button(pin_icon, key=f"pin_{task_id}", use_container_width=True):
                    new_pin_value = 0 if task["pinned"] else 1
                    c.execute("UPDATE tasks SET pinned = ? WHERE id = ?", (new_pin_value, task_id))
                    conn.commit()
                    st.rerun()

            with col_d:
                if st.button("🗑️ Delete", key=f"delete_{task_id}", use_container_width=True):
                    c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                    conn.commit()
                    st.session_state.deleted_count += 1
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("🌸 No tasks yet! Add something sweet to do! 🌸")

elif not st.session_state.user_name:
    st.info("💖 Please enter your name to start your pretty to-do list! 💖")

# ----------------------------
# Footer decoration
# ----------------------------
st.markdown('<div class="flower-decoration">💕 Made with love for your tasks 💕</div>', unsafe_allow_html=True)
st.markdown('<div class="flower-decoration">🌸 🦋 🌸 🦋 🌸</div>', unsafe_allow_html=True)
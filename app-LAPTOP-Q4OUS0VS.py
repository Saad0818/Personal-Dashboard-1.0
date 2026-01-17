# app.py
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta, date
from collections import defaultdict
from sqlalchemy.orm import Session
from db import (
    init_db, SessionLocal,
    Project, System, Experiment, Task
)

# Initialize DB
init_db()

# --------- APP CONFIG ---------

st.set_page_config(
    page_title="Saad Mission Control",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Palette (Monochromatic / Premium)
CHARCOAL = "#0F172A" 
ONYX = "#000000"
SLATE = "#64748B"
ACCENT_PRIMARY = "#000000" 
ACCENT_SECONDARY = "#334155"
CLOUD = "#F8FAFC"
PURE_WHITE = "#FFFFFF"
BG_COLOR = "#F1F5F9" # Slightly darker for contrast with the white card

# --------- GLOBAL STYLE ---------

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Reset & Base */
.stApp {{
    background-color: {BG_COLOR};
    color: {CHARCOAL};
    font-family: 'Outfit', sans-serif;
}}

/* Hide Streamlit Header & Footer */
header[data-testid="stHeader"] {{ display: none; }}
footer {{ display: none; }}

/* Main Dashboard Card (The "Island") */
.block-container {{
    padding-top: 0rem !important;
    padding-bottom: 5rem !important;
    max-width: 1400px;
    margin: 2rem auto !important;
    background-color: {PURE_WHITE};
    border-radius: 40px;
    box-shadow: 0 40px 100px rgba(15, 23, 42, 0.08); /* Deep, sophisticated shadow */
    border: 1px solid rgba(0,0,0,0.02);
}}

/* Premium Top Header Area (The Folder Tabs) */
.premium-nav-header {{
    background-color: #E2E8F0; /* Light grey for the "back" of the folder */
    padding: 2rem 2rem 0rem 2.5rem;
    border-radius: 40px 40px 0 0;
    margin: -1px -1px 0 -1px; /* Removed bottom margin to connect */
    display: flex;
    justify-content: flex-start; /* Align tabs to the left like a folder */
    align-items: flex-end;
    gap: 4px;
    border-bottom: 2px solid #FFFFFF; /* Seamless white line */
}}

/* Tab Links */
.nav-pill-link {{
    background: rgba(255, 255, 255, 0.4);
    color: #475569;
    text-decoration: none !important;
    padding: 14px 28px;
    border-radius: 20px 20px 0 0; /* Only top corners rounded */
    font-weight: 700;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(0,0,0,0.05);
    border-bottom: none;
    position: relative;
    top: 2px; /* Pull down to overlap the border */
    backdrop-filter: blur(4px);
}}

.nav-pill-link:hover {{
    background: rgba(255, 255, 255, 0.7);
    color: #0F172A;
    transform: translateY(-2px);
}}

.nav-pill-link.active {{
    background: #FFFFFF;
    color: #000000;
    padding: 18px 36px; /* Slightly larger active tab */
    top: 2px;
    z-index: 10;
    border: 1px solid rgba(0,0,0,0.08);
    border-bottom: 2px solid #FFFFFF; /* Matches the content face */
    box-shadow: 0 -10px 25px rgba(0,0,0,0.03);
}}

/* The Inverted Corner Magic */
.nav-pill-link.active::before,
.nav-pill-link.active::after {{
    content: "";
    position: absolute;
    bottom: -2px;
    width: 20px;
    height: 20px;
    background: transparent;
    pointer-events: none;
}}

.nav-pill-link.active::before {{
    left: -21px;
    border-bottom-right-radius: 20px;
    box-shadow: 5px 5px 0 5px #FFFFFF;
}}

.nav-pill-link.active::after {{
    right: -21px;
    border-bottom-left-radius: 20px;
    box-shadow: -5px 5px 0 5px #FFFFFF;
}}

.nav-pill-icon {{
    font-size: 1.2rem;
}}

/* Heading Improvements */
h1, h2, h3 {{
    font-family: 'Outfit', sans-serif;
}}

.sa-section-head {{
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    color: #64748B;
    font-weight: 800;
    margin-bottom: 1.5rem;
    padding-bottom: 10px;
    border-bottom: 3px solid #F1F5F9;
}}

.sa-task-row {{
    background: {PURE_WHITE};
    border-radius: 16px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    border: 1px solid #F1F5F9;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    transition: all 0.2s;
}}

.sa-task-row:hover {{
    border-color: #E2E8F0;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    transform: translateY(-1px);
}}

/* Custom Scrollbar */
::-webkit-scrollbar {{ width: 8px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #E2E8F0; border-radius: 10px; }}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_nav_bar():
    # Detect current page from query params
    qp = {k: v[0] if v else None for k, v in st.experimental_get_query_params().items()}
    current_page = qp.get("page", "home")
    project_id = qp.get("project_id")

    if project_id:
        db = SessionLocal()
        proj = db.query(Project).filter(Project.id == project_id).first()
        if proj:
            area = (proj.area or "").lower()
            if area in ["research", "writing", "paper"]:
                current_page = "research"
            elif area in ["trading", "algo", "patent", "business"]:
                current_page = "business"
            else:
                current_page = "home"
        db.close()

    pages = [
        {"id": "home", "label": "Mission Control", "icon": "🌊"},
        {"id": "research", "label": "Research Hub", "icon": "🧪"},
        {"id": "business", "label": "Business Hub", "icon": "💼"},
        {"id": "milestones", "label": "Milestones", "icon": "🏁"},
        {"id": "history", "label": "History", "icon": "📜"}
    ]

    # Generate HTML for the navigation bar
    nav_html = '<div class="premium-nav-header">'
    for p in pages:
        is_active = current_page == p["id"]
        active_class = "active" if is_active else "" or ""
        # Using a link that sets the query parameter. Streamlit URLs handle this.
        nav_html += f'<a href="/?page={p["id"]}" target="_self" class="nav-pill-link {active_class}"><span class="nav-pill-icon">{p["icon"]}</span><span>{p["label"]}</span></a>'
    nav_html += '</div>'
    
    st.markdown(nav_html, unsafe_allow_html=True)


# --------- HELPERS (Data Fetching) ---------

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

def get_data(db):
    tasks = db.query(Task).all()
    
    # Areas
    by_area = defaultdict(list)
    for t in tasks: by_area[(t.area or "").lower()].append(t)
    
    def calc_stats(tl):
        if not tl: return 0,0,0
        d = len([x for x in tl if x.status=='done'])
        return d/len(tl), d, len(tl)-d

    r_stats = calc_stats(by_area['research'])
    t_stats = calc_stats(by_area['trading'])
    
    # Pending
    pending = [t for t in tasks if t.status in ['inbox','next','doing']]
    p_map = {'high':3, 'medium':2, 'low':1}
    pending.sort(key=lambda x: (-p_map.get((x.priority or '').lower(),1), x.due_date or datetime.max))
    
    # Milestone (Explicitly chosen by user)
    active_m = db.query(Task).filter(Task.is_active_milestone == True, Task.status != 'done').first()
    if not active_m:
        # Fallback: Nearest high priority task with due date
        future = [t for t in pending if t.due_date and t.due_date.date() >= datetime.now().date() and (t.priority or '').lower() == 'high']
        future.sort(key=lambda x: x.due_date)
        active_m = future[0] if future else None
        
    milestone = (active_m, (active_m.due_date.date() - datetime.now().date()).days if active_m and active_m.due_date else 0) if active_m else (None, 0)

    # Activity (Chart Data - Last 7 Days)
    completed = [t for t in tasks if t.status=='done' and t.completed_at]
    today = datetime.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)] # This creates Mon, Tue, ... order ending today
    
    daily_counts = {d: 0 for d in dates}
    for t in completed:
        d = t.completed_at.date()
        if d in daily_counts:
            daily_counts[d] += 1
            
    history_df = pd.DataFrame({
        "Date": dates,
        "Day": [d.strftime("%a") for d in dates],
        "Tasks": [daily_counts[d] for d in dates]
    })

    # Projects
    projects = db.query(Project).all()
    
    # Categorize Projects (not tasks)
    papers_proj = [p for p in projects if (p.area or '').lower() == 'paper']
    algos_proj = [p for p in projects if (p.area or '').lower() == 'algo']
    patents_proj = [p for p in projects if (p.area or '').lower() == 'patent']

    return {
        'research': r_stats,
        'trading': t_stats,
        'pending': pending[:6],
        'papers': papers_proj,
        'algos': algos_proj,
        'patents': patents_proj,
        'milestone': milestone,
        'history_df': history_df
    }

def add_task_ui(db, area):
    with st.form(key=f"add_{area}", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        title = c1.text_input("Task", label_visibility="collapsed", placeholder=f"New {area} task...")
        prio = c2.selectbox("Prio", ["low","medium","high"], index=1, label_visibility="collapsed")
        if st.form_submit_button("Add"):
            if title:
                db.add(Task(
                    title=title, status="inbox", area=area, priority=prio,
                    created_at=datetime.now(), due_date=datetime.now()
                ))
                db.commit()
                st.experimental_rerun()

# --------- MAIN LAYOUT ---------

def page_home():
    db = next(get_db())
    data = get_data(db)
    
    # Header
    c_head, c_date = st.columns([3, 1])
    c_head.markdown(f"## Mission Control")
    c_date.markdown(f"<div style='text-align:right; color:{SLATE}; font-weight:600;'>{datetime.now().strftime('%A, %B %d')}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # 3-Column Grid for Condensed View
    col1, col2, col3 = st.columns([1.1, 1.1, 1.4], gap="large")

    # --- COLUMN 1: THE DRIVER (Goal + Historical Perf) ---
    with col1:
        # Milestone
        st.markdown('<div class="sa-section-head">Big Goal</div>', unsafe_allow_html=True)
        ms, days = data['milestone']
        if ms:
            html_parts = []
            html_parts.append(f"""<div style="background: linear-gradient(135deg, #334155 0%, #000000 100%); border-radius:32px; padding:2.5rem 2rem; position: relative; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);">""")
            html_parts.append(f"""    <div style="position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, rgba(0,0,0,0) 60%);"></div>""")
            html_parts.append(f"""    <div style="position: relative; z-index: 1;">""")
            html_parts.append(f"""            <div style="font-size:0.85rem; font-weight:800; color:rgba(255,255,255,0.6); text-transform:uppercase; letter-spacing:0.12em; margin-bottom:0.5rem;">Next Milestone</div>""")
            html_parts.append(f"""            <div style="font-size:3.8rem; font-weight:800; color:#FFFFFF; line-height:1; letter-spacing:-0.04em; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3));">""")
            html_parts.append(f"""            {days}<span style="font-size:1.1rem; font-weight:700; color:rgba(255,255,255,0.6); margin-left:10px; vertical-align:middle;">DAYS LEFT</span>""")
            html_parts.append(f"""        </div>""")
            html_parts.append(f"""            <div style="margin: 1.8rem 0; height: 8px; width: 100%; background: rgba(255,255,255,0.1); border-radius: 100px; overflow:hidden;">""")
            html_parts.append(f"""            <div style="height: 100%; width: {max(0, min(100, 100 - (days*5)))}%; background: #FFFFFF; border-radius: 100px; box-shadow: 0 0 20px rgba(255,255,255,0.3);"></div>""")
            html_parts.append(f"""        </div>""")
            html_parts.append(f"""        <div style="font-size:1.6rem; font-weight:800; color:#FFFFFF; line-height:1.2; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">""")
            html_parts.append(f"""            {ms.title}""")
            html_parts.append(f"""        </div>""")
            html_parts.append(f"""            <div style="margin-top:1.8rem; display:inline-flex; align-items:center; gap:8px; padding: 10px 20px; background:rgba(255,255,255,0.08); backdrop-filter: blur(10px); border-radius:100px; border:1px solid rgba(255,255,255,0.15);">""")
            html_parts.append(f"""            <span style="font-size:1.1rem;">🎯</span>""")
            html_parts.append(f"""            <span style="font-size:0.9rem; font-weight:700; color:#FFFFFF;">Target: {ms.due_date.strftime('%b %d')}</span>""")
            html_parts.append(f"""        </div>""")
            html_parts.append(f"""    </div>""")
            html_parts.append(f"""</div>""")
            
            card_html = "".join(html_parts)
            st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No active milestone.")

        # Historical Performance (Altair Chart)
        st.markdown('<div class="sa-section-head">Historical Performance</div>', unsafe_allow_html=True)
        
        hist = data['history_df']
        wk_total = hist['Tasks'].sum()
        avg = hist['Tasks'].mean()
        
        # Stats summary
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; margin-bottom:12px; padding:0 8px;">
                <div>
                    <div style="font-size:1.5rem; font-weight:800; color:{ONYX}; line-height:1;">{wk_total}</div>
                    <div style="font-size:0.65rem; color:{SLATE}; text-transform:uppercase; font-weight:600; margin-top:4px;">Last 7 Days</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.5rem; font-weight:800; color:{ONYX}; line-height:1;">{avg:.1f}</div>
                    <div style="font-size:0.65rem; color:{SLATE}; text-transform:uppercase; font-weight:600; margin-top:4px;">Daily Avg</div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        
        # Chart - "Your Statistics" Style
        # Ensure chronological order
        base = alt.Chart(hist).encode(
            x=alt.X('Day', sort=alt.SortField(field="Date", order="ascending"), 
                  axis=alt.Axis(labelAngle=0, grid=False, title=None, labelColor=SLATE, tickSize=0, domain=False))
        )

        # Layer 1: Smooth Line
        line = base.mark_line(
            interpolate='monotone',
            stroke=ACCENT_PRIMARY,
            strokeWidth=4
        ).encode(
            y=alt.Y('Tasks', axis=alt.Axis(grid=False, title=None, tickMinStep=1, labelColor=SLATE, tickSize=0, domain=False))
        )
        
        # Layer 2: Subtle Area (No gradient)
        area = base.mark_area(
            interpolate='monotone',
            opacity=0.05,
            color=ACCENT_PRIMARY
        ).encode(
            y='Tasks'
        )

        
        # Layer 3: Points
        points = base.mark_circle(
            size=80,
            color=PURE_WHITE,
            opacity=1,
            stroke=ACCENT_PRIMARY,
            strokeWidth=3
        ).encode(
            y='Tasks',
            tooltip=['Date', 'Tasks']
        )
        
        # Layer 4: Floating Labels
        text = base.mark_text(
            align='center',
            baseline='bottom',
            dy=-12,
            fontSize=12,
            fontWeight='bold',
            color=CHARCOAL
        ).encode(
            y='Tasks',
            text=alt.Text('Tasks', format='d')
        )

        chart = (area + line + points + text).configure_view(
            strokeWidth=0
        ).properties(
            height=220
        ).configure(
            background='transparent'
        )
        
        st.altair_chart(chart, use_container_width=True, theme=None)

    # --- COLUMN 2: FOCUS (Pie Charts) ---
    with col2:
        st.markdown('<div class="sa-section-head">Focus Areas</div>', unsafe_allow_html=True)
        
        # Research
        rp, rd, ro = data['research']
        st.markdown(
            f"""
            <div style="background:{PURE_WHITE}; padding:1.5rem; border-radius:24px; text-align:center; margin-bottom:1.5rem; border:1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="font-weight:700; color:{CHARCOAL}; margin-bottom:1.2rem; font-size:1rem; letter-spacing:0.02em;">Research</div>
                <div style="
                    width:120px; height:120px; margin:0 auto; border-radius:50%;
                    background: conic-gradient({ACCENT_PRIMARY} 0% {int(rp*100)}%, #F1F5F9 0);
                    display:flex; align-items:center; justify-content:center;
                    position: relative;
                ">
                     <div style="background:{PURE_WHITE}; width:90px; height:90px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.5rem; color:{CHARCOAL}; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);">
                        {int(rp*100)}%
                    </div>
                </div>
                <div style="font-size:0.8rem; margin-top:1.2rem; color:{SLATE}; font-weight:500;">
                    <span style="color:{ACCENT_PRIMARY}; font-weight:700;">{rd}</span> done <span style="margin:0 4px; opacity:0.3;">|</span> {ro} open
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        with st.expander("Add Research Task"):
            add_task_ui(db, "research")
            
        # Trading
        tp, td, to = data['trading']
        st.markdown(
            f"""
            <div style="background:{PURE_WHITE}; padding:1.5rem; border-radius:24px; text-align:center; margin-bottom:1.5rem; margin-top:2rem; border:1px solid #E5E7EB; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="font-weight:700; color:{CHARCOAL}; margin-bottom:1.2rem; font-size:1rem; letter-spacing:0.02em;">Algo Trading</div>
                <div style="
                    width:120px; height:120px; margin:0 auto; border-radius:50%;
                    background: conic-gradient({ACCENT_SECONDARY} 0% {int(tp*100)}%, #F1F5F9 0);
                    display:flex; align-items:center; justify-content:center;
                ">
                    <div style="background:{PURE_WHITE}; width:90px; height:90px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:1.5rem; color:{CHARCOAL}; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);">
                        {int(tp*100)}%
                    </div>
                </div>
                <div style="font-size:0.8rem; margin-top:1.2rem; color:{SLATE}; font-weight:500;">
                    <span style="color:{ACCENT_SECONDARY}; font-weight:700;">{td}</span> done <span style="margin:0 4px; opacity:0.3;">|</span> {ro} open
                </div>
            </div>
            """, unsafe_allow_html=True
        )
        with st.expander("Add Trading Task"):
            add_task_ui(db, "trading")

    # --- COLUMN 3: QUEUE ---
    with col3:
        st.markdown('<div class="sa-section-head">Current Work</div>', unsafe_allow_html=True)
        
        # Helper to render multiple Project cards
        def render_project_group(title, projects, icon="b"):
            if not projects: return
            st.markdown(f'<div class="sa-sub-head"><span>{icon}</span> {title}</div>', unsafe_allow_html=True)
            for p in projects:
                # Count open tasks
                open_tasks = len([t for t in p.tasks if t.status != 'done'])
                
                # We use a button that acts as a link trigger
                # Using a workaround with columns to make the row look decent
                
                # Visual Card
                st.markdown(
                   f"""
                    <div class="sa-task-row" style="cursor: pointer; display:block;">
                        <div style="font-weight:700; font-size:0.95rem; color:{CHARCOAL};">
                            {p.name}
                        </div>
                        <div style="font-size:0.75rem; color:{SLATE}; margin-top:4px; display:flex; justify-content:space-between;">
                            <span>{p.description if p.description else ''}</span>
                            <span style="font-weight:600; color:{CHARCOAL}; background:#E2E6EA; padding:2px 8px; border-radius:10px;">{open_tasks} Tasks</span>
                        </div>
                    </div>
                   """, unsafe_allow_html=True
                )
                # Hidden button to trigger navigation
                if st.button(f"Open {p.name}", key=f"btn_{p.id}"):
                    st.experimental_set_query_params(project_id=str(p.id))
                    st.experimental_rerun()

        render_project_group("Papers", data['papers'], "📚")
        render_project_group("Algorithms", data['algos'], "⚡")
        render_project_group("Patents", data['patents'], "🛡️")

        st.markdown("---")
        with st.expander("➕ New Project"):
            with st.form("new_project_form"):
                p_name = st.text_input("Project Name")
                p_desc = st.text_area("Description")
                p_area = st.selectbox("Category", ["paper", "algo", "patent", "research", "trading"])
                if st.form_submit_button("Create Project"):
                    if p_name:
                        db = next(get_db())
                        db.add(Project(name=p_name, description=p_desc, area=p_area))
                        db.commit()
                        st.experimental_rerun()

def page_project_detail(project_id):
    st.markdown("<br><br>", unsafe_allow_html=True)
    db = next(get_db())
    proj = db.query(Project).filter(Project.id == project_id).first()
    
    if not proj:
        st.error("Project not found.")
        if st.button("Back to Home"):
            st.experimental_set_query_params()
            st.rerun()
        return

    # Header
    st.markdown(
        f"""
        <div style="margin-bottom: 2rem;">
            <div style="color:{SLATE}; text-transform:uppercase; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; margin-bottom:0.5rem;">
                Project / {(proj.area or '').upper()}
            </div>
            <h1 style="font-size:3rem;">{proj.name}</h1>
            <div style="font-size:1.1rem; color:{SLATE}; margin-top:0.5rem; max-width:600px;">
                {proj.description or 'No description.'}
            </div>
        </div>
        """, unsafe_allow_html=True
    )
    
    # Task Lists
    tasks = db.query(Task).filter(Task.project_id == proj.id).all()

    # Action Buttons
    c_back, c_del = st.columns([1, 1])
    if c_back.button("← Back to Mission Control", use_container_width=True):
        st.experimental_set_query_params()
        st.rerun()
        
    if c_del.button("🗑️ Delete Project", use_container_width=True, type="secondary"):
        if st.session_state.get(f"confirm_del_{proj.id}"):
            # Delete associated tasks first
            for t in tasks: db.delete(t)
            db.delete(proj)
            db.commit()
            st.experimental_set_query_params()
            st.rerun()
        else:
            st.session_state[f"confirm_del_{proj.id}"] = True
            st.warning("Click again to confirm deletion.")
        
    st.markdown("---")
    
    # Add Task Form
    with st.expander("Add New Task", expanded=True):
        with st.form("new_task"):
            c1, c2 = st.columns([4, 1])
            t_title = c1.text_input("Task Title")
            t_prio = c2.selectbox("Priority", ["low", "medium", "high"])
            if st.form_submit_button("Create Task"):
                if t_title:
                    db.add(Task(
                        title=t_title, 
                        project_id=proj.id, 
                        priority=t_prio,
                        status="inbox",
                        area=proj.area,
                        created_at=datetime.now()
                    ))
                    db.commit()
                    st.experimental_rerun()

    # Task Lists
    tasks = db.query(Task).filter(Task.project_id == proj.id).all()
    pending = [t for t in tasks if t.status != 'done']
    done = [t for t in tasks if t.status == 'done']
    
    # Sort pending by priority
    p_map = {'high': 0, 'medium': 1, 'low': 2}
    pending.sort(key=lambda x: p_map.get(x.priority, 1))

    st.markdown("### Pending Tasks")
    if not pending:
        st.info("No active tasks.")
        
    for t in pending:
        c1, c2, c3 = st.columns([0.5, 4, 1])
        # Priority Badge
        prio = t.priority
        color = ONYX if prio == 'high' else ("#E2E6EA" if prio == 'medium' else "#F3F5F9")
        text_c = "#FFF" if prio == 'high' else CHARCOAL
        
        c1.markdown(f"""
            <div style="background:{color}; color:{text_c}; padding:4px 8px; border-radius:6px; font-size:0.7rem; font-weight:700; text-align:center; text-transform:uppercase;">
                {prio[:3]}
            </div>
        """, unsafe_allow_html=True)
        
        c2.markdown(f"**{t.title}**")
        
        if c3.button("Complete", key=f"done_{t.id}"):
            t.status = "done"
            t.completed_at = datetime.now()
            db.commit()
            st.rerun()
            
    if done:
        st.markdown("### Completed", unsafe_allow_html=True)
        for t in done:
            st.markdown(f"<div style='color:{SLATE}; text-decoration:line-through; font-size:0.9rem; padding: 4px 0;'>{t.title}</div>", unsafe_allow_html=True)



def page_research_hub():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 🧪 Research Hub")
    db = next(get_db())
    # Unified with 'paper', 'research', and 'writing'
    projects = db.query(Project).filter(Project.area.in_(["research", "writing", "paper"])).all()
    
    if not projects:
        st.info("No research or paper projects found.")
        return

    cols = st.columns(2)
    for i, p in enumerate(projects):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:{PURE_WHITE}; padding:1.5rem; border-radius:24px; border:1px solid #E5E7EB; margin-bottom:1.5rem; min-height: 180px;">
                <div style="color:{SLATE}; text-transform:uppercase; font-size:0.7rem; font-weight:700; letter-spacing:0.1em; margin-bottom:0.5rem;">{(p.area or "Research").upper()}</div>
                <h3 style="margin:0;">{p.name}</h3>
                <p style="color:{SLATE}; font-size:0.9rem;">{p.description or 'No description'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show top 3 pending tasks
            tasks = [t for t in p.tasks if t.status != 'done']
            for t in tasks[:3]:
                # Use a cleaner way to show tasks in hub view
                st.markdown(f"• **{t.title}**")
            
            if st.button(f"View Project: {p.name}", key=f"view_{p.id}", use_container_width=True):
                st.experimental_set_query_params(project_id=str(p.id))
                st.experimental_rerun()
            st.markdown("<br>", unsafe_allow_html=True)

def page_business_hub():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 💼 Business Hub")
    db = next(get_db())
    # Projects for financial gain (trading, algorithms, etc.)
    projects = db.query(Project).filter(Project.area.in_(["trading", "algo", "patent"])).all()
    
    if not projects:
        st.info("No business projects found.")
        return

    cols = st.columns(2)
    for i, p in enumerate(projects):
        with cols[i % 2]:
            st.markdown(f"""
            <div style="background:{PURE_WHITE}; padding:1.5rem; border-radius:24px; border:1px solid #E5E7EB; margin-bottom:1.5rem;">
                <h3 style="margin:0;">{p.name}</h3>
                <p style="color:{SLATE}; font-size:0.9rem;">{p.description or 'No description'}</p>
            </div>
            """, unsafe_allow_html=True)
            tasks = [t for t in p.tasks if t.status != 'done']
            for t in tasks[:3]:
                st.checkbox(t.title, key=f"b_t_{t.id}")
            if st.button(f"Manage {p.name}", key=f"edit_{p.id}"):
                st.experimental_set_query_params(project_id=str(p.id))
                st.experimental_rerun()

def page_milestones():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("## 🏁 Milestones Management")
    db = next(get_db())
    
    # Add Milestone Form
    with st.expander("➕ Add New Milestone"):
        with st.form("new_milestone"):
            title = st.text_input("Milestone Title")
            desc = st.text_area("Description")
            deadline = st.date_input("Deadline", value=datetime.now().date() + timedelta(days=30))
            is_active = st.checkbox("Set as Active (Show in Mission Control)", value=True)
            if st.form_submit_button("Create Milestone"):
                if title:
                    if is_active:
                        # Deactivate others
                        db.query(Task).filter(Task.is_active_milestone == True).update({"is_active_milestone": False})
                    
                    new_m = Task(
                        title=title, description=desc, 
                        due_date=datetime.combine(deadline, datetime.min.time()),
                        is_milestone=True, is_active_milestone=is_active,
                        status="next", created_at=datetime.now()
                    )
                    db.add(new_m)
                    db.commit()
                    st.experimental_rerun()

    # List Milestones
    m_tasks = db.query(Task).filter(Task.is_milestone == True).order_by(Task.status == 'done', Task.due_date).all()
    
    if not m_tasks:
        st.info("No milestones found. Create one above!")
        return

    for m in m_tasks:
        is_done = m.status == "done"
        active_tag = " [ACTIVE]" if m.is_active_milestone and not is_done else ""
        done_tag = " ✅ COMPLETED" if is_done else ""
        
        with st.container():
            st.markdown(f"### {m.title}{active_tag}{done_tag}")
            st.write(m.description or "No description.")
            st.write(f"Deadline: {m.due_date.strftime('%Y-%m-%d') if m.due_date else 'No deadline'}")
            
            c1, c2, c3 = st.columns([1, 1, 3])
            
            if not is_done:
                if c1.button("Mark Completed", key=f"comp_{m.id}"):
                    m.status = "done"
                    m.completed_at = datetime.now()
                    m.is_active_milestone = False
                    db.commit()
                    st.experimental_rerun()
                
                if not m.is_active_milestone:
                    if c2.button("Set Active", key=f"act_{m.id}"):
                        db.query(Task).filter(Task.is_active_milestone == True).update({"is_active_milestone": False})
                        m.is_active_milestone = True
                        db.commit()
                        st.experimental_rerun()
            
            if c3.button("🗑️ Delete", key=f"del_m_{m.id}"):
                db.delete(m)
                db.commit()
                st.experimental_rerun()
            
            st.markdown("---")


def page_history():
    st.markdown("<br><br>", unsafe_allow_html=True)
    db = next(get_db())
    
    # Header
    c1, c2 = st.columns([1, 5])
    if c1.button("← Back"):
        st.experimental_set_query_params()
        st.rerun()
        
    c2.markdown("## Completed Tasks History")
    
    tasks = db.query(Task).filter(Task.status == 'done').order_by(Task.completed_at.desc()).all()
    
    if not tasks:
        st.info("No completed tasks found in history.")
        return

    data_rows = []
    for t in tasks:
        duration_str = "-"
        if t.completed_at and t.created_at:
            # simple duration
            delta = t.completed_at - t.created_at
            days = delta.days
            hours, remainder = divmod(delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                duration_str = f"{days}d {hours}h"
            elif hours > 0:
                duration_str = f"{hours}h {minutes}m"
            else:
                duration_str = f"{minutes}m"

        project_name = t.project.name if t.project else (t.system.name if t.system else "-")
        
        data_rows.append({
            "Title": t.title,
            "Project/System": project_name,
            "Area": t.area,
            "Completed At": t.completed_at.strftime("%Y-%m-%d %H:%M") if t.completed_at else "-",
            "Duration": duration_str
        })
    
    df = pd.DataFrame(data_rows)
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Title": st.column_config.TextColumn("Task", width="large"),
            "Project/System": st.column_config.TextColumn("Context", width="medium"),
            "Area": st.column_config.TextColumn("Area", width="small"),
            "Completed At": st.column_config.TextColumn("Finished", width="medium"),
            "Duration": st.column_config.TextColumn("Time Taken", width="small"),
        },
        hide_index=True
    )


if __name__ == "__main__":
    render_nav_bar()
    # Router
    qp = {k: v[0] if v else None for k, v in st.experimental_get_query_params().items()}
    pid = qp.get("project_id")
    page = qp.get("page", "home")
    
    if pid:
        page_project_detail(pid)
    elif page == "research":
        page_research_hub()
    elif page == "business":
        page_business_hub()
    elif page == "milestones":
        page_milestones()
    elif page == "history":
        page_history()
    else:
        page_home()
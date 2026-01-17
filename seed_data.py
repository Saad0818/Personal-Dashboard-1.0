
import random
from datetime import datetime, timedelta
from db import init_db, SessionLocal, Task, Project

def seed():
    init_db()
    db = SessionLocal()

    # Clear existing
    db.query(Task).delete()
    db.query(Project).delete()
    db.commit()

    print("Cleared existing data.")

    # --- 1. PROJECTS (The "Current Work") ---
    
    # PAPERS
    p_paper = Project(
        name="Attention is All You Need",
        description="Deep dive into the transformer architecture.",
        area="paper",
        status="active",
        target_date=datetime.now() + timedelta(days=5)
    )
    db.add(p_paper)
    
    # ALGOS
    p_algo = Project(
        name="Oasis Algo System",
        description="Mean reversion strategy on H1 timeframe.",
        area="algo",
        status="active",
        target_date=datetime.now() + timedelta(days=14)
    )
    db.add(p_algo)
    
    # PATENTS
    p_patent = Project(
        name="Transformer Market Prediction",
        description="System and method for financial time series forecasting using attention mechanisms.",
        area="patent",
        status="active",
        target_date=datetime.now() + timedelta(days=60)
    )
    db.add(p_patent)
    
    db.commit() # Get IDs

    # --- 2. TASKS (Associated with Projects) ---

    # Paper Tasks
    db.add(Task(title="Read Abstract & Intro", status="done", priority="high", project_id=p_paper.id, area="research", completed_at=datetime.now()))
    db.add(Task(title="Annotate Architecture Diagram", status="inbox", priority="medium", project_id=p_paper.id, area="research", due_date=datetime.now()))
    db.add(Task(title="Summarize key contributions", status="inbox", priority="medium", project_id=p_paper.id, area="research", due_date=datetime.now()+timedelta(days=1)))
    
    # Milestone Task
    db.add(Task(title="Paper Published", status="inbox", priority="high", project_id=p_paper.id, area="research", due_date=datetime.now()+timedelta(days=14)))

    # Algo Tasks
    db.add(Task(title="Fix slippage model", status="inbox", priority="medium", project_id=p_algo.id, area="trading", due_date=datetime.now()))
    db.add(Task(title="Implement Kelly Criterion", status="inbox", priority="medium", project_id=p_algo.id, area="trading", due_date=datetime.now()+timedelta(days=2)))
    db.add(Task(title="Backtest 2020-2023", status="done", priority="high", project_id=p_algo.id, area="trading", completed_at=datetime.now()-timedelta(days=1)))

    # Patent Tasks
    db.add(Task(title="Draft Claims 1-10", status="inbox", priority="medium", project_id=p_patent.id, area="writing", due_date=datetime.now()+timedelta(days=5)))
    db.add(Task(title="Prior Art Search", status="done", priority="medium", project_id=p_patent.id, area="writing", completed_at=datetime.now()-timedelta(days=2)))

    # --- 3. HISTORY (General Stats) ---
    # Random unlinked tasks for the chart
    areas = ["research", "trading", "writing", "personal"]
    past_tasks = [
        "Weekly review", "Gym session", "Tax filing", "Clean desk", "Server maintenance",
        "Read newsletter", "Update dependencies", "Code review", "Team meeting"
    ]
    
    end_date = datetime.now()
    for _ in range(25):
        title = random.choice(past_tasks)
        days_ago = random.randint(1, 14)
        done_date = end_date - timedelta(days=days_ago)
        
        db.add(Task(
            title=title,
            status="done",
            area=random.choice(areas),
            priority="low",
            created_at=done_date - timedelta(days=1),
            completed_at=done_date
        ))

    db.commit()
    db.close()
    print("Database seeded with Projects & Tasks.")

if __name__ == "__main__":
    seed()

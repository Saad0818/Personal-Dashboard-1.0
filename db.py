# db.py
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime,
    Float, Text, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

import os

# --- DB CONFIGURATION ---
# Check for environment variable (e.g. from Railway/Heroku/Streamlit Cloud)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Fix for some cloud providers that use "postgres://" instead of "postgresql://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # PRODUCTION (PostgreSQL)
    engine = create_engine(DATABASE_URL, echo=False, future=True)
else:
    # LOCAL DEVELOPMENT (SQLite)
    DB_URL = "sqlite:///data.db"
    engine = create_engine(DB_URL, echo=False, future=True, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    status = Column(String, default="active")  # active / on_hold / done
    area = Column(String, default="trading")   # trading / research / writing / personal
    created_at = Column(DateTime, default=datetime.utcnow)
    target_date = Column(DateTime, nullable=True)

    systems = relationship("System", back_populates="project")
    tasks = relationship("Task", back_populates="project")


class System(Base):
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    status = Column(String, default="rd")  # idea / rd / paper / live / deprecated
    system_type = Column(String, default="trend")  # trend / mean_rev / etc.
    repo_url = Column(String)
    platform = Column(String, default="QuantConnect")
    created_at = Column(DateTime, default=datetime.utcnow)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="systems")

    experiments = relationship("Experiment", back_populates="system")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "RSI14_SL2_TP4"
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=False)

    run_date = Column(DateTime, default=datetime.utcnow)
    period = Column(String)  # "2010-2024", "2018", etc.
    qc_url = Column(String)  # link to QuantConnect backtest
    code_version = Column(String)  # e.g. git commit hash

    sharpe = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    cagr = Column(Float, nullable=True)
    win_rate = Column(Float, nullable=True)
    rr_ratio = Column(Float, nullable=True)  # risk:reward
    trades = Column(Integer, nullable=True)

    notes = Column(Text)
    decision = Column(String, default="undecided")  # accept / reject / investigate

    system = relationship("System", back_populates="experiments")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, default="next")   # inbox / next / doing / done
    area = Column(String, default="trading") # trading / research / writing / personal
    priority = Column(String, default="medium")  # low / medium / high

    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    project = relationship("Project", back_populates="tasks")

    system_id = Column(Integer, ForeignKey("systems.id"), nullable=True)
    system = relationship("System")

    is_today_focus = Column(Boolean, default=False)
    is_milestone = Column(Boolean, default=False)
    is_active_milestone = Column(Boolean, default=False)


def init_db():
    Base.metadata.create_all(bind=engine)
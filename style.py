CSS = """
<style>
/* --- Global dark theme --- */
[data-testid="stAppViewContainer"] {
    background: #111118;
    color: #d1d5db;
}

[data-testid="stHeader"] {
    background: transparent;
}

/* --- Sidebar --- */
[data-testid="stSidebar"] {
    background: #16161e;
    border-right: 1px solid #222230;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: #b0b8c8;
}

/* --- Title styling --- */
.game-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 700;
    color: #f0f0f5;
    margin-bottom: 0.3rem;
    letter-spacing: 4px;
}

.game-subtitle {
    text-align: center;
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}

/* --- Score cards --- */
.score-card {
    background: #1e1e2a;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 20px 14px;
    text-align: center;
    color: #e5e7eb;
    margin: 10px 0;
    transition: border-color 0.2s ease;
}

.score-card:hover {
    border-color: #4a9eff;
}

.score-card .score-value {
    font-size: 3rem;
    font-weight: 700;
    margin: 0;
    line-height: 1;
    color: #4a9eff;
}

.score-card .score-label {
    font-size: 0.8rem;
    margin: 8px 0 0 0;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #6b7280;
}

.score-card-p2 .score-value {
    color: #f472b6;
}

.score-card-p2:hover {
    border-color: #f472b6;
}

/* --- Status indicator --- */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 5px 14px;
    border-radius: 16px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 1px;
}

.status-live {
    background: rgba(74, 222, 128, 0.1);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.25);
}

.status-live::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

.status-idle {
    background: rgba(161, 161, 170, 0.1);
    color: #a1a1aa;
    border: 1px solid rgba(161, 161, 170, 0.2);
}

.status-idle::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #a1a1aa;
    border-radius: 50%;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* --- Info card --- */
.info-card {
    background: #1a1a24;
    border: 1px solid #262633;
    border-radius: 10px;
    padding: 16px;
    color: #9ca3af;
    margin: 10px 0;
    line-height: 1.8;
    font-size: 0.85rem;
}

.info-card b {
    color: #d1d5db;
}

/* --- Sidebar section headers --- */
.sidebar-header {
    font-size: 1rem;
    font-weight: 600;
    color: #d1d5db;
    margin: 18px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #262633;
}

/* --- Button styling --- */
[data-testid="stSidebar"] .stButton > button {
    background: #1e1e2a;
    color: #d1d5db;
    border: 1px solid #333345;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #262633;
    border-color: #4a9eff;
    color: #f0f0f5;
}

/* --- Video container --- */
.video-container {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #222230;
}

/* --- Footer --- */
.footer {
    text-align: center;
    color: #4b5563;
    font-size: 0.75rem;
    margin-top: 2rem;
    padding: 14px 0;
    border-top: 1px solid #1f1f2e;
}

/* --- Hide default Streamlit elements --- */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
"""

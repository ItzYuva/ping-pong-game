import os
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode

from game_processor import PongVideoProcessor
from style import CSS

# TURN credentials from Metered — set as env vars on Render
TURN_USERNAME = os.environ.get("TURN_USERNAME", "")
TURN_PASSWORD = os.environ.get("TURN_PASSWORD", "")

def get_rtc_configuration():
    ice_servers = [{"urls": ["stun:stun.relay.metered.ca:80"]}]
    if TURN_USERNAME and TURN_PASSWORD:
        for url in [
            "turn:a.relay.metered.ca:80",
            "turn:a.relay.metered.ca:80?transport=tcp",
            "turn:a.relay.metered.ca:443",
            "turns:a.relay.metered.ca:443?transport=tcp",
        ]:
            ice_servers.append({
                "urls": url,
                "username": TURN_USERNAME,
                "credential": TURN_PASSWORD,
            })
    return {"iceServers": ice_servers}

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hand Pong | Real Time Hand Tracking Game",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS
st.markdown(CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div class='sidebar-header'>Game Controls</div>",
        unsafe_allow_html=True,
    )

    game_active = st.toggle("Start Game", value=False, key="game_toggle")

    if game_active:
        st.markdown(
            "<span class='status-badge status-live'>LIVE</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='status-badge status-idle'>IDLE</span>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    speed_labels = {"Slow": 8, "Medium": 12, "Fast": 15, "Insane": 22}
    speed_choice = st.select_slider(
        "Ball Speed",
        options=list(speed_labels.keys()),
        value="Medium",
    )
    ball_speed = speed_labels[speed_choice]

    restart = st.button("Restart Game", use_container_width=True)

    st.markdown("---")

    st.markdown(
        "<div class='sidebar-header'>How to Play</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class='info-card'>
            <b>1.</b> Allow camera access when prompted<br>
            <b>2.</b> Toggle <b>Start Game</b> in the sidebar<br>
            <b>3.</b> Show <b>both hands</b> to the camera<br>
            <b>4.</b> Left hand &rarr; left paddle<br>
            <b>5.</b> Right hand &rarr; right paddle<br>
            <b>6.</b> Keep the ball in play to score!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='footer'>
            Built with Streamlit &amp; OpenCV<br>
            Powered by MediaPipe Hand Tracking
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Main Area ────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='game-title'>HAND PONG</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div class='game-subtitle'>Real time hand tracking ping pong — no controllers needed</div>",
    unsafe_allow_html=True,
)

# Score cards + video layout
col_score_l, col_video, col_score_r = st.columns([1, 3, 1])

score_left_ph = col_score_l.empty()
score_right_ph = col_score_r.empty()

# Default scores
score_left_ph.markdown(
    "<div class='score-card'>"
    "<div class='score-value'>0</div>"
    "<div class='score-label'>Player 1</div>"
    "</div>",
    unsafe_allow_html=True,
)
score_right_ph.markdown(
    "<div class='score-card score-card-p2'>"
    "<div class='score-value'>0</div>"
    "<div class='score-label'>Player 2</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ── WebRTC Streamer ──────────────────────────────────────────────────────────
with col_video:
    st.markdown("<div class='video-container'>", unsafe_allow_html=True)
    ctx = webrtc_streamer(
        key="pong-game",
        mode=WebRtcMode.SENDRECV,
        video_processor_factory=PongVideoProcessor,
        media_stream_constraints={
            "video": {"width": {"ideal": 1280}, "height": {"ideal": 720}},
            "audio": False,
        },
        async_processing=True,
        rtc_configuration=get_rtc_configuration(),
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Push UI values into the video processor ──────────────────────────────────
if ctx.video_processor:
    ctx.video_processor.game_active = game_active
    ctx.video_processor.ball_speed = ball_speed

    if restart:
        ctx.video_processor.restart_flag = True

    s = ctx.video_processor.score
    score_left_ph.markdown(
        f"<div class='score-card'>"
        f"<div class='score-value'>{s[0]}</div>"
        f"<div class='score-label'>Player 1</div>"
        f"</div>",
        unsafe_allow_html=True,
    )
    score_right_ph.markdown(
        f"<div class='score-card score-card-p2'>"
        f"<div class='score-value'>{s[1]}</div>"
        f"<div class='score-label'>Player 2</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

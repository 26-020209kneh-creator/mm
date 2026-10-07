import streamlit as st
from st_keyup import st_keyup

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="마지막 교실",
    page_icon="🏫",
    layout="centered"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at center,
            #303030 0%,
            #171717 55%,
            #080808 100%
        );

    color: white;
}

.block-container {
    max-width: 850px;
    padding-top: 1.5rem;
}

/* 제목 */

.game-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #e8d7a5;
    text-shadow:
        3px 3px 0 #000,
        0 0 15px rgba(255,220,120,0.2);

    margin-bottom: 5px;
}

.game-subtitle {
    text-align: center;
    color: #999;
    margin-bottom: 20px;
}

/* 대화창 */

.dialogue {
    background: #111;
    border: 3px solid #666;
    border-radius: 6px;
    padding: 15px;
    margin-top: 15px;
    margin-bottom: 15px;

    box-shadow:
        0 5px 15px rgba(0,0,0,0.5);
}

.dialogue-name {
    color: #e6c65c;
    font-weight: bold;
    margin-bottom: 7px;
}

/* 상태창 */

.status {
    display: flex;
    justify-content: space-between;

    background: #111;
    border: 2px solid #555;
    border-radius: 6px;

    padding: 10px 15px;
    margin-bottom: 12px;
}

/* 맵 */

.map {
    display: flex;
    flex-direction: column;
    align-items: center;

    background: #0b0b0b;

    border: 8px solid #292929;
    border-radius: 5px;

    padding: 10px;

    box-shadow:
        inset 0 0 30px #000,
        0 10px 25px rgba(0,0,0,0.7);
}

.row {
    display: flex;
}

.tile {
    width: 46px;
    height: 46px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 27px;

    box-sizing: border-box;
}

/* 바닥 */

.floor {
    background:
        linear-gradient(
            135deg,
            #62564b 25%,
            #584d43 25%,
            #584d43 50%,
            #62564b 50%,
            #62564b 75%,
            #584d43 75%
        );

    background-size: 18px 18px;

    border: 1px solid #463d35;
}

/* 벽 */

.wall {
    background:
        linear-gradient(
            135deg,
            #252525 25%,
            #303030 25%,
            #303030 50%,
            #252525 50%,
            #252525 75%,
            #303030 75%
        );

    background-size: 12px 12px;

    border: 2px solid #111;
}

/* 버튼 */

.stButton > button {
    min-height: 45px;

    background: #242424;
    color: white;

    border: 2px solid #555;
    border-radius: 5px;

    font-weight: bold;
}

.stButton > button:hover {
    background: #383838;
    border-color: #d6b75b;
}

/* 성공 */

.success-box {
    text-align: center;

    background: #102b19;
    border: 3px solid #4ca866;

    border-radius: 8px;

    padding: 30px;

    box-shadow: 0 0 30px rgba(50,200,100,0.15);
}

/* 힌트 */

.hint {
    background: #242217;

    border: 2px solid #756b37;

    border-radius: 5px;

    padding: 12px;

    color: #e8df9d;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# 맵 데이터
# =========================================================

# # = 벽
# . = 바닥
# P = 플레이어 시작 위치
# B = 상자
# K = 열쇠
# D = 문

DEFAULT_MAP = [
    "##########",
    "#P..#..KD#",
    "#.#.#.#..#",
    "#.B...#..#",
    "#.###....#",
    "#.....##.#",
    "##########",
]


# =========================================================
# 게임 초기화
# =========================================================

def initialize_game():

    st.session_state.game_map = [
        list(row)
        for row in DEFAULT_MAP
    ]

    st.session_state.player_x = 1
    st.session_state.player_y = 1

    st.session_state.has_key = False

    st.session_state.moves = 0

    st.session_state.message = (
        "낯선 교실이다. "
        "어딘가에 있는 열쇠를 찾아 문으로 탈출해야 한다."
    )

    st.session_state.game_clear = False


if "game_map" not in st.session_state:
    initialize_game()


# =========================================================
# 이동 함수
# =========================================================

def move_player(dx, dy):

    if st.session_state.game_clear:
        return

    x = st.session_state.player_x
    y = st.session_state.player_y

    new_x = x + dx
    new_y = y + dy

    game_map = st.session_state.game_map

    # 맵 범위 확인

    if new_y < 0 or new_y >= len(game_map):
        return

    if new_x < 0 or new_x >= len(game_map[0]):
        return

    target = game_map[new_y][new_x]

    # -----------------------------------------------------
    # 벽
    # -----------------------------------------------------

    if target == "#":

        st.session_state.message = (
            "벽이다. 더 이상 갈 수 없다."
        )

        return

    # -----------------------------------------------------
    # 상자
    # -----------------------------------------------------

    if target == "B":

        box_x = new_x + dx
        box_y = new_y + dy

        # 상자 뒤가 맵 밖

        if (
            box_y < 0
            or box_y >= len(game_map)
            or box_x < 0
            or box_x >= len(game_map[0])
        ):
            st.session_state.message = (
                "상자를 더 이상 밀 수 없다."
            )

            return

        behind = game_map[box_y][box_x]

        # 상자를 밀 수 있는 경우

        if behind in [".", "K"]:

            game_map[box_y][box_x] = "B"

            game_map[new_y][new_x] = "."

            st.session_state.player_x = new_x
            st.session_state.player_y = new_y

            st.session_state.moves += 1

            st.session_state.message = (
                "상자를 밀었다."
            )

            return

        else:

            st.session_state.message = (
                "상자가 벽에 막혀 있다."
            )

            return

    # -----------------------------------------------------
    # 열쇠
    # -----------------------------------------------------

    if target == "K":

        st.session_state.player_x = new_x
        st.session_state.player_y = new_y

        st.session_state.has_key = True

        st.session_state.moves += 1

        st.session_state.game_map[new_y][new_x] = "."

        st.session_state.message = (
            "🗝️ 열쇠를 발견했다! "
            "이제 문으로 돌아가자."
        )

        return

    # -----------------------------------------------------
    # 문
    # -----------------------------------------------------

    if target == "D":

        if st.session_state.has_key:

            st.session_state.player_x = new_x
            st.session_state.player_y = new_y

            st.session_state.game_clear = True

            st.session_state.message = (
                "문이 열렸다!"
            )

            return

        else:

            st.session_state.message = (
                "문이 잠겨 있다. "
                "열쇠가 필요하다."
            )

            return

    # -----------------------------------------------------
    # 일반 바닥
    # -----------------------------------------------------

    if target == ".":

        st.session_state.player_x = new_x
        st.session_state.player_y = new_y

        st.session_state.moves += 1

        st.session_state.message = (
            "조용하다..."
        )


# =========================================================
# 시작 화면
# =========================================================

if "started" not in st.session_state:

    st.session_state.started = False


if not st.session_state.started:

    st.markdown(
        '<div class="game-title">🏫 마지막 교실</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="game-subtitle">'
        '쯔꾸르풍 미니 퍼즐 어드벤처'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="dialogue">

    <div class="dialogue-name">
    ??? 
    </div>

    눈을 떠보니 아무도 없는 교실이다.

    <br><br>

    교실의 문은 잠겨 있다.

    <br><br>

    누군가 칠판에 글을 남겨 놓았다.

    <br><br>

    <b>
    "열쇠를 찾고 싶다면 상자를 움직여라."
    </b>

    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if st.button(
        "▶ 게임 시작",
        use_container_width=True
    ):

        st.session_state.started = True

        initialize_game()

        st.rerun()

    st.stop()


# =========================================================
# 엔딩
# =========================================================

if st.session_state.game_clear:

    st.markdown("""
    <div class="success-box">

    <h1>🎉 탈출 성공!</h1>

    <p>
    철컥...
    </p>

    <p>
    잠겨 있던 교실 문이 열렸다.
    </p>

    <p>
    복도 너머로 희미한 아침 햇빛이 들어온다.
    </p>

    <br>

    <h2>THE END</h2>

    </div>
    """, unsafe_allow_html=True)

    st.write("")

    st.write(
        f"🚶 이동 횟수: **{st.session_state.moves}회**"
    )

    st.write("")

    if st.button(
        "🔄 다시 플레이",
        use_container_width=True
    ):

        initialize_game()

        st.rerun()

    st.stop()


# =========================================================
# 게임 제목
# =========================================================

st.markdown(
    '<div class="game-title">🏫 마지막 교실</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="game-subtitle">'
    'Chapter 1 — 잠긴 교실'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 상태
# =========================================================

key_status = (
    "🗝️ 열쇠 있음"
    if st.session_state.has_key
    else "🔒 열쇠 없음"
)

st.markdown(
    f"""
    <div class="status">
        <span>🎒 {key_status}</span>
        <span>👣 이동 {st.session_state.moves}</span>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 맵 출력
# =========================================================

st.markdown(
    '<div class="map">',
    unsafe_allow_html=True
)

for y, row in enumerate(st.session_state.game_map):

    st.markdown(
        '<div class="row">',
        unsafe_allow_html=True
    )

    row_html = ""

    for x, tile in enumerate(row):

        # 플레이어
        if (
            x == st.session_state.player_x
            and y == st.session_state.player_y
        ):

            row_html += (
                '<div class="tile floor">🧍</div>'
            )

        elif tile == "#":

            row_html += (
                '<div class="tile wall">⬛</div>'
            )

        elif tile == "B":

            row_html += (
                '<div class="tile floor">📦</div>'
            )

        elif tile == "K":

            row_html += (
                '<div class="tile floor">🗝️</div>'
            )

        elif tile == "D":

            row_html += (
                '<div class="tile floor">🚪</div>'
            )

        else:

            row_html += (
                '<div class="tile floor"></div>'
            )

    st.markdown(
        row_html,
        unsafe_allow_html=True
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# 대화창
# =========================================================

st.markdown(
    f"""
    <div class="dialogue">

        <div class="dialogue-name">
        🧍 나
        </div>

        {st.session_state.message}

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# 키보드 입력
# =========================================================

st.subheader("🎮 이동")

st.write(
    "아래 입력창에 **W / A / S / D** 또는 "
    "방향키 대신 W,A,S,D를 입력해 캐릭터를 움직일 수 있습니다."
)

keyboard = st_keyup(
    "W A S D",
    key="keyboard",
    placeholder="여기를 클릭하고 W / A / S / D 입력",
    debounce=0
)


# 마지막 입력 문자 확인

if keyboard:

    last_key = keyboard[-1].lower()

    if last_key == "w":

        move_player(0, -1)

    elif last_key == "s":

        move_player(0, 1)

    elif last_key == "a":

        move_player(-1, 0)

    elif last_key == "d":

        move_player(1, 0)


# =========================================================
# 화면 버튼
# =========================================================

st.write("또는 버튼으로 이동하세요.")

col1, col2, col3 = st.columns(3)

with col1:

    if st.button(
        "⬅️",
        use_container_width=True
    ):

        move_player(-1, 0)

        st.rerun()


with col2:

    if st.button(
        "⬆️",
        use_container_width=True
    ):

        move_player(0, -1)

        st.rerun()

    if st.button(
        "⬇️",
        use_container_width=True
    ):

        move_player(0, 1)

        st.rerun()


with col3:

    if st.button(
        "➡️",
        use_container_width=True
    ):

        move_player(1, 0)

        st.rerun()


# =========================================================
# 힌트
# =========================================================

st.divider()

with st.expander("💡 힌트"):

    st.write("""
    **목표**

    1. 캐릭터를 움직인다.
    2. 📦 상자를 밀어서 길을 만든다.
    3. 🗝️ 열쇠를 얻는다.
    4. 🚪 문으로 이동한다.
    5. 탈출한다.

    **조작**

    - W : 위
    - A : 왼쪽
    - S : 아래
    - D : 오른쪽

    모바일에서는 화면의 방향 버튼을 사용하면 됩니다.
    """)


# =========================================================
# 다시 시작
# =========================================================

if st.button(
    "🔄 게임 초기화",
    use_container_width=True
):

    initialize_game()

    st.rerun()

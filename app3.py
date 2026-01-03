import streamlit as st
import pandas as pd
import random

# --- 1. 참가자 설정 ---
PARTICIPANTS = ["단비", "창우", "주희", "온유", "유민", "주형", "예슬", "도현", "성현", "신영", "준일", "주황", "진수", "영찬", "다연", "예원", "주현", "총명", "연제", "윤아", "마리아", "규진", "주한", "건양"]

# --- 2. 핑크 몽글몽글 디자인 (CSS) ---
st.set_page_config(page_title="💖 X-Signal", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Pen+Script&display=swap');
    
    .stApp { background: linear-gradient(180deg, #fff5f7 0%, #ffe4e8 100%); }
    
    /* 채팅 레이아웃 및 줄바꿈 버그 수정 */
    .chat-row { display: flex; margin-bottom: 15px; align-items: flex-start; width: 100%; }
    .row-me { justify-content: flex-end; }
    .row-other { justify-content: flex-start; }
    
    .bubble {
        padding: 12px 18px; border-radius: 20px; 
        font-size: 15px; line-height: 1.5; 
        word-break: break-all; /* 긴 문장 자동 줄바꿈 */
        white-space: pre-wrap; /* 엔터 인식 */
        box-shadow: 2px 2px 8px rgba(255, 182, 197, 0.2);
    }
    .me { background-color: #ffb7c5; color: white; border-top-right-radius: 2px; }
    .other { background-color: white; color: #444; border-top-left-radius: 2px; border: 1px solid #ffe4e8; }
    
    .avatar { width: 45px; height: 45px; border-radius: 50%; border: 2px solid #fff; object-fit: cover; }
    .nick { font-size: 12px; color: #ff8fa3; margin-bottom: 4px; font-weight: bold; }
    
    /* 탭 디자인 커스텀 */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; color: #ff6b81; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 초기화 ---
if 'db' not in st.session_state:
    targets = PARTICIPANTS[:]
    while True:
        random.shuffle(targets)
        if all(PARTICIPANTS[i] != targets[i] for i in range(len(PARTICIPANTS))): break
    
    db = {}
    for i, name in enumerate(PARTICIPANTS):
        target_name = targets[i]
        db[name] = {
            "nickname": f"{target_name}또", 
            "avatar": f"https://api.dicebear.com/7.x/adventurer/svg?seed={random.random()}", # 랜덤 아바타
            "target": target_name,
            "status": "당신의 X는 당신을 기다리고 있습니다",
            "x_chat": [] 
        }
    st.session_state.db = db
    st.session_state.global_chat = []

# --- 4. 로그인 ---
if 'user' not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #ff6b81;'>💗 X-Signal</h1>", unsafe_allow_html=True)
    name_select = st.selectbox("당신의 이름을 선택하세요", ["선택하세요", "운영자"] + PARTICIPANTS)
    if name_select == "운영자":
        pw = st.text_input("비밀번호", type="password")
        if st.button("접속"):
            if pw == "1234": st.session_state.user = "운영자"; st.rerun()
    elif name_select != "선택하세요":
        if st.button("입장하기"): st.session_state.user = name_select; st.rerun()

# --- 5. 메인 화면 ---
else:
    user = st.session_state.user
    if user == "운영자":
        st.title("🕶️ 관리자 모드")
        st.table(pd.DataFrame([{"이름": k, "마니또": v['target']} for k, v in st.session_state.db.items()]))
        if st.button("초기화 (주의!)"): del st.session_state.db; st.rerun()
        if st.button("로그아웃"): del st.session_state.user; st.rerun()
    else:
        my = st.session_state.db[user]
        tab1, tab2, tab3 = st.tabs(["💬 핑크톡", "💌 X-대화", "🎯 추리"])

        # [탭 1: 단체톡]
        with tab1:
            st.markdown("<h3 style='color: #ff8fa3;'>모두와 소통하는 공간</h3>", unsafe_allow_html=True)
            
            # 메시지 입력 및 이미지 업로드
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1: msg = st.text_input("당신의 마음을 전하세요...", key="input_g")
                with col2: img = st.file_uploader("🖼️", type=['jpg','png'], label_visibility="collapsed")
                
                if st.button("전송"):
                    if msg or img:
                        st.session_state.global_chat.append({
                            "name": my['nickname'], "avatar": my['avatar'], "msg": msg, "img": img
                        })
                        st.rerun()

            # 채팅 렌더링
            for c in reversed(st.session_state.global_chat):
                is_me = (c['name'] == my['nickname'])
                align = "row-me" if is_me else "row-other"
                b_type = "me" if is_me else "other"
                
                avatar_tag = f'<img src="{c["avatar"]}" class="avatar">'
                nick_tag = f'<div class="nick" style="text-align: {"right" if is_me else "left"};">{c["name"]}</div>'
                bubble_tag = f'<div class="bubble {b_type}">{c["msg"]}</div>' if c['msg'] else ""
                
                # 핵심 수정: unsafe_allow_html=True 사용
                st.markdown(f"""
                    <div class="chat-row {align}">
                        {'' if is_me else avatar_tag}
                        <div style="max-width: 70%; margin: 0 5px;">
                            {nick_tag}
                            {bubble_tag}
                        </div>
                        {avatar_tag if is_me else ''}
                    </div>
                    """, unsafe_allow_html=True)
                if c['img']: st.image(c['img'], width=250)

        # [탭 2: X-대화 (1:1)]
        with tab2:
            st.markdown(f"<h3 style='color: #ff8fa3;'>내 X({my['target']})와의 대화</h3>", unsafe_allow_html=True)
            target_db = st.session_state.db[my['target']]
            
            x_msg = st.text_area("X에게 보낼 메시지 (답장을 기다려보세요)")
            if st.button("X에게 전송"):
                if x_msg:
                    my['x_chat'].append({"role": "sent", "msg": x_msg}) # 내가 보낸 기록
                    target_db['x_chat'].append({"role": "received", "sender": my['nickname'], "msg": x_msg}) # 상대가 받은 기록
                    st.success("X에게 진심을 보냈습니다.")
                    st.rerun()
            
            st.divider()
            for chat in reversed(my['x_chat']):
                if chat.get("role") == "received":
                    st.markdown(f"""<div class="chat-row row-other"><div class="bubble other"><b>{chat['sender']}님으로부터:</b><br>{chat['msg']}</div></div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="chat-row row-me"><div class="bubble me"><b>나의 메시지:</b><br>{chat['msg']}</div></div>""", unsafe_allow_html=True)

        # [탭 3: 최종선택]
        with tab3:
            st.markdown(f"<h2 style='text-align: center;'>\"{user}님의 X는 당신을 선택했습니다\"</h2>", unsafe_allow_html=True)
            guess = st.selectbox("당신의 X는 누구라고 생각하시나요?", ["선택하세요"] + PARTICIPANTS)
            if st.button("최종 확인"):
                real_x = [k for k, v in st.session_state.db.items() if v['target'] == user][0]
                if guess == real_x:
                    st.balloons()
                    st.markdown("<h2 style='text-align: center; color: #ff6b81;'>마음이 통했습니다! 💖</h2>", unsafe_allow_html=True)
                else:
                    st.error("아쉽지만 당신의 X가 아닌 것 같아요. 🤫")

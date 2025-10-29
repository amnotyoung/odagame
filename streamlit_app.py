#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOICA 소장 시뮬레이터 - Streamlit Web Version
모바일 친화적 웹 인터페이스
"""

import streamlit as st
import json
import sys
import random
from typing import Dict, List, Optional

# Gemini API import (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import game classes from original game
# We'll need to refactor the classes to work with Streamlit's state management
from koica_game import GameState, KOICAGame

# Page configuration
st.set_page_config(
    page_title="KOICA 소장 시뮬레이터",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization
st.markdown("""
<style>
    /* 모바일 최적화 스타일 */
    .main {
        padding: 1rem;
    }

    /* 버튼 스타일 */
    .stButton > button {
        width: 100%;
        height: auto;
        white-space: normal;
        text-align: left;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 1rem;
        line-height: 1.4;
    }

    /* 스탯 표시 */
    .stat-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }

    /* 제목 스타일 */
    h1 {
        font-size: 1.8rem;
        text-align: center;
        margin-bottom: 1rem;
    }

    h2 {
        font-size: 1.4rem;
        margin-top: 1rem;
    }

    h3 {
        font-size: 1.2rem;
    }

    /* 시나리오 텍스트 */
    .scenario-text {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        line-height: 1.6;
    }

    /* 경고 메시지 */
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
    }

    /* 프로그레스 바 라벨 */
    .stProgress > div > div > div > div {
        font-size: 0.9rem;
    }

    /* 모바일에서 사이드바 숨기기 */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }

        h1 {
            font-size: 1.5rem;
        }

        .stButton > button {
            font-size: 0.95rem;
            padding: 0.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """세션 상태 초기화"""
    if 'game' not in st.session_state:
        st.session_state.game = None
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = 'welcome'
    if 'choice_made' not in st.session_state:
        st.session_state.choice_made = False
    if 'result_message' not in st.session_state:
        st.session_state.result_message = ""
    if 'ai_mode' not in st.session_state:
        st.session_state.ai_mode = False
    if 'lifestyle_step' not in st.session_state:
        st.session_state.lifestyle_step = 0


def display_stats(state: GameState):
    """스탯 표시"""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 핵심 지표")

        # 평판
        rep_color = "normal" if state.reputation > 30 else "inverse"
        st.markdown(f"**평판**: {state.reputation}/100")
        st.progress(state.reputation / 100)

        # 예산 집행률
        budget_color = "normal"
        st.markdown(f"**예산 집행률**: {state.budget_execution_rate}/100")
        st.progress(state.budget_execution_rate / 100)

        # 직원 만족도
        morale_color = "normal" if state.staff_morale > 30 else "inverse"
        st.markdown(f"**직원 만족도**: {state.staff_morale}/100")
        st.progress(state.staff_morale / 100)

        # 프로젝트 성공도
        st.markdown(f"**프로젝트 성공도**: {state.project_success}/100")
        st.progress(state.project_success / 100)

    with col2:
        st.markdown("### 🏥 개인 상태")

        # 스트레스
        stress_color = "inverse" if state.stress > 70 else "normal"
        st.markdown(f"**스트레스**: {state.stress}/100")
        st.progress(state.stress / 100)

        # 웰빙
        wellbeing_color = "normal" if state.wellbeing > 30 else "inverse"
        st.markdown(f"**웰빙**: {state.wellbeing}/100")
        st.progress(state.wellbeing / 100)

        # 시간
        st.markdown(f"**📅 {state.year}년차 {state.period}기**")

        # 경고 표시
        warnings = []
        if state.reputation <= 20:
            warnings.append("⚠️ 평판 위기!")
        if state.staff_morale <= 20:
            warnings.append("⚠️ 직원 사기 저하!")
        if state.stress >= 80:
            warnings.append("⚠️ 스트레스 과다!")
        if state.wellbeing <= 20:
            warnings.append("⚠️ 건강 위험!")

        if warnings:
            for warning in warnings:
                st.error(warning)


def welcome_screen():
    """환영 화면"""
    st.title("🌍 KOICA 해외사무소장 시뮬레이터")

    st.markdown("""
    <div class="scenario-text">
    <h3>환영합니다!</h3>

    당신은 <b>KOICA(한국국제협력단) 해외사무소장</b>으로 새로 부임했습니다.

    🌏 <b>KOICA는 전 세계 48개국에 해외사무소를 운영</b>하며,
    대한민국 무상원조사업을 현장에서 직접 실행합니다.

    📊 <b>당신의 조직 (약 37명)</b>
    - 사무소장: 1명 (당신)
    - 부소장: 4명 (분야별 책임자)
    - 코디네이터: 다수
    - YP(영프로페셔널): 7명
    - 현지 직원: 17명

    🎯 <b>임기: 2년 (12 분기)</b>

    당신의 선택이 프로젝트의 성공, 팀의 사기, 그리고 국제 협력의 미래를 만들어갑니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 게임 모드 선택
    st.subheader("🎮 게임 모드 선택")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📖 클래식 모드\n\n사전 제작된 시나리오", key="classic_mode", use_container_width=True):
            st.session_state.ai_mode = False
            st.session_state.current_screen = 'game_intro'
            st.rerun()

    with col2:
        if GEMINI_AVAILABLE:
            if st.button("🤖 AI 모드\n\nGemini AI 동적 시나리오", key="ai_mode", use_container_width=True):
                st.session_state.ai_mode = True
                st.session_state.current_screen = 'ai_setup'
                st.rerun()
        else:
            st.button("🤖 AI 모드\n\n(google-generativeai 설치 필요)", key="ai_mode_disabled", disabled=True, use_container_width=True)


def ai_setup_screen():
    """AI 모드 설정 화면"""
    st.title("🤖 AI 모드 설정")

    st.markdown("""
    AI 모드를 사용하려면 Google Gemini API 키가 필요합니다.

    API 키 발급: https://makersuite.google.com/app/apikey
    """)

    api_key = st.text_input("Gemini API Key", type="password", key="api_key_input")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("시작하기", use_container_width=True):
            if api_key:
                st.session_state.api_key = api_key
                st.session_state.current_screen = 'game_intro'
                st.rerun()
            else:
                st.error("API 키를 입력해주세요.")

    with col2:
        if st.button("뒤로 가기", use_container_width=True):
            st.session_state.current_screen = 'welcome'
            st.rerun()


def game_intro_screen():
    """게임 시작 안내"""
    st.title("🌍 KOICA 소장 시뮬레이터")

    st.markdown("""
    <div class="scenario-text">
    <h3>⚠️ 게임 오버 조건</h3>

    다음 조건 중 하나라도 해당되면 게임이 즉시 종료됩니다:

    - 평판이 0 이하 → 평판 실추로 본부 소환
    - 직원 만족도가 0 이하 → 직원 반발로 사임
    - 스트레스가 100 이상 → 번아웃으로 긴급 귀국
    - 웰빙이 0 이하 → 건강 위기로 의료 후송

    💡 위험한 선택을 할 때는 경고가 표시됩니다.
    </div>
    """, unsafe_allow_html=True)

    if st.button("게임 시작하기", use_container_width=True):
        # 게임 인스턴스 생성
        api_key = st.session_state.get('api_key', None) if st.session_state.ai_mode else None
        st.session_state.game = KOICAGame(ai_mode=st.session_state.ai_mode, api_key=api_key)
        st.session_state.current_screen = 'lifestyle_setup'
        st.session_state.lifestyle_step = 0
        st.rerun()


def lifestyle_setup_screen():
    """초기 생활 설정 화면"""
    st.title("🏠 해외 생활 준비하기")

    game = st.session_state.game
    step = st.session_state.lifestyle_step

    if step == 0:
        # 자동차 선택
        st.markdown("""
        <div class="scenario-text">
        <h3>🚗 자동차는 어떻게 하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("1. 한국에서 자동차를 가져간다\n익숙하지만 비용과 수리가 문제", key="car_1", use_container_width=True):
            game.state.car_choice = "bring_from_korea"
            game.state.update_stats({"stress": -5, "wellbeing": 5})
            st.session_state.lifestyle_step = 1
            st.rerun()

        if st.button("2. 현지에서 중고차를 구입한다\n저렴하지만 품질이 불확실", key="car_2", use_container_width=True):
            game.state.car_choice = "buy_local"
            game.state.update_stats({"stress": 5, "wellbeing": -3})
            st.session_state.lifestyle_step = 1
            st.rerun()

        if st.button("3. 자동차 없이 택시와 대중교통 이용\n자유롭지만 불편", key="car_3", use_container_width=True):
            game.state.car_choice = "no_car"
            game.state.update_stats({"stress": 8, "wellbeing": -5})
            st.session_state.lifestyle_step = 1
            st.rerun()

    elif step == 1:
        # 주거지 선택
        st.markdown("""
        <div class="scenario-text">
        <h3>🏠 주거지는 어떤 곳을 구하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("1. 넓은 집\n여유 공간, 하지만 먼 거리", key="house_1", use_container_width=True):
            game.state.housing_choice = "spacious"
            game.state.update_stats({"stress": -3, "wellbeing": 8})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("2. 좋은 집\n새 건물, 고급 시설, 하지만 비싼 임대료", key="house_2", use_container_width=True):
            game.state.housing_choice = "nice"
            game.state.update_stats({"stress": -5, "wellbeing": 10, "budget": -5})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("3. 사무소 가까운 집\n출퇴근 편리, 하지만 좁고 오래됨", key="house_3", use_container_width=True):
            game.state.housing_choice = "near_office"
            game.state.update_stats({"stress": -10, "wellbeing": -5})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("4. 치안 좋은 동네 집\n안전, 하지만 시내에서 멀고 심심함", key="house_4", use_container_width=True):
            game.state.housing_choice = "secure"
            game.state.update_stats({"stress": -5, "wellbeing": 3})
            st.session_state.lifestyle_step = 2
            st.rerun()

    elif step == 2:
        # 여가 생활 선택
        st.markdown("""
        <div class="scenario-text">
        <h3>🎮 여가 생활은 어떻게 보내시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("1. 독서\n조용하고 지적인 시간", key="leisure_1", use_container_width=True):
            game.state.leisure_choice = "reading"
            game.state.update_stats({"stress": -8, "wellbeing": 5})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("2. 운동\n건강 관리와 스트레스 해소", key="leisure_2", use_container_width=True):
            game.state.leisure_choice = "exercise"
            game.state.update_stats({"stress": -10, "wellbeing": 15})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("3. 음주\n직원들과 친목, 하지만 건강 염려", key="leisure_3", use_container_width=True):
            game.state.leisure_choice = "drinking"
            game.state.update_stats({"stress": -5, "staff_morale": 8, "wellbeing": -8})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("4. 작문/블로그\n경험 기록, 창의적 표현", key="leisure_4", use_container_width=True):
            game.state.leisure_choice = "writing"
            game.state.update_stats({"stress": -7, "wellbeing": 8})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("5. 집에서 뒹굴기\n편안한 휴식", key="leisure_5", use_container_width=True):
            game.state.leisure_choice = "gaming"
            game.state.update_stats({"stress": -12, "wellbeing": -3})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("6. 온라인 강의 듣기\n자기계발", key="leisure_6", use_container_width=True):
            game.state.leisure_choice = "online_courses"
            game.state.update_stats({"stress": -3, "wellbeing": 5, "project_success": 3})
            st.session_state.lifestyle_step = 3
            st.rerun()

    elif step == 3:
        # 식사 스타일 선택
        st.markdown("""
        <div class="scenario-text">
        <h3>🍽️ 식사는 주로 어떻게 하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("1. 집에서 직접 요리\n건강하고 저렴, 하지만 시간 소모", key="meal_1", use_container_width=True):
            game.state.meal_choice = "cook_at_home"
            game.state.update_stats({"stress": 3, "wellbeing": 10})
            st.session_state.lifestyle_step = 4
            st.rerun()

        if st.button("2. 주로 외식\n편리하지만 건강과 예산 부담", key="meal_2", use_container_width=True):
            game.state.meal_choice = "eat_out"
            game.state.update_stats({"stress": -5, "wellbeing": -5, "reputation": 3})
            st.session_state.lifestyle_step = 4
            st.rerun()

        if st.button("3. 혼합 (집+외식)\n균형잡힌 선택", key="meal_3", use_container_width=True):
            game.state.meal_choice = "mixed"
            game.state.update_stats({"wellbeing": 5})
            st.session_state.lifestyle_step = 4
            st.rerun()

    elif step == 4:
        st.success("✅ 초기 설정이 완료되었습니다!")

        if st.button("게임 시작!", use_container_width=True):
            st.session_state.current_screen = 'game_play'
            st.rerun()


def game_play_screen():
    """게임 플레이 화면"""
    game = st.session_state.game
    state = game.state

    # 게임 오버 체크
    if state.game_over:
        st.session_state.current_screen = 'game_over'
        st.rerun()
        return

    # 2년 완료 체크
    if state.year > 2:
        st.session_state.current_screen = 'ending'
        st.rerun()
        return

    # 스탯 표시
    display_stats(state)

    st.markdown("---")

    # 결과 메시지 표시
    if st.session_state.result_message:
        st.markdown(f"""
        <div class="scenario-text">
        {st.session_state.result_message}
        </div>
        """, unsafe_allow_html=True)

        if st.button("다음으로", use_container_width=True):
            st.session_state.result_message = ""
            st.session_state.choice_made = False
            st.rerun()

        return

    # 현재 시나리오 가져오기
    current_scenario_id = state.current_scenario

    # 시작 시나리오인 경우 다음 시나리오로 이동
    if current_scenario_id == "start":
        next_scenarios = [s for s in game.scenarios.keys() if s not in state.visited_scenarios and s != "start"]
        if next_scenarios:
            current_scenario_id = random.choice(next_scenarios)
            state.current_scenario = current_scenario_id
        else:
            st.error("더 이상 시나리오가 없습니다.")
            return

    scenario = game.scenarios.get(current_scenario_id)

    if not scenario:
        st.error("시나리오를 찾을 수 없습니다.")
        return

    # 시나리오 제목 및 설명
    st.subheader(f"📋 {scenario['title']}")
    st.markdown(f"""
    <div class="scenario-text">
    {scenario['description']}
    </div>
    """, unsafe_allow_html=True)

    # 선택지 표시
    st.markdown("### 🤔 어떻게 하시겠습니까?")

    for idx, choice in enumerate(scenario['choices']):
        button_text = f"{idx + 1}. {choice['text']}"

        # 위험한 선택 경고
        result = choice.get('result', {})
        stats = result.get('stats', {})
        is_risky = any([
            stats.get('reputation', 0) < -15,
            stats.get('staff_morale', 0) < -15,
            stats.get('stress', 0) > 15,
            stats.get('wellbeing', 0) < -15
        ])

        if is_risky:
            st.warning(f"⚠️ 선택 {idx + 1}은 위험할 수 있습니다!")

        if st.button(button_text, key=f"choice_{idx}", use_container_width=True):
            # 선택 처리
            handle_choice(game, choice, current_scenario_id)
            st.rerun()


def handle_choice(game: KOICAGame, choice: dict, scenario_id: str):
    """선택 처리"""
    result = choice.get('result', {})

    # 결과 메시지 저장
    st.session_state.result_message = result.get('message', '')

    # 스탯 업데이트
    stats = result.get('stats', {})
    game.state.update_stats(stats)

    # 시나리오 방문 기록
    if scenario_id not in game.state.visited_scenarios:
        game.state.visited_scenarios.append(scenario_id)

    # 시간 진행
    if result.get('advance_time', False):
        game.state.period += 1
        if game.state.period > 6:
            game.state.period = 1
            game.state.year += 1

    # 다음 시나리오 설정
    next_scenario = result.get('next')
    if next_scenario:
        game.state.current_scenario = next_scenario
    else:
        # 랜덤 시나리오 선택
        available = [s for s in game.scenarios.keys()
                    if s not in game.state.visited_scenarios and s != "start"]
        if available:
            game.state.current_scenario = random.choice(available)
        else:
            # 모든 시나리오를 방문했으면 리셋
            game.state.visited_scenarios = []
            game.state.current_scenario = random.choice(list(game.scenarios.keys()))

    # 게임 오버 체크
    if (game.state.reputation <= 0 or
        game.state.staff_morale <= 0 or
        game.state.stress >= 100 or
        game.state.wellbeing <= 0):
        game.state.game_over = True


def game_over_screen():
    """게임 오버 화면"""
    game = st.session_state.game
    state = game.state

    st.title("💔 게임 오버")

    # 게임 오버 원인 파악
    reason = ""
    if state.reputation <= 0:
        reason = "평판이 0 이하로 떨어져 본부에 소환되었습니다."
    elif state.staff_morale <= 0:
        reason = "직원들의 반발로 사임하게 되었습니다."
    elif state.stress >= 100:
        reason = "번아웃으로 긴급 귀국하게 되었습니다."
    elif state.wellbeing <= 0:
        reason = "건강 위기로 의료 후송되었습니다."

    st.markdown(f"""
    <div class="warning-box">
    <h3>{reason}</h3>

    <b>재임 기간:</b> {state.year}년 {state.period}기

    <b>최종 스탯:</b>
    - 평판: {state.reputation}
    - 예산 집행률: {state.budget_execution_rate}
    - 직원 만족도: {state.staff_morale}
    - 프로젝트 성공도: {state.project_success}
    - 스트레스: {state.stress}
    - 웰빙: {state.wellbeing}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("다시 시작", use_container_width=True):
            # 세션 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        if st.button("메인 메뉴", use_container_width=True):
            st.session_state.current_screen = 'welcome'
            st.session_state.game = None
            st.rerun()


def ending_screen():
    """엔딩 화면"""
    game = st.session_state.game
    state = game.state

    st.title("🎉 임기 완수!")

    # 최종 점수 계산
    total_score = (
        state.reputation * 0.3 +
        state.budget_execution_rate * 0.2 +
        state.staff_morale * 0.25 +
        state.project_success * 0.25
    )

    # 엔딩 결정
    if total_score >= 80:
        ending_title = "전설적인 소장"
        ending_desc = "당신은 모든 면에서 탁월한 성과를 달성했습니다!"
        emoji = "🏆"
    elif total_score >= 65:
        ending_title = "성공적인 소장"
        ending_desc = "훌륭한 성과를 달성했습니다!"
        emoji = "🌟"
    elif total_score >= 50:
        ending_title = "평범한 소장"
        ending_desc = "무난하게 임기를 완수했습니다."
        emoji = "👍"
    else:
        ending_title = "고전한 소장"
        ending_desc = "많은 어려움을 겪었지만 임기를 마쳤습니다."
        emoji = "💪"

    st.markdown(f"""
    <div class="scenario-text">
    <h2>{emoji} {ending_title}</h2>
    <p>{ending_desc}</p>

    <h3>최종 점수: {total_score:.1f}/100</h3>

    <h4>최종 스탯:</h4>
    <ul>
    <li>평판: {state.reputation}/100</li>
    <li>예산 집행률: {state.budget_execution_rate}/100</li>
    <li>직원 만족도: {state.staff_morale}/100</li>
    <li>프로젝트 성공도: {state.project_success}/100</li>
    <li>스트레스: {state.stress}/100</li>
    <li>웰빙: {state.wellbeing}/100</li>
    </ul>

    <p>2년간의 여정을 완수하셨습니다. 수고하셨습니다!</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("다시 시작", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col2:
        if st.button("메인 메뉴", use_container_width=True):
            st.session_state.current_screen = 'welcome'
            st.session_state.game = None
            st.rerun()


def main():
    """메인 함수"""
    initialize_session_state()

    screen = st.session_state.current_screen

    if screen == 'welcome':
        welcome_screen()
    elif screen == 'ai_setup':
        ai_setup_screen()
    elif screen == 'game_intro':
        game_intro_screen()
    elif screen == 'lifestyle_setup':
        lifestyle_setup_screen()
    elif screen == 'game_play':
        game_play_screen()
    elif screen == 'game_over':
        game_over_screen()
    elif screen == 'ending':
        ending_screen()


if __name__ == "__main__":
    main()

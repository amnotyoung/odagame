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


def get_stat_grade(value):
    """스탯 변화 값에 따른 등급 반환"""
    if value >= 10:
        return "⭐ 우수"
    elif value >= 5:
        return "✓ 양호"
    elif value >= 0:
        return "✓ 보통"
    elif value >= -10:
        return "⚠️ 주의"
    else:
        return "❌ 위험"

# Page configuration
st.set_page_config(
    page_title="내가 소장이 될 상인가",
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

    /* 로딩 인디케이터 */
    .loading-overlay {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    .loading-spinner {
        display: inline-block;
        width: 60px;
        height: 60px;
        border: 6px solid rgba(255,255,255,0.3);
        border-top: 6px solid white;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 1rem auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        color: white;
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 1rem;
    }

    .loading-subtext {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    /* 시나리오 배지 스타일 */
    .scenario-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 1rem;
        text-align: center;
        margin: 1rem 0 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }

    .scenario-badge-emoji {
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }

    .scenario-badge-title {
        color: white;
        margin: 0;
        font-size: 1.6rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
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

        .loading-overlay {
            padding: 2rem 1rem;
        }

        .loading-text {
            font-size: 1.1rem;
        }

        .loading-subtext {
            font-size: 0.9rem;
        }

        /* 모바일에서 시나리오 배지 최적화 */
        .scenario-badge {
            padding: 1.5rem 1rem;
        }

        .scenario-badge-emoji {
            font-size: 2.5rem;
        }

        .scenario-badge-title {
            font-size: 1.3rem;
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
    if 'free_form_mode' not in st.session_state:
        st.session_state.free_form_mode = False
    if 'free_form_action' not in st.session_state:
        st.session_state.free_form_action = ""
    if 'is_generating_ai' not in st.session_state:
        st.session_state.is_generating_ai = False


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
        period_months = {
            1: "1-2월", 2: "3-4월", 3: "5-6월",
            4: "7-8월", 5: "9-10월", 6: "11-12월"
        }
        period_str = period_months.get(state.period, f"{state.period}기")
        st.markdown(f"**📅 {state.year}년차 {period_str}**")

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
    st.title("🌍 내가 소장이 될 상인가")

    # 허구 disclaimer
    st.markdown("""
    <div class="warning-box">
    <p style="text-align: center; margin: 0; font-size: 0.95rem;">
    ⚠️ <b>이 게임의 모든 내용은 허구입니다.</b><br>
    실제 기관, 인물, 사건과 무관하며 교육 및 재미를 위한 시뮬레이션입니다.
    </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="scenario-text">
    <h3>환영합니다!</h3>

    당신은 <b>KOICA(한국국제협력단) 해외사무소장</b>으로 새로 부임했습니다.

    🌏 <b>KOICA는 전 세계 48개국에 해외사무소를 운영</b>하며,
    대한민국 무상원조사업을 현장에서 직접 실행합니다.

    📊 <b>당신의 조직 (총 17명)</b>
    - 사무소장: 1명 (당신)
    - 부소장: 2명
    - 코디네이터: 2명
    - YP(영프로페셔널): 2명
    - 현지 직원: 10명

    🎯 <b>임기: 2년 (2개월씩 12회 선택)</b>

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
            if st.button("🤖 AI 모드\n\nGemini AI 동적 시나리오", key="ai_mode_btn", use_container_width=True):
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
    st.title("🌍 내가 소장이 될 상인가")

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

        if st.button("1. 한국에서 자동차를 가져간다 (익숙하지만 비용과 수리가 문제)", key="car_1", use_container_width=True):
            game.state.car_choice = "bring_from_korea"
            game.state.update_stats({"stress": -5, "wellbeing": 5})
            st.session_state.lifestyle_step = 1
            st.rerun()

        if st.button("2. 현지에서 중고차를 구입한다 (저렴하지만 품질이 불확실)", key="car_2", use_container_width=True):
            game.state.car_choice = "buy_local"
            game.state.update_stats({"stress": 5, "wellbeing": -3})
            st.session_state.lifestyle_step = 1
            st.rerun()

        if st.button("3. 자동차 없이 택시와 대중교통 이용 (자유롭지만 불편)", key="car_3", use_container_width=True):
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

        if st.button("1. 넓은 집 (여유 공간, 하지만 먼 거리)", key="house_1", use_container_width=True):
            game.state.housing_choice = "spacious"
            game.state.update_stats({"stress": -3, "wellbeing": 8})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("2. 좋은 집 (새 건물, 고급 시설, 하지만 월세 부분 자부담)", key="house_2", use_container_width=True):
            game.state.housing_choice = "nice"
            game.state.update_stats({"stress": -5, "wellbeing": 10, "budget": -5})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("3. 사무소 가까운 집 (출퇴근 편리, 하지만 좁고 오래됨)", key="house_3", use_container_width=True):
            game.state.housing_choice = "near_office"
            game.state.update_stats({"stress": -10, "wellbeing": -5})
            st.session_state.lifestyle_step = 2
            st.rerun()

        if st.button("4. 치안 좋은 동네 집 (안전, 하지만 시내에서 멀고 심심함)", key="house_4", use_container_width=True):
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

        if st.button("1. 독서 (조용하고 지적인 시간)", key="leisure_1", use_container_width=True):
            game.state.leisure_choice = "reading"
            game.state.update_stats({"stress": -8, "wellbeing": 5})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("2. 운동 (건강 관리와 스트레스 해소)", key="leisure_2", use_container_width=True):
            game.state.leisure_choice = "exercise"
            game.state.update_stats({"stress": -10, "wellbeing": 15})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("3. 음주 (직원들과 친목, 하지만 건강 염려)", key="leisure_3", use_container_width=True):
            game.state.leisure_choice = "drinking"
            game.state.update_stats({"stress": -5, "staff_morale": 8, "wellbeing": -8})
            st.session_state.lifestyle_step = 3
            st.rerun()

        if st.button("4. 집에서 뒹굴기 (편안한 휴식)", key="leisure_4", use_container_width=True):
            game.state.leisure_choice = "gaming"
            game.state.update_stats({"stress": -12, "wellbeing": -3})
            st.session_state.lifestyle_step = 3
            st.rerun()

    elif step == 3:
        # 식사 스타일 선택
        st.markdown("""
        <div class="scenario-text">
        <h3>🍽️ 식사는 주로 어떻게 하시겠습니까?</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("1. 집에서 직접 요리 (건강하고 저렴, 하지만 시간 소모)", key="meal_1", use_container_width=True):
            game.state.meal_choice = "cook_at_home"
            game.state.update_stats({"stress": 3, "wellbeing": 10})
            st.session_state.lifestyle_step = 4
            st.rerun()

        if st.button("2. 주로 외식 (편리하지만 건강과 예산 부담)", key="meal_2", use_container_width=True):
            game.state.meal_choice = "eat_out"
            game.state.update_stats({"stress": -5, "wellbeing": -5, "reputation": 3})
            st.session_state.lifestyle_step = 4
            st.rerun()

        if st.button("3. 배달&포장 (편리하고 시간 절약, 하지만 배달비 부담)", key="meal_3", use_container_width=True):
            game.state.meal_choice = "mixed"
            game.state.update_stats({"wellbeing": 5})
            st.session_state.lifestyle_step = 4
            st.rerun()

    elif step == 4:
        st.success("✅ 초기 설정이 완료되었습니다!")

        if st.button("게임 시작!", use_container_width=True):
            st.session_state.current_screen = 'game_play'
            st.rerun()


def get_scenario_visual_style(scenario_id: str, scenario: dict) -> dict:
    """시나리오 ID와 내용을 기반으로 비주얼 스타일 반환

    Returns:
        dict: {
            'emoji': 이모지,
            'gradient': CSS 그라디언트,
            'border_color': 테두리 색상
        }
    """
    # 키워드 기반 분류
    title_lower = scenario.get('title', '').lower()
    desc_lower = scenario.get('description', '').lower()

    # 위기/문제 상황
    crisis_keywords = ['위기', '갈등', '문제', '충돌', '압력', '긴급', '비상', '파탄', '붕괴', '번아웃']
    if any(keyword in title_lower or keyword in desc_lower for keyword in crisis_keywords):
        return {
            'emoji': '🚨',
            'gradient': 'linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%)',
            'border_color': '#c92a2a'
        }

    # 엔딩 (긍정적)
    positive_ending_keywords = ['성공', '승진', '완료', '달성', '전문가', '변화']
    if scenario_id.startswith('ending_') and any(keyword in title_lower or keyword in desc_lower for keyword in positive_ending_keywords):
        return {
            'emoji': '🎉',
            'gradient': 'linear-gradient(135deg, #51cf66 0%, #2f9e44 100%)',
            'border_color': '#2f9e44'
        }

    # 엔딩 (부정적)
    if scenario_id.startswith('ending_'):
        return {
            'emoji': '💔',
            'gradient': 'linear-gradient(135deg, #868e96 0%, #495057 100%)',
            'border_color': '#495057'
        }

    # 생활 이벤트
    if scenario_id.startswith('life_event_'):
        return {
            'emoji': '⭐',
            'gradient': 'linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%)',
            'border_color': '#7c3aed'
        }

    # 시작
    if scenario_id == 'start':
        return {
            'emoji': '🌍',
            'gradient': 'linear-gradient(135deg, #339af0 0%, #1864ab 100%)',
            'border_color': '#1864ab'
        }

    # 기본 (일상적인 업무)
    return {
        'emoji': '📋',
        'gradient': 'linear-gradient(135deg, #748ffc 0%, #5c7cfa 100%)',
        'border_color': '#5c7cfa'
    }


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

        # 스탯 변화 표시
        if hasattr(st.session_state, 'stat_changes') and st.session_state.stat_changes:
            stat_changes = st.session_state.stat_changes

            # 스탯 이름 매핑
            stat_names = {
                'reputation': '평판',
                'budget': '예산 집행률',
                'staff_morale': '직원 사기',
                'project_success': '사업 성과',
                'stress': '스트레스',
                'wellbeing': '웰빙'
            }

            # 긍정적/부정적 변화 분류
            positive_changes = []
            negative_changes = []

            for stat_key, change in stat_changes.items():
                if change == 0:
                    continue

                stat_name = stat_names.get(stat_key, stat_key)
                grade = get_stat_grade(change)

                # 스트레스는 반대 (증가가 부정적)
                if stat_key == 'stress':
                    if change > 0:
                        negative_changes.append((stat_name, change, grade))
                    else:
                        positive_changes.append((stat_name, change, grade))
                else:
                    if change > 0:
                        positive_changes.append((stat_name, change, grade))
                    else:
                        negative_changes.append((stat_name, change, grade))

            # 변화 표시
            if positive_changes or negative_changes:
                st.markdown("### 📊 스탯 변화")

                cols = st.columns(2)

                with cols[0]:
                    if positive_changes:
                        st.markdown("**✅ 긍정적 변화**")
                        for stat_name, change, grade in positive_changes:
                            if change >= 0:
                                st.markdown(f"• {stat_name}: **+{change}** {grade}")
                            else:
                                st.markdown(f"• {stat_name}: **{change}** {grade}")

                with cols[1]:
                    if negative_changes:
                        st.markdown("**⚠️ 부정적 변화**")
                        for stat_name, change, grade in negative_changes:
                            if change >= 0:
                                st.markdown(f"• {stat_name}: **+{change}** {grade}")
                            else:
                                st.markdown(f"• {stat_name}: **{change}** {grade}")

        # 고급 기능: delayed effects 표시
        if hasattr(st.session_state, 'delayed_effects') and st.session_state.delayed_effects:
            st.markdown("---")
            for effect in st.session_state.delayed_effects:
                st.info(f"⏰ **과거 선택의 장기 영향:** {effect.get('message', '')}")
            st.session_state.delayed_effects = None

        if st.button("다음으로", use_container_width=True):
            st.session_state.result_message = ""
            st.session_state.stat_changes = {}
            st.session_state.choice_made = False
            st.rerun()

        return

    # 현재 시나리오 가져오기
    current_scenario_id = state.current_scenario

    # AI 모드에서 'ai_generated' 시나리오 처리
    if st.session_state.ai_mode and current_scenario_id == 'ai_generated':
        # 로딩 인디케이터 표시
        st.markdown("""
        <div class="loading-overlay">
            <div class="loading-spinner"></div>
            <div class="loading-text">🤖 AI가 맞춤형 시나리오를 생성중입니다</div>
            <div class="loading-subtext">플레이어의 선택을 분석하여 최적의 시나리오를 준비하고 있습니다...</div>
        </div>
        """, unsafe_allow_html=True)

        # AI 시나리오 생성
        scenario = game.gemini.generate_scenario(state)

        if not scenario:
            st.warning("AI 시나리오 생성 실패. 기본 시나리오를 사용합니다.")
            # 폴백: 랜덤 시나리오 선택
            fallback_scenarios = ['budget_crisis_1', 'cultural_conflict', 'staff_problem_1']
            available_fallbacks = [s for s in fallback_scenarios if s in game.scenarios]
            if available_fallbacks:
                current_scenario_id = random.choice(available_fallbacks)
                scenario = game.scenarios.get(current_scenario_id)
            else:
                # 모든 폴백이 없으면 아무 시나리오나 선택
                current_scenario_id = random.choice([s for s in game.scenarios.keys()
                                                     if not s.startswith("ending_") and s != "start"])
                scenario = game.scenarios.get(current_scenario_id)
    else:
        scenario = game.scenarios.get(current_scenario_id)

    if not scenario:
        st.error("시나리오를 찾을 수 없습니다.")
        return

    # 특별 이벤트 발생 알림
    if hasattr(st.session_state, 'life_event_triggered') and st.session_state.life_event_triggered:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px; border-radius: 10px; margin-bottom: 20px;
                    border: 3px solid #5a67d8; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: white; text-align: center; margin: 0; font-size: 28px;">
                ⭐ 특별 이벤트가 발생했습니다! ⭐
            </h2>
            <p style="color: #e0e7ff; text-align: center; margin-top: 10px; font-size: 16px;">
                예상치 못한 상황이 발생했습니다. 신중하게 대응하세요.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # 시나리오 비주얼 스타일 가져오기
    visual_style = get_scenario_visual_style(current_scenario_id, scenario)

    # 컬러 배지 표시
    st.markdown(f"""
    <div style="background: {visual_style['gradient']};
                padding: 2rem 1.5rem;
                border-radius: 1rem;
                text-align: center;
                margin: 1rem 0 2rem 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                border: 3px solid {visual_style['border_color']};">
        <div style="font-size: 3.5rem; margin-bottom: 0.5rem;">
            {visual_style['emoji']}
        </div>
        <h2 style="color: white; margin: 0; font-size: 1.6rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            {scenario['title']}
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # 시나리오 설명
    st.markdown(f"""
    <div class="scenario-text">
    {scenario['description']}
    </div>
    """, unsafe_allow_html=True)

    # 엔딩 시나리오 처리 (choices가 없는 경우)
    if 'choices' not in scenario:
        st.markdown("---")
        if st.button("다음으로", use_container_width=True):
            # 게임 오버 상태인지 확인
            if state.check_game_over():
                st.session_state.current_screen = 'game_over'
            else:
                st.session_state.current_screen = 'ending'
            st.rerun()
        return

    # 자유 답변 모드 처리
    if st.session_state.free_form_mode:
        st.markdown("### 💡 자유 답변 모드")
        st.markdown("원하는 행동을 자유롭게 입력하세요. 예: '현지 부족장들과 직접 만나 대화한다', '직원들과 회의를 소집한다' 등")

        action = st.text_area("행동:", value=st.session_state.free_form_action, key="free_action_input", height=100)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("실행", use_container_width=True):
                if action.strip():
                    # 자유 답변 처리
                    success = handle_free_form_action(game, action.strip())
                    if success:
                        # 성공 시에만 자유 답변 모드 종료
                        st.session_state.free_form_mode = False
                        st.session_state.free_form_action = ""
                        st.rerun()
                    else:
                        # 실패 시 입력 내용 유지하여 다시 입력할 수 있도록
                        # st.rerun()을 호출하지 않아 에러 메시지가 표시됨
                        st.session_state.free_form_mode = True
                        st.session_state.free_form_action = action
                else:
                    st.error("행동을 입력해주세요.")

        with col2:
            if st.button("취소", use_container_width=True):
                st.session_state.free_form_mode = False
                st.session_state.free_form_action = ""
                st.rerun()

        return

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

        # 선택지 상세 정보 표시
        with st.container():
            if st.button(button_text, key=f"choice_{idx}", use_container_width=True):
                # 선택 처리
                handle_choice(game, choice, current_scenario_id)
                st.rerun()

            # subtext와 trade_off 표시
            subtext = choice.get('subtext', '')
            trade_off = choice.get('trade_off', '')

            if subtext or trade_off:
                with st.expander(f"ℹ️ 선택지 {idx + 1} 상세 정보"):
                    if subtext:
                        st.markdown(f"**{subtext}**")
                    if trade_off:
                        st.markdown(f"📊 **예상 효과:** {trade_off}")

            if is_risky:
                st.warning(f"⚠️ 선택 {idx + 1}은 위험할 수 있습니다!")

    # AI 모드에서만 자유 답변 버튼 표시
    if st.session_state.ai_mode and game.gemini and game.gemini.enabled:
        st.markdown("---")
        if st.button("💡 자유롭게 답변하기 (AI)", use_container_width=True):
            st.session_state.free_form_mode = True
            st.rerun()


def handle_free_form_action(game: KOICAGame, action: str) -> bool:
    """자유 답변 처리

    Returns:
        bool: 성공 시 True, 실패 시 False
    """
    # AI 모드 체크
    if not game.gemini or not game.gemini.enabled:
        st.error("⚠️ AI 모드가 활성화되어 있지 않습니다.")
        return False

    # 로딩 인디케이터 표시
    st.markdown("""
    <div class="loading-overlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">🤖 AI가 결과를 계산중입니다</div>
        <div class="loading-subtext">플레이어의 행동을 분석하여 결과를 생성하고 있습니다...</div>
    </div>
    """, unsafe_allow_html=True)

    try:
        result = game.gemini.generate_free_form_result(game.state, action)
    except Exception as e:
        st.error(f"⚠️ AI 처리 중 오류가 발생했습니다: {str(e)}")
        return False

    if result and result.get('success'):
        # 결과 메시지 저장
        st.session_state.result_message = result.get('message', '행동을 수행했습니다.')

        # 스탯 업데이트
        stats = result.get('stats', {})
        game.state.update_stats(stats)

        # 선택 히스토리 기록
        game.state.choice_history.append({
            'year': game.state.year,
            'period': game.state.period,
            'action': action,
            'custom': True
        })

        # 다음 시나리오는 AI 생성 또는 랜덤
        game.state.current_scenario = 'ai_generated' if game.gemini.enabled else random.choice(
            [s for s in game.scenarios.keys() if not s.startswith("ending_") and s != "start"]
        )

        # AI 자유 입력은 항상 시간을 진행시킴
        # 다음 period_N 시나리오를 예측하여 시간 설정
        game.state.period += 1
        if game.state.period > 6:
            game.state.period = 1
            game.state.year += 1

        # 생활 이벤트 체크 (시간이 진행되었으므로)
        life_event_id = game.check_and_trigger_life_event()
        if life_event_id:
            # 생활 이벤트 발생 - 중복 방지를 위해 추적 세트에 추가
            game.state.triggered_life_events.add(life_event_id)
            # 원래 다음 시나리오를 저장하고, 생활 이벤트를 먼저 표시
            st.session_state.pending_next_scenario = game.state.current_scenario
            game.state.current_scenario = life_event_id
            # 생활 이벤트 발생 플래그 설정
            st.session_state.life_event_triggered = True

        # 게임 오버 체크
        if (game.state.reputation <= 0 or
            game.state.staff_morale <= 0 or
            game.state.stress >= 100 or
            game.state.wellbeing <= 0):
            game.state.game_over = True

        return True
    else:
        # 실패 시 에러 메시지
        if result:
            error_msg = result.get('message', '해당 행동은 불가능합니다.')
            st.error(f"⚠️ {error_msg}")
        else:
            st.error("⚠️ AI가 응답을 생성하지 못했습니다. 다시 시도해주세요.")
            st.info("💡 팁: 더 구체적이고 현실적인 행동을 입력해보세요.")
        return False


def handle_choice(game: KOICAGame, choice: dict, scenario_id: str):
    """선택 처리"""
    result = choice.get('result', {})

    # 결과 메시지 저장
    st.session_state.result_message = result.get('message', '')

    # 스탯 변화 저장 (표시용)
    stats = result.get('stats', {})
    st.session_state.stat_changes = stats.copy() if stats else {}

    # 스탯 업데이트
    game.state.update_stats(stats)

    # 시나리오 ID와 year/period 매핑 (동기화)
    scenario_period_map = {
        'start': (1, 1),
        'period_2': (1, 2), 'period_3': (1, 3), 'period_4': (1, 4),
        'period_5': (1, 5), 'period_6': (1, 6),
        'period_7': (2, 1), 'period_8': (2, 2), 'period_9': (2, 3),
        'period_10': (2, 4), 'period_11': (2, 5), 'period_12': (2, 6)
    }

    # 다음 시나리오의 year/period 동기화
    next_scenario = result.get('next')
    if next_scenario and next_scenario in scenario_period_map:
        expected_year, expected_period = scenario_period_map[next_scenario]
        if game.state.year != expected_year or game.state.period != expected_period:
            game.state.year = expected_year
            game.state.period = expected_period

    # 부소장 사기 변경 처리
    if 'deputy_morale' in result:
        for personality, change in result['deputy_morale'].items():
            game.state.update_deputy_morale(personality, change)

    # 고급 기능: delayed_effects 처리
    if 'delayed_effects' in result:
        # Backward compatibility: Initialize pending_delayed_effects if it doesn't exist
        if not hasattr(game.state, 'pending_delayed_effects'):
            game.state.pending_delayed_effects = []
        for effect in result['delayed_effects']:
            game.state.pending_delayed_effects.append(effect.copy())

    # 시나리오 방문 기록
    if scenario_id not in game.state.visited_scenarios:
        game.state.visited_scenarios.append(scenario_id)

    # 선택 히스토리 기록
    game.state.choice_history.append({
        'scenario_id': scenario_id,
        'choice_text': choice.get('text', ''),
        'year': game.state.year,
        'period': game.state.period,
        'result': result
    })

    # 다음 시나리오 설정
    # 생활 이벤트 이후 pending_next_scenario가 있으면 그걸로 이동
    if hasattr(st.session_state, 'pending_next_scenario') and st.session_state.pending_next_scenario:
        game.state.current_scenario = st.session_state.pending_next_scenario
        # 생활 이벤트 복귀 후 year/period 재동기화
        if game.state.current_scenario in scenario_period_map:
            expected_year, expected_period = scenario_period_map[game.state.current_scenario]
            game.state.year = expected_year
            game.state.period = expected_period
        st.session_state.pending_next_scenario = None
        # 생활 이벤트 플래그 제거
        if hasattr(st.session_state, 'life_event_triggered'):
            st.session_state.life_event_triggered = False
    else:
        next_scenario = result.get('next')
        if next_scenario and next_scenario in game.scenarios:
            # 다음 시나리오가 존재하는 경우에만 설정
            game.state.current_scenario = next_scenario
        else:
            # AI 모드인 경우 AI가 생성한 시나리오 사용
            if st.session_state.ai_mode and game.gemini and game.gemini.enabled:
                game.state.current_scenario = 'ai_generated'
            else:
                # 다음 시나리오가 없거나 존재하지 않으면 랜덤 시나리오 선택
                # 엔딩 시나리오는 제외
                available = [s for s in game.scenarios.keys()
                            if s not in game.state.visited_scenarios
                            and s != "start"
                            and not s.startswith("ending_")]
                if available:
                    game.state.current_scenario = random.choice(available)
                else:
                    # 모든 시나리오를 방문했으면 리셋 (엔딩 시나리오는 여전히 제외)
                    game.state.visited_scenarios = []
                    non_ending_scenarios = [s for s in game.scenarios.keys()
                                           if not s.startswith("ending_") and s != "start"]
                    if non_ending_scenarios:
                        game.state.current_scenario = random.choice(non_ending_scenarios)
                    else:
                        game.state.current_scenario = "start"

    # 생활 이벤트 체크 (advance_time이 true인 경우에만)
    if result.get('advance_time', False):
        life_event_id = game.check_and_trigger_life_event()
        if life_event_id:
            # 생활 이벤트 발생 - 중복 방지를 위해 추적 세트에 추가
            game.state.triggered_life_events.add(life_event_id)
            # 원래 다음 시나리오를 저장하고, 생활 이벤트를 먼저 표시
            st.session_state.pending_next_scenario = game.state.current_scenario
            game.state.current_scenario = life_event_id
            # 생활 이벤트 발생 플래그 설정
            st.session_state.life_event_triggered = True

        # 고급 기능: 부소장 임계값 이벤트 체크
        deputy_event_id = game.check_deputy_threshold_events()
        if deputy_event_id:
            game.state.triggered_deputy_events.add(deputy_event_id)
            st.session_state.pending_next_scenario = game.state.current_scenario
            game.state.current_scenario = deputy_event_id
            st.session_state.deputy_event_triggered = True

        # 고급 기능: 장기 영향(delayed effects) 체크
        triggered_effects = game.check_delayed_effects()
        if triggered_effects:
            st.session_state.delayed_effects = triggered_effects

        # 고급 기능: 고급 엔딩 조건 체크
        advanced_ending = game.check_advanced_endings()
        if advanced_ending:
            game.state.game_over = True
            game.state.ending = advanced_ending

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

    period_months = {
        1: "1-2월", 2: "3-4월", 3: "5-6월",
        4: "7-8월", 5: "9-10월", 6: "11-12월"
    }
    period_str = period_months.get(state.period, f"{state.period}기")

    st.markdown(f"""
    <div class="warning-box">
    <h3>{reason}</h3>

    <b>재임 기간:</b> {state.year}년 {period_str}

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

    # 소장 유형 결정 (이제 1개만 반환됨)
    director_types = game._determine_director_types()
    director_type = director_types[0] if director_types else "소장"

    # 선택 분석을 통한 풍부한 설명 생성
    choice_explanation = _generate_choice_explanation(state, director_type)

    st.markdown(f"""
    <div class="scenario-text">
    <h2>✨ 당신의 소장 유형: {director_type}</h2>
    <p style="line-height: 1.8; margin-top: 15px;">{choice_explanation}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="scenario-text">
    <h3>📊 영역별 성과</h3>
    <ul>
    <li>🌟 평판: {state.reputation}/100</li>
    <li>💰 예산 집행률: {state.budget_execution_rate}/100</li>
    <li>😊 직원 만족도: {state.staff_morale}/100</li>
    <li>📊 프로젝트 성공도: {state.project_success}/100</li>
    </ul>

    <h3>🏥 개인 상태</h3>
    <ul>
    <li>😰 스트레스: {state.stress}/100</li>
    <li>😌 웰빙: {state.wellbeing}/100</li>
    </ul>

    <p style="margin-top: 20px;">2년간의 여정을 완수하셨습니다. 수고하셨습니다!</p>
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


def _generate_choice_explanation(state: GameState, director_type: str) -> str:
    """선택 히스토리를 분석하여 소장 유형에 대한 드라마틱한 설명 생성"""

    style = state.player_style
    total_choices = len(state.choice_history)

    if total_choices == 0:
        return "축하합니다. 2년간의 임기를 완수하셨습니다."

    # 주요 관심사 파악
    focus_areas = {
        '평판': style['reputation_focused'],
        '예산': style['budget_focused'],
        '직원': style['staff_focused'],
        '프로젝트': style['project_focused']
    }

    # 위험 감수 성향
    risk_ratio = style['risk_taking'] / total_choices if total_choices > 0 else 0

    # 상위 관심사
    sorted_focus = sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)
    top_concern = sorted_focus[0][0] if sorted_focus[0][1] > 0 else "사무소 운영"

    # === 드라마틱한 구조로 재구성 ===
    paragraphs = []

    # 1. 오프닝: 축하와 여정의 완수
    paragraphs.append("축하합니다. 2년간의 험난한 여정을 완수하셨습니다.")

    # 2. 위기와 성공의 대비
    crisis_parts = []
    success_parts = []

    # 어려움 파악
    if state.reputation < 50:
        crisis_parts.append("<b>평판 위기</b>")
    if state.staff_morale < 50:
        crisis_parts.append("<b>직원들의 불만</b>")
    if state.stress >= 60:
        crisis_parts.append("<b>극심한 스트레스</b>")
    if state.budget_execution_rate < 60:
        crisis_parts.append("<b>예산 집행의 어려움</b>")

    # 성공 파악
    if state.reputation >= 60:
        success_parts.append("<b>신뢰 구축</b>")
    if state.project_success >= 60:
        success_parts.append("<b>프로젝트 성공</b>")
    if state.staff_morale >= 60:
        success_parts.append("<b>팀워크 형성</b>")
    if state.budget_execution_rate >= 70:
        success_parts.append("<b>효율적인 예산 운영</b>")

    # 위기와 성공을 문장으로 구성
    if crisis_parts and success_parts:
        para2 = f"{', '.join(crisis_parts[:2])}의 위기도 있었고, {', '.join(success_parts[:2])}의 순간도 있었습니다."
    elif crisis_parts:
        para2 = f"{', '.join(crisis_parts[:2])}의 위기가 있었지만, 당신은 흔들리지 않았습니다."
    elif success_parts:
        para2 = f"{', '.join(success_parts[:2])}을 이루며 빛나는 순간들이 있었습니다."
    else:
        para2 = "크고 작은 사건들이 있었습니다."

    para2 += " 예산 부족과 문화적 갈등, 예상치 못한 사건들이 연이어 닥쳤지만, 당신은 포기하지 않고 한 걸음씩 나아갔습니다."
    paragraphs.append(para2)

    # 3. 리더십 스타일과 헌신
    # 의사결정 스타일
    if risk_ratio > 0.35:
        leadership_style = "혁신적"
    elif risk_ratio > 0.2:
        leadership_style = "도전적"
    elif risk_ratio < 0.1:
        leadership_style = "신중"
    else:
        leadership_style = "균형잡힌"

    para3 = f"당신의 <b>{top_concern}</b>에 대한 헌신, <b>{leadership_style}</b>한 리더십은 이곳 사람들의 삶에 실질적인 변화를 만들어냈습니다."
    paragraphs.append(para3)

    # 4. 유산과 기억
    para4 = f"이제 사람들은 당신을 '<b>{director_type}</b>'으로 기억할 것입니다. 그리고 당신이 남긴 발자국은 오랫동안 이 땅에 남을 것입니다."
    paragraphs.append(para4)

    return "<br><br>".join(paragraphs)


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

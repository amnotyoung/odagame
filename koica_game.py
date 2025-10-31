#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOICA 소장 시뮬레이터
텍스트 기반 선택형 게임
"""

import json
import os
import sys
import re
import time
import random
import argparse
from typing import Dict, List, Optional, Tuple

# Gemini API import (optional - graceful degradation if not available)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. AI features will be disabled.")


class GameState:
    """게임 상태를 관리하는 클래스"""

    def __init__(self):
        self.year = 1
        self.period = 1  # 격월 단위 (1=1-2월, 2=3-4월, 3=5-6월, 4=7-8월, 5=9-10월, 6=11-12월)
        self.reputation = 25  # 평판 (0-100) - 더 어려운 시작점
        self.budget_execution_rate = 25  # 예산 집행률 (0-100), 80-100%가 이상적 - 더 어려운 시작점
        self.staff_morale = 30  # 직원 만족도 (0-100) - 더 어려운 시작점
        self.project_success = 25  # 프로젝트 성공도 (0-100) - 더 어려운 시작점

        # 생활 스탯 추가
        self.stress = 50  # 스트레스 (0-100, 낮을수록 좋음) - 더 높은 시작점
        self.wellbeing = 35  # 웰빙 (0-100, 높을수록 좋음) - 더 낮은 시작점

        self.current_scenario = "start"
        self.visited_scenarios = []
        self.game_over = False
        self.ending = None

        # 초기 생활 선택 (게임 시작 시 결정)
        self.car_choice = None  # "bring_from_korea", "buy_local", "no_car"
        self.housing_choice = None  # "spacious", "nice", "near_office", "secure"
        self.leisure_choice = None  # "reading", "exercise", "drinking", "writing", "gaming", "online_courses"
        self.meal_choice = None  # "cook_at_home", "eat_out", "mixed"

        # Enhanced: Player history tracking
        self.choice_history = []  # 선택 히스토리
        self.stat_history = []  # 스탯 변화 히스토리
        self.major_decisions = []  # 주요 결정 포인트
        self.player_style = {  # 플레이어 스타일 분석
            "reputation_focused": 0,
            "budget_focused": 0,
            "staff_focused": 0,
            "project_focused": 0,
            "risk_taking": 0,
            "principle_oriented": 0
        }

        # 발생한 생활 이벤트 추적 (중복 방지)
        self.triggered_life_events = set()

        # 생활 이벤트 발생 횟수 추적 (최대 4회로 제한)
        self.life_events_count = 0

        # 고급 기능: 부소장 임계값 이벤트 추적
        self.triggered_deputy_events = set()

        # 고급 기능: 대기 중인 장기 효과 (delayed_effects)
        self.pending_delayed_effects = []

        # 고급 기능: 윤리 위반 횟수 (새로운 엔딩 조건용)
        self.ethics_violations = 0

        # 부소장 및 코디네이터 관리 시스템 (부소장 2명, 코디 2명)
        self.deputies = self._initialize_deputies()
        self.coordinators = self._initialize_coordinators()

        # YP 및 현지직원 관리 시스템 (YP 2명, 현지직원 10명)
        self.yps = self._initialize_yps()
        self.local_staff = self._initialize_local_staff()

    def update_stats(self, changes):
        """스탯 업데이트 및 히스토리 기록"""
        old_stats = {
            'reputation': self.reputation,
            'budget_execution_rate': self.budget_execution_rate,
            'staff_morale': self.staff_morale,
            'project_success': self.project_success,
            'stress': self.stress,
            'wellbeing': self.wellbeing
        }

        if 'reputation' in changes:
            self.reputation = max(0, min(100, self.reputation + changes['reputation']))
        if 'budget' in changes:
            # budget 변화값을 예산 집행률로 변환
            self.budget_execution_rate = max(0, min(100, self.budget_execution_rate + changes['budget']))
        if 'staff_morale' in changes:
            self.staff_morale = max(0, min(100, self.staff_morale + changes['staff_morale']))
        if 'project_success' in changes:
            self.project_success = max(0, min(100, self.project_success + changes['project_success']))
        if 'stress' in changes:
            self.stress = max(0, min(100, self.stress + changes['stress']))
        if 'wellbeing' in changes:
            self.wellbeing = max(0, min(100, self.wellbeing + changes['wellbeing']))

        # 스탯 변화 기록
        self.stat_history.append({
            'year': self.year,
            'period': self.period,
            'changes': changes,
            'old': old_stats,
            'new': {
                'reputation': self.reputation,
                'budget_execution_rate': self.budget_execution_rate,
                'staff_morale': self.staff_morale,
                'project_success': self.project_success,
                'stress': self.stress,
                'wellbeing': self.wellbeing
            }
        })

    def _initialize_deputies(self):
        """2명의 부소장 초기화 (성격과 사기 부여)"""
        deputy_types = [
            {
                "name": "부소장 1",
                "personality": "principled",  # 원칙주의자
                "description": "규정과 원칙을 중시하는 스타일",
                "morale": 50
            },
            {
                "name": "부소장 2",
                "personality": "local_friendly",  # 현지친화형
                "description": "현지 파트너와의 관계를 중시하는 스타일",
                "morale": 50
            }
        ]
        return deputy_types

    def _initialize_coordinators(self):
        """2명의 코디네이터 초기화"""
        coordinators = [
            {
                "name": "코디 1",
                "morale": 50
            },
            {
                "name": "코디 2",
                "morale": 50
            }
        ]
        return coordinators

    def _initialize_yps(self):
        """2명의 YP (Young Professional) 초기화"""
        yps = [
            {
                "name": "YP 1",
                "morale": 50,
                "specialty": "monitoring_evaluation"  # 모니터링 평가 전문
            },
            {
                "name": "YP 2",
                "morale": 50,
                "specialty": "community_development"  # 지역사회 개발 전문
            }
        ]
        return yps

    def _initialize_local_staff(self):
        """10명의 현지직원 초기화"""
        local_staff = []
        roles = [
            ("행정", 2),  # 행정 직원 2명
            ("통역", 2),  # 통역사 2명
            ("운전기사", 2),  # 운전기사 2명
            ("프로젝트 보조", 3),  # 프로젝트 보조 직원 3명
            ("청소/경비", 1)  # 청소/경비 1명
        ]

        staff_id = 1
        for role, count in roles:
            for i in range(count):
                local_staff.append({
                    "id": staff_id,
                    "name": f"{role} {i+1}" if count > 1 else role,
                    "role": role,
                    "morale": 50,
                    "salary_satisfaction": 50  # 급여 만족도
                })
                staff_id += 1

        return local_staff

    def update_deputy_morale(self, personality_type, change):
        """특정 성격의 부소장 사기 변경"""
        for deputy in self.deputies:
            if deputy["personality"] == personality_type:
                deputy["morale"] = max(0, min(100, deputy["morale"] + change))
                break

    def get_deputy_by_personality(self, personality_type):
        """특정 성격의 부소장 정보 반환"""
        for deputy in self.deputies:
            if deputy["personality"] == personality_type:
                return deputy
        return None

    def get_low_morale_deputies(self, threshold=40):
        """사기가 낮은 부소장 목록 반환"""
        return [d for d in self.deputies if d["morale"] < threshold]

    def get_average_deputy_morale(self):
        """부소장 평균 사기 계산"""
        return sum(d["morale"] for d in self.deputies) / len(self.deputies)

    def update_coordinator_morale(self, coordinator_index, change):
        """코디네이터 사기 변경 (0-based index)"""
        if 0 <= coordinator_index < len(self.coordinators):
            self.coordinators[coordinator_index]["morale"] = max(0, min(100, self.coordinators[coordinator_index]["morale"] + change))

    def update_yp_morale(self, yp_index, change):
        """YP 사기 변경 (0-based index)"""
        if 0 <= yp_index < len(self.yps):
            self.yps[yp_index]["morale"] = max(0, min(100, self.yps[yp_index]["morale"] + change))

    def update_all_yp_morale(self, change):
        """모든 YP의 사기 일괄 변경"""
        for yp in self.yps:
            yp["morale"] = max(0, min(100, yp["morale"] + change))

    def get_average_yp_morale(self):
        """YP 평균 사기 계산"""
        if len(self.yps) == 0:
            return 50
        return sum(yp["morale"] for yp in self.yps) / len(self.yps)

    def update_local_staff_morale(self, staff_id, change):
        """특정 현지직원 사기 변경 (ID 기반)"""
        for staff in self.local_staff:
            if staff["id"] == staff_id:
                staff["morale"] = max(0, min(100, staff["morale"] + change))
                break

    def update_all_local_staff_morale(self, change):
        """모든 현지직원 사기 일괄 변경"""
        for staff in self.local_staff:
            staff["morale"] = max(0, min(100, staff["morale"] + change))

    def update_local_staff_by_role(self, role, change):
        """특정 역할의 현지직원 사기 변경"""
        for staff in self.local_staff:
            if staff["role"] == role:
                staff["morale"] = max(0, min(100, staff["morale"] + change))

    def get_average_local_staff_morale(self):
        """현지직원 평균 사기 계산"""
        if len(self.local_staff) == 0:
            return 50
        return sum(staff["morale"] for staff in self.local_staff) / len(self.local_staff)

    def get_low_morale_local_staff(self, threshold=40):
        """사기가 낮은 현지직원 목록 반환"""
        return [s for s in self.local_staff if s["morale"] < threshold]

    def get_staff_count_by_role(self, role):
        """특정 역할의 직원 수 반환"""
        return sum(1 for s in self.local_staff if s["role"] == role)

    def get_total_staff_count(self):
        """전체 직원 수 반환 (부소장 + 코디 + YP + 현지직원)"""
        return len(self.deputies) + len(self.coordinators) + len(self.yps) + len(self.local_staff)

    def record_choice(self, scenario_id, choice_text, choice_index, result):
        """선택 기록 및 플레이어 스타일 분석"""
        self.choice_history.append({
            'scenario_id': scenario_id,
            'choice_text': choice_text,
            'choice_index': choice_index,
            'year': self.year,
            'period': self.period,
            'result': result
        })

        # 플레이어 스타일 분석 (가중치 기반)
        if 'stats' in result:
            stats = result['stats']

            # 평판 중심: 큰 변화에 가중치 부여
            if 'reputation' in stats:
                rep_change = stats['reputation']
                if abs(rep_change) >= 10:
                    # 큰 변화는 2배 가중치
                    self.player_style['reputation_focused'] += 2 if rep_change > 0 else 1
                elif rep_change > 0:
                    self.player_style['reputation_focused'] += 1
                elif rep_change <= -5:
                    # 큰 희생을 감수한 경우도 일부 반영 (다른 목표를 위한 tradeoff)
                    self.player_style['reputation_focused'] += 0.5

            # 예산 중심: 예산 집행률 관리에 신경 쓰는 선택
            if 'budget' in stats:
                budget_change = stats['budget']
                if abs(budget_change) >= 10:
                    self.player_style['budget_focused'] += 2 if budget_change > 0 else 1
                elif budget_change != 0:
                    self.player_style['budget_focused'] += 1

            # 직원 중심: 직원 만족도 증가 선택
            if 'staff_morale' in stats:
                morale_change = stats['staff_morale']
                if abs(morale_change) >= 10:
                    self.player_style['staff_focused'] += 2 if morale_change > 0 else 1
                elif morale_change > 0:
                    self.player_style['staff_focused'] += 1
                elif morale_change <= -5:
                    self.player_style['staff_focused'] += 0.5

            # 프로젝트 중심: 프로젝트 성공도 증가 선택
            if 'project_success' in stats:
                project_change = stats['project_success']
                if abs(project_change) >= 10:
                    self.player_style['project_focused'] += 2 if project_change > 0 else 1
                elif project_change > 0:
                    self.player_style['project_focused'] += 1
                elif project_change <= -5:
                    self.player_style['project_focused'] += 0.5

            # 위험 감수 성향 분석 (큰 변화를 선택하는 경우)
            total_change = sum(abs(v) for v in stats.values())
            if total_change >= 30:
                # 매우 큰 변화
                self.player_style['risk_taking'] += 2
            elif total_change >= 20:
                # 큰 변화
                self.player_style['risk_taking'] += 1

    def get_play_summary(self):
        """플레이 요약 반환 (Gemini에게 전달할 컨텍스트)"""
        return {
            'current_stats': {
                'year': self.year,
                'period': self.period,
                'reputation': self.reputation,
                'budget_execution_rate': self.budget_execution_rate,
                'staff_morale': self.staff_morale,
                'project_success': self.project_success,
                'stress': self.stress,
                'wellbeing': self.wellbeing
            },
            'lifestyle_choices': {
                'car': self.car_choice,
                'housing': self.housing_choice,
                'leisure': self.leisure_choice,
                'meal': self.meal_choice
            },
            'visited_scenarios': self.visited_scenarios,
            'choice_history': self.choice_history[-5:] if len(self.choice_history) > 5 else self.choice_history,  # 최근 5개만
            'player_style': self.player_style,
            'major_decisions': self.major_decisions
        }

    def advance_time(self):
        """시간 진행 (격월)"""
        self.period += 1
        if self.period > 6:
            self.period = 1
            self.year += 1

    def check_game_over(self):
        """게임 오버 조건 확인"""
        if self.reputation <= 0:
            self.game_over = True
            self.ending = "reputation_loss"
            return True
        if self.staff_morale <= 0:
            self.game_over = True
            self.ending = "staff_revolt"
            return True
        if self.stress >= 100:
            self.game_over = True
            self.ending = "burnout"
            return True
        if self.wellbeing <= 0:
            self.game_over = True
            self.ending = "health_crisis"
            return True
        if self.year > 2:
            self.game_over = True
            self.calculate_final_ending()
            return True
        return False

    def will_cause_game_over(self, stat_changes):
        """선택이 게임 오버를 초래할지 확인"""
        temp_reputation = self.reputation
        temp_staff_morale = self.staff_morale
        temp_stress = self.stress
        temp_wellbeing = self.wellbeing

        if 'reputation' in stat_changes:
            temp_reputation += stat_changes['reputation']
        if 'staff_morale' in stat_changes:
            temp_staff_morale += stat_changes['staff_morale']
        if 'stress' in stat_changes:
            temp_stress += stat_changes['stress']
        if 'wellbeing' in stat_changes:
            temp_wellbeing += stat_changes['wellbeing']

        return temp_reputation <= 0 or temp_staff_morale <= 0 or temp_stress >= 100 or temp_wellbeing <= 0

    def calculate_final_ending(self):
        """최종 엔딩 계산"""
        # 예산 집행률 평가: 80-100%가 이상적 (100점), 그 외는 감점
        if 80 <= self.budget_execution_rate <= 100:
            budget_score = 100
        elif self.budget_execution_rate < 80:
            # 80% 미만은 선형 감점 (0%=0점, 80%=100점)
            budget_score = (self.budget_execution_rate / 80) * 100
        else:
            # 100% 초과는 없어야 하지만, 만약 있다면 100점으로 처리
            budget_score = 100

        total_score = (self.reputation + self.staff_morale + self.project_success + budget_score) / 4

        if total_score >= 80:
            self.ending = "legendary_director"
        elif total_score >= 65:
            self.ending = "successful_director"
        elif total_score >= 50:
            self.ending = "average_director"
        else:
            self.ending = "struggling_director"

    def display_status(self):
        """현재 상태 표시"""
        # 격월 단위를 월 범위로 변환
        period_months = {
            1: "1-2월", 2: "3-4월", 3: "5-6월",
            4: "7-8월", 5: "9-10월", 6: "11-12월"
        }
        period_str = period_months.get(self.period, f"{self.period}기")

        print("\n" + "="*60)
        print(f"📅 {self.year}년차 {period_str}")
        print("-"*60)
        print("💼 업무 스탯")
        print(f"🌟 평판: {self.reputation}/100 {'■' * (self.reputation//5)}{'□' * (20-self.reputation//5)}")
        print(f"💰 예산 집행률: {self.budget_execution_rate}/100 {'■' * (self.budget_execution_rate//5)}{'□' * (20-self.budget_execution_rate//5)}")
        print(f"😊 직원 만족도: {self.staff_morale}/100 {'■' * (self.staff_morale//5)}{'□' * (20-self.staff_morale//5)}")
        print(f"📊 프로젝트 성공도: {self.project_success}/100 {'■' * (self.project_success//5)}{'□' * (20-self.project_success//5)}")
        print("-"*60)
        print("🏠 생활 스탯")
        print(f"😰 스트레스: {self.stress}/100 {'■' * (self.stress//5)}{'□' * (20-self.stress//5)}")
        print(f"😌 웰빙: {self.wellbeing}/100 {'■' * (self.wellbeing//5)}{'□' * (20-self.wellbeing//5)}")
        print("-"*60)
        print("👥 부소장 사기")
        for deputy in self.deputies:
            morale_bar = '■' * (deputy['morale']//10) + '□' * (10-deputy['morale']//10)
            print(f"  • {deputy['name']}: {deputy['morale']}/100 {morale_bar}")
        print("\n👔 코디네이터 사기")
        for coordinator in self.coordinators:
            morale_bar = '■' * (coordinator['morale']//10) + '□' * (10-coordinator['morale']//10)
            print(f"  • {coordinator['name']}: {coordinator['morale']}/100 {morale_bar}")
        print("="*60 + "\n")


class GeminiIntegration:
    """Gemini API 연동 클래스 - 동적 시나리오 및 선택지 생성"""

    def __init__(self, api_key: Optional[str] = None):
        self.enabled = GEMINI_AVAILABLE and api_key is not None
        if self.enabled:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        else:
            self.model = None

    def generate_scenario(self, game_state: GameState) -> Optional[Dict]:
        """게임 상태를 기반으로 동적 시나리오 생성"""
        if not self.enabled:
            return None

        summary = game_state.get_play_summary()

        # 플레이어 스타일 분석
        style_desc = self._analyze_player_style(game_state.player_style)

        prompt = f"""
당신은 KOICA 해외사무소장 시뮬레이터 게임의 시나리오 작가입니다.
플레이어는 KOICA 48개국 해외사무소 중 한 곳의 사무소장으로서 15년 이상 경력의 전문가입니다.

## 조직 구성 (약 37명)
- 소장: 1명 (플레이어), 부소장: 2명, 코디네이터: 2명
- YP(영프로페셔널): 7명 (19-34세), 현지 직원: 17명 (4개 섹터)

## KOICA 예산 구조 (중요!)
**본부 (HQ)**:
- 외교부 등으로부터 전체 예산을 확보
- 사업 계획과 전략에 따라 각 국가별, 사업별로 예산을 편성하고 배정
- 전체적인 '예산집행지침' 마련 및 예산 이월 등 중요 변경사항 최종 승인

**해외사무소 (Offices)**:
- 본부로부터 사업별로 배정받은 예산을 집행하는 역할
- 실제 사업 현장에서 돈을 지출하고 정산하는 실무 담당
- **중요: 해외사무소는 배정받은 예산을 다른 사업으로 재배분할 권한 없음**
- **중요: 해외사무소는 자체적으로 예산을 늘릴 수 없음**

**따라서 시나리오 작성시 주의사항**:
- 본부가 신규 사업 추진을 요청할 때는 반드시 예산 추가 배정과 함께 와야 함
- "해외사무소가 예산을 추가로 헌신"하라는 요구는 구조적으로 불가능 (비현실적)
- 현지 사무소는 A 사업 예산을 B 사업으로 옮기는 재배분 권한 없음
- 추가 예산이 필요한 경우 본부에 요청하는 것이 정상적이고 자연스러운 절차
- 사무소장의 예산 관련 딜레마는 "배정받은 예산을 효율적으로 집행"이거나 "본부에 추가 예산 요청 여부"여야 함

## 사무소장의 6대 핵심 역할
1. **사업 발굴 및 형성**: 현지 수요조사, 국별협력전략(CPS) 수립, PCP 접수/검토
2. **사업 이행 및 관리**: 프로젝트 총괄, 착수/추진계획, 현장 모니터링, 평가/사후관리
3. **연수사업 지원**: 연수생 선발 추천, 비자 발급, 출국 지원, 귀국 후 평가
4. **해외봉사단 지원**: 단원 적응 훈련, 비자/신분증 관리, 안전관리, 활동 모니터링
5. **협력 네트워크**: 협력국 정부 정기 협의, 타 공여국(UN 등) 동향 파악, 민관합동 회의, NGO 간담회
6. **본부-협력국 중간 연결**: 정책 전달, 현지 상황 보고, 실시간 피드백, 의사소통 가교

## 사무소장의 직무 및 책임
- 조직 총괄: 인력/자산/회계 관리, 리더십, 팀워크 형성
- 사업 총괄: 최종 의사결정, 성과 및 예산 책임
- 대외 협력: 협력국 정부 고위급 협의, 재외공관(대사관) 협력, 국제기구 조율
- 위기관리: 파견 인력 안전 총괄, 긴급상황 대응
- 전략적 의사결정: 국별 협력전략 수립, 우선순위 설정, 자원 배분
- 소통 및 보고: 정기 본부 보고, 연례 해외사무소장 회의(48개국) 참석

## 현재 게임 상태
- 시기: {summary['current_stats']['year']}년차 {summary['current_stats']['period']}기 (격월 단위: 1=1-2월, 2=3-4월, 3=5-6월, 4=7-8월, 5=9-10월, 6=11-12월)
- 평판: {summary['current_stats']['reputation']}/100
- 예산 집행률: {summary['current_stats']['budget_execution_rate']}/100 (80-100%가 이상적)
- 직원 만족도: {summary['current_stats']['staff_morale']}/100
- 프로젝트 성공도: {summary['current_stats']['project_success']}/100

## 플레이어 성향
{style_desc}

## 최근 방문한 시나리오
{', '.join(summary['visited_scenarios'][-3:])}

## 요구사항
1. KOICA 해외사무소장이 직면하는 현실적인 상황을 제시하세요
2. 사무소장의 역할(사업 발굴, 파트너십, 인력 관리, 전략 수립 등)을 반영하세요
3. 플레이어의 현재 상태(특히 낮은 스탯)를 고려한 시나리오를 만드세요
4. 4개의 선택지를 제공하되, 각각 명확한 장단점이 있어야 합니다
5. 각 선택의 결과로 스탯 변화를 제안하세요 (reputation, budget, staff_morale, project_success)
   - budget 값은 예산 집행률 변화를 의미 (양수=집행률 상승, 음수=집행률 하락)
6. 결과 메시지(result.message)는 3-5문장으로 풍부하게 작성하세요:
   - 선택한 행동이 어떻게 실행되었는지
   - 이해관계자들(직원, 파트너, 본부 등)의 구체적인 반응
   - 최종적으로 어떤 결과와 영향이 발생했는지
   - 인과관계를 명확히 보여주세요

## 응답 형식 (반드시 JSON 형식으로)
{{
  "title": "시나리오 제목",
  "description": "상황 설명 (3-5문장)",
  "choices": [
    {{
      "text": "선택지 텍스트",
      "result": {{
        "message": "결과 설명",
        "stats": {{
          "reputation": 변화값 (-30~30),
          "budget": 변화값 (-40~40),
          "staff_morale": 변화값 (-30~30),
          "project_success": 변화값 (-30~30)
        }}
      }}
    }}
  ]
}}

중요: 순수 JSON만 반환하세요. 추가 설명이나 마크다운 코드 블록 없이.
"""

        try:
            response = self.model.generate_content(prompt)
            scenario_json = self._extract_json(response.text)

            if scenario_json:
                # advance_time과 next 필드 추가
                for choice in scenario_json.get('choices', []):
                    choice['result']['advance_time'] = True
                    choice['result']['next'] = 'ai_generated'  # AI 생성 시나리오는 계속 AI 생성

                return scenario_json
            else:
                print("Warning: Failed to parse AI response as JSON")
                return None

        except Exception as e:
            print(f"Error generating scenario: {e}")
            return None

    def generate_free_form_result(self, game_state: GameState, player_action: str) -> Optional[Dict]:
        """플레이어의 자유 입력에 대한 결과 생성"""
        if not self.enabled:
            return None

        summary = game_state.get_play_summary()
        current_scenario = game_state.current_scenario

        prompt = f"""
당신은 KOICA 해외사무소장 시뮬레이터 게임의 게임 마스터입니다.
플레이어는 KOICA 48개국 해외사무소 중 한 곳의 사무소장으로서 약 37명(부소장 2명, 코디네이터 2명, YP 7명, 현지 직원 17명)을 총괄합니다.
플레이어가 자유롭게 입력한 행동에 대해 결과를 판정하고 스탯 변화를 계산하세요.

## KOICA 예산 구조 (중요!)
**본부**: 전체 예산 확보 및 사업별로 각 해외사무소에 배정
**해외사무소**: 본부로부터 사업별로 배정받은 예산을 집행하는 역할
**중요**:
- 해외사무소는 A 사업 예산을 B 사업으로 재배분할 권한 없음
- 해외사무소는 자체적으로 예산을 늘릴 수 없음
- 추가 예산이 필요하면 본부에 요청하는 것이 정상적이고 자연스러운 절차

## 사무소장의 6대 핵심 역할과 권한
1. 사업 발굴 및 형성 (CPS 수립, PCP 검토)
2. 사업 이행 및 관리 (프로젝트 총괄, 모니터링, 평가)
3. 연수사업 지원 (연수생 선발, 출국 지원)
4. 해외봉사단 지원 (안전 관리, 활동 모니터링)
5. 협력 네트워크 구축 (정부/UN/NGO 협의, 재외공관 협력)
6. 본부-협력국 중간 연결 (보고, 조율, 피드백)

## 사무소장의 직무 권한
- 조직 총괄: 약 37명 인력 관리, 자산/회계 책임
- 최종 의사결정권자: 모든 사업의 승인 권한
- 외교관 준하는 지위: 수원국 장관급 면담
- 위기관리 총괄: 파견 인력 안전 최종 책임

## 현재 상황
- 시기: {summary['current_stats']['year']}년차 {summary['current_stats']['period']}기 (격월 단위: 1=1-2월, 2=3-4월, 3=5-6월, 4=7-8월, 5=9-10월, 6=11-12월)
- 평판: {summary['current_stats']['reputation']}/100
- 예산 집행률: {summary['current_stats']['budget_execution_rate']}/100 (80-100%가 이상적)
- 직원 만족도: {summary['current_stats']['staff_morale']}/100
- 프로젝트 성공도: {summary['current_stats']['project_success']}/100

## 플레이어의 행동
"{player_action}"

## 요구사항
1. 플레이어의 행동을 최대한 수용하세요. 사무소장으로서 할 수 있는 다양한 창의적 시도를 긍정적으로 해석하세요
2. 행동의 결과를 3-5문장으로 풍부하게 설명하세요:
   - 첫 문장: 즉각적인 결과나 반응
   - 중간 문장들: 구체적인 과정과 영향 (누가 어떻게 반응했는지, 어떤 변화가 일어났는지)
   - 마지막 문장: 최종 결과와 조직/개인에 미친 영향
3. 4가지 스탯에 미치는 영향을 계산하세요 (합리적인 범위 내에서)
4. 창의적이고 전략적인 행동은 적극 보상하세요
5. 극단적으로 비윤리적이거나 범죄적인 행동이 아닌 이상 success: true로 처리하세요
6. 인과관계를 명확히: "이 행동으로 인해 → 이런 일이 발생 → 그 결과" 흐름을 자연스럽게 서술하세요

## 응답 형식 (반드시 JSON 형식으로)
{{
  "success": true/false,
  "message": "결과 설명",
  "stats": {{
    "reputation": 변화값,
    "budget": 변화값,
    "staff_morale": 변화값,
    "project_success": 변화값
  }}
}}

중요: 순수 JSON만 반환하세요.
"""

        try:
            response = self.model.generate_content(prompt)
            result_json = self._extract_json(response.text)
            return result_json
        except Exception as e:
            print(f"Error processing free-form input: {e}")
            return None

    def generate_personalized_ending(self, game_state: GameState) -> str:
        """플레이어의 플레이 스타일을 분석하여 개인화된 엔딩 생성"""
        if not self.enabled:
            return ""

        summary = game_state.get_play_summary()
        total_score = (game_state.reputation + game_state.staff_morale +
                      game_state.project_success + game_state.budget / 2) / 3.5

        prompt = f"""
당신은 KOICA 소장 시뮬레이터 게임의 엔딩 작가입니다.
플레이어의 2년간의 여정을 분석하여 개인화된 엔딩 내러티브를 작성하세요.

## 최종 스탯
- 평판: {game_state.reputation}/100
- 예산 집행률: {game_state.budget_execution_rate}/100
- 직원 만족도: {game_state.staff_morale}/100
- 프로젝트 성공도: {game_state.project_success}/100
- 총점: {total_score:.1f}/100

## 플레이어 성향
{self._analyze_player_style(game_state.player_style)}

## 주요 결정
{self._format_major_decisions(game_state.choice_history[-10:])}

## 요구사항
1. 플레이어의 선택과 성향을 반영한 맞춤형 엔딩을 작성하세요
2. 3-5개의 문단으로 구성하세요
3. 플레이어의 유산(legacy)과 장기적 영향을 설명하세요
4. 감동적이고 의미있는 마무리를 제공하세요

엔딩 내러티브를 작성하세요:
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating personalized ending: {e}")
            return ""

    def _extract_json(self, text: str) -> Optional[Dict]:
        """텍스트에서 JSON 추출"""
        # 마크다운 코드 블록 제거
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # JSON 파싱 시도
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # JSON 객체 찾기 시도
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    return None
            return None

    def _analyze_player_style(self, player_style: Dict) -> str:
        """플레이어 스타일 분석"""
        styles = []

        max_value = max(player_style.values()) if player_style.values() else 0

        if max_value == 0:
            return "초기 단계로 아직 명확한 성향이 드러나지 않았습니다."

        if player_style['reputation_focused'] == max_value:
            styles.append("평판과 관계를 중시하는 외교적 리더")
        if player_style['budget_focused'] == max_value:
            styles.append("재정 관리를 중시하는 실무형 관리자")
        if player_style['staff_focused'] == max_value:
            styles.append("팀워크와 직원 복지를 우선하는 인본주의자")
        if player_style['project_focused'] == max_value:
            styles.append("프로젝트 성과를 최우선하는 완벽주의자")

        risk_level = player_style.get('risk_taking', 0)
        if risk_level > 3:
            styles.append("대담한 결정을 내리는 혁신가")
        elif risk_level < 2:
            styles.append("신중하고 안정적인 전략가")

        return ", ".join(styles) if styles else "균형잡힌 접근을 시도하는 리더"

    def _format_major_decisions(self, choices: List[Dict]) -> str:
        """주요 결정 포맷팅"""
        if not choices:
            return "아직 중요한 결정을 내리지 않았습니다."

        formatted = []
        for choice in choices[-5:]:  # 마지막 5개만
            formatted.append(f"- {choice.get('scenario_id', '알 수 없음')}: {choice.get('choice_text', '선택 없음')}")

        return "\n".join(formatted)


class KOICAGame:
    """메인 게임 클래스"""

    def __init__(self, ai_mode: bool = False, api_key: Optional[str] = None, demo_mode: bool = False):
        self.state = GameState()
        self.scenarios = self.load_scenarios()
        self.ai_mode = ai_mode
        self.gemini = GeminiIntegration(api_key) if ai_mode else None
        self.demo_mode = demo_mode

    def load_scenarios(self):
        """시나리오 데이터 로드"""
        try:
            with open('scenarios.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("오류: scenarios.json 파일을 찾을 수 없습니다.")
            sys.exit(1)

    def clear_screen(self):
        """화면 지우기"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def display_intro(self):
        """인트로 화면"""
        self.clear_screen()
        print("\n" + "="*60)
        print(" "*15 + "KOICA 해외사무소장 시뮬레이터")
        print("="*60)
        if self.demo_mode:
            print(" "*20 + "🤖 [데모 모드]")
            print("="*60)
        print("\n당신은 KOICA 해외사무소장으로 새로 부임했습니다.")
        print("\n🌏 KOICA는 전 세계 48개국에 해외사무소를 운영하며,")
        print("   대한민국 무상원조사업을 현장에서 직접 실행합니다.")
        print("\n📊 당신의 사무소 조직 구성:")
        print("   • 사무소장: 1명 (당신)")
        print("   • 부소장: 2명 (사업 책임자)")
        print("   • 코디네이터: 2명 (사업 실무 담당)")
        print("   • YP(영프로페셔널): 7명 (만 19-34세 청년인재)")
        print("   • 현지 직원: 17명 (4개 섹터 지원)")
        print("\n👔 사무소장으로서 당신의 6대 핵심 역할:")
        print("   1️⃣  사업 발굴 및 형성 (신규 사업, CPS 수립)")
        print("   2️⃣  사업 이행 및 관리 (프로젝트 총괄, 모니터링, 평가)")
        print("   3️⃣  연수사업 지원 (연수생 선발, 출국/귀국 관리)")
        print("   4️⃣  해외봉사단 지원 (단원 안전 관리, 활동 모니터링)")
        print("   5️⃣  협력 네트워크 구축 (정부, UN, 타 공여국, NGO)")
        print("   6️⃣  본부-협력국 간 중간 연결 (소통, 보고, 조율)")
        print("\n🎯 앞으로 2년(격월 12회 선택) 동안의 임기 동안,")
        print("   당신의 결정이 프로젝트의 성공, 팀의 사기,")
        print("   그리고 국제 협력의 미래를 만들어갑니다.")
        print("\n⚠️  15년 이상 경력의 전문가로서, 외교관에 준하는")
        print("   지위로 수원국 장관급 인사와 협의할 것입니다.")
        print("\n" + "─"*60)
        print("📋 게임 오버 조건 (반드시 숙지하세요!)")
        print("─"*60)
        print("다음 조건 중 하나라도 해당되면 게임이 즉시 종료됩니다:")
        print("  • 평판이 0 이하 → 평판 실추로 본부 소환")
        print("  • 직원 만족도가 0 이하 → 직원 반발로 사임")
        print("  • 스트레스가 100 이상 → 번아웃으로 긴급 귀국")
        print("  • 웰빙이 0 이하 → 건강 위기로 의료 후송")
        print("\n💡 위험한 선택을 할 때는 경고가 표시됩니다.")
        print("   각 상황에서 신중하게 선택하세요!")
        print("="*60 + "\n")

        if not self.demo_mode:
            input("Enter를 눌러 시작...")
        else:
            print("🤖 [데모 모드] 자동으로 게임을 시작합니다...")
            time.sleep(2)

    def initial_lifestyle_setup(self):
        """게임 시작 시 초기 생활 선택"""
        self.clear_screen()
        print("\n" + "="*60)
        print(" "*15 + "해외 생활 준비하기")
        print("="*60)
        print("\n부임 전, 몇 가지 생활 관련 결정을 내려야 합니다.")
        print("이 선택들은 앞으로 2년간의 생활에 영향을 미칩니다.\n")

        # 1. 자동차 선택
        print("="*60)
        print("🚗 자동차는 어떻게 하시겠습니까?")
        print("="*60)
        print("1. 한국에서 자동차를 가져간다 (익숙하지만 비용과 수리가 문제)")
        print("2. 현지에서 중고차를 구입한다 (저렴하지만 품질이 불확실)")
        print("3. 자동차 없이 택시와 대중교통 이용 (자유롭지만 불편)")

        if self.demo_mode:
            car_choice = random.randint(1, 3)
            print(f"\n🤖 [데모 모드] 선택: {car_choice}")
            time.sleep(1)
        else:
            car_choice = self._get_choice_input(3)

        car_effects = {
            1: {"stress": -3, "wellbeing": 4, "choice": "bring_from_korea"},
            2: {"stress": 4, "wellbeing": -2, "choice": "buy_local"},
            3: {"stress": 6, "wellbeing": -4, "choice": "no_car"}
        }
        self.state.car_choice = car_effects[car_choice]["choice"]
        self.state.update_stats({"stress": car_effects[car_choice]["stress"],
                                  "wellbeing": car_effects[car_choice]["wellbeing"]})

        # 2. 주거지 선택
        print("\n" + "="*60)
        print("🏠 주거지는 어떤 곳을 구하시겠습니까?")
        print("="*60)
        print("1. 넓은 집 (여유 공간, 하지만 먼 거리)")
        print("2. 좋은 집 (새 건물, 고급 시설, 하지만 월세 부분 자부담)")
        print("3. 사무소 가까운 집 (출퇴근 편리, 하지만 좁고 오래됨)")
        print("4. 치안 좋은 동네 집 (안전, 하지만 시내에서 멀고 심심함)")

        if self.demo_mode:
            housing_choice = random.randint(1, 4)
            print(f"\n🤖 [데모 모드] 선택: {housing_choice}")
            time.sleep(1)
        else:
            housing_choice = self._get_choice_input(4)

        housing_effects = {
            1: {"stress": -2, "wellbeing": 6, "choice": "spacious"},
            2: {"stress": -3, "wellbeing": 7, "budget": -3, "choice": "nice"},
            3: {"stress": -6, "wellbeing": -3, "choice": "near_office"},
            4: {"stress": -3, "wellbeing": 2, "choice": "secure"}
        }
        self.state.housing_choice = housing_effects[housing_choice]["choice"]
        self.state.update_stats({k: v for k, v in housing_effects[housing_choice].items() if k != "choice"})

        # 3. 여가 생활 선택
        print("\n" + "="*60)
        print("🎮 여가 생활은 어떻게 보내시겠습니까?")
        print("="*60)
        print("1. 독서 (조용하고 지적인 시간)")
        print("2. 운동 (건강 관리와 스트레스 해소)")
        print("3. 음주 (직원들과 친목, 하지만 건강 염려)")
        print("4. 집에서 뒹굴기 (편안한 휴식)")

        if self.demo_mode:
            leisure_choice = random.randint(1, 4)
            print(f"\n🤖 [데모 모드] 선택: {leisure_choice}")
            time.sleep(1)
        else:
            leisure_choice = self._get_choice_input(4)

        leisure_effects = {
            1: {"stress": -5, "wellbeing": 4, "choice": "reading"},
            2: {"stress": -6, "wellbeing": 10, "choice": "exercise"},
            3: {"stress": -3, "wellbeing": -3, "staff_morale": 4, "choice": "drinking"},
            4: {"stress": -2, "wellbeing": 2, "choice": "gaming"}
        }
        self.state.leisure_choice = leisure_effects[leisure_choice]["choice"]
        self.state.update_stats({k: v for k, v in leisure_effects[leisure_choice].items() if k != "choice"})

        # 4. 식사 방식 선택
        print("\n" + "="*60)
        print("🍽️ 식사는 어떻게 해결하시겠습니까?")
        print("="*60)
        print("1. 집에서 직접 요리 (건강하지만 시간 소요)")
        print("2. 외식 위주 (편리하지만 비용과 건강)")
        print("3. 배달&포장 (편리하고 시간 절약, 하지만 배달비 부담)")

        if self.demo_mode:
            meal_choice = random.randint(1, 3)
            print(f"\n🤖 [데모 모드] 선택: {meal_choice}")
            time.sleep(1)
        else:
            meal_choice = self._get_choice_input(3)

        meal_effects = {
            1: {"stress": 3, "wellbeing": 7, "choice": "cook_at_home"},
            2: {"stress": -2, "wellbeing": -3, "budget": -3, "choice": "eat_out"},
            3: {"stress": 0, "wellbeing": 2, "budget": -1, "choice": "mixed"}
        }
        self.state.meal_choice = meal_effects[meal_choice]["choice"]
        self.state.update_stats({k: v for k, v in meal_effects[meal_choice].items() if k != "choice"})

        # 결과 요약
        print("\n" + "="*60)
        print("✅ 생활 준비가 완료되었습니다!")
        print("="*60)
        print("\n선택하신 내용:")
        car_desc = {
            "bring_from_korea": "한국에서 가져온 자동차",
            "buy_local": "현지에서 구입한 중고차",
            "no_car": "자동차 없이 대중교통"
        }
        housing_desc = {
            "spacious": "넓은 집",
            "nice": "좋은 집",
            "near_office": "사무소 가까운 집",
            "secure": "치안 좋은 동네 집"
        }
        leisure_desc = {
            "reading": "독서",
            "exercise": "운동",
            "drinking": "음주",
            "gaming": "집에서 뒹굴기"
        }
        meal_desc = {
            "cook_at_home": "집에서 요리",
            "eat_out": "외식 위주",
            "mixed": "배달&포장"
        }

        print(f"🚗 자동차: {car_desc[self.state.car_choice]}")
        print(f"🏠 주거: {housing_desc[self.state.housing_choice]}")
        print(f"🎮 여가: {leisure_desc[self.state.leisure_choice]}")
        print(f"🍽️ 식사: {meal_desc[self.state.meal_choice]}")
        print("\n이제 본격적인 사무소장 업무를 시작합니다!")
        print("="*60 + "\n")

        if not self.demo_mode:
            input("Enter를 눌러 계속...")
        else:
            time.sleep(2)

    def _get_choice_input(self, max_choice):
        """선택 입력 헬퍼 함수"""
        while True:
            try:
                choice = int(input(f"\n선택 (1-{max_choice}): ").strip())
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    print(f"1부터 {max_choice} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n\n게임을 종료합니다.")
                sys.exit(0)

    def check_and_trigger_life_event(self):
        """주기적 생활 이벤트 발생 확인 - 전체 플레이 동안 최대 4회 랜덤 발생"""
        # 운동 습관의 패시브 효과: 웰빙 하락 방어
        if self.state.leisure_choice == "exercise" and self.state.wellbeing < 40:
            # 운동 습관이 웰빙 하락을 방어해 줌
            self.state.update_stats({'wellbeing': 5, 'stress': -5})
            print("\n💪 [운동 습관 효과] 규칙적인 운동으로 정신 건강이 개선되었습니다. (웰빙 +5, 스트레스 -5)")

        # 이미 4회 발생했으면 더 이상 발생하지 않음
        if self.state.life_events_count >= 4:
            return None

        # 기본 확률 계산 (2년 12 periods 동안 평균 4회 발생하도록 조정)
        # 남은 횟수에 따라 확률 동적 조정
        remaining_events = 4 - self.state.life_events_count
        remaining_periods = (2 - self.state.year) * 6 + (6 - self.state.period) + 1

        # 남은 기간이 없으면 발생 안 함
        if remaining_periods <= 0:
            return None

        # 기본 확률: 남은 이벤트 수 / 남은 기간 수
        base_chance = remaining_events / remaining_periods

        # 최소 15%, 최대 50% 확률로 제한
        base_chance = max(0.15, min(0.50, base_chance))

        # 스트레스/웰빙 상태에 따라 확률 조정
        if self.state.stress > 70:
            base_chance += 0.10  # 스트레스 높으면 이벤트 확률 증가
        if self.state.wellbeing < 30:
            base_chance += 0.10  # 웰빙 낮으면 이벤트 확률 증가

        # 확률을 60%로 제한 (너무 자주 발생하지 않도록)
        base_chance = min(0.60, base_chance)

        # 랜덤으로 이벤트 발생 여부 결정
        if random.random() < base_chance:
            event = self.select_life_event()
            if event:
                # 중복 방지를 위해 추적 세트에 즉시 추가
                self.state.triggered_life_events.add(event)
                # 생활 이벤트 발생 횟수 증가
                self.state.life_events_count += 1
            return event
        return None

    def select_life_event(self):
        """모든 타입의 이벤트 선택 - 생활, 서사, 부소장, 연차별 이벤트 포함 (최대 4회 발생)"""
        available_events = []

        # === 생활 이벤트 (생활 선택과 연동) ===
        # 건강 이벤트 (웰빙 낮을 때) - 음주 습관 + 스트레스 시 확률 증가
        if self.state.wellbeing < 40 and "life_event_health_issue" not in self.state.triggered_life_events:
            weight = 3
            # 음주 + 스트레스 조합은 건강 위험 증가
            if self.state.leisure_choice == "drinking" and self.state.stress > 60:
                weight = 6  # 확률 2배 증가
            available_events.append(("life_event_health_issue", weight))

        # 향수병 (기간에 따라 - 5-6개월 이상 지났을 때)
        if self.state.year >= 1 and self.state.period >= 3 and "life_event_homesickness" not in self.state.triggered_life_events:
            available_events.append(("life_event_homesickness", 2))

        # 심리적 압박 (스트레스 높을 때)
        if self.state.stress > 60 and "life_event_psychological_pressure" not in self.state.triggered_life_events:
            available_events.append(("life_event_psychological_pressure", 3))

        # 자동차 고장 (자동차가 있는 경우) - 현지 중고차는 고장 확률 높음
        if self.state.car_choice in ["bring_from_korea", "buy_local"] and "life_event_car_breakdown" not in self.state.triggered_life_events:
            weight = 1
            if self.state.car_choice == "buy_local":
                weight = 4  # 현지 중고차는 고장 확률 4배
            available_events.append(("life_event_car_breakdown", weight))

        # 주거 문제 (모든 경우) - 사무실 근처 집은 문제 발생 확률 높음
        if "life_event_housing_issue" not in self.state.triggered_life_events:
            weight = 1
            if self.state.housing_choice == "near_office":
                weight = 3  # 좁고 오래된 집은 문제 발생 확률 3배
            available_events.append(("life_event_housing_issue", weight))

        # === 서사 이벤트 ===

        # --- 긍정적 이벤트 (높은 stat 요구) ---
        if self.state.project_success >= 70 and self.state.year >= 1 and "narrative_event_project_opening" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_project_opening", 2))

        if self.state.staff_morale >= 60 and "narrative_event_volunteer_success" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_volunteer_success", 2))

        if self.state.project_success >= 60 and self.state.year >= 1 and "narrative_event_partner_growth" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_partner_growth", 2))

        if self.state.project_success >= 65 and "narrative_event_unexpected_impact" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_unexpected_impact", 2))

        if self.state.reputation >= 60 and "narrative_event_emergency_relief" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_emergency_relief", 1))

        if self.state.staff_morale >= 60 and self.state.year >= 1 and "narrative_event_staff_wedding" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_staff_wedding", 2))

        if self.state.reputation >= 60 and self.state.period >= 1 and "narrative_event_new_year_letters" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_new_year_letters", 1))

        if self.state.reputation >= 70 and self.state.year >= 1 and "narrative_event_minister_trust" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_minister_trust", 2))

        if self.state.staff_morale >= 65 and "narrative_event_staff_dedication" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_staff_dedication", 2))

        if self.state.project_success >= 75 and self.state.reputation >= 75 and "narrative_event_international_award" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_international_award", 1))

        if self.state.reputation >= 70 and "narrative_event_media_interview" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_media_interview", 2))

        # --- 부정적 이벤트 (낮은 stat 또는 위기 상황) ---
        if self.state.period == 6 and "narrative_event_policy_shift" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_policy_shift", 2))

        if self.state.period >= 10 and self.state.budget_execution_rate < 70 and "narrative_event_budget_pressure" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_budget_pressure", 3))

        if "narrative_event_volunteer_safety" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_volunteer_safety", 1))

        if self.state.year >= 1 and "narrative_event_regime_change" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_regime_change", 1))

        if self.state.reputation < 60 and "narrative_event_jica_competition" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_jica_competition", 2))

        if (self.state.period == 9 or self.state.period == 3) and "narrative_event_audit" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_audit", 2))

        if (self.state.period == 5 or self.state.period == 11) and "narrative_event_congress_visit" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_congress_visit", 2))

        if self.state.stress > 50 and self.state.staff_morale < 50 and "narrative_event_yp_adaptation_failure" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_yp_adaptation_failure", 2))

        if "narrative_event_currency_crisis" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_currency_crisis", 1))

        if "narrative_event_corruption_pressure" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_corruption_pressure", 1))

        if self.state.project_success < 60 and "narrative_event_harsh_evaluation" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_harsh_evaluation", 2))

        if self.state.reputation < 50 and "narrative_event_media_attack" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_media_attack", 2))

        # --- 양면적 이벤트 (복잡한 선택지) ---
        if "narrative_event_china_proposal" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_china_proposal", 1))

        if "narrative_event_hq_unrealistic_schedule" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_hq_unrealistic_schedule", 1))

        if self.state.year >= 1 and "narrative_event_staff_salary_demand" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_staff_salary_demand", 2))

        if "narrative_event_ppp_suspicion" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_ppp_suspicion", 1))

        if "narrative_event_gender_culture" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_gender_culture", 1))

        if (self.state.period == 4 or self.state.period == 10) and "narrative_event_ramadan_schedule" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_ramadan_schedule", 1))

        if self.state.project_success < 50 and "narrative_event_admitting_failure" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_admitting_failure", 2))

        if self.state.staff_morale >= 50 and "narrative_event_volunteer_social_enterprise" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_volunteer_social_enterprise", 1))

        if "narrative_event_family_emergency" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_family_emergency", 1))

        if "narrative_event_local_crisis_support" not in self.state.triggered_life_events:
            available_events.append(("narrative_event_local_crisis_support", 1))

        # === 부소장 관련 이벤트 ===
        # 특정 부소장의 사기가 낮을 때
        low_morale_deputies = self.state.get_low_morale_deputies(threshold=30)
        if low_morale_deputies and "deputy_event_low_morale" not in self.state.triggered_life_events:
            available_events.append(("deputy_event_low_morale", 3))

        # 부소장 간 갈등
        if self.state.year >= 1 and self.state.period >= 3 and "deputy_event_conflict" not in self.state.triggered_life_events:
            available_events.append(("deputy_event_conflict", 2))

        # === 연차별 특화 이벤트 ===
        # 1년차 전용: 신임 소장 적응
        if self.state.year == 1 and self.state.period <= 3 and "year1_event_adaptation" not in self.state.triggered_life_events:
            available_events.append(("year1_event_adaptation", 2))

        # 2년차 전용: 본부 정기 감사
        if self.state.year == 2 and self.state.period >= 2 and "year2_event_audit" not in self.state.triggered_life_events:
            available_events.append(("year2_event_audit", 3))

        # 2년차 전용: 임기 말 평가 압박
        if self.state.year == 2 and self.state.period >= 9 and "year2_event_final_evaluation" not in self.state.triggered_life_events:
            available_events.append(("year2_event_final_evaluation", 4))

        # 2년차 전용: 차기 CPS 구상
        if self.state.year == 2 and self.state.period >= 6 and "year2_event_cps_planning" not in self.state.triggered_life_events:
            available_events.append(("year2_event_cps_planning", 2))

        if not available_events:
            return None

        # 가중치를 고려한 랜덤 선택
        events = [e[0] for e in available_events]
        weights = [e[1] for e in available_events]
        total_weight = sum(weights)
        rand = random.uniform(0, total_weight)

        cumulative = 0
        for event, weight in zip(events, weights):
            cumulative += weight
            if rand <= cumulative:
                return event

        return events[0]  # 폴백

    # ============================================================
    # 고급 기능: 부소장 임계값 이벤트 체크
    # ============================================================

    def check_deputy_threshold_events(self):
        """부소장 임계값 이벤트 체크 (morale, 프로젝트 성공도, 평판)"""
        # Backward compatibility: Initialize triggered_deputy_events if it doesn't exist
        if not hasattr(self.state, 'triggered_deputy_events'):
            self.state.triggered_deputy_events = set()

        # 전체 이벤트 발생 횟수 제한 체크 (4회)
        if self.state.life_events_count >= 4:
            return None

        deputy_principled = self.state.get_deputy_by_personality("principled")
        deputy_local = self.state.get_deputy_by_personality("local_friendly")

        if not deputy_principled or not deputy_local:
            return None

        event_id = None

        # 김태영 부소장 효율성 우려 이벤트 (프로젝트 성공도 낮을 때)
        if (self.state.project_success <= 30 and
            'deputy_principled_efficiency_concern' not in self.state.triggered_deputy_events):
            event_id = 'deputy_principled_efficiency_concern'
        # 이수진 부소장 투명성 우려 이벤트 (평판 낮을 때)
        elif (self.state.reputation <= 30 and
            'deputy_local_friendly_transparency_concern' not in self.state.triggered_deputy_events):
            event_id = 'deputy_local_friendly_transparency_concern'
        # 김태영 부소장 고충성도 이벤트
        elif (deputy_principled['morale'] >= 50 and
            'deputy_principled_high_loyalty' not in self.state.triggered_deputy_events):
            event_id = 'deputy_principled_high_loyalty'
        # 김태영 부소장 전보 위기 이벤트
        elif (deputy_principled['morale'] <= 20 and
            'deputy_principled_low_resignation' not in self.state.triggered_deputy_events):
            event_id = 'deputy_principled_low_resignation'
        # 이수진 부소장 네트워크 보너스 이벤트
        elif (deputy_local['morale'] >= 50 and
            'deputy_local_friendly_network_bonus' not in self.state.triggered_deputy_events):
            event_id = 'deputy_local_friendly_network_bonus'
        # 이수진 부소장 문화 갈등 이벤트
        elif (deputy_local['morale'] <= 20 and
            'deputy_local_friendly_cultural_crisis' not in self.state.triggered_deputy_events):
            event_id = 'deputy_local_friendly_cultural_crisis'

        # 이벤트가 선택되면 카운트 증가 및 추적 세트에 추가
        if event_id:
            self.state.triggered_deputy_events.add(event_id)
            self.state.life_events_count += 1

        return event_id

    # ============================================================
    # 고급 기능: 장기 영향(delayed effects) 체크
    # ============================================================

    def check_delayed_effects(self):
        """대기 중인 장기 효과 체크 및 발동"""
        # Backward compatibility: Initialize pending_delayed_effects if it doesn't exist
        if not hasattr(self.state, 'pending_delayed_effects'):
            self.state.pending_delayed_effects = []

        triggered_effects = []

        for effect in self.state.pending_delayed_effects[:]:  # 복사본 순회
            # trigger_period 체크
            current_period_number = (self.state.year - 1) * 6 + self.state.period
            if current_period_number >= effect.get('trigger_period', 0):
                # condition 체크
                condition = effect.get('condition', 'always')

                should_trigger = False
                if condition == 'always':
                    should_trigger = True
                elif condition.startswith('random'):
                    # "random < 0.3" 같은 조건
                    prob = float(condition.split('<')[1].strip())
                    if random.random() < prob:
                        should_trigger = True
                elif '>=' in condition:
                    # "project_success >= 50" 같은 조건
                    stat_name, threshold = condition.split('>=')
                    stat_name = stat_name.strip()
                    threshold = int(threshold.strip())
                    current_value = getattr(self.state, stat_name, 0)
                    if current_value >= threshold:
                        should_trigger = True
                elif '<=' in condition:
                    stat_name, threshold = condition.split('<=')
                    stat_name = stat_name.strip()
                    threshold = int(threshold.strip())
                    current_value = getattr(self.state, stat_name, 0)
                    if current_value <= threshold:
                        should_trigger = True

                if should_trigger:
                    triggered_effects.append(effect)
                    self.state.pending_delayed_effects.remove(effect)

        return triggered_effects

    # ============================================================
    # 고급 기능: 게임 오버 조건 확장
    # ============================================================

    def check_advanced_endings(self):
        """고급 엔딩 조건 체크"""
        # Backward compatibility: Initialize ethics_violations if it doesn't exist
        if not hasattr(self.state, 'ethics_violations'):
            self.state.ethics_violations = 0

        # 번아웃 엔딩
        if self.state.stress >= 100 or self.state.wellbeing <= 0:
            return 'ending_burnout'

        # 평판 추락 엔딩
        if self.state.reputation <= 0:
            return 'ending_reputation_collapse'

        # 윤리 위반 엔딩
        if self.state.ethics_violations >= 3:
            return 'ending_ethical_crisis'

        # 완벽한 균형 엔딩 (임기 종료 시)
        if self.state.year >= 2 and self.state.period >= 6:
            # 모든 스탯이 80 이상
            if (self.state.reputation >= 80 and
                self.state.project_success >= 80 and
                self.state.staff_morale >= 80 and
                self.state.budget_execution_rate >= 70):
                # 양측 부소장 모두 높은 morale
                deputy_principled = self.state.get_deputy_by_personality("principled")
                deputy_local = self.state.get_deputy_by_personality("local_friendly")
                if (deputy_principled and deputy_local and
                    deputy_principled['morale'] >= 40 and
                    deputy_local['morale'] >= 40):
                    return 'ending_perfect_balance'

        return None

    def display_scenario(self, scenario_id):
        """시나리오 표시 (AI 생성 지원)"""
        # AI 모드에서 'ai_generated' 시나리오 ID인 경우 동적 생성
        if self.ai_mode and scenario_id == 'ai_generated':
            print("\n🤖 AI가 맞춤형 시나리오를 생성중입니다...\n")
            scenario = self.gemini.generate_scenario(self.state)

            if not scenario:
                print("AI 시나리오 생성 실패. 기본 시나리오를 사용합니다.")
                # 폴백: 랜덤 시나리오 선택
                import random
                fallback_scenarios = ['budget_crisis_1', 'cultural_conflict', 'staff_problem_1']
                scenario_id = random.choice(fallback_scenarios)
                scenario = self.scenarios.get(scenario_id)
        else:
            scenario = self.scenarios.get(scenario_id)

        if not scenario:
            print(f"오류: 시나리오 '{scenario_id}'를 찾을 수 없습니다.")
            return None

        self.clear_screen()
        self.state.display_status()

        print(f"📖 {scenario['title']}\n")
        print(scenario['description'])
        print()

        return scenario

    def display_choices(self, choices):
        """선택지 표시 및 입력 받기 (자유 입력 모드 지원)"""
        print("\n선택하세요:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")

        # AI 모드에서는 자유 입력 옵션 추가
        if self.ai_mode and self.gemini.enabled:
            print(f"{len(choices) + 1}. 💡 직접 행동 입력하기 (자유 입력)")

        # 데모 모드: 자동 선택
        if self.demo_mode:
            time.sleep(1.5)  # 읽을 시간 제공
            # 균형잡힌 선택을 위한 가중치 기반 선택
            choice_index = self._demo_choose(choices)
            print(f"\n🤖 [데모 모드] 선택: {choice_index + 1}. {choices[choice_index]['text']}")
            time.sleep(1)
            return choice_index

        while True:
            try:
                choice_input = input("\n선택 (번호 입력): ").strip()
                choice_num = int(choice_input)

                # 자유 입력 모드
                if self.ai_mode and choice_num == len(choices) + 1:
                    return -1  # 자유 입력 신호

                if 1 <= choice_num <= len(choices):
                    return choice_num - 1
                else:
                    print(f"1부터 {len(choices) + (1 if self.ai_mode else 0)} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n\n게임을 종료합니다.")
                sys.exit(0)

    def _demo_choose(self, choices) -> int:
        """데모 모드에서 균형잡힌 선택을 위한 로직"""
        # 각 선택지의 스탯 영향을 평가
        choice_scores = []

        for i, choice in enumerate(choices):
            score = 0
            if 'result' in choice and 'stats' in choice['result']:
                stats = choice['result']['stats']

                # 낮은 스탯을 올리는 선택에 가중치 부여
                if 'reputation' in stats:
                    if self.state.reputation < 40 and stats['reputation'] > 0:
                        score += 3
                    elif stats['reputation'] < 0 and self.state.reputation > 60:
                        score += 1

                if 'budget' in stats:
                    # 예산 집행률을 80-100% 범위로 맞추는 선택 선호
                    if self.state.budget_execution_rate < 60 and stats['budget'] > 0:
                        score += 3
                    elif self.state.budget_execution_rate >= 80:
                        # 이미 적정 수준이면 현상 유지 선택
                        if abs(stats['budget']) < 5:
                            score += 2

                if 'staff_morale' in stats:
                    if self.state.staff_morale < 40 and stats['staff_morale'] > 0:
                        score += 3
                    elif stats['staff_morale'] < 0 and self.state.staff_morale > 60:
                        score += 1

                if 'project_success' in stats:
                    if self.state.project_success < 40 and stats['project_success'] > 0:
                        score += 3
                    elif stats['project_success'] < 0 and self.state.project_success > 60:
                        score += 1

            choice_scores.append(score)

        # 점수가 같으면 랜덤, 아니면 가장 높은 점수 선택
        max_score = max(choice_scores)
        best_choices = [i for i, s in enumerate(choice_scores) if s == max_score]

        return random.choice(best_choices)

    def handle_free_form_input(self):
        """자유 입력 모드 처리"""
        print("\n" + "="*60)
        print("💡 자유 입력 모드")
        print("="*60)
        print("원하는 행동을 자유롭게 입력하세요.")
        print("예: '현지 부족장들과 직접 만나 대화한다', '직원들과 회의를 소집한다' 등")
        print("(취소하려면 'cancel' 입력)")
        print()

        action = input("행동: ").strip()

        if action.lower() == 'cancel':
            return None

        print("\n🤖 AI가 결과를 계산중입니다...\n")
        result = self.gemini.generate_free_form_result(self.state, action)

        if result and result.get('success'):
            return {
                'message': result.get('message', '행동을 수행했습니다.'),
                'stats': result.get('stats', {}),
                'advance_time': True,
                'next': 'ai_generated',
                'custom_action': action
            }
        elif result:
            print(f"\n⚠️ {result.get('message', '해당 행동은 불가능합니다.')}")
            input("\nEnter를 눌러 다시 선택...")
            return None
        else:
            print("\n⚠️ AI 처리 실패. 다시 시도해주세요.")
            input("\nEnter를 눌러 다시 선택...")
            return None

    def apply_choice_result(self, result):
        """선택 결과 적용"""
        if 'message' in result:
            print(f"\n💬 {result['message']}")
            if not self.demo_mode:
                input("\nEnter를 눌러 계속...")
            else:
                time.sleep(1.5)

        if 'stats' in result:
            self.state.update_stats(result['stats'])

        # 부소장 사기 변경 처리
        if 'deputy_morale' in result:
            print("\n👥 부소장 사기 변화:")
            for personality, change in result['deputy_morale'].items():
                self.state.update_deputy_morale(personality, change)
                deputy = self.state.get_deputy_by_personality(personality)
                if deputy:
                    change_str = f"+{change}" if change > 0 else str(change)
                    print(f"  • {deputy['name']}: {change_str} (현재 사기: {deputy['morale']})")

        # 고급 기능: 장기 영향(delayed_effects) 추가
        if 'delayed_effects' in result:
            # Backward compatibility: Initialize pending_delayed_effects if it doesn't exist
            if not hasattr(self.state, 'pending_delayed_effects'):
                self.state.pending_delayed_effects = []
            for effect in result['delayed_effects']:
                self.state.pending_delayed_effects.append(effect.copy())
            print(f"\n⏰ 장기 영향 {len(result['delayed_effects'])}개가 등록되었습니다.")

        if 'advance_time' in result and result['advance_time']:
            self.state.advance_time()

    def _determine_director_types(self) -> List[str]:
        """플레이어의 스탯과 선택 패턴을 분석하여 가장 적합한 소장 유형 1개를 결정

        점수 기반 시스템으로 12개 유형의 확률을 균등하게 배분합니다.
        각 유형마다 조건을 체크하고 점수를 부여하며, 가장 높은 점수를 받은 유형이 선택됩니다.
        """
        stats = self.state
        style = stats.player_style

        # 각 스탯의 상대적 수준 분석
        work_stats = {
            'reputation': stats.reputation,
            'budget': stats.budget_execution_rate,
            'staff': stats.staff_morale,
            'project': stats.project_success
        }

        # 가장 높은 스탯 찾기
        max_stat = max(work_stats.values()) if work_stats.values() else 50
        max_stat_name = max(work_stats, key=work_stats.get)

        # 스탯 균형도 계산
        stat_values = list(work_stats.values())
        avg_stat = sum(stat_values) / len(stat_values) if stat_values else 50
        variance = sum((v - avg_stat) ** 2 for v in stat_values) / len(stat_values) if stat_values else 0

        # 플레이 스타일 분석
        total_choices = len(stats.choice_history)
        risk_ratio = style['risk_taking'] / total_choices if total_choices > 0 else 0

        # 가장 중점을 둔 영역 찾기
        focus_areas = {
            'reputation': style['reputation_focused'],
            'budget': style['budget_focused'],
            'staff': style['staff_focused'],
            'project': style['project_focused']
        }
        max_focus = max(focus_areas.values()) if focus_areas.values() else 0
        most_focused = max(focus_areas, key=focus_areas.get) if max_focus > 0 else None

        # === 점수 기반 유형 결정 (12개 유형) ===
        type_scores = {}

        # 1. 혁신적인 소장 - 높은 위험 감수 + 우수한 성과
        score = 0
        if risk_ratio > 0.45:
            score += 50
        elif risk_ratio > 0.35:
            score += 30
        elif risk_ratio > 0.25:
            score += 10
        if max_stat >= 70:
            score += 30
        elif max_stat >= 60:
            score += 20
        elif max_stat >= 50:
            score += 10
        type_scores["혁신적인 소장"] = score

        # 2. 여유로운 소장 - 높은 웰빙 + 낮은 스트레스
        score = 0
        if stats.wellbeing >= 70:
            score += 40
        elif stats.wellbeing >= 60:
            score += 25
        elif stats.wellbeing >= 50:
            score += 10
        if stats.stress <= 30:
            score += 40
        elif stats.stress <= 40:
            score += 25
        elif stats.stress <= 50:
            score += 10
        if avg_stat >= 50:
            score += 20
        type_scores["여유로운 소장"] = score

        # 3. 헌신적인 소장 - 높은 스트레스 + 높은 성과 (조건 더 완화)
        score = 0
        if stats.stress >= 65:
            score += 40
        elif stats.stress >= 55:
            score += 30
        elif stats.stress >= 45:
            score += 20
        if avg_stat >= 60:
            score += 40
        elif avg_stat >= 50:
            score += 30
        elif avg_stat >= 40:
            score += 20
        type_scores["헌신적인 소장"] = score

        # 4. 균형잡힌 소장 - 낮은 분산 + 좋은 평균 (조건 더 완화)
        score = 0
        if variance < 250:
            score += 45
        elif variance < 350:
            score += 35
        elif variance < 450:
            score += 25
        elif variance < 600:
            score += 15
        if avg_stat >= 50:
            score += 40
        elif avg_stat >= 40:
            score += 30
        elif avg_stat >= 30:
            score += 20
        type_scores["균형잡힌 소장"] = score

        # 5. 온화한 소장 - 직원 중심 + 낮은 스트레스
        score = 0
        if most_focused == 'staff':
            score += 35
        if style['staff_focused'] >= 8:
            score += 35
        elif style['staff_focused'] >= 5:
            score += 20
        elif style['staff_focused'] >= 3:
            score += 10
        if stats.stress <= 40:
            score += 30
        elif stats.stress <= 50:
            score += 15
        if work_stats['staff'] >= 65:
            score += 25
        elif work_stats['staff'] >= 55:
            score += 15
        type_scores["온화한 소장"] = score

        # 6. 사람 중심 소장 - 직원 만족도 우선
        score = 0
        if most_focused == 'staff':
            score += 40
        if style['staff_focused'] >= 8:
            score += 40
        elif style['staff_focused'] >= 5:
            score += 25
        elif style['staff_focused'] >= 3:
            score += 15
        if work_stats['staff'] >= 70:
            score += 35
        elif work_stats['staff'] >= 60:
            score += 25
        elif work_stats['staff'] >= 50:
            score += 15
        type_scores["사람 중심 소장"] = score

        # 7. 신중한 외교가 - 평판 중심 + 낮은 위험
        score = 0
        if most_focused == 'reputation':
            score += 40
        if style['reputation_focused'] >= 8:
            score += 35
        elif style['reputation_focused'] >= 5:
            score += 20
        elif style['reputation_focused'] >= 3:
            score += 10
        if risk_ratio < 0.15:
            score += 35
        elif risk_ratio < 0.25:
            score += 20
        if work_stats['reputation'] >= 65:
            score += 25
        elif work_stats['reputation'] >= 55:
            score += 15
        type_scores["신중한 외교가"] = score

        # 8. 외교적인 소장 - 평판 우선
        score = 0
        if most_focused == 'reputation':
            score += 40
        if style['reputation_focused'] >= 8:
            score += 40
        elif style['reputation_focused'] >= 5:
            score += 25
        elif style['reputation_focused'] >= 3:
            score += 15
        if work_stats['reputation'] >= 70:
            score += 35
        elif work_stats['reputation'] >= 60:
            score += 25
        elif work_stats['reputation'] >= 50:
            score += 15
        type_scores["외교적인 소장"] = score

        # 9. 진취적인 소장 - 프로젝트 중심 + 높은 위험
        score = 0
        if most_focused == 'project':
            score += 35
        if style['project_focused'] >= 8:
            score += 30
        elif style['project_focused'] >= 5:
            score += 20
        elif style['project_focused'] >= 3:
            score += 10
        if risk_ratio > 0.35:
            score += 35
        elif risk_ratio > 0.25:
            score += 25
        elif risk_ratio > 0.18:
            score += 15
        if work_stats['project'] >= 65:
            score += 20
        elif work_stats['project'] >= 55:
            score += 10
        type_scores["진취적인 소장"] = score

        # 10. 성과 중심 소장 - 프로젝트 성공 우선
        score = 0
        if most_focused == 'project':
            score += 40
        if style['project_focused'] >= 8:
            score += 40
        elif style['project_focused'] >= 5:
            score += 25
        elif style['project_focused'] >= 3:
            score += 15
        if work_stats['project'] >= 70:
            score += 35
        elif work_stats['project'] >= 60:
            score += 25
        elif work_stats['project'] >= 50:
            score += 15
        type_scores["성과 중심 소장"] = score

        # 11. 실무형 소장 - 예산 집행 우선
        score = 0
        if most_focused == 'budget':
            score += 40
        if style['budget_focused'] >= 8:
            score += 40
        elif style['budget_focused'] >= 5:
            score += 25
        elif style['budget_focused'] >= 3:
            score += 15
        if work_stats['budget'] >= 70:
            score += 35
        elif work_stats['budget'] >= 60:
            score += 25
        elif work_stats['budget'] >= 50:
            score += 15
        type_scores["실무형 소장"] = score

        # 12. 분투한 소장 - 낮은 성과 (폴백)
        score = 0
        if avg_stat < 45:
            score += 60
        elif avg_stat < 50:
            score += 40
        elif avg_stat < 55:
            score += 20
        if max_stat < 50:
            score += 30
        type_scores["분투한 소장"] = score

        # 가장 높은 점수를 받은 유형 선택 (동점이면 랜덤)
        if not type_scores:
            return ["분투한 소장"]

        max_score = max(type_scores.values())
        top_types = [t for t, s in type_scores.items() if s == max_score]

        # 동점이면 랜덤 선택
        import random
        return [random.choice(top_types)]

    def display_ending(self):
        """엔딩 표시 (AI 개인화 지원)"""
        self.clear_screen()
        print("\n" + "="*60)
        print(" "*20 + "게임 종료")
        print("="*60 + "\n")

        # AI 모드에서 개인화된 엔딩 생성
        if self.ai_mode and self.gemini.enabled and len(self.state.choice_history) > 5:
            print("🤖 AI가 당신만의 엔딩을 생성중입니다...\n")
            personalized_ending = self.gemini.generate_personalized_ending(self.state)

            if personalized_ending:
                print(f"🏆 당신만의 이야기\n")
                print(personalized_ending)
                print()
            else:
                # 폴백: 기본 엔딩 사용
                self._display_standard_ending()
        else:
            # 클래식 모드에서 템플릿 기반 두꺼운 설명 생성 (정상 종료시에만)
            if self.state.ending in ["legendary_director", "successful_director", "average_director", "struggling_director"] and len(self.state.choice_history) > 3:
                print(f"🏆 당신만의 이야기\n")
                thick_description = self._generate_classic_thick_description()
                print(thick_description)
                print()
            else:
                # 게임 오버(비정상 종료)는 기본 엔딩 사용
                self._display_standard_ending()

        self.state.display_status()

        # 소장 유형 평가 (1개만 표시)
        print("\n✨ 당신의 소장 유형:")
        director_types = self._determine_director_types()
        director_type = director_types[0] if director_types else "소장"
        print(f"   🎯 {director_type}")

        # 선택 분석을 통한 풍부한 설명
        choice_explanation = self._generate_choice_explanation_console(director_type)
        print(f"\n{choice_explanation}")

        print("\n📊 영역별 성과:")
        print(f"   🌟 평판: {self.state.reputation}/100")
        print(f"   💰 예산 집행률: {self.state.budget_execution_rate}/100")
        print(f"   😊 직원 만족도: {self.state.staff_morale}/100")
        print(f"   📊 프로젝트 성공도: {self.state.project_success}/100")

        # 예산 집행률 평가 표시
        if 80 <= self.state.budget_execution_rate <= 100:
            print(f"\n   💰 예산 집행: 우수 ({self.state.budget_execution_rate}%)")
        elif self.state.budget_execution_rate >= 60:
            print(f"\n   💰 예산 집행: 양호 ({self.state.budget_execution_rate}%)")
        else:
            print(f"\n   💰 예산 집행: 미흡 ({self.state.budget_execution_rate}%)")

        # 플레이 스타일 요약 (AI 모드)
        if self.ai_mode and len(self.state.choice_history) > 0:
            print("\n💡 당신의 플레이 스타일:")
            style_summary = self._summarize_play_style()
            print(style_summary)

        print("\n게임을 플레이해 주셔서 감사합니다!")
        print("="*60 + "\n")

    def _display_standard_ending(self):
        """표준 엔딩 표시"""
        endings = {
            "reputation_loss": {
                "title": "평판 실추로 소환",
                "description": "당신의 평판이 너무 낮아져 본부로 소환되었습니다.\n현지 사무소는 다른 소장에게 인계됩니다."
            },
            "budget_crisis": {
                "title": "예산 위기로 인한 해임",
                "description": "예산 관리 실패로 사무소 운영이 불가능해졌습니다.\n당신은 소장직에서 해임되었습니다."
            },
            "staff_revolt": {
                "title": "직원 반발로 사임",
                "description": "직원들의 사기가 최저점에 달해 집단 사직이 발생했습니다.\n당신은 책임을 지고 사임했습니다."
            },
            "burnout": {
                "title": "번아웃으로 긴급 귀국",
                "description": "스트레스가 한계를 넘었습니다.\n\n과도한 업무, 문화적 적응의 어려움, 쉴 새 없는 압박이 당신을 지쳐 쓰러지게 만들었습니다.\n어느 날 아침, 침대에서 일어날 수 없었습니다. 본부는 긴급 귀국 조치를 내렸습니다.\n\n당신은 6개월간의 휴직 후 본부 내부 업무로 복귀했지만, 다시는 해외 파견을 지원하지 않았습니다.\n\n\"가장 중요한 프로젝트는 당신 자신의 건강입니다.\""
            },
            "health_crisis": {
                "title": "건강 위기로 의료 후송",
                "description": "건강이 급격히 악화되었습니다.\n\n불규칙한 식사, 부족한 운동, 현지 의료 시스템의 한계가 겹쳐 심각한 건강 문제가 발생했습니다.\n의료진은 즉시 한국으로 돌아가야 한다고 권고했습니다.\n\n의료 후송 항공편으로 한국에 도착한 당신은 3개월간 입원 치료를 받았습니다.\n임기는 후임자에게 인계되었습니다.\n\n\"몸이 건강해야 마음도 일도 제대로 할 수 있습니다.\""
            },
            "legendary_director": {
                "title": "전설적인 소장",
                "description": "당신은 KOICA 역사상 가장 성공적인 소장으로 기억될 것입니다!\n모든 프로젝트가 성공적이었고, 현지 사회에 큰 긍정적 영향을 미쳤습니다.\n당신은 본부의 고위 간부로 승진했습니다."
            },
            "successful_director": {
                "title": "성공적인 소장",
                "description": "2년의 임기를 성공적으로 마쳤습니다.\n여러 어려움이 있었지만 전반적으로 좋은 성과를 냈습니다.\n현지 주민들과 직원들이 당신의 노고를 인정합니다."
            },
            "average_director": {
                "title": "평범한 소장",
                "description": "2년의 임기를 무난하게 마쳤습니다.\n특별한 성과는 없었지만 큰 실수도 없었습니다.\n다음 소장에게 안정적으로 업무를 인계했습니다."
            },
            "struggling_director": {
                "title": "고전한 소장",
                "description": "2년의 임기가 끝났지만 많은 어려움을 겪었습니다.\n일부 프로젝트는 실패했고 여러 문제들이 남아있습니다.\n하지만 끝까지 포기하지 않은 당신의 노력은 인정받습니다."
            }
        }

        ending_info = endings.get(self.state.ending, {
            "title": "엔딩",
            "description": "게임이 종료되었습니다."
        })

        print(f"🏆 {ending_info['title']}\n")
        print(ending_info['description'])
        print()

    def _generate_choice_explanation_console(self, director_type: str) -> str:
        """선택 히스토리를 분석하여 소장 유형에 대한 드라마틱한 설명 생성 (콘솔용)"""
        stats = self.state
        style = stats.player_style
        total_choices = len(stats.choice_history)

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
        if stats.reputation < 50:
            crisis_parts.append("평판 위기")
        if stats.staff_morale < 50:
            crisis_parts.append("직원들의 불만")
        if stats.stress >= 60:
            crisis_parts.append("극심한 스트레스")
        if stats.budget_execution_rate < 60:
            crisis_parts.append("예산 집행의 어려움")

        # 성공 파악
        if stats.reputation >= 60:
            success_parts.append("신뢰 구축")
        if stats.project_success >= 60:
            success_parts.append("프로젝트 성공")
        if stats.staff_morale >= 60:
            success_parts.append("팀워크 형성")
        if stats.budget_execution_rate >= 70:
            success_parts.append("효율적인 예산 운영")

        # 위기와 성공을 문장으로 구성
        if crisis_parts and success_parts:
            para2 = f"{', '.join(crisis_parts[:2])}의 위기도 있었고, {', '.join(success_parts[:2])}의 순간도 있었습니다."
        elif crisis_parts:
            para2 = f"{', '.join(crisis_parts[:2])}의 위기가 있었지만, 당신은 흔들리지 않았습니다."
        elif success_parts:
            para2 = f"{', '.join(success_parts[:2])}을 이루며 빛나는 순간들이 있었습니다."
        else:
            para2 = "크고 작은 사건들이 있었습니다."

        para2 += "\n예산 부족과 문화적 갈등, 예상치 못한 사건들이 연이어 닥쳤지만, 당신은 포기하지 않고 한 걸음씩 나아갔습니다."
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

        para3 = f"당신의 {top_concern}에 대한 헌신, {leadership_style}한 리더십은\n이곳 사람들의 삶에 실질적인 변화를 만들어냈습니다."
        paragraphs.append(para3)

        # 4. 유산과 기억
        para4 = f"이제 사람들은 당신을 '{director_type}'으로 기억할 것입니다.\n그리고 당신이 남긴 발자국은 오랫동안 이 땅에 남을 것입니다."
        paragraphs.append(para4)

        return "\n\n".join(paragraphs)

    def _summarize_play_style(self) -> str:
        """플레이 스타일 요약"""
        style = self.state.player_style
        total_choices = len(self.state.choice_history)

        if total_choices == 0:
            return "선택을 내리지 않았습니다."

        summary = []

        # 주요 관심사
        max_focus = max(style['reputation_focused'], style['budget_focused'],
                       style['staff_focused'], style['project_focused'])

        if max_focus > 0:
            focuses = []
            if style['reputation_focused'] == max_focus:
                focuses.append("평판")
            if style['budget_focused'] == max_focus:
                focuses.append("예산")
            if style['staff_focused'] == max_focus:
                focuses.append("직원")
            if style['project_focused'] == max_focus:
                focuses.append("프로젝트")

            summary.append(f"• 주요 관심사: {', '.join(focuses)}")

        # 위험 성향
        risk_ratio = style['risk_taking'] / total_choices if total_choices > 0 else 0
        if risk_ratio > 0.3:
            summary.append("• 성향: 대담한 도전을 선호")
        elif risk_ratio < 0.1:
            summary.append("• 성향: 안정적이고 신중한 접근")
        else:
            summary.append("• 성향: 균형잡힌 의사결정")

        return "\n".join(summary) if summary else "다양한 접근 시도"

    def _generate_classic_thick_description(self) -> str:
        """클래식 모드용 두꺼운 설명(thick description) 생성 - 템플릿 기반"""

        # 스탯 분석
        stats = self.state

        # 플레이어 스타일 분석
        style = stats.player_style
        max_focus = max(style['reputation_focused'], style['budget_focused'],
                       style['staff_focused'], style['project_focused'])

        # 리더십 스타일 결정
        leadership_style = []
        if style['reputation_focused'] == max_focus:
            leadership_style.append("외교적")
        if style['budget_focused'] == max_focus:
            leadership_style.append("실무형")
        if style['staff_focused'] == max_focus:
            leadership_style.append("인본주의적")
        if style['project_focused'] == max_focus:
            leadership_style.append("성과 중심적")

        if not leadership_style:
            leadership_style.append("균형잡힌")

        # 위험 성향
        total_choices = len(stats.choice_history)
        risk_ratio = style['risk_taking'] / total_choices if total_choices > 0 else 0

        if risk_ratio > 0.3:
            risk_desc = "혁신가"
        elif risk_ratio < 0.1:
            risk_desc = "안정적 전략가"
        else:
            risk_desc = "신중한 리더"

        # 엔딩 설명 구성
        paragraphs = []

        # 첫 문단: 여정의 전반적 평가
        para1 = f"소장님의 2년은 단순히 시간을 보내는 것이 아닌, 변화를 이끌어내는 여정이었습니다. "

        # 예산 집행률 언급
        if stats.budget_execution_rate >= 80:
            budget_context = f"예산 집행률 {stats.budget_execution_rate}%를 달성하며 재정 관리의 모범을 보였고, "
        elif stats.budget_execution_rate >= 60:
            budget_context = f"예산 집행률 {stats.budget_execution_rate}%로 재정 운영에 노력하였고, "
        else:
            budget_context = f"제한된 예산이라는 현실 속에서도, "

        para1 += budget_context

        # 평판 언급
        if stats.reputation >= 80:
            para1 += f"평판 {stats.reputation}점이라는 높은 신뢰를 얻었습니다. "
        elif stats.reputation >= 50:
            para1 += f"평판 {stats.reputation}점으로 안정적인 관계를 유지했습니다. "
        else:
            para1 += f"여러 도전 속에서도 포기하지 않았습니다. "

        # 소장 유형 언급
        director_types = self._determine_director_types()
        if director_types:
            types_str = ' · '.join(director_types)
            para1 += f"당신은 {types_str}으로서의 여정을 완수했습니다."
        else:
            para1 += f"2년간의 노력을 통해 자신만의 길을 만들어냈습니다."

        paragraphs.append(para1)

        # 두 번째 문단: 리더십 스타일과 주요 결정
        para2 = f"소장님은 {' · '.join(leadership_style)} 리더십을 발휘하며 사무소를 이끌었습니다. "

        # 주요 결정들 언급 (최근 5-8개)
        recent_choices = stats.choice_history[-8:] if len(stats.choice_history) > 8 else stats.choice_history

        if recent_choices:
            # 중요한 결정들을 선별 (큰 스탯 변화를 일으킨 것들)
            significant_choices = []
            for choice in recent_choices:
                if 'result' in choice and 'stats' in choice['result']:
                    stat_changes = choice['result']['stats']
                    total_change = sum(abs(v) for v in stat_changes.values())
                    if total_change > 15:  # 큰 변화
                        significant_choices.append(choice)

            if significant_choices:
                para2 += f"{risk_desc}로서, "

                # 첫 번째 중요한 결정 언급
                first_choice = significant_choices[0]
                choice_text = first_choice.get('choice_text', '중요한 결정')
                # 선택 텍스트에서 핵심만 추출 (너무 길면 생략)
                if len(choice_text) > 40:
                    choice_text = choice_text[:37] + "..."
                para2 += f"'{choice_text}'와 같은 결정을 내리며 "

                if len(significant_choices) > 1:
                    para2 += "여러 중요한 순간마다 "

                    # 결정의 성향 분석
                    positive_outcomes = sum(1 for c in significant_choices
                                           if 'result' in c and 'stats' in c['result']
                                           and sum(c['result']['stats'].values()) > 0)

                    if positive_outcomes >= len(significant_choices) * 0.7:
                        para2 += "효과적인 선택을 이어갔습니다. "
                    elif positive_outcomes >= len(significant_choices) * 0.4:
                        para2 += "균형잡힌 판단을 추구했습니다. "
                    else:
                        para2 += "어려운 상황 속에서도 최선을 다했습니다. "
                else:
                    para2 += "신중하게 사무소를 운영했습니다. "
            else:
                para2 += f"{risk_desc}로서 안정적으로 사무소를 운영했습니다. "
        else:
            para2 += "새로운 시작을 준비했습니다. "

        paragraphs.append(para2)

        # 세 번째 문단: 구체적 성과
        para3 = "소장님의 리더십 아래, 해외사무소는 "

        # 프로젝트 성공도
        if stats.project_success >= 80:
            para3 += f"{stats.project_success}%라는 높은 프로젝트 성공도로 "
            para3 += "현장에서 실질적인 변화를 만들어냈습니다. "
        elif stats.project_success >= 50:
            para3 += f"{stats.project_success}%의 프로젝트 성공도로 "
            para3 += "의미있는 성과를 거두었습니다. "
        else:
            para3 += "여러 도전에 직면했지만, "
            para3 += "포기하지 않고 끝까지 노력했습니다. "

        # 직원 만족도
        if stats.staff_morale >= 70:
            para3 += f"{stats.staff_morale}%의 직원 만족도는 "
            para3 += "소장님의 리더십에 대한 팀의 신뢰를 보여줍니다. "
        elif stats.staff_morale >= 40:
            para3 += f"{stats.staff_morale}%의 직원 만족도는 "
            para3 += "어려운 상황 속에서도 팀이 함께했음을 의미합니다. "
        else:
            para3 += "직원들과의 관계에서 어려움이 있었지만, "
            para3 += "함께 임기를 마칠 수 있었습니다. "

        paragraphs.append(para3)

        # 네 번째 문단: 유산과 미래
        para4 = "이제 소장님의 2년 여정이 막을 내리지만, "

        if total_score >= 70:
            para4 += "소장님이 남긴 유산은 오랫동안 빛을 발할 것입니다. "
            para4 += "당신의 헌신과 리더십은 KOICA의 역사 속에 기억될 것입니다. "
        elif total_score >= 50:
            para4 += "소장님이 쌓은 경험과 성과는 다음 세대에게 귀중한 자산이 될 것입니다. "
        else:
            para4 += "소장님이 겪은 어려움과 도전은 소중한 배움의 기회였습니다. "

        # 마무리 문구
        if total_score >= 80:
            para4 += "당신은 KOICA 해외사무소가 나아가야 할 모범적인 방향을 제시했으며, "
            para4 += "이는 미래의 여러 난관 속에서도 새로운 길을 찾아나갈 귀중한 나침반이 될 것입니다. "
            para4 += "소장님의 탁월한 업적에 진심으로 감사드립니다."
        elif total_score >= 60:
            para4 += "당신의 노력과 헌신이 만들어낸 변화는 "
            para4 += "수많은 사람들의 삶에 긍정적인 영향을 미쳤습니다. "
            para4 += "소장님의 헌신에 감사드립니다."
        else:
            para4 += "어려운 여정을 끝까지 포기하지 않은 당신의 용기에 경의를 표합니다. "
            para4 += "이 경험은 앞으로의 여정에 소중한 밑거름이 될 것입니다."

        paragraphs.append(para4)

        return "\n\n".join(paragraphs)

    def play(self):
        """게임 플레이 메인 루프 (AI 기능 통합)"""
        self.display_intro()
        self.initial_lifestyle_setup()

        while not self.state.game_over:
            scenario = self.display_scenario(self.state.current_scenario)

            if not scenario:
                break

            self.state.visited_scenarios.append(self.state.current_scenario)

            if 'choices' not in scenario:
                # 엔딩 시나리오
                if not self.demo_mode:
                    input("\nEnter를 눌러 계속...")
                else:
                    time.sleep(2)
                self.state.game_over = True
                break

            # 선택 받기
            choice_index = self.display_choices(scenario['choices'])

            # 자유 입력 모드 처리
            if choice_index == -1:
                free_form_result = self.handle_free_form_input()
                if free_form_result:
                    # 자유 입력 선택 기록
                    self.state.record_choice(
                        self.state.current_scenario,
                        free_form_result.get('custom_action', '자유 입력'),
                        -1,
                        free_form_result
                    )
                    self.apply_choice_result(free_form_result)

                    if self.state.check_game_over():
                        break

                    if 'next' in free_form_result:
                        self.state.current_scenario = free_form_result['next']
                    else:
                        self.state.current_scenario = 'ai_generated'
                else:
                    # 자유 입력 취소시 다시 선택
                    continue
            else:
                # 일반 선택 처리
                selected_choice = scenario['choices'][choice_index]

                # 게임 오버를 초래할 수 있는 선택인지 확인
                if 'stats' in selected_choice['result']:
                    if self.state.will_cause_game_over(selected_choice['result']['stats']):
                        # 확인 프롬프트 표시
                        print("\n" + "="*60)
                        print("⚠️  경고: 위험한 선택")
                        print("="*60)
                        print("이 선택은 즉각적인 게임 종료를 초래할 수 있습니다!")

                        # 예상되는 스탯 변화 표시
                        changes = selected_choice['result']['stats']
                        print("\n예상 스탯 변화:")
                        if 'reputation' in changes and changes['reputation'] < 0:
                            new_rep = max(0, self.state.reputation + changes['reputation'])
                            print(f"  평판: {self.state.reputation} → {new_rep}")
                        if 'staff_morale' in changes and changes['staff_morale'] < 0:
                            new_morale = max(0, self.state.staff_morale + changes['staff_morale'])
                            print(f"  직원 만족도: {self.state.staff_morale} → {new_morale}")

                        print("\n정말로 이 선택을 진행하시겠습니까?")
                        print("="*60)

                        if not self.demo_mode:
                            confirm = input("\n진행하려면 'yes' 입력, 다시 선택하려면 Enter: ").strip().lower()
                            if confirm != 'yes':
                                print("\n선택을 취소했습니다. 다시 선택하세요.")
                                continue
                        else:
                            print("\n🤖 [데모 모드] 위험한 선택이지만 계속 진행합니다...")
                            time.sleep(2)

                # 선택 기록
                self.state.record_choice(
                    self.state.current_scenario,
                    selected_choice['text'],
                    choice_index,
                    selected_choice['result']
                )

                self.apply_choice_result(selected_choice['result'])

                if self.state.check_game_over():
                    break

                # 생활 이벤트 체크 (advance_time이 true인 경우에만)
                if selected_choice['result'].get('advance_time', False):
                    life_event_id = self.check_and_trigger_life_event()
                    if life_event_id:
                        # 생활 이벤트 발생
                        life_event_scenario = self.display_scenario(life_event_id)
                        if life_event_scenario and 'choices' in life_event_scenario:
                            print("\n" + "="*60)
                            print("🏠 생활 이벤트가 발생했습니다!")
                            print("="*60)
                            if not self.demo_mode:
                                input("\nEnter를 눌러 계속...")
                            else:
                                time.sleep(1)

                            # 생활 이벤트 선택 처리
                            life_choice_index = self.display_choices(life_event_scenario['choices'])
                            if life_choice_index >= 0:
                                life_selected = life_event_scenario['choices'][life_choice_index]
                                self.state.record_choice(life_event_id, life_selected['text'], life_choice_index, life_selected['result'])
                                self.apply_choice_result(life_selected['result'])

                                if self.state.check_game_over():
                                    break

                    # 고급 기능: 부소장 임계값 이벤트 체크
                    deputy_event_id = self.check_deputy_threshold_events()
                    if deputy_event_id:
                        self.state.triggered_deputy_events.add(deputy_event_id)
                        deputy_event_scenario = self.display_scenario(deputy_event_id)
                        if deputy_event_scenario and 'choices' in deputy_event_scenario:
                            print("\n" + "="*60)
                            print("👥 부소장 관련 특별 이벤트가 발생했습니다!")
                            print("="*60)
                            if not self.demo_mode:
                                input("\nEnter를 눌러 계속...")
                            else:
                                time.sleep(1)

                            # 부소장 이벤트 선택 처리
                            deputy_choice_index = self.display_choices(deputy_event_scenario['choices'])
                            if deputy_choice_index >= 0:
                                deputy_selected = deputy_event_scenario['choices'][deputy_choice_index]
                                self.state.record_choice(deputy_event_id, deputy_selected['text'], deputy_choice_index, deputy_selected['result'])
                                self.apply_choice_result(deputy_selected['result'])

                                if self.state.check_game_over():
                                    break

                    # 고급 기능: 장기 영향(delayed effects) 체크
                    triggered_effects = self.check_delayed_effects()
                    for effect in triggered_effects:
                        print("\n" + "="*60)
                        print("⏰ 과거 선택의 장기 영향이 나타났습니다!")
                        print("="*60)
                        print(f"\n💬 {effect.get('message', '과거의 선택이 영향을 미치고 있습니다.')}")
                        if 'stats' in effect:
                            self.state.update_stats(effect['stats'])
                        if not self.demo_mode:
                            input("\nEnter를 눌러 계속...")
                        else:
                            time.sleep(1.5)

                    # 고급 기능: 고급 엔딩 조건 체크
                    advanced_ending = self.check_advanced_endings()
                    if advanced_ending:
                        self.state.game_over = True
                        self.state.ending = advanced_ending
                        break

                if 'next' in selected_choice['result']:
                    self.state.current_scenario = selected_choice['result']['next']
                else:
                    print("\n오류: 다음 시나리오가 지정되지 않았습니다.")
                    break

        self.display_ending()


def main():
    """메인 함수 - 게임 모드 선택"""
    # argparse 설정
    parser = argparse.ArgumentParser(
        description='KOICA 해외사무소장 시뮬레이터',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python3 koica_game.py          # 일반 플레이
  python3 koica_game.py --demo   # 자동 데모 플레이
        """
    )
    parser.add_argument('--demo', action='store_true',
                       help='데모 모드 (자동 플레이)')
    parser.add_argument('--speed', type=float, default=1.5,
                       help='데모 모드 속도 (초 단위, 기본: 1.5초)')

    args = parser.parse_args()

    # 데모 모드
    if args.demo:
        print("\n" + "="*60)
        print(" "*15 + "KOICA 소장 시뮬레이터")
        print(" "*20 + "🤖 [데모 모드]")
        print("="*60)
        print("\n자동으로 게임을 플레이합니다...")
        time.sleep(2)
        game = KOICAGame(ai_mode=False, demo_mode=True)
        game.play()
        return

    # 일반 모드
    print("\n" + "="*60)
    print(" "*15 + "KOICA 소장 시뮬레이터")
    print("="*60)
    print("\n게임 모드를 선택하세요:")
    print("1. 클래식 모드 (기본 시나리오)")
    print("2. AI 모드 (Gemini 연동 - 동적 시나리오, 자유 입력)")
    print()

    mode_choice = input("선택 (1 또는 2): ").strip()

    if mode_choice == "2":
        # AI 모드
        if not GEMINI_AVAILABLE:
            print("\n⚠️  오류: google-generativeai 패키지가 설치되지 않았습니다.")
            print("AI 모드를 사용하려면 다음 명령어를 실행하세요:")
            print("pip install google-generativeai")
            print("\n클래식 모드로 시작합니다...")
            input("\nEnter를 눌러 계속...")
            game = KOICAGame(ai_mode=False)
        else:
            # API 키 입력
            print("\nGemini API 키를 입력하세요:")
            print("(API 키는 https://makersuite.google.com/app/apikey 에서 발급받을 수 있습니다)")
            print("(환경변수 GEMINI_API_KEY가 설정되어 있으면 Enter를 누르세요)")

            api_key_input = input("\nAPI Key: ").strip()

            if not api_key_input:
                # 환경변수에서 가져오기 시도
                api_key = os.environ.get('GEMINI_API_KEY')
                if not api_key:
                    print("\n⚠️  API 키가 제공되지 않았습니다. 클래식 모드로 시작합니다.")
                    input("\nEnter를 눌러 계속...")
                    game = KOICAGame(ai_mode=False)
                else:
                    print("\n✅ 환경변수에서 API 키를 불러왔습니다.")
                    print("🤖 AI 모드로 시작합니다!\n")
                    input("Enter를 눌러 계속...")
                    game = KOICAGame(ai_mode=True, api_key=api_key)
            else:
                print("\n🤖 AI 모드로 시작합니다!\n")
                input("Enter를 눌러 계속...")
                game = KOICAGame(ai_mode=True, api_key=api_key_input)
    else:
        # 클래식 모드
        game = KOICAGame(ai_mode=False)

    game.play()


if __name__ == "__main__":
    main()

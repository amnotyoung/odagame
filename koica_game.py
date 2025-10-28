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
        self.quarter = 1
        self.reputation = 50  # 평판 (0-100)
        self.budget = 100  # 예산 (0-200)
        self.staff_morale = 50  # 직원 만족도 (0-100)
        self.project_success = 50  # 프로젝트 성공도 (0-100)
        self.current_scenario = "start"
        self.visited_scenarios = []
        self.game_over = False
        self.ending = None

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

    def update_stats(self, changes):
        """스탯 업데이트 및 히스토리 기록"""
        old_stats = {
            'reputation': self.reputation,
            'budget': self.budget,
            'staff_morale': self.staff_morale,
            'project_success': self.project_success
        }

        if 'reputation' in changes:
            self.reputation = max(0, min(100, self.reputation + changes['reputation']))
        if 'budget' in changes:
            self.budget = max(0, min(200, self.budget + changes['budget']))
        if 'staff_morale' in changes:
            self.staff_morale = max(0, min(100, self.staff_morale + changes['staff_morale']))
        if 'project_success' in changes:
            self.project_success = max(0, min(100, self.project_success + changes['project_success']))

        # 스탯 변화 기록
        self.stat_history.append({
            'year': self.year,
            'quarter': self.quarter,
            'changes': changes,
            'old': old_stats,
            'new': {
                'reputation': self.reputation,
                'budget': self.budget,
                'staff_morale': self.staff_morale,
                'project_success': self.project_success
            }
        })

    def record_choice(self, scenario_id, choice_text, choice_index, result):
        """선택 기록 및 플레이어 스타일 분석"""
        self.choice_history.append({
            'scenario_id': scenario_id,
            'choice_text': choice_text,
            'choice_index': choice_index,
            'year': self.year,
            'quarter': self.quarter,
            'result': result
        })

        # 플레이어 스타일 분석
        if 'stats' in result:
            stats = result['stats']
            if 'reputation' in stats and stats['reputation'] > 0:
                self.player_style['reputation_focused'] += 1
            if 'budget' in stats and stats['budget'] > 0:
                self.player_style['budget_focused'] += 1
            if 'staff_morale' in stats and stats['staff_morale'] > 0:
                self.player_style['staff_focused'] += 1
            if 'project_success' in stats and stats['project_success'] > 0:
                self.player_style['project_focused'] += 1

            # 위험 감수 성향 분석 (큰 변화를 선택하는 경우)
            total_change = sum(abs(v) for v in stats.values())
            if total_change > 20:
                self.player_style['risk_taking'] += 1

    def get_play_summary(self):
        """플레이 요약 반환 (Gemini에게 전달할 컨텍스트)"""
        return {
            'current_stats': {
                'year': self.year,
                'quarter': self.quarter,
                'reputation': self.reputation,
                'budget': self.budget,
                'staff_morale': self.staff_morale,
                'project_success': self.project_success
            },
            'visited_scenarios': self.visited_scenarios,
            'choice_history': self.choice_history[-5:] if len(self.choice_history) > 5 else self.choice_history,  # 최근 5개만
            'player_style': self.player_style,
            'major_decisions': self.major_decisions
        }

    def advance_time(self):
        """시간 진행 (분기)"""
        self.quarter += 1
        if self.quarter > 4:
            self.quarter = 1
            self.year += 1

    def check_game_over(self):
        """게임 오버 조건 확인"""
        if self.reputation <= 0:
            self.game_over = True
            self.ending = "reputation_loss"
            return True
        if self.budget <= 0:
            self.game_over = True
            self.ending = "budget_crisis"
            return True
        if self.staff_morale <= 0:
            self.game_over = True
            self.ending = "staff_revolt"
            return True
        if self.year > 3:
            self.game_over = True
            self.calculate_final_ending()
            return True
        return False

    def calculate_final_ending(self):
        """최종 엔딩 계산"""
        total_score = (self.reputation + self.staff_morale + self.project_success + self.budget / 2) / 3.5

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
        print("\n" + "="*60)
        print(f"📅 {self.year}년차 {self.quarter}분기")
        print("-"*60)
        print(f"🌟 평판: {self.reputation}/100 {'■' * (self.reputation//5)}{'□' * (20-self.reputation//5)}")
        print(f"💰 예산: {self.budget}/200 {'■' * (self.budget//10)}{'□' * (20-self.budget//10)}")
        print(f"😊 직원 만족도: {self.staff_morale}/100 {'■' * (self.staff_morale//5)}{'□' * (20-self.staff_morale//5)}")
        print(f"📊 프로젝트 성공도: {self.project_success}/100 {'■' * (self.project_success//5)}{'□' * (20-self.project_success//5)}")
        print("="*60 + "\n")


class GeminiIntegration:
    """Gemini API 연동 클래스 - 동적 시나리오 및 선택지 생성"""

    def __init__(self, api_key: Optional[str] = None):
        self.enabled = GEMINI_AVAILABLE and api_key is not None
        if self.enabled:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
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
당신은 KOICA 소장 시뮬레이터 게임의 시나리오 작가입니다.
플레이어의 현재 상태와 과거 선택을 바탕으로 적절한 새로운 시나리오를 생성하세요.

## 현재 게임 상태
- 시기: {summary['current_stats']['year']}년차 {summary['current_stats']['quarter']}분기
- 평판: {summary['current_stats']['reputation']}/100
- 예산: {summary['current_stats']['budget']}/200
- 직원 만족도: {summary['current_stats']['staff_morale']}/100
- 프로젝트 성공도: {summary['current_stats']['project_success']}/100

## 플레이어 성향
{style_desc}

## 최근 방문한 시나리오
{', '.join(summary['visited_scenarios'][-3:])}

## 요구사항
1. KOICA 현지 사무소 운영과 관련된 현실적인 딜레마를 제시하세요
2. 플레이어의 현재 상태(특히 낮은 스탯)를 고려한 시나리오를 만드세요
3. 4-5개의 선택지를 제공하되, 각각 명확한 장단점이 있어야 합니다
4. 각 선택의 결과로 스탯 변화를 제안하세요 (reputation, budget, staff_morale, project_success)

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
당신은 KOICA 소장 시뮬레이터 게임의 게임 마스터입니다.
플레이어가 자유롭게 입력한 행동에 대해 결과를 판정하고 스탯 변화를 계산하세요.

## 현재 상황
- 시기: {summary['current_stats']['year']}년차 {summary['current_stats']['quarter']}분기
- 평판: {summary['current_stats']['reputation']}/100
- 예산: {summary['current_stats']['budget']}/200
- 직원 만족도: {summary['current_stats']['staff_morale']}/100
- 프로젝트 성공도: {summary['current_stats']['project_success']}/100

## 플레이어의 행동
"{player_action}"

## 요구사항
1. 플레이어의 행동이 현실적으로 가능한지 판단하세요
2. 행동의 결과를 2-4문장으로 설명하세요
3. 4가지 스탯에 미치는 영향을 계산하세요 (합리적인 범위 내에서)
4. 창의적이고 합리적인 행동은 보상하고, 무책임한 행동은 결과를 주세요

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
플레이어의 3년간의 여정을 분석하여 개인화된 엔딩 내러티브를 작성하세요.

## 최종 스탯
- 평판: {game_state.reputation}/100
- 예산: {game_state.budget}/200
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

    def __init__(self, ai_mode: bool = False, api_key: Optional[str] = None):
        self.state = GameState()
        self.scenarios = self.load_scenarios()
        self.ai_mode = ai_mode
        self.gemini = GeminiIntegration(api_key) if ai_mode else None

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
        print(" "*15 + "KOICA 소장 시뮬레이터")
        print("="*60)
        print("\n당신은 새로 임명된 KOICA 현지 사무소장입니다.")
        print("앞으로 3년 동안 다양한 상황에 직면하게 될 것입니다.")
        print("당신의 선택이 프로젝트의 성공, 직원들의 사기,")
        print("그리고 국제 협력의 미래를 결정할 것입니다.")
        print("\n각 상황에서 신중하게 선택하세요!")
        print("="*60 + "\n")
        input("Enter를 눌러 시작하세요...")

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
            input("\nEnter를 눌러 계속...")

        if 'stats' in result:
            self.state.update_stats(result['stats'])

        if 'advance_time' in result and result['advance_time']:
            self.state.advance_time()

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
            self._display_standard_ending()

        self.state.display_status()

        print("\n최종 점수:")
        total_score = (self.state.reputation + self.state.staff_morale +
                      self.state.project_success + self.state.budget / 2) / 3.5
        print(f"⭐ {total_score:.1f}/100")

        # 플레이 스타일 요약 (AI 모드)
        if self.ai_mode and len(self.state.choice_history) > 0:
            print("\n📊 당신의 플레이 스타일:")
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
            "legendary_director": {
                "title": "전설적인 소장",
                "description": "당신은 KOICA 역사상 가장 성공적인 소장으로 기억될 것입니다!\n모든 프로젝트가 성공적이었고, 현지 사회에 큰 긍정적 영향을 미쳤습니다.\n당신은 본부의 고위 간부로 승진했습니다."
            },
            "successful_director": {
                "title": "성공적인 소장",
                "description": "3년의 임기를 성공적으로 마쳤습니다.\n여러 어려움이 있었지만 전반적으로 좋은 성과를 냈습니다.\n현지 주민들과 직원들이 당신의 노고를 인정합니다."
            },
            "average_director": {
                "title": "평범한 소장",
                "description": "3년의 임기를 무난하게 마쳤습니다.\n특별한 성과는 없었지만 큰 실수도 없었습니다.\n다음 소장에게 안정적으로 업무를 인계했습니다."
            },
            "struggling_director": {
                "title": "고전한 소장",
                "description": "3년의 임기가 끝났지만 많은 어려움을 겪었습니다.\n일부 프로젝트는 실패했고 여러 문제들이 남아있습니다.\n하지만 끝까지 포기하지 않은 당신의 노력은 인정받습니다."
            }
        }

        ending_info = endings.get(self.state.ending, {
            "title": "엔딩",
            "description": "게임이 종료되었습니다."
        })

        print(f"🏆 {ending_info['title']}\n")
        print(ending_info['description'])
        print()

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

    def play(self):
        """게임 플레이 메인 루프 (AI 기능 통합)"""
        self.display_intro()

        while not self.state.game_over:
            scenario = self.display_scenario(self.state.current_scenario)

            if not scenario:
                break

            self.state.visited_scenarios.append(self.state.current_scenario)

            if 'choices' not in scenario:
                # 엔딩 시나리오
                input("\nEnter를 눌러 계속...")
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

                if 'next' in selected_choice['result']:
                    self.state.current_scenario = selected_choice['result']['next']
                else:
                    print("\n오류: 다음 시나리오가 지정되지 않았습니다.")
                    break

        self.display_ending()


def main():
    """메인 함수 - 게임 모드 선택"""
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

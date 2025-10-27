#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOICA 소장 시뮬레이터
텍스트 기반 선택형 게임
"""

import json
import os
import sys


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

    def update_stats(self, changes):
        """스탯 업데이트"""
        if 'reputation' in changes:
            self.reputation = max(0, min(100, self.reputation + changes['reputation']))
        if 'budget' in changes:
            self.budget = max(0, min(200, self.budget + changes['budget']))
        if 'staff_morale' in changes:
            self.staff_morale = max(0, min(100, self.staff_morale + changes['staff_morale']))
        if 'project_success' in changes:
            self.project_success = max(0, min(100, self.project_success + changes['project_success']))

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


class KOICAGame:
    """메인 게임 클래스"""

    def __init__(self):
        self.state = GameState()
        self.scenarios = self.load_scenarios()

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
        """시나리오 표시"""
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
        """선택지 표시 및 입력 받기"""
        print("\n선택하세요:")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice['text']}")

        while True:
            try:
                choice_input = input("\n선택 (번호 입력): ").strip()
                choice_num = int(choice_input)
                if 1 <= choice_num <= len(choices):
                    return choice_num - 1
                else:
                    print(f"1부터 {len(choices)} 사이의 숫자를 입력하세요.")
            except ValueError:
                print("올바른 숫자를 입력하세요.")
            except KeyboardInterrupt:
                print("\n\n게임을 종료합니다.")
                sys.exit(0)

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
        """엔딩 표시"""
        self.clear_screen()
        print("\n" + "="*60)
        print(" "*20 + "게임 종료")
        print("="*60 + "\n")

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

        self.state.display_status()

        print("\n최종 점수:")
        total_score = (self.state.reputation + self.state.staff_morale +
                      self.state.project_success + self.state.budget / 2) / 3.5
        print(f"⭐ {total_score:.1f}/100")
        print("\n게임을 플레이해 주셔서 감사합니다!")
        print("="*60 + "\n")

    def play(self):
        """게임 플레이 메인 루프"""
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

            choice_index = self.display_choices(scenario['choices'])
            selected_choice = scenario['choices'][choice_index]

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
    """메인 함수"""
    game = KOICAGame()
    game.play()


if __name__ == "__main__":
    main()

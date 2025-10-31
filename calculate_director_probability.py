#!/usr/bin/env python3
"""
소장 유형 도달 확률 계산 스크립트
몬테카를로 시뮬레이션을 통해 각 소장 유형에 도달할 확률을 분석합니다.
"""

import random
from collections import Counter
from typing import Dict, List


def determine_director_type(
    reputation: int,
    budget_execution_rate: int,
    staff_morale: int,
    project_success: int,
    stress: int,
    wellbeing: int,
    reputation_focused: int,
    budget_focused: int,
    staff_focused: int,
    project_focused: int,
    risk_taking: int,
    total_choices: int
) -> str:
    """소장 유형 결정 로직 (koica_game.py의 _determine_director_types 로직 복제)

    점수 기반 시스템으로 12개 유형의 확률을 균등하게 배분합니다.
    """

    work_stats = {
        'reputation': reputation,
        'budget': budget_execution_rate,
        'staff': staff_morale,
        'project': project_success
    }

    # 가장 높은 스탯 찾기
    max_stat = max(work_stats.values()) if work_stats.values() else 50
    max_stat_name = max(work_stats, key=work_stats.get)

    # 스탯 균형도 계산
    stat_values = list(work_stats.values())
    avg_stat = sum(stat_values) / len(stat_values) if stat_values else 50
    variance = sum((v - avg_stat) ** 2 for v in stat_values) / len(stat_values) if stat_values else 0

    # 플레이 스타일 분석
    risk_ratio = risk_taking / total_choices if total_choices > 0 else 0

    # 가장 중점을 둔 영역 찾기
    focus_areas = {
        'reputation': reputation_focused,
        'budget': budget_focused,
        'staff': staff_focused,
        'project': project_focused
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
    if wellbeing >= 70:
        score += 40
    elif wellbeing >= 60:
        score += 25
    elif wellbeing >= 50:
        score += 10
    if stress <= 30:
        score += 40
    elif stress <= 40:
        score += 25
    elif stress <= 50:
        score += 10
    if avg_stat >= 50:
        score += 20
    type_scores["여유로운 소장"] = score

    # 3. 헌신적인 소장 - 높은 스트레스 + 높은 성과 (조건 더 완화)
    score = 0
    if stress >= 65:
        score += 40
    elif stress >= 55:
        score += 30
    elif stress >= 45:
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

    # 5. 온화한 소장 - 직원 중심 + 낮은 스트레스 (점수 상향)
    score = 0
    if most_focused == 'staff':
        score += 32
    if staff_focused >= 5:
        score += 30
    elif staff_focused >= 3:
        score += 18
    if stress <= 40:
        score += 30
    elif stress <= 55:
        score += 18
    if work_stats['staff'] >= 60:
        score += 20
    type_scores["온화한 소장"] = score

    # 6. 사람 중심 소장 - 직원 만족도 우선
    score = 0
    if most_focused == 'staff':
        score += 35
    if staff_focused >= 5:
        score += 35
    elif staff_focused >= 3:
        score += 20
    elif staff_focused >= 1:
        score += 10
    if work_stats['staff'] >= 65:
        score += 30
    elif work_stats['staff'] >= 55:
        score += 20
    elif work_stats['staff'] >= 45:
        score += 10
    type_scores["사람 중심 소장"] = score

    # 7. 신중한 외교가 - 평판 중심 + 낮은 위험
    score = 0
    if most_focused == 'reputation':
        score += 35
    if reputation_focused >= 5:
        score += 30
    elif reputation_focused >= 3:
        score += 15
    if risk_ratio < 0.15:
        score += 35
    elif risk_ratio < 0.25:
        score += 20
    elif risk_ratio < 0.35:
        score += 10
    if work_stats['reputation'] >= 60:
        score += 20
    type_scores["신중한 외교가"] = score

    # 8. 외교적인 소장 - 평판 우선
    score = 0
    if most_focused == 'reputation':
        score += 35
    if reputation_focused >= 5:
        score += 35
    elif reputation_focused >= 3:
        score += 20
    elif reputation_focused >= 1:
        score += 10
    if work_stats['reputation'] >= 65:
        score += 30
    elif work_stats['reputation'] >= 55:
        score += 20
    elif work_stats['reputation'] >= 45:
        score += 10
    type_scores["외교적인 소장"] = score

    # 9. 진취적인 소장 - 프로젝트 중심 + 높은 위험 (최종 조정)
    score = 0
    if most_focused == 'project':
        score += 28
    if project_focused >= 5:
        score += 26
    elif project_focused >= 3:
        score += 16
    if risk_ratio > 0.32:
        score += 30
    elif risk_ratio > 0.24:
        score += 20
    elif risk_ratio > 0.17:
        score += 10
    if work_stats['project'] >= 60:
        score += 16
    type_scores["진취적인 소장"] = score

    # 10. 성과 중심 소장 - 프로젝트 성공 우선 (최종 조정)
    score = 0
    if most_focused == 'project':
        score += 32
    if project_focused >= 5:
        score += 32
    elif project_focused >= 3:
        score += 22
    elif project_focused >= 1:
        score += 14
    if work_stats['project'] >= 65:
        score += 30
    elif work_stats['project'] >= 55:
        score += 22
    elif work_stats['project'] >= 45:
        score += 14
    type_scores["성과 중심 소장"] = score

    # 11. 실무형 소장 - 예산 집행 우선 (점수 조정)
    score = 0
    if most_focused == 'budget':
        score += 28
    if budget_focused >= 5:
        score += 28
    elif budget_focused >= 3:
        score += 18
    elif budget_focused >= 1:
        score += 10
    if work_stats['budget'] >= 65:
        score += 25
    elif work_stats['budget'] >= 55:
        score += 18
    elif work_stats['budget'] >= 45:
        score += 10
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
        return "분투한 소장"

    max_score = max(type_scores.values())
    top_types = [t for t, s in type_scores.items() if s == max_score]

    # 동점이면 랜덤 선택
    return random.choice(top_types)


def generate_random_game_state() -> Dict:
    """랜덤한 게임 상태 생성"""
    # 총 선택 횟수 (게임 플레이 시 일반적인 범위)
    total_choices = random.randint(20, 35)

    # 각 focus 영역의 선택 횟수
    # 하나의 영역에 집중하거나, 골고루 분산될 수 있음
    focus_distribution = random.choice([
        'single_focus',      # 한 영역 집중
        'dual_focus',        # 두 영역 집중
        'balanced',          # 균등 분배
        'random'             # 완전 랜덤
    ])

    if focus_distribution == 'single_focus':
        # 한 영역에 집중
        main_focus = random.choice(['reputation', 'budget', 'staff', 'project'])
        reputation_focused = random.randint(8, 15) if main_focus == 'reputation' else random.randint(0, 3)
        budget_focused = random.randint(8, 15) if main_focus == 'budget' else random.randint(0, 3)
        staff_focused = random.randint(8, 15) if main_focus == 'staff' else random.randint(0, 3)
        project_focused = random.randint(8, 15) if main_focus == 'project' else random.randint(0, 3)
    elif focus_distribution == 'dual_focus':
        # 두 영역에 집중
        focuses = random.sample(['reputation', 'budget', 'staff', 'project'], 2)
        reputation_focused = random.randint(6, 12) if 'reputation' in focuses else random.randint(0, 3)
        budget_focused = random.randint(6, 12) if 'budget' in focuses else random.randint(0, 3)
        staff_focused = random.randint(6, 12) if 'staff' in focuses else random.randint(0, 3)
        project_focused = random.randint(6, 12) if 'project' in focuses else random.randint(0, 3)
    elif focus_distribution == 'balanced':
        # 균등하게 분배
        avg = total_choices // 4
        reputation_focused = random.randint(avg - 2, avg + 2)
        budget_focused = random.randint(avg - 2, avg + 2)
        staff_focused = random.randint(avg - 2, avg + 2)
        project_focused = random.randint(avg - 2, avg + 2)
    else:
        # 완전 랜덤
        reputation_focused = random.randint(0, 10)
        budget_focused = random.randint(0, 10)
        staff_focused = random.randint(0, 10)
        project_focused = random.randint(0, 10)

    risk_taking = random.randint(0, total_choices)

    # 스탯 생성 (시작 스탯에서 변화를 고려)
    # 시작: reputation=40, staff_morale=45, budget=30, project_success=35
    # 일반적으로 30-80 범위로 움직임
    reputation = random.randint(20, 90)
    budget_execution_rate = random.randint(20, 90)
    staff_morale = random.randint(20, 90)
    project_success = random.randint(20, 90)

    # 스트레스와 웰빙 (0-100)
    stress = random.randint(0, 100)
    wellbeing = random.randint(0, 100)

    return {
        'reputation': reputation,
        'budget_execution_rate': budget_execution_rate,
        'staff_morale': staff_morale,
        'project_success': project_success,
        'stress': stress,
        'wellbeing': wellbeing,
        'reputation_focused': reputation_focused,
        'budget_focused': budget_focused,
        'staff_focused': staff_focused,
        'project_focused': project_focused,
        'risk_taking': risk_taking,
        'total_choices': total_choices
    }


def run_simulation(num_simulations: int = 100000) -> Dict[str, float]:
    """몬테카를로 시뮬레이션 실행"""
    print(f"🎲 {num_simulations:,}회 시뮬레이션 시작...\n")

    results = []
    for i in range(num_simulations):
        if (i + 1) % 10000 == 0:
            print(f"진행중: {i + 1:,} / {num_simulations:,} ({(i+1)/num_simulations*100:.1f}%)")

        state = generate_random_game_state()
        director_type = determine_director_type(**state)
        results.append(director_type)

    # 결과 집계
    counter = Counter(results)
    total = len(results)

    probabilities = {
        director_type: (count / total) * 100
        for director_type, count in counter.items()
    }

    return probabilities, counter


def print_results(probabilities: Dict[str, float], counter: Counter):
    """결과 출력"""
    print("\n" + "="*70)
    print("📊 소장 유형 도달 확률 분석 결과")
    print("="*70)

    # 확률 기준으로 정렬
    sorted_results = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)

    print(f"\n{'순위':<4} {'소장 유형':<20} {'확률':<12} {'시뮬레이션 횟수':<15} {'막대 그래프'}")
    print("-" * 70)

    for rank, (director_type, prob) in enumerate(sorted_results, 1):
        count = counter[director_type]
        bar_length = int(prob * 0.5)  # 스케일링
        bar = "█" * bar_length
        print(f"{rank:<4} {director_type:<20} {prob:>6.2f}%     {count:>8,}회      {bar}")

    print("-" * 70)

    # 통계 요약
    max_prob = max(probabilities.values())
    min_prob = min(probabilities.values())
    avg_prob = sum(probabilities.values()) / len(probabilities)

    print(f"\n📈 통계 요약:")
    print(f"   - 총 유형 수: {len(probabilities)}개")
    print(f"   - 평균 확률: {avg_prob:.2f}% (균등 분포 시 {100/12:.2f}%)")
    print(f"   - 최대 확률: {max_prob:.2f}%")
    print(f"   - 최소 확률: {min_prob:.2f}%")
    print(f"   - 확률 편차: {max_prob - min_prob:.2f}%p")

    # 편중도 분석
    print(f"\n⚠️  편중도 분석:")
    high_prob_types = [t for t, p in probabilities.items() if p > avg_prob * 1.5]
    low_prob_types = [t for t, p in probabilities.items() if p < avg_prob * 0.5]

    if high_prob_types:
        print(f"   - 높은 확률 유형 (평균의 1.5배 이상):")
        for t in high_prob_types:
            print(f"      • {t}: {probabilities[t]:.2f}%")

    if low_prob_types:
        print(f"   - 낮은 확률 유형 (평균의 0.5배 이하):")
        for t in low_prob_types:
            print(f"      • {t}: {probabilities[t]:.2f}%")

    print("\n" + "="*70)


if __name__ == "__main__":
    # 시뮬레이션 실행
    probabilities, counter = run_simulation(num_simulations=100000)

    # 결과 출력
    print_results(probabilities, counter)

    print("\n💡 분석:")
    print("   우선순위 기반 결정 트리 구조로 인해 상위 조건에 해당하는")
    print("   유형들이 더 높은 확률을 가지며, 하위 폴백 조건의 유형들은")
    print("   상대적으로 낮은 확률을 가집니다.")
    print()

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
    """소장 유형 결정 로직 (koica_game.py의 _determine_director_types 로직 복제)"""

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
    is_balanced = variance < 200

    # 플레이 스타일 분석
    risk_ratio = risk_taking / total_choices if total_choices > 0 else 0

    # 스트레스와 웰빙으로 생활 패턴 분석
    is_high_stress = stress >= 70
    is_high_wellbeing = wellbeing >= 65
    is_low_stress = stress <= 35

    # 가장 중점을 둔 영역 찾기
    focus_areas = {
        'reputation': reputation_focused,
        'budget': budget_focused,
        'staff': staff_focused,
        'project': project_focused
    }
    max_focus = max(focus_areas.values()) if focus_areas.values() else 0
    most_focused = max(focus_areas, key=focus_areas.get) if max_focus > 0 else None

    # === 유형 결정 로직 (우선순위 기반) ===

    # 1. 극단적 특성 먼저 체크
    if risk_ratio > 0.35 and max_stat >= 55:
        return "혁신적인 소장"

    if is_high_wellbeing and is_low_stress and avg_stat >= 55:
        return "여유로운 소장"

    if is_high_stress and avg_stat >= 65:
        return "헌신적인 소장"

    # 2. 균형형 체크
    if is_balanced and avg_stat >= 60:
        return "균형잡힌 소장"

    # 3. 스탯 + 플레이 스타일 조합으로 결정
    if most_focused == 'staff' and staff_focused >= 3:
        if is_low_stress and max_stat >= 60:
            return "온화한 소장"
        return "사람 중심 소장"

    if most_focused == 'reputation' and reputation_focused >= 3:
        if risk_ratio < 0.15 and max_stat >= 60:
            return "신중한 외교가"
        return "외교적인 소장"

    if most_focused == 'project' and project_focused >= 3:
        if risk_ratio > 0.25:
            return "진취적인 소장"
        return "성과 중심 소장"

    if most_focused == 'budget' and budget_focused >= 3:
        return "실무형 소장"

    # 4. 스탯 기반 결정 (플레이 스타일이 명확하지 않을 때)
    if max_stat_name == 'staff' and max_stat >= 60:
        return "사람 중심 소장"
    elif max_stat_name == 'reputation' and max_stat >= 60:
        return "외교적인 소장"
    elif max_stat_name == 'project' and max_stat >= 60:
        return "성과 중심 소장"
    elif max_stat_name == 'budget' and max_stat >= 60:
        return "실무형 소장"

    # 5. 기본 유형
    if avg_stat >= 55:
        return "안정적인 소장"
    elif avg_stat >= 45:
        return "성실한 소장"
    else:
        return "분투한 소장"


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
    print(f"   - 평균 확률: {avg_prob:.2f}% (균등 분포 시 {100/14:.2f}%)")
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

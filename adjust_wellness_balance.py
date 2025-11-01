#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
웰빙 밸런스 조정 스크립트
- 웰빙 감소를 완화
- 웰빙 증가를 강화
"""

import json
import math

def adjust_wellbeing(value):
    """웰빙 값을 조정

    규칙:
    - 큰 감소 (-10 이상): 70%로 완화
    - 중간 감소 (-5~-9): 80%로 완화
    - 작은 감소 (-1~-4): 80%로 완화
    - 증가 (양수): 120%로 강화
    - 0: 변경 없음
    """
    if value == 0:
        return 0
    elif value > 0:
        # 증가는 120%로 강화
        return round(value * 1.2)
    elif value <= -10:
        # 큰 감소는 70%로 완화 (절대값 기준)
        return round(value * 0.7)
    else:
        # 작은~중간 감소는 80%로 완화
        return round(value * 0.8)

def process_scenarios(scenarios):
    """시나리오 내의 모든 웰빙 값을 조정"""
    changes_count = 0

    for scenario_id, scenario in scenarios.items():
        if 'choices' not in scenario:
            continue

        for choice in scenario['choices']:
            if 'result' not in choice:
                continue

            result = choice['result']

            # stats 내의 wellbeing 조정
            if 'stats' in result and 'wellbeing' in result['stats']:
                old_value = result['stats']['wellbeing']
                new_value = adjust_wellbeing(old_value)

                if old_value != new_value:
                    result['stats']['wellbeing'] = new_value
                    changes_count += 1
                    print(f"[{scenario_id}] wellbeing: {old_value} → {new_value}")

    return changes_count

def main():
    # scenarios.json 읽기
    with open('scenarios.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    print("=" * 60)
    print("웰빙 밸런스 조정 시작")
    print("=" * 60)

    # 조정 실행
    changes_count = process_scenarios(scenarios)

    print("=" * 60)
    print(f"총 {changes_count}개의 웰빙 값이 조정되었습니다.")
    print("=" * 60)

    # 백업 생성
    with open('scenarios.json.backup', 'w', encoding='utf-8') as f:
        # 원본을 다시 읽어서 백업
        with open('scenarios.json', 'r', encoding='utf-8') as orig:
            f.write(orig.read())

    print("백업 파일 생성: scenarios.json.backup")

    # 수정된 내용 저장
    with open('scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    print("수정 완료: scenarios.json")

if __name__ == "__main__":
    main()

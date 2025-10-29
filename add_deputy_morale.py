#!/usr/bin/env python3
"""
시나리오 파일에 deputy_morale을 자동으로 추가하는 스크립트
"""
import json
import sys

def add_deputy_morale_to_scenarios(scenarios_file):
    """시나리오 파일을 읽어서 deputy_morale이 없는 선택지에 추가"""

    with open(scenarios_file, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    modified_count = 0

    for scenario_id, scenario_data in scenarios.items():
        if 'choices' not in scenario_data:
            continue

        for choice in scenario_data['choices']:
            if 'result' not in choice:
                continue

            result = choice['result']

            # deputy_morale이 이미 있으면 스킵
            if 'deputy_morale' in result:
                continue

            # stats가 있는 경우에만 deputy_morale 추가
            if 'stats' not in result:
                continue

            # 선택지 텍스트를 기반으로 deputy_morale 결정
            choice_text = choice.get('text', '').lower()

            # 기본값
            principled_change = 3
            local_friendly_change = 3

            # 키워드 기반 분석
            principled_keywords = ['규정', '원칙', '절차', '체계', '본부', '보고서', '계획']
            local_keywords = ['현지', '주민', '파트너', '협력', '간담회', '관계', '소통']

            principled_score = sum(1 for kw in principled_keywords if kw in choice_text)
            local_score = sum(1 for kw in local_keywords if kw in choice_text)

            if principled_score > local_score:
                principled_change = 8
                local_friendly_change = 2
            elif local_score > principled_score:
                principled_change = 2
                local_friendly_change = 8
            else:
                principled_change = 5
                local_friendly_change = 5

            # deputy_morale 추가
            result['deputy_morale'] = {
                'principled': principled_change,
                'local_friendly': local_friendly_change
            }
            modified_count += 1

    # 파일에 저장
    with open(scenarios_file, 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    print(f"✓ {modified_count}개의 선택지에 deputy_morale을 추가했습니다.")
    return modified_count

if __name__ == '__main__':
    scenarios_file = 'scenarios.json'
    if len(sys.argv) > 1:
        scenarios_file = sys.argv[1]

    try:
        count = add_deputy_morale_to_scenarios(scenarios_file)
        print(f"완료: {scenarios_file}")
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)

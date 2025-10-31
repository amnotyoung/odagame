#!/usr/bin/env python3
"""
게임 밸런스 조정 스크립트
스탯 증가폭을 줄이고 부정적 효과를 강화하여 난이도를 높입니다.
"""
import json
import math

def adjust_stat_value(value):
    """
    스탯 값을 밸런스 조정합니다.

    긍정적 값(증가): 큰 값일수록 더 많이 감소
    - 30+ → 약 60% (18)
    - 25-29 → 약 55% (14-16)
    - 20-24 → 약 50-55% (10-13)
    - 15-19 → 약 55-60% (8-11)
    - 10-14 → 약 60-70% (6-9)
    - 5-9 → 약 70-80% (4-7)
    - 1-4 → 유지

    부정적 값(감소): 20% 더 강화
    """
    if value > 0:
        # 긍정적 증가 - 큰 값일수록 더 많이 감소
        if value >= 30:
            return int(value * 0.6)
        elif value >= 25:
            return int(value * 0.55)
        elif value >= 20:
            return int(value * 0.52)
        elif value >= 15:
            return int(value * 0.58)
        elif value >= 10:
            return int(value * 0.65)
        elif value >= 5:
            return int(value * 0.75)
        else:
            return value  # 1-4는 유지
    elif value < 0:
        # 부정적 감소 - 20% 더 강화
        return int(value * 1.2)
    else:
        return 0

def adjust_stats_in_dict(data):
    """재귀적으로 딕셔너리/리스트를 순회하며 stats 값을 조정"""
    if isinstance(data, dict):
        # stats 필드를 찾으면 조정
        if 'stats' in data and isinstance(data['stats'], dict):
            for stat_name in ['reputation', 'budget', 'staff_morale', 'project_success',
                            'stress', 'wellbeing']:
                if stat_name in data['stats']:
                    original = data['stats'][stat_name]
                    adjusted = adjust_stat_value(original)
                    data['stats'][stat_name] = adjusted
                    if original != adjusted:
                        print(f"  {stat_name}: {original:+d} → {adjusted:+d}")

        # 모든 키-값 쌍에 대해 재귀 처리
        for key, value in data.items():
            adjust_stats_in_dict(value)

    elif isinstance(data, list):
        # 리스트의 각 항목에 대해 재귀 처리
        for item in data:
            adjust_stats_in_dict(item)

def main():
    # JSON 파일 읽기
    input_file = '/home/user/odagame/scenarios.json'

    print("게임 밸런스 조정 중...")
    print("=" * 60)

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 스탯 조정
    print("\n스탯 변화:")
    adjust_stats_in_dict(data)

    # 결과 저장
    with open(input_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("✓ 밸런스 조정 완료!")
    print(f"✓ {input_file} 업데이트됨")

if __name__ == '__main__':
    main()

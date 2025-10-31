#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시나리오 가독성 개선 스크립트
- 배경 설명과 주요 이슈를 구분
- 각 이슈를 불릿 포인트로 표시
"""

import json
import re

def improve_description(description):
    """
    시나리오 설명을 가독성 좋게 포맷팅
    """
    # 이미 불릿 포인트가 있으면 그대로 반환
    if '\n- ' in description or '\n• ' in description:
        return description

    # \n\n으로 구분된 단락들을 분리
    paragraphs = description.split('\n\n')

    if len(paragraphs) >= 2:
        # 첫 번째 단락은 배경 설명
        background = paragraphs[0]
        result = background + '\n\n'

        # 나머지 단락들을 불릿 포인트로
        for para in paragraphs[1:]:
            # 단락을 접속어 기준으로 추가 분할
            issues = split_by_connectors(para)
            for issue in issues:
                if issue.strip():
                    result += '- ' + issue.strip() + '\n'

        return result.rstrip()

    # 단락이 하나인 경우, 접속어 기준으로 분할 시도
    text = description

    # 배경 설명과 이슈를 구분하는 패턴 찾기
    # "당신의", "부소장이", "현재", "이때" 등으로 시작하는 문장을 이슈의 시작으로 간주
    issue_start_pattern = r'(?<=[.!?]\s)(?=당신의|부소장이|현재|이때|동시에|또한|한편|그런데|그러나|하지만)'

    parts = re.split(issue_start_pattern, text)

    if len(parts) <= 1:
        # 분할 실패 시 원본 반환
        return description

    # 첫 부분은 배경
    background = parts[0].strip()
    result = background + '\n\n'

    # 나머지는 이슈로 처리
    remaining = ' '.join(parts[1:])
    issues = split_by_connectors(remaining)

    for issue in issues:
        if issue.strip():
            result += '- ' + issue.strip() + '\n'

    return result.rstrip()

def split_by_connectors(text):
    """
    접속어를 기준으로 텍스트를 분할
    """
    # 접속어 패턴: "동시에", "또한", "한편" 등
    # 마침표, 느낌표, 물음표 또는 인용문(") 뒤에 오는 접속어를 찾음
    connector_pattern = r'(?<=[.!?"]\s)(?=동시에|또한|한편|그런데|그러나|하지만|더불어)'

    parts = re.split(connector_pattern, text)

    # 빈 문자열 제거
    return [p.strip() for p in parts if p.strip()]

def main():
    # JSON 파일 읽기
    with open('scenarios.json', 'r', encoding='utf-8') as f:
        scenarios = json.load(f)

    # 각 시나리오의 description 개선
    modified_count = 0
    for key, scenario in scenarios.items():
        if 'description' in scenario:
            original = scenario['description']
            improved = improve_description(original)

            if original != improved:
                scenario['description'] = improved
                modified_count += 1
                print(f"✓ {key} - description 개선 완료")

    # JSON 파일 저장 (들여쓰기 2칸, 한글 유니코드 그대로)
    with open('scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=2)

    print(f"\n총 {modified_count}개 시나리오 가독성 개선 완료!")

if __name__ == '__main__':
    main()

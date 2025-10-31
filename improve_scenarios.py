#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOICA 시뮬레이션 개선 스크립트
- period_8: 부패 묵인 선택지 삭제 및 대체
- period_2: PMC 선정 설명 강화
- period_5: 자원 제약 명확화
- period_9: 안전 위기 패널티 논리 강화
- period_11: 솔직한 인계 재평가
"""

import json
import sys
from pathlib import Path

def load_scenarios():
    """scenarios.json 파일 로드"""
    with open('scenarios.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_scenarios(data):
    """scenarios.json 파일 저장"""
    with open('scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def improve_period_8(scenarios):
    """
    CRITICAL: period_8의 '현지 관행 묵인' 선택지를
    '제3자 감사 + 시스템 개선 병행'으로 교체
    """
    print("🔴 CRITICAL: period_8 개선 중...")

    period_8 = scenarios['period_8']

    # 4번째 선택지 (인덱스 3) 교체
    period_8['choices'][3] = {
        "text": "제3자 감사 + 시스템 개선 병행 - 투명성과 재발 방지",
        "subtext": "✦ 철학: 투명한 조사 + 장기적 시스템 개선",
        "trade_off": "신뢰성↑, 재발 방지 | 시간과 비용 소요",
        "result": {
            "message": "외부 회계법인에 의뢰해 투명한 조사를 진행하는 동시에, 재발 방지를 위한 내부 통제 시스템을 강화했습니다. 시간과 비용이 들었지만 조직의 신뢰성을 지켰고, 이후 유사 사례가 발생하지 않았습니다. 현지 파트너들도 \"공정한 조사였다\"고 인정했습니다.",
            "stats": {
                "reputation": 10,
                "project_success": 3,
                "budget": -24,
                "staff_morale": 6
            },
            "trade_off_message": "✓ 투명한 문제 해결과 시스템 개선. ⚠️ 단, 시간과 비용 소요",
            "deputy_morale": {
                "principled": 15,
                "local_friendly": 5
            },
            "advance_time": True,
            "next": "period_9"
        }
    }

    # 기존 1-3번 선택지에도 subtext, trade_off 추가
    period_8['choices'][0]['subtext'] = "✦ 철학: 투명성과 원칙 최우선"
    period_8['choices'][0]['trade_off'] = "평판↑, 원칙 지킴 | 사업 지연, 직원 부담"
    period_8['choices'][0]['result']['trade_off_message'] = "✓ 원칙적 대응으로 신뢰 확보. ⚠️ 단, 사업 지연과 관계 악화"

    period_8['choices'][1]['subtext'] = "✦ 철학: 관계 유지하며 문제 해결"
    period_8['choices'][1]['trade_off'] = "관계 유지, 사업 계속 | 본부 의심, 평판 리스크"
    period_8['choices'][1]['result']['trade_off_message'] = "✓ 조용한 해결로 관계 유지. ⚠️ 단, 본부의 의심과 감사 리스크"

    period_8['choices'][2]['subtext'] = "✦ 철학: 객관성과 공정성 확보"
    period_8['choices'][2]['trade_off'] = "공정성↑, 의혹 해소 | 비용과 시간 소요"
    period_8['choices'][2]['result']['trade_off_message'] = "✓ 객관적 조사로 의혹 해소. ⚠️ 단, 비용과 시간 필요"

    print("   ✅ period_8 개선 완료")

def improve_period_2(scenarios):
    """
    MAJOR: period_2 PMC 선정 - 설명 및 선택지 강화
    """
    print("🟡 MAJOR: period_2 개선 중...")

    period_2 = scenarios['period_2']

    # description 강화
    period_2['description'] = """3월입니다. 본부 지역실을 통해 신규 국별협력사업의 PMC(사업관리 컨설턴트) 선정이 완료되었습니다. 기술가격종합평가 결과 A사 컨소시엄이 최종 선정되어 계약이 체결되었습니다.

**현재 상황:**
- PMC는 전문성 높지만, 현지 네트워크 부족
- 본부는 명확한 성과지표 달성 요구
- 현지 정부는 참여형 접근 선호
- 당신의 관리 역량은 제한적 (다른 업무도 많음)

**중요:** 향후 2-3년 협력 방식을 결정하는 순간입니다.
부소장이 조언합니다: "소장님, PMC 관리 방식은 한 번 정하면 바꾸기 어렵습니다. 우리 역량과 상황을 고려해 현실적으로 선택해야 합니다."
다음 주 착수보고회가 예정되어 있고, 4월 KOICA 설립기념일(4.1) 전까지 프로젝트 착수 계획을 확정해야 합니다."""

    # 선택지 강화
    period_2['choices'][0]['text'] = "PMC 전문성 신뢰 - 자율성 최대 부여"
    period_2['choices'][0]['subtext'] = "✦ 철학: 전문가에게 맡기고 결과로 평가"
    period_2['choices'][0]['trade_off'] = "PMC 사기↑, 속도↑ | 통제력↓, 방향 이탈 리스크"
    period_2['choices'][0]['result']['message'] = "PMC에게 최대한의 자율성을 부여하기로 했습니다. 착수보고회에서 A사의 체계적인 계획이 발표되었고, 본부와 현지 정부 모두 만족스러워합니다. PMC팀도 사무소의 신뢰에 감사를 표하며 \"기대에 부응하겠다\"고 다짐합니다."
    period_2['choices'][0]['result']['trade_off_message'] = "✓ PMC의 전문성을 최대한 활용. ⚠️ 단, 예상치 못한 방향 전환이 있을 수 있습니다."

    period_2['choices'][1]['text'] = "밀착 모니터링 - 주간 회의 + 월간 점검"
    period_2['choices'][1]['subtext'] = "✦ 철학: 작은 문제도 조기 발견, 철저한 관리"
    period_2['choices'][1]['trade_off'] = "문제 조기 발견 | PMC 부담↑, 당신 업무량↑↑"
    period_2['choices'][1]['result']['message'] = "주간 회의와 월간 모니터링을 통해 PMC와 밀착 협력하기로 했습니다. 초기에는 다소 부담스러워했으나, 현지 정부와의 소통 과정에서 사무소의 적극적 지원이 큰 도움이 되었습니다. 당신의 업무 강도는 상당히 높아졌습니다."
    period_2['choices'][1]['result']['trade_off_message'] = "✓ 철저한 관리로 리스크 감소. ⚠️ 단, 팀 전체가 지칠 수 있습니다."

    period_2['choices'][2]['text'] = "현지 네트워크 연결 - 중재자 역할 집중"
    period_2['choices'][2]['subtext'] = "✦ 철학: PMC 약점 보완, 현지 관계 활용"
    period_2['choices'][2]['trade_off'] = "현지 신뢰↑, 장기 파트너십 | 성과 측정 어려움"
    period_2['choices'][2]['result']['message'] = "PMC와 현지 이해관계자를 연결하는 데 집중하기로 했습니다. 현지 정부 부처, 시민사회, 대학 등을 PMC팀에게 소개했습니다. PMC 팀장이 감사를 표합니다. \"사무소의 네트워크가 큰 자산입니다. 혼자서는 불가능했을 겁니다.\""
    period_2['choices'][2]['result']['trade_off_message'] = "✓ 현지 관계 강화로 장기 성공 가능성↑. ⚠️ 단, 단기 성과는 불명확."

    period_2['choices'][3]['text'] = "성과 지표 중심 - 명확한 KPI와 분기 평가"
    period_2['choices'][3]['subtext'] = "✦ 철학: 투명한 성과 관리, 책임성 강화"
    period_2['choices'][3]['trade_off'] = "명확한 목표, 본부 만족 | 관계 경직, 창의성↓"
    period_2['choices'][3]['result']['message'] = "PMC와 명확한 성과지표(KPI)를 설정하고 분기별 평가 체계를 수립했습니다. 투명한 성과 관리로 책임성이 강화되었고, PMC도 목표가 명확해져 효율적으로 일할 수 있게 되었습니다. 초기 세팅에 시간이 걸렸으나 체계적인 관리가 가능해졌습니다."
    period_2['choices'][3]['result']['trade_off_message'] = "✓ 명확한 책임성 확보. ⚠️ 단, 현지 파트너는 '수치 중심'을 불편해할 수 있음."

    print("   ✅ period_2 개선 완료")

def improve_period_5(scenarios):
    """
    MAJOR: period_5 자원 제약 상황 명확화
    """
    print("🟡 MAJOR: period_5 개선 중...")

    period_5 = scenarios['period_5']

    # description 강화
    period_5['description'] = """가을입니다. 연수 프로그램이 종강을 맞이하고, 봉사단 환송 시즌입니다.

**동시에 발생한 세 가지 기회:**
1. 주요 프로젝트 중간 완료 → 정부·언론 초청 성과보고회 제안
2. 6개월 임기 마친 KOICA 봉사단 8명 환송식 준비 필요
3. 현지 NGO 네트워크의 장기 협력 MOU 체결 제안

**현실적 제약:**
- 사무소 인력: 15명 (이미 일상 업무로 바쁨)
- 가용 예산: 2천만원
- 당신의 시간: 이번 달 3주만 집중 가능

부소장이 말합니다: "소장님, 세 가지 모두 의미있지만 우리 역량으로는 하나만 제대로 할 수 있습니다. 무엇에 집중하시겠습니까?\""""

    # 선택지 강화
    period_5['choices'][0]['text'] = "성과 보고회 집중 - 대규모 이벤트 (예산 2천만원)"
    period_5['choices'][0]['subtext'] = "✦ 전략: 대외 이미지, 차년도 예산 확보"
    period_5['choices'][0]['trade_off'] = "평판↑↑, 예산 기회 | 내부 사기 소홀"
    period_5['choices'][0]['result']['message'] = "프로젝트 성과가 널리 알려졌습니다. 현지 언론이 크게 보도했고, 평판이 급상승했습니다. 정부 고위층도 참석해 차년도 협력 확대를 약속했습니다. 하지만 봉사단 환송식은 간소하게 진행되어 일부 단원들이 아쉬워했습니다."
    period_5['choices'][0]['result']['trade_off_message'] = "✓ 대외적 성공. ⚠️ 단, 조직 내부는 \"외부만 신경쓴다\"고 느낌"

    period_5['choices'][1]['text'] = "봉사단 환송 집중 - 감동적이고 의미있는 이별 (예산 500만원)"
    period_5['choices'][1]['subtext'] = "✦ 전략: 조직 문화, 향후 지원자 확보"
    period_5['choices'][1]['trade_off'] = "내부 결속↑, 모집↑ | 외부 기회 상실"
    period_5['choices'][1]['result']['message'] = "환송식이 감동적이었습니다. 봉사단원들이 SNS에 감사 메시지를 올렸고, 조직 분위기가 매우 좋아졌습니다. \"KOICA는 사람을 소중히 여긴다\"는 평판이 퍼져 다음 기수 지원자가 크게 늘었습니다. 하지만 성과 보고 기회는 놓쳤습니다."
    period_5['choices'][1]['result']['trade_off_message'] = "✓ 조직 문화 강화. ⚠️ 단, 대외 성과 홍보 기회는 아쉬움"

    period_5['choices'][2]['text'] = "NGO 네트워크 구축 - 장기 파트너십 투자 (예산 1천만원)"
    period_5['choices'][2]['subtext'] = "✦ 전략: 미래 준비, 지속가능성"
    period_5['choices'][2]['trade_off'] = "장기 기반↑ | 단기 성과 없음"
    period_5['choices'][2]['result']['message'] = "5개 NGO와 MOU를 체결했습니다. 향후 사업 확장의 발판이 되었으나, 당장의 눈에 띄는 성과는 미미합니다. 본부에서는 \"이게 뭐가 중요한 거냐\"는 반응이고, 직원들도 \"이게 무슨 의미인지\" 의문을 품습니다."
    period_5['choices'][2]['result']['trade_off_message'] = "✓ 장기 투자. ⚠️ 단, 1-2년 내 성과로 드러나지 않음"

    period_5['choices'][3]['text'] = "세 가지 균등 분배 - 모두 '적당히' 진행 (예산 1천만원)"
    period_5['choices'][3]['subtext'] = "✦ 전략: 안전한 선택, 리스크 회피"
    period_5['choices'][3]['trade_off'] = "실패 없음 | 기회도 못 잡음, 평범함"
    period_5['choices'][3]['result']['message'] = "세 가지를 모두 진행했습니다. 성과 보고회는 소규모로, 환송식은 간소하게, NGO는 MOU만 체결했습니다. 무난했지만 특별한 것은 없었습니다. 부소장이 조심스럽게 말합니다. \"소장님, 무난했지만... 기회를 살리지는 못한 것 같습니다.\""
    period_5['choices'][3]['result']['trade_off_message'] = "✓ 안전한 선택. ⚠️ 하지만 '리더십 부재'라는 평가 가능"

    print("   ✅ period_5 개선 완료")

def improve_period_9(scenarios):
    """
    MINOR: period_9 안전 위기 패널티 논리 강화
    """
    print("🟢 MINOR: period_9 개선 중...")

    period_9 = scenarios['period_9']

    # 선택지 강화
    period_9['choices'][0]['subtext'] = "⚠️ 가장 안전하지만 '과잉 대응' 비판 가능"
    period_9['choices'][0]['trade_off'] = "생명 보호 최우선 | 현지 신뢰 손실, 과잉 대응 논란"
    period_9['choices'][0]['result']['message'] = "신속한 철수로 인명 피해는 없었습니다. 본부와 가족들이 안도했습니다. 하지만 현지에서는 \"실제 위험은 멀었는데 너무 겁을 먹었다\", \"우리는 여기서 계속 살아야 하는데...\"라는 비판이 나왔습니다. 현지 파트너들이 서운해하며 \"진짜 위기였다면 이해하지만, 이번은 과했다\"고 말합니다."
    period_9['choices'][0]['result']['trade_off_message'] = "✓ 생명 보호. ❌ 단, 현지에서 '신뢰 잃은 파트너'로 인식"

    period_9['choices'][1]['subtext'] = "✦ 위험도 평가하며 유연하게 대응"
    period_9['choices'][1]['trade_off'] = "평판 유지, 사업 계속 | 직원 불안과 스트레스"
    period_9['choices'][1]['result']['message'] = "신중한 판단이었습니다. 매일 안보 상황을 모니터링하며 대기했고, 다행히 상황이 악화되지 않아 사업을 유지했습니다. 현지 평판도 지켰습니다. 하지만 직원들은 \"만약 악화됐다면?\"이라는 불안 속에 긴장된 시간을 보냈습니다."
    period_9['choices'][1]['result']['trade_off_message'] = "✓ 균형잡힌 판단. ⚠️ 단, 직원들의 심리적 부담 컸음"

    period_9['choices'][2]['subtext'] = "✦ 리스크 분산, 유연한 대응"
    period_9['choices'][2]['trade_off'] = "균형잡힌 대응 | 결정 기준 불명확"
    period_9['choices'][2]['result']['trade_off_message'] = "✓ 균형잡힌 대응. ⚠️ 단, 일관성 부족 우려"

    period_9['choices'][3]['subtext'] = "✦ 안전 확보 + 사업 연속성 준비"
    period_9['choices'][3]['trade_off'] = "안전 + 복귀 가능성 | 사업 일시 중단, 비용"
    period_9['choices'][3]['result']['trade_off_message'] = "✓ 안전 확보와 복귀 준비. ⚠️ 단, 현지 파트너는 실망"

    print("   ✅ period_9 개선 완료")

def improve_period_11(scenarios):
    """
    MAJOR: period_11 솔직한 인계 재평가
    """
    print("🟡 MAJOR: period_11 개선 중...")

    period_11 = scenarios['period_11']

    # 4번째 선택지 강화
    period_11['choices'][3]['text'] = "미해결 과제 + 리스크 중심 인계 - 투명하고 책임있는 조언"
    period_11['choices'][3]['subtext'] = "✦ 철학: 후임자의 성공이 진짜 성과"
    period_11['choices'][3]['trade_off'] = "후임 성공 가능성↑ | 본부는 다소 불편"
    period_11['choices'][3]['result']['message'] = "성과보다는 '미해결 과제'와 '잠재적 위험'을 솔직하게 정리해 후임자에게 전달했습니다. 어느 파트너가 신뢰도가 낮은지, 어떤 사업이 위험한지 숨김없이 공유했습니다. 후임자는 \"이런 인수인계는 처음입니다. 정말 감사합니다\"라며 깊이 감사했고, 현지 직원들도 소장님의 책임감에 존경을 표했습니다. 본부는 다소 불편해했지만, 6개월 후 후임자가 \"덕분에 시행착오를 줄였다\"고 보고했습니다."
    period_11['choices'][3]['result']['stats']['reputation'] = 3
    period_11['choices'][3]['result']['trade_off_message'] = "✓ 진정한 책임감. 본부는 처음엔 불편했지만 장기적으로 긍정 평가"

    # 다른 선택지에도 subtext, trade_off 추가
    period_11['choices'][0]['subtext'] = "✦ 전략: 대외 레거시, 가시적 성과"
    period_11['choices'][0]['trade_off'] = "평판↑↑, 레거시 | 직원 소홀, 비용"
    period_11['choices'][0]['result']['trade_off_message'] = "✓ 화려한 마무리. ⚠️ 단, 내실보다 외형"

    period_11['choices'][1]['subtext'] = "✦ 전략: 후임 지원, 조직 안정"
    period_11['choices'][1]['trade_off'] = "내실↑, 직원 안정 | 대외 인지도↓"
    period_11['choices'][1]['result']['trade_off_message'] = "✓ 내실있는 인계. ⚠️ 단, 대외적으로는 조용함"

    period_11['choices'][2]['subtext'] = "✦ 전략: 관계 자산 축적"
    period_11['choices'][2]['trade_off'] = "장기 네트워크↑ | 비용, 즉각적 효과 미미"
    period_11['choices'][2]['result']['trade_off_message'] = "✓ 관계의 유산. ⚠️ 단, 비용과 시간 필요"

    print("   ✅ period_11 개선 완료")

def main():
    print("=" * 60)
    print("KOICA 시뮬레이션 개선 작업 시작")
    print("=" * 60)

    # 백업 생성
    print("\n📁 기존 파일 백업 중...")
    import shutil
    shutil.copy2('scenarios.json', 'scenarios.json.before_improvement')
    print("   ✅ 백업 완료: scenarios.json.before_improvement")

    # 파일 로드
    print("\n📖 scenarios.json 로드 중...")
    scenarios = load_scenarios()
    print("   ✅ 로드 완료")

    # 각 period 개선
    print("\n🔧 개선 작업 진행...")
    improve_period_8(scenarios)
    improve_period_2(scenarios)
    improve_period_5(scenarios)
    improve_period_9(scenarios)
    improve_period_11(scenarios)

    # 파일 저장
    print("\n💾 scenarios.json 저장 중...")
    save_scenarios(scenarios)
    print("   ✅ 저장 완료")

    print("\n" + "=" * 60)
    print("✅ 모든 개선 작업 완료!")
    print("=" * 60)
    print("\n주요 변경사항:")
    print("  🔴 CRITICAL:")
    print("     - period_8: '부패 묵인' 선택지 → '제3자 감사 + 시스템 개선' 교체")
    print("  🟡 MAJOR:")
    print("     - period_2: PMC 선정 설명 및 선택지 강화")
    print("     - period_5: 자원 제약 상황 명확화")
    print("     - period_11: 솔직한 인계 선택지 재평가")
    print("  🟢 MINOR:")
    print("     - period_9: 안전 위기 패널티 논리 강화")
    print("\n모든 선택지에 다음 추가:")
    print("  - subtext: 선택의 철학/전략")
    print("  - trade_off: 예상되는 장단점")
    print("  - trade_off_message: 결과에 대한 설명")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOICA 시뮬레이션 고급 기능 구현 스크립트

1. 부소장 Morale 임계값 이벤트 시스템
2. 장기 영향 시스템 (delayed_effects)
3. 새로운 엔딩 조건
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


# ============================================================
# 1. 부소장 Morale 임계값 이벤트 시나리오
# ============================================================

DEPUTY_THRESHOLD_EVENTS = {
    "deputy_principled_high_loyalty": {
        "title": "🌟 김원칙 부소장의 전폭적 지지",
        "description": "김원칙 부소장이 찾아옵니다. \"소장님, 그동안 함께 일하면서 많이 배웠습니다. 소장님의 원칙적인 리더십 덕분에 KOICA의 진정한 가치를 깨달았습니다.\"\n\n그는 자신의 네트워크를 총동원하여 어려운 프로젝트를 성사시켰고, 본부에 당신의 업적을 적극 홍보했습니다. 직원들도 부소장의 헌신적인 모습에 감동받아 사기가 크게 올랐습니다.",
        "threshold_type": "principled",
        "threshold_value": 50,
        "one_time": True,
        "choices": [
            {
                "text": "감사를 표하고 함께 더 나은 조직을 만들자고 격려",
                "result": {
                    "message": "\"우리가 함께라면 더 큰 일을 해낼 수 있습니다.\" 당신의 말에 김원칙 부소장이 고개를 끄덕입니다. 팀 전체가 하나로 뭉쳤습니다.",
                    "stats": {
                        "reputation": 8,
                        "staff_morale": 10,
                        "project_success": 5
                    },
                    "deputy_morale": {
                        "principled": 10
                    },
                    "advance_time": False,
                    "next": None
                }
            },
            {
                "text": "부소장에게 중요한 프로젝트 전권 위임",
                "result": {
                    "message": "김원칙 부소장에게 차기 주요 사업의 전권을 위임했습니다. 그는 이 신뢰에 보답하듯 완벽한 성과를 냈고, 본부에서도 극찬했습니다.",
                    "stats": {
                        "project_success": 15,
                        "reputation": 10,
                        "staff_morale": 5
                    },
                    "deputy_morale": {
                        "principled": 15
                    },
                    "advance_time": False,
                    "next": None
                }
            }
        ],
        "ascii_art": "⭐ 부소장 충성도 ⭐\n    김원칙 부소장\n      ┌─────┐\n      │ 💼  │\n      │ 😊  │\n      └─────┘\n    ✨ 전폭 지지 ✨"
    },

    "deputy_principled_low_resignation": {
        "title": "⚠️ 김원칙 부소장의 전보 신청",
        "description": "본부에서 긴급 연락이 왔습니다. 김원칙 부소장이 전보 신청서를 제출했다는 것입니다. 그는 \"소장님의 리더십 방식과 제 가치관이 맞지 않는 것 같다\"는 사유를 적었습니다.\n\n현지 직원들 사이에서도 \"부소장님이 떠나신다\"는 소문이 돌면서 불안감이 커지고 있습니다. 이대로 두면 조직 분위기가 크게 악화될 것입니다.",
        "threshold_type": "principled",
        "threshold_value": -30,
        "one_time": True,
        "choices": [
            {
                "text": "부소장과 진솔한 대화 시도 - 소통으로 해결",
                "result": {
                    "message": "부소장을 찾아가 진솔한 대화를 나눴습니다. \"제가 소통이 부족했습니다.\" 당신의 솔직함에 부소장도 마음을 열었고, 전보 신청을 철회했습니다. 하지만 관계 회복에는 시간이 필요합니다.",
                    "stats": {
                        "staff_morale": 8,
                        "reputation": 3,
                        "stress": 12
                    },
                    "deputy_morale": {
                        "principled": 20
                    },
                    "advance_time": False,
                    "next": None
                }
            },
            {
                "text": "전보를 수용하고 새 부소장 영입",
                "result": {
                    "message": "부소장의 전보를 받아들였습니다. 새로운 부소장이 왔지만, 조직에는 \"소장님이 사람을 버렸다\"는 인식이 퍼졌고, 직원들의 신뢰가 크게 떨어졌습니다.",
                    "stats": {
                        "staff_morale": -18,
                        "reputation": -12,
                        "project_success": -12,
                        "stress": 8
                    },
                    "deputy_morale": {
                        "principled": 0,
                        "local_friendly": 0
                    },
                    "advance_time": False,
                    "next": None
                }
            }
        ],
        "ascii_art": "⚠️ 위기 상황 ⚠️\n      📋 전보신청서\n      ┌─────┐\n      │ 😞  │\n      └─────┘\n    관계 회복 필요"
    },

    "deputy_local_friendly_network_bonus": {
        "title": "🌐 박현지 부소장의 네트워크 효과",
        "description": "박현지 부소장이 그동안 쌓아온 현지 네트워크가 빛을 발하는 순간입니다. 현지 정부 고위 관료가 비공식 루트로 중요한 정보를 전달했습니다.\n\n\"다음 주 정부 예산 심의에서 우리 사업이 모델 케이스로 거론될 예정입니다. 지금 추가 제안을 하시면 승인 가능성이 높습니다.\"\n\n박현지 부소장이 말합니다. \"소장님, 지금이 절호의 기회입니다. 어떻게 하시겠습니까?\"",
        "threshold_type": "local_friendly",
        "threshold_value": 50,
        "one_time": True,
        "choices": [
            {
                "text": "즉시 추가 사업 제안서 제출 - 기회 포착",
                "result": {
                    "message": "밤을 새워 추가 제안서를 작성해 제출했습니다. 일주일 후, 정부로부터 사업 확대 승인이 떨어졌습니다. 박현지 부소장의 네트워크가 만든 기적입니다.",
                    "stats": {
                        "project_success": 20,
                        "reputation": 15,
                        "budget": 25,
                        "staff_morale": -8,
                        "stress": 15
                    },
                    "deputy_morale": {
                        "local_friendly": 15
                    },
                    "advance_time": False,
                    "next": None
                }
            },
            {
                "text": "부소장에게 감사하고 다음 기회를 준비",
                "result": {
                    "message": "\"이번엔 준비가 부족합니다. 다음 기회를 더 잘 준비하죠.\" 박현지 부소장이 이해하며 고개를 끄덕입니다. 무리하지 않은 현명한 판단이었습니다.",
                    "stats": {
                        "staff_morale": 5,
                        "reputation": 3
                    },
                    "deputy_morale": {
                        "local_friendly": 5
                    },
                    "advance_time": False,
                    "next": None
                }
            }
        ],
        "ascii_art": "🌐 네트워크 효과 🌐\n    박현지 부소장\n      ┌─────┐\n      │ 💼  │\n      │ 🤝  │\n      └─────┘\n    관계의 힘 발휘"
    },

    "deputy_local_friendly_cultural_crisis": {
        "title": "🔥 박현지 부소장의 문화적 갈등",
        "description": "박현지 부소장이 현지 파트너들과 너무 가까워지면서 문제가 발생했습니다. 본부 감사팀에서 연락이 왔습니다.\n\n\"박현지 부소장이 현지 업체 대표와 사적 만남이 잦다는 제보가 들어왔습니다. 이해 충돌 의혹이 있으니 조사가 필요합니다.\"\n\n박현지 부소장은 억울해합니다. \"현지에서는 이게 정상적인 관계 구축입니다. 오해입니다!\" 하지만 본부는 원칙을 요구하고 있습니다.",
        "threshold_type": "local_friendly",
        "threshold_value": -30,
        "one_time": True,
        "choices": [
            {
                "text": "부소장 옹호 - 문화 차이 설명",
                "result": {
                    "message": "본부에 현지 문화를 설명하고 부소장을 적극 옹호했습니다. 조사 결과 문제가 없었고, 박현지 부소장은 감사했지만 본부는 당신의 '느슨한 관리'를 우려합니다.",
                    "stats": {
                        "staff_morale": 10,
                        "reputation": -12,
                        "project_success": 3
                    },
                    "deputy_morale": {
                        "local_friendly": 15
                    },
                    "advance_time": False,
                    "next": None
                }
            },
            {
                "text": "원칙 준수 - 부소장에게 경고 및 행동 수정 요구",
                "result": {
                    "message": "부소장에게 본부 규정을 상기시키고 행동 수정을 요구했습니다. 그는 서운해했지만 따랐고, 본부는 당신의 원칙적 대응을 높이 평가했습니다.",
                    "stats": {
                        "reputation": 10,
                        "staff_morale": -8,
                        "project_success": -6
                    },
                    "deputy_morale": {
                        "local_friendly": -10,
                        "principled": 5
                    },
                    "advance_time": False,
                    "next": None
                }
            }
        ],
        "ascii_art": "🔥 갈등 상황 🔥\n      ⚖️ 문화 vs 원칙\n      ┌─────┐\n      │ 😰  │\n      └─────┘\n    어려운 선택"
    }
}


# ============================================================
# 2. 새로운 엔딩 조건 및 시나리오
# ============================================================

NEW_ENDINGS = {
    "ending_perfect_balance": {
        "title": "👑 완벽한 균형의 리더",
        "description": """2년의 임기가 끝났습니다. 당신은 기적을 만들어냈습니다.

**최종 성과:**
- 평판: 최고 수준
- 사업 성과: 모든 프로젝트 성공
- 직원 사기: 팀의 신뢰와 존경
- 예산: 효율적 집행
- 부소장들: 양측 모두의 지지

본부 이사장이 직접 전화를 걸어왔습니다. "소장님, 정말 대단합니다. 본부와 현지, 성과와 사람, 원칙과 유연성 사이에서 완벽한 균형을 찾으셨습니다. 차기 본부 이사로 모시고 싶습니다."

현지 정부 장관이 말합니다. "당신 같은 파트너는 처음입니다. 당신 덕분에 우리 국가가 발전했습니다."

직원들이 눈물을 흘리며 송별회를 준비했습니다. "소장님이 아니었다면 우리는 이렇게 성장하지 못했을 겁니다."

**당신은 KOICA 역사에 남을 전설적인 소장이 되었습니다.**

귀국 후, 당신은 본부 이사로 승진하여 더 많은 해외사무소를 이끄는 리더가 되었습니다. 당신의 리더십 철학은 KOICA의 새로운 표준이 되었습니다.""",
        "ascii_art": "👑 완벽한 균형 👑\n      ⚖️\n    ┌─────┐\n    │ 🏆  │\n    │ 🌟  │\n    └─────┘\n  전설적 리더십",
        "stats_display": True,
        "ending_type": "perfect"
    },

    "ending_burnout": {
        "title": "💔 번아웃으로 조기 귀국",
        "description": """더 이상 버틸 수 없습니다.

**당신의 상태:**
- 스트레스: 한계 초과
- 웰빙: 건강 심각
- 수면: 거의 없음
- 판단력: 저하

어느 날 아침, 침대에서 일어날 수 없었습니다. 병원 진단 결과는 '심각한 번아웃 증후군'. 의사가 말합니다. "즉시 휴식이 필요합니다. 계속 일하면 생명이 위험합니다."

본부에서 긴급 소환 명령이 떨어졌습니다. 후임자가 급히 파견되었고, 당신은 제대로 인수인계도 못한 채 한국으로 돌아왔습니다.

직원들이 공항까지 배웅을 나왔지만, 당신은 그들을 똑바로 볼 수 없었습니다. "제가 더 잘했어야 했는데..."

**6개월간의 치료 후, 당신은 KOICA를 떠나 작은 NGO에서 새 출발을 했습니다.**

돌이켜보면, '모든 것을 완벽하게' 하려던 욕심이 화근이었습니다. 때로는 '적당히'도 필요하다는 것을 너무 늦게 깨달았습니다.""",
        "ascii_art": "💔 번아웃 💔\n      😰\n    ┌─────┐\n    │ 💊  │\n    │ 🏥  │\n    └─────┘\n  건강 최우선",
        "ending_type": "bad",
        "forced": True
    },

    "ending_reputation_collapse": {
        "title": "📉 평판 추락으로 경질",
        "description": """본부에서 긴급 소환 명령이 떨어졌습니다.

**상황:**
- 평판: 회복 불가능한 수준
- 현지 정부: 신뢰 상실
- 본부: 실망과 분노
- 언론: 부정적 보도

본부 회의실. 이사장이 차갑게 말합니다. "소장님, 더 이상 현장에 계실 수 없습니다. 즉시 귀국하십시오."

현지 언론이 대서특필했습니다. "KOICA 소장 경질, 외교적 참사"

당신이 쌓아온 모든 것이 무너졌습니다. 프로젝트는 중단되었고, 직원들은 뿔뿔이 흩어졌으며, 파트너들은 등을 돌렸습니다.

귀국 후, 당신은 본부 한 구석의 자료실로 발령받았습니다. 아무도 당신과 이야기하려 하지 않습니다.

**1년 후, 당신은 조용히 사직서를 제출했습니다.**

무엇이 잘못되었을까요? 돌이켜보면, 중요한 순간마다 잘못된 선택을 했습니다. 평판은 한번 무너지면 회복하기 어렵다는 것을 배웠지만, 이미 늦었습니다.""",
        "ascii_art": "📉 평판 추락 📉\n      😔\n    ┌─────┐\n    │ ❌  │\n    │ 📰  │\n    └─────┘\n  신뢰의 중요성",
        "ending_type": "bad",
        "forced": True
    },

    "ending_ethical_crisis": {
        "title": "⚖️ 윤리 위반으로 징계",
        "description": """본부 감사팀이 당신을 소환했습니다.

**감사 결과:**
- 다수의 윤리 위반 사례 발견
- 부적절한 의사결정 패턴
- 부패 방조 혐의

"소장님, 여러 차례 부적절한 결정을 내렸습니다. 특히 부패 사례를 제대로 처리하지 않은 것은 심각한 문제입니다."

감사관이 차갑게 말합니다. "KOICA의 핵심 가치는 투명성과 책임성입니다. 소장님의 행동은 이에 정면으로 위배됩니다."

**징계 결과: 직위 해제 및 3개월 정직**

현지 파트너들은 "그래도 우리를 이해해준 유일한 사람이었다"며 아쉬워했지만, 본부의 결정은 확고했습니다.

정직 기간 동안, 당신은 많은 생각을 했습니다. '현지 관행'과 '원칙' 사이에서 타협했던 순간들이 주마등처럼 스쳐 지나갔습니다.

**6개월 후, 당신은 조용히 사표를 제출했습니다.**

"원칙은 불편하지만, 지키지 않으면 모든 것을 잃는다"는 교훈을 얻었지만, 대가가 너무 컸습니다.""",
        "ascii_art": "⚖️ 윤리 위반 ⚖️\n      😞\n    ┌─────┐\n    │ ⚠️  │\n    │ 📋  │\n    └─────┘\n  원칙의 중요성",
        "ending_type": "bad",
        "forced": True
    }
}


# ============================================================
# 3. 장기 영향(delayed effects)을 가진 시나리오 수정
# ============================================================

def add_delayed_effects(scenarios):
    """기존 시나리오에 장기 영향 추가"""

    # period_5 NGO 네트워크 구축 선택지에 장기 효과 추가
    if 'period_5' in scenarios:
        # NGO 네트워크 구축 선택지 (인덱스 2)
        scenarios['period_5']['choices'][2]['result']['delayed_effects'] = [
            {
                "trigger_period": 10,  # 2년차 4-5월
                "condition": "project_success >= 50",
                "message": "🌟 9개월 전 구축한 NGO 네트워크가 빛을 발합니다! 5개 NGO가 공동으로 새로운 사업을 제안했고, 현지 정부도 적극 지지하고 있습니다. '장기 투자'가 결실을 맺는 순간입니다.",
                "stats": {
                    "reputation": 12,
                    "project_success": 10,
                    "budget": 15
                },
                "effect_id": "ngo_network_payoff"
            }
        ]

    # period_2 PMC 자율성 부여 선택지에 리스크 추가
    if 'period_2' in scenarios:
        # PMC 전문성 신뢰 선택지 (인덱스 0)
        scenarios['period_2']['choices'][0]['result']['delayed_effects'] = [
            {
                "trigger_period": 6,  # 1년차 11-12월
                "condition": "random < 0.3",  # 30% 확률
                "message": "⚠️ PMC가 사무소와 충분한 협의 없이 사업 방향을 일부 변경했습니다. 전문성은 높지만, 초기에 부여한 '과도한 자율성'이 통제력 상실로 이어진 것입니다. 현지 정부가 혼란스러워하고 있습니다.",
                "stats": {
                    "reputation": -8,
                    "project_success": -6,
                    "stress": 12
                },
                "effect_id": "pmc_autonomy_risk"
            }
        ]

    # period_8 내부 시스템 개선의 장기 효과
    if 'period_8' in scenarios:
        # 제3자 감사 + 시스템 개선 선택지 (인덱스 3)
        if len(scenarios['period_8']['choices']) > 3:
            scenarios['period_8']['choices'][3]['result']['delayed_effects'] = [
                {
                    "trigger_period": 11,  # 2년차 9-10월
                    "condition": "always",
                    "message": "✅ 1년 전 구축한 내부 통제 시스템이 완벽하게 작동하고 있습니다. 모든 사업이 투명하게 진행되고, 본부 감사에서도 '모범 사례'로 선정되었습니다. 초기 투자가 장기적으로 큰 자산이 되었습니다.",
                    "stats": {
                        "reputation": 15,
                        "project_success": 8,
                        "staff_morale": 10
                    },
                    "effect_id": "internal_control_success"
                }
            ]

    # period_9 안전 위기 - 철수 선택의 장기 영향
    if 'period_9' in scenarios:
        # 즉각 전원 철수 선택지 (인덱스 0)
        scenarios['period_9']['choices'][0]['result']['delayed_effects'] = [
            {
                "trigger_period": 11,  # 2년차 9-10월
                "condition": "reputation < 50",
                "message": "💔 과거 '과잉 철수' 사건의 후유증이 계속됩니다. 현지 파트너들이 \"또 위기가 오면 도망갈 사람들\"이라며 협력을 꺼리고 있습니다. 한번 잃은 신뢰는 쉽게 회복되지 않습니다.",
                "stats": {
                    "reputation": -10,
                    "project_success": -8
                },
                "effect_id": "evacuation_stigma"
            }
        ]

    return scenarios


def add_deputy_events_to_scenarios(scenarios):
    """부소장 임계값 이벤트를 scenarios에 추가"""
    scenarios.update(DEPUTY_THRESHOLD_EVENTS)
    return scenarios


def add_new_endings_to_scenarios(scenarios):
    """새로운 엔딩을 scenarios에 추가"""
    scenarios.update(NEW_ENDINGS)
    return scenarios


def main():
    print("=" * 60)
    print("KOICA 시뮬레이션 고급 기능 구현 시작")
    print("=" * 60)

    # 백업 생성
    print("\n📁 기존 파일 백업 중...")
    import shutil
    shutil.copy2('scenarios.json', 'scenarios.json.before_advanced')
    print("   ✅ 백업 완료: scenarios.json.before_advanced")

    # 파일 로드
    print("\n📖 scenarios.json 로드 중...")
    scenarios = load_scenarios()
    print("   ✅ 로드 완료")

    # 고급 기능 추가
    print("\n🔧 고급 기능 구현 중...")

    print("🌟 1. 부소장 임계값 이벤트 추가 중...")
    scenarios = add_deputy_events_to_scenarios(scenarios)
    print(f"   ✅ {len(DEPUTY_THRESHOLD_EVENTS)}개 이벤트 추가 완료")

    print("📊 2. 장기 영향 시스템 추가 중...")
    scenarios = add_delayed_effects(scenarios)
    print("   ✅ delayed_effects 추가 완료")

    print("🏆 3. 새로운 엔딩 조건 추가 중...")
    scenarios = add_new_endings_to_scenarios(scenarios)
    print(f"   ✅ {len(NEW_ENDINGS)}개 엔딩 추가 완료")

    # 파일 저장
    print("\n💾 scenarios.json 저장 중...")
    save_scenarios(scenarios)
    print("   ✅ 저장 완료")

    print("\n" + "=" * 60)
    print("✅ 모든 고급 기능 구현 완료!")
    print("=" * 60)
    print("\n추가된 기능:")
    print("  🌟 부소장 임계값 이벤트:")
    print("     - 김원칙 부소장 고충성도 이벤트")
    print("     - 김원칙 부소장 전보 위기 이벤트")
    print("     - 박현지 부소장 네트워크 보너스 이벤트")
    print("     - 박현지 부소장 문화 갈등 이벤트")
    print("\n  📊 장기 영향 시스템:")
    print("     - period_5: NGO 네트워크의 장기 효과")
    print("     - period_2: PMC 자율성의 리스크")
    print("     - period_8: 시스템 개선의 장기 효과")
    print("     - period_9: 철수 결정의 낙인 효과")
    print("\n  🏆 새로운 엔딩:")
    print("     - ending_perfect_balance: 완벽한 균형의 리더")
    print("     - ending_burnout: 번아웃으로 조기 귀국")
    print("     - ending_reputation_collapse: 평판 추락 경질")
    print("     - ending_ethical_crisis: 윤리 위반 징계")

if __name__ == '__main__':
    main()

# Comprehensive Stat Issues Analysis - Summary

## Overview
Total issues found: **127 instances** across 7 categories

## Issue Breakdown by Category

### 1. Budget Errors (48 instances)
**Pattern**: Budget increases appear where no financial transaction occurs, or financial costs are represented as budget increases.

**Most Common Mistakes**:
- **Conferences/Events generating budget** instead of costing money (10 instances)
  - period_5 choice 0: Large conference gives +8 budget (should be -15)
  - period_11 choice 0: Farewell conference gives +8 budget (should be -20)
  - International travel gives budget instead of costing it

- **Administrative actions generating budget** (15 instances)
  - Report writing, internal meetings, evaluations giving budget
  - PMC management decisions (autonomy, monitoring, pressure) affecting budget

- **Career/personal decisions affecting budget** (3 instances)
  - Returning to HQ, leaving KOICA affecting office budget

**Critical Examples**:
- `period_5 choice 0`: 200-person conference costs 20M won but gives +8 budget
- `narrative_event_international_award choice 0`: Paris trip gives +10 budget (should be -30)
- `period_2 choice 0`: Granting PMC autonomy gives -18 budget (makes no sense)

---

### 2. Stress Direction Errors (8 instances)
**Pattern**: Major crises reduce stress or have no stress tracking at all.

**Critical Issues**:
- **period_9 (Security Crisis)**: All 3 choices completely MISSING stress stats
  - Armed conflict, evacuation decisions - no stress tracked!

- **narrative_event_volunteer_safety choice 0**: Medical emergency gives stress -12
  - Emergency evacuation REDUCES stress? Should increase to +12

**Missing Stress in Overwork**:
- period_3 choice 2: All-in on reports (no stress)
- period_5 choice 0: Major conference prep (no stress)
- period_10 choice 0: All-out push to 92% KPI (no stress)
- period_11 choice 0: Large farewell event (no stress)

---

### 3. Principled/Local_Friendly Over-Conflicts (10 instances)
**Pattern**: Actions that benefit both principles AND local relationships show artificial conflict.

**Key Examples**:
- **period_3 choice 0**: Caring for volunteer welfare
  - Current: principled -3, local_friendly 8
  - Should: principled 8, local_friendly 8
  - Reason: Staff welfare is a core ethical principle!

- **period_10 choice 1**: Sustainability planning
  - Current: principled 8, local_friendly 2
  - Should: principled 8, local_friendly 7
  - Reason: Sustainability benefits local partners directly

- **narrative_event_partner_growth choice 1**: Promoting capable local partner
  - Current: principled 2, local_friendly 8
  - Should: principled 7, local_friendly 8
  - Reason: Merit-based advancement is both ethical AND builds relationships

**Common Pattern**: Collaboration, capacity building, and partnership actions treated as "unprincipled" when they're actually core development principles.

---

### 4. Project Success Overvaluation (4 instances)
**Pattern**: Networking/conferences/presentations get same or higher project_success as actual work.

**Comparisons**:
1. **period_5**:
   - Choice 0 (PR conference): project_success 8
   - Choice 1 (Volunteer farewell): project_success 3
   - Should be reversed - farewell is internal, but conference shouldn't equal actual work

2. **period_11**:
   - Choice 0 (Farewell conference): project_success 8
   - Choice 1 (Documentation handover): project_success 6
   - Conference > handover? Backwards priority

3. **narrative_event_unexpected_impact**:
   - Choice 0 (UN presentation): project_success 10
   - Choice 2 (Joint expansion plan): project_success 13
   - Presentation almost equals actual expansion planning

**Pattern**: Talking about work valued nearly as high as doing work.

---

### 5. Missing Wellbeing (7 instances)
**Pattern**: Overwork scenarios with major staff_morale drops but no wellbeing tracking.

**All instances involve high-intensity work**:
- period_2 choice 1: Weekly meetings + monthly monitoring (staff_morale -12)
- period_3 choice 2: All-in report writing (staff_morale -12)
- period_10 choice 0: Push to 92% KPI (staff_morale -12, text says "exhausted")
- period_11 choice 0: 200-person conference (staff_morale -6)

**Pattern**: When staff_morale drops 10+, wellbeing should also drop 10-20.

---

### 6. Reputation for Internal Actions (5 instances)
**Pattern**: Private internal management decisions affecting external reputation.

**Examples**:
- deputy_event_low_morale choice 0: 1:1 meeting gives reputation +3
- deputy_event_conflict choice 0: Internal mediation gives reputation +3
- year1_event_adaptation choice 0: Internal pacing decision gives reputation +6
- deputy_principled_low_resignation choice 0: Private retention talk gives reputation +3
- deputy_local_friendly_transparency_concern choice 0: Internal document review gives reputation +10

**Issue**: External stakeholders don't know about internal conversations.

---

### 7. Budget Adjustment Paradoxes (2 instances)
**Pattern**: Requesting budget increases immediately grants budget without delay/cost.

**Examples**:
1. **period_4 choice 0**: Request additional budget → immediately get +8 budget
   - Should: First pay cost of delay/negotiation (-6), then get budget via delayed_effect

2. **narrative_event_china_proposal choice 2**: Request budget increase → +8 budget
   - Should: +3 budget (partial approval) or delayed_effect

**Pattern**: In reality, budget requests take time, negotiation, and have opportunity costs.

---

## Recommendations by Priority

### HIGH PRIORITY (Fix Immediately)
1. **period_9 security crisis**: Add stress stats to all 3 choices (currently missing entirely)
2. **Budget for conferences/events**: Flip signs on all major events (they cost money!)
3. **narrative_event_volunteer_safety**: Fix stress direction (emergency should increase stress)
4. **Principled/local conflicts**: Fix 10 cases where both should increase

### MEDIUM PRIORITY
5. **Project success overvaluation**: Reduce conference/presentation values by 50%
6. **Missing wellbeing**: Add wellbeing stats to 7 overwork scenarios
7. **Budget adjustment paradoxes**: Add delay/cost to budget requests

### LOW PRIORITY
8. **Reputation for internal actions**: Remove reputation from 5 internal-only scenarios
9. **Administrative budget errors**: Remove budget from reports, meetings, evaluations

---

## Statistics
- Total scenarios analyzed: 60+
- Total choices analyzed: 180+
- Issues per scenario (average): 2.1
- Most problematic scenario: period_5 (4 different issue types)
- Cleanest scenarios: Life events (health, homesickness, housing)

---

## Next Steps
1. Review `/home/user/odagame/stat_issues_comprehensive.json` for detailed fixes
2. Apply fixes systematically by category
3. Test game balance after each category of fixes
4. Consider adding validation rules to prevent future similar issues

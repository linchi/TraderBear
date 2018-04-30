
_PRICE_VAR_THRESHOLD = 0.02
_PRICE_WEEKLY_DRIFT_THRESHOLD = 0.01
_MAX_NUM_WEEKS_TO_TRAVERSE = 10

def ComputeTightness(nodes):
    qualified_weeks = []
    for i in range(_MAX_NUM_WEEKS_TO_TRAVERSE):
        tightness_score = ((nodes[i].high - nodes[i].low)/nodes[i].close,
                           (nodes[i+1].close - nodes[i].close)/nodes[i].close)
        if tightness_score[0] > _PRICE_VAR_THRESHOLD:
            break
        qualified_weeks.append(tightness_score)
        if tightness_score[1] > _PRICE_WEEKLY_DRIFT_THRESHOLD:
            break
    return qualified_weeks
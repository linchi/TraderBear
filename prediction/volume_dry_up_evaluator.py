
_QUALIFY_THRESHOLD = 0.6
_MAX_NUM_WEEKS_TO_TRAVERSE = 10
_NUM_FULL_WEEKS_FOR_AVG = 7

def _ComputeAvgWeeklyVolume(nodes, ind, num_weeks):
    if ind+num_weeks >= len(nodes):
        raise ValueError('Out of range when compute average weekly volume ! ind - %d, num_weeks - %d',
                         'length of nodes list - %d', ind, num_weeks, len(nodes))
    total_volume = 0
    for i in range(num_weeks):
        total_volume += nodes[ind+i].volume
    return total_volume/num_weeks

def ComputeVolumeDryUpScore(nodes):
    qualified_weeks = []
    for i in range(_MAX_NUM_WEEKS_TO_TRAVERSE):
        weekly_avg = _ComputeAvgWeeklyVolume(nodes, i, _NUM_FULL_WEEKS_FOR_AVG)
        if nodes[i].volume/weekly_avg < _QUALIFY_THRESHOLD:
            qualified_weeks.append((weekly_avg-nodes[i].volume)/weekly_avg)
        else:
            break
    return qualified_weeks
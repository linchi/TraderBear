import collections
import datetime
import time
import stock_data_store

def GenerateWeeklyData(nodes, num_weeks):
    result = []
    # remove the tailing week days if the latest day is smaller than Fri.
    latest_ts = nodes[-1].timestamp
    latest_weekday = datetime.datetime.utcfromtimestamp(latest_ts).weekday() + 1
    if latest_weekday < 5:
        nodes = nodes[:-latest_weekday]
    weekly_groups = collections.defaultdict(list)
    for node in reversed(nodes):
        day_begin_ts = datetime.datetime.utcfromtimestamp(node.timestamp).replace(
            hour=0, minute=0, second=0, microsecond=0)
        week_begin_ts = long(time.mktime((day_begin_ts - datetime.timedelta(days=day_begin_ts.weekday())).timetuple()))
        weekly_groups[week_begin_ts].append(node)
        if len(weekly_groups) > num_weeks:
            break
    for week_ts, week_nodes in weekly_groups.items():
        high = 0
        low = 1e10
        open = 0
        close = 0
        volume = 0
        for node in week_nodes:
            high = max(high, node.high)
            low = min(low, node.low)
            open += node.open
            close += node.close
            volume += node.volume
        open /= len(week_nodes)
        close /= len(week_nodes)
        week_node = stock_data_store.StockDataNode(week_ts, open, high, low, close, volume)
        result.append(week_node)
    result.sort(key=lambda node: node.timestamp, reverse=True)
    result = result[:-1]
    return result
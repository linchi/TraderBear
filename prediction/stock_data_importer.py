import csv
import datetime
import glob
import os
import re
import time
import stock_data_store
import weekly_data_generator
import volume_dry_up_evaluator
import tightness_evaluator

_MAX_FILES_TO_ANALYZE = 100

def ReadStockDataFromFile(filename):
    result = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            result.append(stock_data_store.StockDataNode(
                timestamp=long(time.mktime(datetime.datetime.strptime(row[0], '%Y%m%d').timetuple())),
                open=float(row[2]),
                high=float(row[3]),
                low=float(row[4]),
                close=float(row[5]),
                volume=float(row[6])
            ))
    return result


def ReadStockData(base_dir):
    result = stock_data_store.StockDataStore()
    paths = glob.glob(os.path.join(base_dir, '*.csv'))
    counter = 0
    for path in paths:
        m = re.match(r'table_(.+).csv', os.path.basename(path))
        company_code = m.group(1)
        nodes = ReadStockDataFromFile(path)
        result.data[company_code] = nodes
        print(path)
        counter += 1
        if counter >= _MAX_FILES_TO_ANALYZE:
            break;
    return result


def main():
    data_store = ReadStockData('C:/Users/Alan/Downloads/quantquote_daily_sp500_83986/daily')
    for company_code, nodes in data_store.data.items():
        week_nodes = weekly_data_generator.GenerateWeeklyData(nodes, 20)
        volume_score_list = volume_dry_up_evaluator.ComputeVolumeDryUpScore(week_nodes)
        tightness_score_list = tightness_evaluator.ComputeTightness(week_nodes)
        print('Volume score list for company %s: ', company_code)
        print(volume_score_list)
        print('Tightness score list for company %s: ', company_code)
        print(tightness_score_list)

if __name__ == "__main__":
    main()
import sys
import datetime
from travle_log import *
from PyQt5.QtCore import pyqtSignal, QObject

init_time = datetime.datetime(2020, 5, 7, 0)
send_route_to_gui_signal = pyqtSignal(dict)

# 获取最佳路径
def get_best_route(mission_dict, traveller_list, city_graph):
    mission = mission_dict

    traveller = traveller_list[mission['traveller_id']]
    traveller['departure'] = mission['departure']
    traveller['destination'] = mission['destination']
    traveller['start_time'] = mission['start_time']
    traveller['arrived'] = 0
    traveller['route_index'] = 0

    if mission['plan'] == 0:
        mission["time_limit"] = sys.maxsize
        print("执行最小风险算法，出发地：{}，目的地：{}，出发时间：{}".format(traveller['departure'], traveller['destination'],
                                                      init_time + datetime.timedelta(hours=mission['start_time'])))

    else:
        print("执行限时最小风险算法,出发地：{}，目的地：{}，出发时间：{}，限制时间：{}小时".format(traveller['departure'], traveller['destination'],
                                                                  init_time + datetime.timedelta(
                                                                      hours=mission['start_time']),
                                                                  mission["time_limit"]))
    time_limit = mission["time_limit"]

    (traveller['route'], traveller['risk'], traveller['time']) = minimize_risk_algorithm(traveller['start_time'],
                                                                                         traveller['departure'],
                                                                                         traveller['destination'],
                                                                                         city_graph, time_limit)
    # 单纯在控制台输出旅行方案
    print_travel_route(traveller)

# DFS获取最佳路径
def minimize_risk_algorithm(start_time, dep, dest, city_graph, time_limit):
    # 每天的航班表是一样的，因此只用知道是几点钟即可
    # 但是注意跨了一天的现象
    depart_time = start_time % 24
    route = []
    cur_dep = dep
    cur_dest = dest
    # 记录去过的城市，一个方案不会经过一个城市两次
    arrived_city = set()
    min_risk = sys.maxsize
    min_risk_route = []
    min_risk_time = 0

    def minimize_risk_dfs(depart_time, dep, final_dest, city_graph, time_limit, total_time, total_risk, route,
                          arrived_city):
        nonlocal min_risk, min_risk_route, min_risk_time

        trans_weight = {'飞机': 9, '火车': 5, '汽车': 2}
        # 修枝，加快运行速度
        if total_risk > min_risk:
            return
        # 限时模式修枝
        if total_time > time_limit:
            return

        # 到达终点
        if dep == final_dest:
            if total_risk < min_risk:
                min_risk = total_risk
                min_risk_route = route.copy()
                min_risk_time = total_time
            return

        # 深度搜索每一个没去过的城市
        trans_list = city_graph[dep]["transportation"]
        for trans in trans_list:
            if trans['destination'] not in arrived_city:
                # 在到达城市的同一天出发
                # 等待时间不会超过24h，不然永远无法到达
                if trans['depart_time'] >= depart_time:
                    arrived_city.add(trans['destination'])
                    # 隔日抵达？
                    if trans['arrive_time'] > trans['depart_time']:
                        trans_time = trans['arrive_time'] - trans['depart_time']
                    else:
                        trans_time = trans['arrive_time'] + 24 - trans['depart_time']
                    wait_time = trans['depart_time'] - depart_time
                    risk = wait_time * city_graph[dep]['weight'] + trans_time * city_graph[dep]['weight'] * \
                           trans_weight[trans['way']]
                    trans['time_interval'] = wait_time + total_time
                    trans['trans_time'] = trans_time
                    route.append(trans.copy())
                    minimize_risk_dfs(trans['arrive_time'], trans['destination'], dest, city_graph, time_limit,
                                      (total_time + trans_time + wait_time), total_risk + risk, route,
                                      arrived_city)
                    route.pop()
                    arrived_city.remove(trans['destination'])
                # 等到第二天再出发
                else:
                    arrived_city.add(trans['destination'])
                    if trans['arrive_time'] > trans['depart_time']:
                        trans_time = trans['arrive_time'] - trans['depart_time']
                    else:
                        trans_time = trans['arrive_time'] + 24 - trans['depart_time']
                    wait_time = trans['depart_time'] + 24 - depart_time
                    risk = wait_time * city_graph[dep]['weight'] + trans_time * city_graph[dep]['weight'] * \
                           trans_weight[trans['way']]
                    trans['time_interval'] = wait_time + total_time
                    trans['trans_time'] = trans_time
                    route.append(trans.copy())

                    minimize_risk_dfs(trans['arrive_time'], trans['destination'], dest, city_graph, time_limit,
                                      (total_time + trans_time + wait_time), total_risk + risk, route,
                                      arrived_city)
                    route.pop()
                    arrived_city.remove(trans['destination'])

    minimize_risk_dfs(depart_time, dep, dest, city_graph, time_limit, 0, 0, route, arrived_city)
    return (min_risk_route, min_risk, min_risk_time)

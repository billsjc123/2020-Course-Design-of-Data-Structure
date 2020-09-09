import datetime

init_time = datetime.datetime(2020, 5, 7, 0)


def print_travel_log(file,traveller_list,present_time):
    print("当前时间为：{}".format(init_time + datetime.timedelta(hours=present_time)))
    if len(traveller_list) == 0:
        print("当前无旅客")
        return
    for travller in traveller_list:
        # print(travller)
        route_index = travller['route_index']
        present_route = travller['route'][route_index]

        if travller['arrived'] == 1:
            # print("旅客{}已到达目的地，等待下一条指令".format(travller['id']))
            file.write("旅客{}已到达目的地，等待下一条指令\n".format(travller['id']))
            continue
        dep_time = present_route['depart_time']
        arr_time = present_route['arrive_time']
        # 判断乘客在等待还是正在车上
        if ((present_time % 24 > dep_time or present_time % 24 < arr_time) and dep_time > arr_time) or (
                present_time % 24 > dep_time and present_time < arr_time):
            print(
                "旅客{}目前正在{}前往{}的{}次{}上".format(travller['id'], present_route['departure'], present_route['destination'],
                                               present_route['id'], present_route['way']))
        elif present_time % 24 == present_route['arrive_time']:
            print("旅客{}抵达{}".format(travller['id'], present_route['destination']))
            if (travller['route_index'] == len(travller['route']) - 1):
                travller['arrived'] = 1
            else:
                travller['route_index'] = route_index + 1
        else:
            print("旅客{}在{}等待{}次{}".format(travller['id'], present_route['departure'],
                                          present_route['id'], present_route['way']))


def print_traveller_state(travller_list, present_time):
    print("当前时间为：{}".format(init_time + datetime.timedelta(hours=present_time)))
    if len(travller_list) == 0:
        print("当前无旅客")
        return
    for travller in travller_list:
        # print(travller)
        route_index = travller['route_index']
        present_route = travller['route'][route_index]

        if travller['arrived'] == 1:
            print("旅客{}已到达目的地，等待下一条指令".format(travller['id']))
            continue
        dep_time = present_route['depart_time']
        arr_time = present_route['arrive_time']
        # 判断乘客在等待还是正在车上
        if ((present_time % 24 > dep_time or present_time%24 < arr_time)and dep_time>arr_time) or (present_time % 24 > dep_time and present_time < arr_time):
            print(
                "旅客{}目前正在{}前往{}的{}次{}上".format(travller['id'], present_route['departure'], present_route['destination'],
                                               present_route['id'], present_route['way']))
        elif present_time % 24 == present_route['arrive_time']:
            print("旅客{}抵达{}".format(travller['id'], present_route['destination']))
            if (travller['route_index'] == len(travller['route']) - 1):
                travller['arrived'] = 1
            else:
                travller['route_index']=route_index+1
        else:
            print("旅客{}在{}等待{}次{}".format(travller['id'], present_route['departure'],
                                          present_route['id'], present_route['way']))


def print_travel_route(traveller):
    if len(traveller['route']) == 0:
        print("旅客{}无法到达目的地，请修改时限！！".format(traveller['id']))
        return
    print("旅客{}的路线已规划完毕！".format(traveller['id']))
    print("感染风险：{}".format(traveller['risk']))
    print("旅途耗时：{}".format(traveller['time']))
    for trans in traveller['route']:
        dep = trans['departure']
        dest = trans['destination']
        id = trans['id']
        way = trans['way']
        dep_time = init_time + datetime.timedelta(hours=(traveller['start_time'] + trans['time_interval']))
        print("{},旅客{}由{}乘坐{}号{}前往{}".format(dep_time, traveller['id'], dep, id, way, dest))


import datetime


# 通过Time.txt得到城市的邻接表
def get_city_graph():
    f = open("Time.txt", "r+", encoding='utf-8')
    line = f.readline()
    city_name = ['北京', '上海', '广州', '哈尔滨', '沈阳', '天津', '兰州', '成都', '贵阳', '武汉', '海口', '乌鲁木齐']
    city_weight = [0.9, 0.9, 0.9, 0.5, 0.2, 0.5, 0.2, 0.9, 0.5, 0.5, 0.2, 0.2]
    way = ['飞机', '火车', '汽车']
    graph = {'北京': {"transportation": [], "id": 0}, '上海': {"transportation": [], "id": 1},
             '广州': {"transportation": [], "id": 2},
             '哈尔滨': {"transportation": [], "id": 3},
             '沈阳': {"transportation": [], "id": 4}, '天津': {"transportation": [], "id": 5},
             '兰州': {"transportation": [], "id": 6},
             '成都': {"transportation": [], "id": 7},
             '贵阳': {"transportation": [], "id": 8}, '武汉': {"transportation": [], "id": 9},
             '海口': {"transportation": [], "id": 10},
             '乌鲁木齐': {"transportation": [], "id": 11}}
    while (line):

        str_list = line.strip("\n").split(" ")
        if (len(str_list) == 7):
            vertex = {"departure": city_name[int(str_list[0])], "destination": city_name[int(str_list[1])],
                      "way": way[int(str_list[2])],
                      "id": str_list[3], "depart_time": int(str_list[5]), "arrive_time": int(str_list[6])}
            weight = city_weight[int(str_list[0])]
            graph[city_name[int(str_list[0])]]["transportation"].append(vertex)
            graph[city_name[int(str_list[0])]]["weight"] = weight
        line = f.readline()
    f.close()
    #print("graph:",graph)
    return graph


# 通过Time.txt得到交通工具时刻表
def get_schedule():
    f = open("Time.txt", "r+", encoding='utf-8')
    line = f.readline()
    city_name = ['北京', '上海', '广州', '哈尔滨', '沈阳', '天津', '兰州', '成都', '贵阳', '武汉', '海口', '乌鲁木齐']
    way = ['飞机', '火车', '汽车']
    schedule = []
    while (line):
        str_list = line.strip("\n").split(" ")
        vertex = {"出发地": city_name[int(str_list[0])], "目的地": city_name[int(str_list[1])], "交通工具": way[int(str_list[2])],
                  "班次": str_list[3], "出发时间": int(str_list[5]), "到达时间": int(str_list[6])}
        schedule.append(vertex)
        line = f.readline()
    f.close()
    #print("schedule:", schedule)
    return schedule

# get_city_graph()
# get_schedule()

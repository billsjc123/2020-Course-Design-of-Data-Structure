from pyecharts import GeoLines, Style, Page, Map, Geo

##### 生成航线网页
# 函数功能：产生一个从start_city到dest_city的航线
# 需传入参数为：起始城市，到达城市，交通工具
def generate_travel_state_page(travel_line_list):
    # on_route 0代表在城市等待，1代表在路上，2代表到达
    style = Style(width=800, height=600, background_color="#404a59")
    geolines = GeoLines("", **style.init_style)
    geolines.add('', [])
    for traveller in travel_line_list.keys():
        # 在路上
        if travel_line_list[traveller] == {}:
            continue
        departure = travel_line_list[traveller]['departure']
        destination = travel_line_list[traveller]["destination"]
        if travel_line_list[traveller]['on_route'] == 1:
            vehicle = travel_line_list[traveller]['way']
            # 飞机是飞机，火车是菱形，汽车是圆形
            if vehicle == '飞机':
                v = 'plane'
            elif vehicle == '火车':
                v = 'diamond'
            elif vehicle == '汽车':
                v = 'circle'
            geolines.add(traveller, [[departure, destination]],
                         is_legend_show=True, legend_text_color="#eee",line_curve=0.2,
                         geo_effect_symbol=v, geo_effect_symbolsize=20)
        # 在等待
        elif travel_line_list[traveller]['on_route'] == 0:
            geolines.add(traveller, [[departure, departure]],
                         is_legend_show=True, legend_text_color="#eee")
        # 到达目的地
        elif travel_line_list[traveller]['on_route'] == 2:
            geolines.add(traveller, [[destination,destination]],
                         is_legend_show=True, legend_text_color="#eee")
    geolines.render('当前旅行状态查询页.html')

##### 生成抵达城市网页
# 函数功能：产生一个所在城市的发散动态点标识
# 需传入参数为：城市
def point_generate_travel_state_page(city_list):
    id = [0, 1, 2, 3, 4, 5]
    color = ["#ffffff", "#ff7500", "#fff143", "#21a675", "#8d4bbb", "#44cef6"]
    for i in id:
        city = city_list["旅客"+str(i)]
        geo = Geo(width=800, height=600, background_color="#404a59")
        if city == '': # 城市如果是空串，则生成无城市的图
            continue
        else: # 否则生成对应城市的发散动态点标识图
            geo.add("旅客"+str(i), [city], value=[5], type="effectScatter", effect_scale=5,
                    visual_text_color="#fff", symbol_size=10, is_roam=True)
        geo.render(path="当前旅行状态查询页.html")

# 测试函数，忽略
if __name__ == '__main__':
    travel_line_list = {"旅客1": {"destination":"北京","departure":"武汉","way":"飞机","on_route":0},
                        "旅客2": {"destination":"乌鲁木齐","departure":"海口","way":"火车","on_route":1},
                        "旅客3": {"destination":"武汉","departure":"广州","way":"飞机","on_route":1},
                        "旅客4": {"destination":"贵阳","departure":"上海","way":"飞机","on_route":2},
                        "旅客0": {"destination":"上海","departure":"广州","way":"飞机","on_route":1},
                        "旅客5": {"destination":"乌鲁木齐","departure":"沈阳","way":"飞机","on_route":1}}
    generate_travel_state_page(travel_line_list)
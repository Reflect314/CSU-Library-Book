import requests
import json
import csv
from datetime import datetime

from config import BASE_URL
from config import HEADERS

def fetch_areas(area_id):
    """
    随便一个area_id就可以获取所有座位区域
    :param area_id:
    """
    url = f"{BASE_URL}/api.php/v3areas/{area_id}"

    headers = HEADERS
    headers["referer"] = f"{BASE_URL}/home/web/seat/area/{area_id}"

    resp = requests.get(url, headers=HEADERS, timeout=10)
    try:
        resp.raise_for_status()
        # print("请求成功")
        data = resp.json()
        seatinfos = data.get('data', {}).get('list', {}).get('seatinfo', [])

        # # 打开 CSV 文件，使用追加模式
        # with open("areas.csv", "w", newline='', encoding="utf-8") as f:
        #     writer = csv.writer(f)
        #     # 检查文件是否为空，如果为空则写入表头
        #     f.seek(0, 2)  # 移动到文件末尾
        #     if f.tell() == 0:  # 文件为空
        #         writer.writerow(['id', 'name'])
        #     # 写入数据
        #     for seatinfo in seatinfos:
        #         writer.writerow([
        #             seatinfo.get('id', ''),
        #             seatinfo.get('name', ''),
        #         ])
        return [seat.get('id') for seat in seatinfos],[seat.get('name') for seat in seatinfos]
    except requests.exceptions.HTTPError as e:
        print("请求失败:", e)
        return 0,0

def fetch_seat_list(area_id, areaday_id, today, start_time, end_time):
    """
    获取所有座位信息
    http://libzw.csu.edu.cn/api.php/spaces_old?area=44&segment=1715969&day=2026-04-24&startTime=10%3A29&endTime=22%3A00
    """
    url = f"{BASE_URL}/api.php/spaces_old"
    params = {
        "area": area_id,
        "segment": areaday_id,
        "day": today,
        "startTime": start_time,
        "endTime": end_time
    }
    resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
    try:
        resp.raise_for_status()
        print("请求成功")
    except requests.exceptions.HTTPError as e:
        print("请求失败:", e)
    return resp.json()


def save_seat_csv(data,area_name):
    # 提取 list 中的数据
    seat_list = data.get('data', {}).get('list', [])

    if not seat_list:
        print("没有找到座位数据")
        return

    # 打开 CSV 文件，使用追加模式
    with open("seats.csv", "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)

        # 检查文件是否为空，如果为空则写入表头
        f.seek(0, 2)  # 移动到文件末尾
        if f.tell() == 0:  # 文件为空
            writer.writerow(['id', 'name', 'area','area_name'])

        # 写入数据
        for seat in seat_list:
            writer.writerow([
                seat.get('id', ''),
                seat.get('name', ''),
                seat.get('area', ''),
                area_name
            ])

def get_areaday_ids(area,today):
    url = f"{BASE_URL}/api.php/v3areadays/{area}"
    # print(url)
    headers = HEADERS
    headers["referer"] = f"{BASE_URL}/web/seat2/area/{area}/day/{today}"
    resp = requests.get(url, headers=HEADERS, timeout=10)

    data = resp.json()
    # print(data)
    # 返回今天和明天的day和areaday_id
    # 提取所有的 day
    # days = [item["day"] for item in data["data"]["list"]]

    # 提取所有的 id
    areaday_ids = [item["id"] for item in data["data"]["list"]]

    return areaday_ids

def get_seats_csv(area_ids,area_names):
    """
    获取各区域座位信息并保存为 csv
    """
    for area_id,area_name in zip(area_ids,area_names):
        try:

            now = datetime.now()
            today= f"{now.year}-{now.month}-{now.day}"
            time_now = now.strftime('%H:%M')
            close_time = "22:00"

            try:
                areaday_ids = get_areaday_ids(area_id,today)
                today_areaday_ids = areaday_ids[0]

                seats = fetch_seat_list(area_id, today_areaday_ids, today, time_now, close_time)
                save_seat_csv(seats,area_name)
            except Exception as e:
                print(e)
                continue
        except requests.RequestException as e:
            print(f"[{area_id}] 网络错误: {e}")
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[{area_id}] 数据解析失败: {e}")
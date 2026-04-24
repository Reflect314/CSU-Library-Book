import re
import csv
from config import BASE_URL,HEADERS

# ========== 根据座位名称获取ID ==========
def get_book_info_from_csv(seat):
    """
    根据座位名称（如'XF2A001'）从CSV文件中查找对应的区域ID和座位ID
    CSV格式：id,name,area,area_name
    返回: (area_id, seat_id)
    """
    try:
        with open('seats.csv', 'r', encoding='utf-8') as file:
            # 使用DictReader自动处理表头
            reader = csv.DictReader(file)

            for row in reader:
                # 根据实际的列名调整，假设列名为 'name', 'id', 'area'
                if str(seat) == row.get('name'):
                    seat_id = int(row.get('id', 0))
                    area_id = int(row.get('area', 0))
                    return area_id, seat_id
        return None, None

    except FileNotFoundError:
        print("seats.csv 文件未找到")
        return None, None
    except Exception as e:
        print(f"读取CSV文件出错: {e}")
        return None, None


# ========== 座位预约 ==========
def reservation(seat_id, area_id,areaday_id,today,now, session):
    """
    预约座位
    """
    cookies = session.cookies.get_dict()
    # 构造请求头
    params = {
        "access_token": cookies["access_token"],
        "userid": cookies["userid"],
        "segment": areaday_id,
        "type": "1",
        "operateChannel": "2",
    }
    headers = HEADERS
    headers["referer"] = f"{BASE_URL}/web/seat3?area={area_id}&segment={areaday_id}&day={today}&startTime={now}endTime=22:00"

    book_API = f"{BASE_URL}/api.php/spaces/{seat_id}/book"
    book_resp = session.post(book_API, headers=headers, params=params, timeout=10)
    book_result = re.findall(r'"msg":"(.*?)"', book_resp.text, re.DOTALL)
    if book_result:
        msg = book_result[0].encode("utf-8").decode("unicode_escape")
        print(f'预约结果是：{msg}')
    else:
        print(f'预约结果解析失败，原始响应: {book_result.text}')
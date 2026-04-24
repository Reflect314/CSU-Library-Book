from datetime import datetime

from get_seats_data import get_areaday_ids
from library_seat_book import get_book_info_from_csv, reservation
from login_to_cas_center import login_to_cas_center

from config import USERNAME,PASSWORD,SEATS

# 用已认证的 session 访问图书馆
def access_library_with_auth(session):
    """
    使用已登录 CAS 的 session 访问图书馆系统
    教务系统会检测到 CASTGC Cookie，自动完成单点登录
    """
    LIBRARY_URL = "http://libzw.csu.edu.cn/cas/index.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    print("访问图书馆座位预约系统...")
    # 关键：用同一个 session，Cookie 会自动携带
    resp = session.get(LIBRARY_URL, headers=headers, allow_redirects=True)

    print(f"   📊 响应状态: {resp.status_code}")
    print(f"   🌐 最终 URL: {resp.url}")
    print(f"   🍪 当前 Cookie 数量: {len(session.cookies)}")

    response = session.get("http://libzw.csu.edu.cn/home/web/f_second")

    # 查看 session 中保存的所有 Cookie（包括之前请求积累的）
    # cookies = session.cookies.get_dict()
    # access_token = cookies["access_token"]
    # for cookie in session.cookies:
    #     print(f"{cookie.name}={cookie.value}, domain={cookie.domain}, path={cookie.path}")
    return session





# ============ 主流程 ============
if __name__ == "__main__":

    # 登录 CAS 认证中心（不带 service）
    session = login_to_cas_center(USERNAME, PASSWORD)

    # 用已认证的 session 访问图书馆系统
    session = access_library_with_auth(session)

    # 开始预约
    for seat in SEATS:
        area_id, seat_id = get_book_info_from_csv(seat)
        now = datetime.now()
        today = f"{now.year}-{now.month}-{now.day}"

        areaday_ids = get_areaday_ids(area_id, today)
        areaday_id = areaday_ids[0]  # 要今天的
        # print(areaday_id)
    
        reservation(seat_id,area_id, areaday_id, today, now, session)

    # 更新座位数据
    # area_ids,area_names = fetch_areas(1)
    # if area_ids:
    #     print(area_ids)
    #     print(area_names)
    #     get_seats_csv(area_ids,area_names)
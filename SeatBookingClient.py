import requests


class SeatBookingClient:
    def __init__(self, user_id,cookies):
        """
        :param user_id: 用户ID
        :param cookies: cookies
        """
        self.url = "http://libzw.csu.edu.cn/user/index/book"
        self.base_url = "http://libzw.csu.edu.cn"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "http://libzw.csu.edu.cn/home/web/f_second",
            "Host": "libzw.csu.edu.cn"
        }

        self.user_id = user_id
        self.cookies = cookies

        self.session = requests.Session()
        self.session.get(
            self.url,
            headers=self.headers,
            cookies=cookies,
            timeout=10
        )

    def _post(self, book_id, method):
        url = f"{self.base_url}/api.php/profile/books/{book_id}"

        data = {
            "_method": method,
            "id": book_id,
            "userid": self.user_id,
            "access_token": self.cookies["access_token"],
            "operateChannel": 2
        }

        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "referer": "http://libzw.csu.edu.cn/user/index/book",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
            "x-requested-with": "XMLHttpRequest"
        }

        resp = self.session.post(url, data=data, headers=headers)
        try:
            return resp.json()
        except:
            return resp.text

    # =============================
    # 1. 取消预约
    # =============================
    def cancel(self, book_id):
        return self._post(book_id, "delete")

    # =============================
    # 2. 签到（开始使用）
    # =============================
    def checkin(self, book_id):
        return self._post(book_id, "checkin")

    # =============================
    # 3. 临时离开
    # =============================
    def leave(self, book_id):
        return self._post(book_id, "leave")

    # =============================
    # 4. 完全离开（签离）
    # 有些系统需要走另一个接口
    # =============================
    def checkout(self, book_id):
        return self._post(book_id, "checkout")


# 下面几个参数均在网站中抓包 book 的文件获取：http://libzw.csu.edu.cn/user/index/book
PHPSESSID = "PHPSESSID"
userid = "学号"
access_token = "access_token"
book_id = "座位预约号"

# Cookie（从抓包内容提取）
cookies = {
    "PHPSESSID": PHPSESSID,
    "userid": userid,
    "access_token": access_token,
}

client = SeatBookingClient(
    user_id=userid,
    cookies = cookies
)

# # 取消预约（可用，但是这个没啥用）
# print(client.cancel(book_id))

# 签到（不可用，显示只能在局域网内使用）
# print(client.checkin(book_id))

# 临时离开（不可用，显示只能在局域网内使用）
# print(client.leave(book_id))

# 完全离开（不可用，显示只能在局域网内使用）
# print(client.checkout(book_id))
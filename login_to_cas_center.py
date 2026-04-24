import random
import base64
import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ========== AES 加密部分==========
AES_CHARS = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"


def random_string(n):
    return ''.join(random.choice(AES_CHARS) for _ in range(n))


def get_aes_string(plaintext, key, iv):
    key_bytes = key.strip().encode('utf-8') if isinstance(key, str) else key
    iv_bytes = iv.encode('utf-8') if isinstance(iv, str) else iv

    if len(key_bytes) not in (16, 24, 32):
        raise ValueError(f"AES密钥长度错误: {len(key_bytes)}")

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    encrypted_bytes = cipher.encrypt(pad(plaintext, AES.block_size))
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def encrypt_aes(password, random_str):
    prefix = random_string(64)
    iv_str = random_string(16)
    plaintext = (prefix + password).encode('utf-8')
    return get_aes_string(plaintext, random_str, iv_str)


def encrypt_password(password, random_str):
    try:
        return encrypt_aes(password, random_str)
    except Exception as e:
        print(f"加密失败: {e}")
        return None


# ========== 加密部分结束 ==========


# 登录 CAS 认证中心
def login_to_cas_center(username, password):
    """
    直接登录 CAS 认证中心，完成身份认证
    登录成功后，session 中会包含全局认证 Cookie（如 CASTGC）
    """
    session = requests.session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    CAS_URL = "https://ca.csu.edu.cn/authserver/login"

    print("访问 CAS 登录页...")
    # 直接访问登录页
    resp = session.get(CAS_URL, headers=headers)

    # 解析页面参数
    soup = BeautifulSoup(resp.text, 'html.parser')
    salt = soup.find('input', id='pwdEncryptSalt')
    execution = soup.find('input', id='execution')
    lt = soup.find('input', id='lt')

    if not salt or not execution:
        raise Exception("❌ 未找到关键表单字段，页面结构可能变化")

    salt_val = salt['value']
    exec_val = execution['value']
    lt_val = lt['value'] if lt else ''

    print(f"   ✓ salt: {salt_val}")
    print(f"   ✓ execution: {exec_val[:20]}...")

    # 加密密码
    encrypted_pwd = encrypt_password(password, salt_val)
    if not encrypted_pwd:
        raise Exception("密码加密失败")

    # 构造登录数据
    payload = {
        'username': username,
        'password': encrypted_pwd,
        'captcha': '',
        '_eventId': 'submit',
        'cllt': 'userNameLogin',
        'dllt': 'generalLogin',
        'lt': lt_val,
        'execution': exec_val,
    }

    print("提交登录表单...")
    # POST 登录（跟随重定向，让 CAS 设置全局认证 Cookie）
    resp_login = session.post(
        resp.url,  # 使用 GET 后的最终 URL
        data=payload,
        headers=headers,
        allow_redirects=True  # ✅ 跟随重定向，让 CAS 完成认证流程
    )

    # 调试输出
    print(f"   📊 登录响应状态: {resp_login.status_code}")
    print(f"   🍪 Cookie 数量: {len(session.cookies)}")
    print(f"   🍪 Cookie 名称: {list(session.cookies.keys())}")

    return session
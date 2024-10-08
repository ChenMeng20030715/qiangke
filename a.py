# https://curlconverter.com/     url转换网站
# 该代码运行之后可以退出浏览器，但是不可以再登录学生选课网站，建议浏览器选课界面一直登录，不要退出。
# 我在获取url的时候是已经登录了我的学生账号，所以不用再进行登录
# 如果使用mession进行选课处理，会进入一个登录界面，我现在没有办法绕过登录界面的验证码
# 选课日志被存储再文件根目录文件夹下的logfile.txt文件中（无需手动创建）

# ---------------------------------------------------------------------------------------------
# 代码调试过程
# 登录自己的选课系统
# f12/鼠标右键-检查打开DevTools我使用的是Edge浏览器，点击网络
# 点击你想要选课项目的选课按钮，再网络界面会出现一个记录，右键记录选择复制-复制为cURL(Bash)
# 进入网站https://curlconverter.com/ 复制你的cURL转化为python代码
# python代码应该会包含一下内容
# cookies headers params response
# 将我所展示代码的这几部分替换为你的
# 其中params需要注意，这里不是简单的替换，需要修改，因为我为了实现多线程而把他写在了一个函数之中
# 当然不同学校params中的属性可能有所不同但是实现逻辑大同小异
# 修改之后即可直接运行进行选课
# 我们学校的反爬虫机制并不强，所以我并没有使程序在运行一遍之后进行休眠，如果你们学校的反爬虫比较厉害，可以尝试添加休眠
# 实际操作可以参考【【手把手带你写抢课脚本】②人满了也能抢！】 https://www.bilibili.com/video/BV1nG4y1K7XL/?p=2&share_source=copy_web&vd_source=a16dde0142133f06ce523319ecbb5c3c
#------------------------------------------------------------------------------------------------

# random是在随机休眠时间部分使用
import random

import requests
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import SSLError

# 配置日志，使用自定义格式，日志只存储网页报错和选课成功信息，选课失败信息不存储
logging.basicConfig(level=logging.INFO)

# 创建一个自定义的Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建一个StreamHandler，并设置Formatter
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# 创建一个FileHandler，指定文件路径和设置Formatter
file_handler = logging.FileHandler('logfile.txt', encoding='utf-8')  # 替换为你想要保存日志的文件路径
file_handler.setFormatter(formatter)

# 获取root logger，并添加StreamHandler和FileHandler
logger = logging.getLogger()
logger.addHandler(stream_handler)
logger.addHandler(file_handler)

cookies = {
    'bzb_jsxsd': '74EC8EF2F41F463CB99BB5812C528A51',
    'SERVERID': 'CD6F4305F472E69F7B7291DF3567DAF9',
    'bzb_njw': '129',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
    'Referer': 'https://bkzhjx.wh.sdu.edu.cn/jsxsd/xsxkkc/getXxxk',
    # 'Cookie': 'bzb_jsxsd=DCF34A11077E2DAA935BFCE41F83E7EF; bzb_njw=29E4F224B04996EE3DE652856B93FC8A; SERVERID=125',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


def task(kcid, jx0404id):
    params = {
        'kcid': kcid,
        'cfbs': 'null',
        'jx0404id': jx0404id,
        'xkzy': '',
        'trjf': '',
    }
    count = 0
    localtime = time.asctime(time.localtime(time.time()))
    while True:
        try:
            count += 1
            response = requests.get('https://bkzhjx.wh.sdu.edu.cn/jsxsd/xsxkkc/xxxkOper', params=params,
                                    cookies=cookies,
                                    headers=headers
                                    )
            # 判断返回是否为空
            if response and response.status_code == 200:
                res = json.loads(response.text)
                print("相应text::   ")
                print(response.text)
                success = res['success']

                localtime = time.asctime(time.localtime(time.time()))
                # 选课成功
                if success:
                    logging.info(f"{localtime} - 选课成功！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！ {kcid}")
                    print(f"{localtime} - 选课成功！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！ {kcid}")
                    break
                # 选课失败则继续进行选课，每一百次输出一次
                elif count % 100 == 0:
                    # logging.warning(f"{localtime} - 选课失败！ {kcid}    {count}")
                    print(f"{response.text}")
                    print(f"{localtime} - 选课失败！ {kcid}    {count}")
            else:
                logging.error(f"{localtime} - Request failed with status code: {response.status_code}")
                logging.error(f"Server response: {response.text}")
        # JSON解析错误我遇到的都是服务器请求超时，还是直接重启进程即可
        except json.JSONDecodeError as json_error:
            logging.error(f"{localtime} - JSON解析错误: {json_error}")
            logging.error(f"Response Text: {response.text}")
            continue
        except requests.exceptions.RequestException as req_exc:
            # ssl错误应该是服务器检测到你多次访问，然后进行真人验证，我没有办法进行验证，但是在进程挂掉之后我们直接重启进程即可
            if isinstance(req_exc.__cause__, SSLError):
                ssl_error = req_exc.__cause__
                logging.error(f"{localtime} - SSLError: {ssl_error}")
                logging.error(
                    f"SSL Protocol Version: {ssl_error.args[0]}, SSL Verify Options: {ssl_error.verify_flags}")
            else:
                logging.error(f"{localtime} - RequestException: {req_exc}")
                # 这里的等待我感觉没有必要，所以直接注释掉，也没有出现错误
                time.sleep(2)
            # 重启进程
            continue
        # 其他相关错误的输出，但是我没有遇到
        except Exception as e:
            logging.error(f"{localtime} - Exception in thread {kcid}: {str(e)}")
            # 重启进程
            continue
        # # 生成1到2之间的随机浮点数，表示休眠时间，看网站反扒机制决定是否使用和参数
        sleep_time = 2
        # # 休眠，防止被发现
        time.sleep(sleep_time)


def run():
    # 想选课程的课程号和相关数据，可在前端f12获取
    ke = [
        ['sd01331130', '202420251004074'],
        ['sd01332200', '202420251004077']
    ]
    # ke = [
    #     ['sd01332290', '202420251004078']
    # ]
    # ['sd03030321', '202320242001527']计算机图形学
    # 设置了五个线程，其实要选几门课就设置几个线程即可
    with ThreadPoolExecutor(2) as t:
        for k in ke:
            kcid = k[0]
            jx0404id = k[1]
            t.submit(task, kcid, jx0404id)
    try:
        # 等待所有线程完成
        t.shutdown(wait=True)
    except Exception as e:
        logging.error(f"Exception: {e}")


if __name__ == '__main__':
    run()
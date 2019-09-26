# coding: utf-8
from json import loads
from time import sleep, time
from pickle import dump, load
from os.path import exists
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Concert(object):
    def __init__(self, session, price, real_name, nick_name, ticket_num, damai_url, target_url):
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element_by_class_name(name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    def get_cookie(self):
        self.driver.get(self.damai_url)
        print(u"###请点击登录###")
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print(u"###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb")) 
        print(u"###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain':'.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print(u'###载入Cookie###')
        except Exception as e:
            print(e)

    def login(self):
        print(u'###开始登录###')
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            self.get_cookie()
        self.driver.get(self.target_url)
        self.set_cookie()

    def enter_concert(self):
        print(u'###打开浏览器，进入大麦网###')
        self.driver = webdriver.Firefox()  # 默认火狐浏览器
        self.driver.maximize_window()
        self.login()
        self.driver.refresh()
        try:
            locator = (By.XPATH, "/html/body/div[1]/div/div[3]/div[1]/a[2]/div")
            element = WebDriverWait(self.driver, 3, 0.3).until(EC.text_to_be_present_in_element(locator, self.nick_name))
            self.status = 1
            print(u"###登录成功###")
            self.time_start = time()
        except:
            self.status = 0
            self.driver.quit()
            raise Exception(u"***错误：登录失败,请删除cookie后重试***")

    def choose_ticket(self):
        print(u"###进入抢票界面###")
        
        while self.driver.title.find('确认订单') == -1:  # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
            self.num += 1
            # 确认页面刷新成功
            try:
                box = WebDriverWait(self.driver, 2, 0.2).until(EC.presence_of_element_located((By.CLASS_NAME, 'perform__order__box')))
            except:
                raise Exception(u"***Error: 页面刷新出错***")

            try:
                buybutton = box.find_element_by_class_name('buybtn')
                buybutton_text = buybutton.text
            except:
                raise Exception(u"***Error: buybutton 位置找不到***")

            if buybutton_text == "即将开抢" or buybutton_text == "即将开售":
                self.status = 2
                raise Exception(u"---尚未开售，刷新等待---")

            try:
                selects = box.find_elements_by_class_name('perform__order__select')
                for item in selects:
                    if item.find_element_by_class_name('select_left').text == '场次':
                        session = item
                        # print('\t场次定位成功')
                    elif item.find_element_by_class_name('select_left').text == '票档':
                        price = item
                        # print('\t票档定位成功')

                session_list = session.find_elements_by_class_name('select_right_list_item')
                # print('可选场次数量为：{}'.format(len(session_list)))
                for i in self.session: # 根据优先级选择一个可行场次
                    j = session_list[i-1]
                    k = self.isClassPresent(j, 'presell', True)
                    if k: # 如果找到了带presell的类
                        if k.text == '无票':
                            continue
                        elif k.text == '预售':
                            j.click()
                            break
                    else:
                        j.click()
                        break

                price_list = price.find_elements_by_class_name('select_right_list_item')
                # print('可选票档数量为：{}'.format(len(price_list)))
                for i in self.price:
                    j = price_list[i-1]
                    k = self.isClassPresent(j, 'notticket')
                    if k:  # 存在notticket代表存在缺货登记，跳过
                        continue
                    else:
                        j.click()
                        break
            except:
                raise Exception(u"***Error: 选择场次or票档不成功***")

            try:
                ticket_num_up = box.find_element_by_class_name('cafe-c-input-number-handler-up')
            except:
                if buybutton_text == "选座购买":  # 选座购买没有增减票数键
                    buybutton.click()
                    self.status = 5
                    print(u"###请自行选择位置和票价，你有60秒的时间###")
                    break
                elif buybutton_text == "提交缺货登记":
                    raise Exception(u'###票已被抢完，持续捡漏中...或请终止程序并手动提交缺货登记###')
                else:
                    raise Exception(u"***Error: ticket_num_up 位置找不到***")

            if buybutton_text == "立即预订":
                for i in range(self.ticket_num-1):  # 设置增加票数
                    ticket_num_up.click()
                buybutton.click()
                self.status = 3

            elif buybutton_text == "立即购买":
                for i in range(self.ticket_num-1):  # 设置增加票数
                    ticket_num_up.click()
                buybutton.click()
                self.status = 4


    def check_order(self):
        if self.status in [3, 4, 5]:
            try:
                if self.status in [3, 4]:
                    tb = WebDriverWait(self.driver, 5, 0.2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div[2]/div[1]')))
                else:  # 自行选座
                    tb = WebDriverWait(self.driver, 60, 0.2).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/div[2]/div[2]/div[1]')))
                print(u'###开始确认订单###')
                print(u'###选择购票人信息###')
                init_sleeptime = 0.
                Labels = tb.find_elements_by_tag_name('label')
                for num_people in self.real_name:
                    Labels[num_people-1].find_element_by_tag_name('input').click() # 选择第self.real_name个实名者
                    if num_people != self.real_name[-1]:
                        sleep(init_sleeptime)

                # 防止点击过快导致没有选择多个人
                all_true = False
                while not all_true:
                    init_sleeptime += 0.1
                    true_num = 0
                    for num_people in self.real_name:
                        tag_input = Labels[num_people-1].find_element_by_tag_name('input')
                        if tag_input.get_attribute('aria-checked') == 'false':
                            sleep(init_sleeptime)
                            tag_input.click()
                        else:
                            true_num += 1
                    if true_num == len(self.real_name):
                        break
            except:
                if self.real_name is not None:
                    raise Exception(u"***Error：实名信息选择框没有显示***")
            # print('###不选择订单优惠###')
            # print('###请在付款完成后下载大麦APP进入订单详情页申请开具###')
            self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/div[9]/button').click() # 同意以上协议并提交订单
            '''
            try:
                buttons = self.driver.find_elements_by_tag_name('button') # 找出所有该页面的button
                for button in buttons:
                    if button.text == '同意以上协议并提交订单':
                        button.click()
                        break
            except Exception as e:
                raise Exception('***错误：没有找到提交订单按钮***')
           '''

            # 等待title出现并判断title是不是支付宝
            try:
                WebDriverWait(self.driver, 20, 0.2).until_not(EC.title_contains('确认订单'))
            except:
                raise Exception(u'***Error: 提交订单失败（打不开付款页面）***')

            element = EC.title_contains('支付宝')(self.driver)
            if element:
                self.status = 6
                print(u'###成功提交订单,请手动支付###')
                self.time_end = time()
            else:
                raise Exception(u'***Error: 提交订单失败（跳转到其他界面）***')


if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址
        con = Concert(config['sess'], config['price'], config['real_name'], config['nick_name'], config['ticket_num'], config['damai_url'], config['target_url'])
        con.enter_concert()
    except Exception as e:
        print(e)
        exit(1)
    while True:
        try:
            con.choose_ticket()
            con.check_order()
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue

        if con.status == 6:
            print(u"###经过%d轮奋斗，共耗时%.1f秒，抢票成功！请确认订单信息###" % (con.num, round(con.time_end-con.time_start, 3)))
            break

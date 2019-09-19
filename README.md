# damai_ticket
大麦网自动抢票工具

## Preliminary
Python 3.6+

## Set up
Firefox Browser (测试版本：v68.0.1.7137)

geckodriver.exe (测试版本：v0.24.0)

--以上两个安装包文件夹内均包含--

Firefox 浏览器安装好后需将geckodriver.exe放置于Firefox浏览器目录下

pip install selenium

## Basic usage
在config.json中输入相应配置信息，具体说明如下：

{
    
    "sess": [ # 场次优先级列表，如本例中共有三个场次，根据下表，则优先选择1，再选择2，最后选择3；也可以仅设置1个。
        1,
        2,
        3,
    ],
    "price": [ # 票价优先级，如本例中共有三档票价，根据下表，则优先选择1，再选择3；也可以仅设置1个。
        1,
        3
    ],
    "real_name": [1,2], # 实名者序号，如本例中根据序号共选择两位实名者，根据序号，也可仅选择一位
                        （选择一位或是多位根据购票需知要求，若一个订单仅需提供一位购票人信息则选择一位；
                        若一张门票对应一位购票人信息则选择多位）。
    "nick_name": "<Your nick_name>", # <Your nick_name>改为用户的昵称，用于验证登录是否成功
    "ticket_num": 2, # 购买票数
    "damai_url": "https://www.damai.cn/", # 大麦网官网网址
    "target_url": "https://detail.damai.cn/item.htm?id=599834886497" # 目标购票网址
    
}

1）部分门票需要选择城市，只需选择相应城市后将其网址复制到config.json文件的target_url参数即可。

![avatar](/picture/1.png)

2）根据需要选择的场次和票价分别修改config.json文件中的sess和price参数。

![avatar](/picture/2.png)

3）查看购票须知中实名制一栏，若每笔订单只需一个证件号则config.json文件中的real_name参数只需选择一个；若每张门票需要一个证件号，则real_name参数根据需购票数量进行相应添加。

![avatar](/picture/3.png)

若是首次登录，根据终端输出的提示，依次点击登录、扫码登录，代码将自动保存cookie文件（cookie.pkl）

使用前请将待抢票者的姓名、手机、地址设为默认。

配置完成后执行python damai_ticket.py即可。

本代码为保证抢票顺利，设置循环直到抢票成功才退出循环，若中途需要退出程序请直接终止程序。

## Ref
本代码基于以下的Repo进行简单的改进：
Entromorgan:https://github.com/Entromorgan/Autoticket

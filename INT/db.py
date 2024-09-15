# -*- coding: UTF-8 -*-
import pymysql.cursors
import time
from datetime import datetime
import json


    # 数据库配置信息
config = {
'user': 'root',
'password': '',
'host': '',
'database': 'In-band telemetry'
}
# 连接到数据库
connection = pymysql.connect(user=config['user'],
                                password=config['password'],
                                host=config['host'],
                                database=config['database'],
                                port=3306,
                                cursorclass=pymysql.cursors.DictCursor)




def add_int_data(swid, hop_delay, queue_depth, queue_delay):
 
    try:
        
        with connection.cursor() as cursor:
            # 插入数据的SQL语句
            add_data = ("INSERT INTO `In-band telemetry`.`int data` (`swid`, `hop_delay`, `queue_depth`, `queue_delay`)"
                            " VALUES (%s, %s, %s, %s) "
                            " ON DUPLICATE KEY UPDATE "
                            " `hop_delay` = VALUES(`hop_delay`), "
                            " `queue_depth` = VALUES(`queue_depth`), "
                            " `queue_delay` = VALUES(`queue_delay`)")
            
            # 执行插入数据操作
            cursor.execute(add_data, (swid, hop_delay, queue_depth, queue_delay))
        
        # 提交数据
        connection.commit()
        print(f"Successfully added sw_id INT data: {swid}")
        

    except pymysql.MySQLError as e:
        print(e)
        
    
def int_server ():
    filename = "int_data.json"
    with open(filename, 'r') as f:
        int_data = json.load(f)
        results = []

    for swid, attributes in int_data.items():
        swid_number = swid.replace("swid", "")
        hop_delay = attributes.get("hop_delay", "0us")
        queue_depth = attributes.get("queue_depth", "0")
        queue_delay = attributes.get("queue_delay", '0us')
        results.append((swid_number, hop_delay))
        add_int_data (swid_number, hop_delay, queue_depth, queue_delay)


    
if __name__ == '__main__':
    int_server()
    connection.close()
    # while(True){
    #     int_server()
    #     time.sleep(1)
    # }
#     # 要添加的数据
#     sw_id_value = 3  # 根据需要修改此值
    
#     # 添加数据到sw_id列
#     # t1 = str(datetime.now())
#     # timeArray = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f") # 然后转换成 datetime.datetime 类型
#     # timeStamp = int(time.mktime(timeArray.timetuple()) * 1000.0 + timeArray.microsecond / 1000.0)
#     # print(timeStamp)

#     add_data_to_sw_id(sw_id_value)
    
#     # t1 = str(datetime.now())
#     # timeArray = datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f") # 然后转换成 datetime.datetime 类型
#     # timeStamp = int(time.mktime(timeArray.timetuple()) * 1000.0 + timeArray.microsecond / 1000.0)
#     # print(timeStamp)


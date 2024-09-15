import psutil
import GPUtil
def monitor_txt():
    #内存
    mem = psutil.virtual_memory()
    # 系统总计内存
    zj = float(mem.total) / 1024 / 1024 
    # 系统已经使用内存
    ysy = float(mem.used) / 1024 / 1024 
    # 系统空闲内存
    kx = float(mem.free) / 1024 / 1024 

    cpu = (str(psutil.cpu_percent(interval=0.5))) + '%'
    GPUs = GPUtil.getGPUs()
    #将感知信息写入txt文件
    with open('node-info.txt', 'w') as f:

        # 查看cpu信息
        print("主频: %s" %psutil.cpu_freq().current,file = f)      
        print(u"CPU核心数: %s" % psutil.cpu_count(logical=False), file=f)          
        print(u"CPU线程数: %s" % psutil.cpu_count(), file=f)
        print(u"cpu使用率: %s" % cpu, file=f)

        # 写入内存信息
        print('总内存:%.2fMB' % zj, file=f)
        print('已使用内存:%.2fMB' % ysy,  file=f)
        print('内存占用率:%s' % mem.percent, file=f)

        #写入磁盘信息
        disk_partion = psutil.disk_partitions()
        for i in range(len(disk_partion)):
            disk_path = str(disk_partion[i]).split('device=\'')[1].split('\'')[0]
            print(disk_path + '磁盘容量：%s'  %psutil.disk_usage(disk_path).total, file=f)
            print(disk_path + '磁盘占用率：%s'  %psutil.disk_usage(disk_path).percent, file=f)

        #写入GPU信息
        for i in range(len(GPUs)):
            print('GPU型号:'+ GPUs[i].name, file=f)
            print('GPU负载:'+ str(GPUs[i].load), file=f)
            print('显存利用率:'+ str(GPUs[i].memoryUtil), file=f)

monitor_txt()

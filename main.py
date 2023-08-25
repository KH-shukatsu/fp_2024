
import csv
import math
import datetime

#変数決定
N = 1

m = 2
t = 100


#csv読み込み後、確認日時、サーバアドレス、応答結果のリストを作成
NETWORKLOG_TIME = []
NETWORKLOG_ADDRESS = []
NETWORKLOG_PING = []
with open('networklog.csv') as networklog:
    reader = csv.reader(networklog)
    for row in reader:
        NETWORKLOG_TIME.append(row[0])
        NETWORKLOG_ADDRESS.append(row[1])
        NETWORKLOG_PING.append(row[2])


#サーバアドレスの種類
address_list = []
for ii in range(len(NETWORKLOG_ADDRESS)):
    if not NETWORKLOG_ADDRESS[ii] in address_list:
        address_list.append(NETWORKLOG_ADDRESS[ii])


# サーバアドレスごとに、確認時刻、応答結果のリスト作成
for idx in range(len(address_list)):
    str_newlist_time = 'time_list_' + str(idx) + ' = []'
    str_newlist_ping = 'ping_list_' + str(idx) + ' = []'
    exec(str_newlist_time)
    exec(str_newlist_ping)

for ii in range(len(NETWORKLOG_ADDRESS)):

    idx = address_list.index(NETWORKLOG_ADDRESS[ii])

    str_makelist_time = 'time_list_' + str(idx) + \
                        '.append(datetime.datetime.strptime(str(' + NETWORKLOG_TIME[ii] + '), \'%Y%m%d%H%M%S\'))'

    if NETWORKLOG_PING[ii].isdecimal():
        str_makelist_ping = 'ping_list_' + str(idx) + '.append(' + NETWORKLOG_PING[ii] + ')'
    else:
        str_makelist_ping = 'ping_list_' + str(idx) + '.append(float(\'nan\'))'
    
    exec(str_makelist_time)
    exec(str_makelist_ping)


'''# チェック用
for idx in range(len(address_list)):
    print(idx)
    print(address_list[idx])
    str_checklist_time = 'print(time_list_' + str(idx) + ')'
    str_checklist_ping = 'print(ping_list_' + str(idx) + ')'
    exec(str_checklist_time)
    exec(str_checklist_ping)
'''


## サーバの故障、及び過負荷状態の期間を確認する
print('\n')
for idx_net in range(len(address_list)): #サーバアドレスごとに評価

    timeoutcounter = 0

    datetime_first_timeout = []
    datetime_last_timeout = []

    frag_condition_1 = 1
    frag_condition_2 = 1

    now_name_address = address_list[idx_net]
    print('サーバアドレス：' + now_name_address)

    now_ping_list = []
    str_nowpinglist = 'now_ping_list = ping_list_' + str(idx_net)
    exec(str_nowpinglist)

    now_time_list = []
    str_nowtimelist = 'now_time_list = time_list_' + str(idx_net)
    exec(str_nowtimelist)

    totalnum_ping = len(now_ping_list)

    now_ping = []

    # 故障の判定
    for idx_ping in range(totalnum_ping): #時系列順に応答結果をチェック

        now_ping = now_ping_list[idx_ping]

        if math.isnan(now_ping):

            if timeoutcounter == 0:
                datetime_first_timeout = now_time_list[idx_ping]

            timeoutcounter = timeoutcounter + 1

        else:

            if timeoutcounter >= N:

                datetime_last_timeout = now_time_list[idx_ping]

                if frag_condition_1:
                    print('・以下の期間で故障が確認されました。')
                    frag_condition_1 = 0

                print('　' + datetime_first_timeout.strftime('%Y/%m/%d %H:%M:%S') + \
                      ' ~ ' + datetime_last_timeout.strftime('%Y/%m/%d %H:%M:%S'))

            datetime_first_timeout = []
            datetime_last_timeout = []
            timeoutcounter = 0

    if frag_condition_1:
        print('・対象のサーバで故障は確認されませんでした。')


    # 過負荷状態の判定
    for idx_ping in range(totalnum_ping):

        now_ping = now_ping_list[idx_ping]

        k = m - 1
        if idx_ping >= k:

            datetime_first_sample = []
            datetime_last_sample = []
            pingsample_count = 0
            pingsample_sum = 0

            for idx_pingsample in range(idx_ping-k,idx_ping+1):
                
                if not math.isnan(now_ping_list[idx_pingsample]):

                    pingsample_sum = pingsample_sum + now_ping_list[idx_pingsample]
                    pingsample_count = pingsample_count + 1

                    if datetime_first_sample == []:
                        datetime_first_sample = now_time_list[idx_pingsample]
                    
                    datetime_last_sample = now_time_list[idx_pingsample]
            
            if not pingsample_count == 0:

                pingsample_mean = pingsample_sum / pingsample_count
                if pingsample_mean > t:

                    if frag_condition_2:
                        print('・以下の期間で過負荷状態が確認されました。')
                        frag_condition_2 = 0

                    print('　' + datetime_first_sample.strftime('%Y/%m/%d %H:%M:%S') + \
                            ' ~ ' + datetime_last_sample.strftime('%Y/%m/%d %H:%M:%S'))
       
    if frag_condition_2:
        print('・対象のサーバで過負荷状態は確認されませんでした。')

    print('\n')
        

## サブネットの故障検出

#ネットワークプレフィックス長ごとにサーバーを分配
network_24_list = []
network_16_list = []
for idx_net in range(len(address_list)):
    now_address = address_list[idx_net]
    if now_address[-2:] == '24':
        if not now_address in network_24_list:
            network_24_list.append(now_address)
    if now_address[-2:] == '16':
        if not now_address in network_16_list:
            network_16_list.append(now_address)

#サブネットの種類をネットワークプレフィックス長ごと獲得
subnet24_address = []
for ii in range(len(network_24_list)):
    now_address = network_24_list[ii]
    now_address = now_address.replace('/24','')
    now_address = now_address.split('.')
    del now_address[3]
    now_address = '.'.join(now_address)
    if not now_address in subnet24_address:
        subnet24_address.append(now_address)
subnet16_address = []
for ii in range(len(network_16_list)):
    now_address = network_16_list[ii]
    now_address = now_address.replace('/16','')
    now_address = now_address.split('.')
    del now_address[2:]
    now_address = '.'.join(now_address)
    if not now_address in subnet16_address:
        subnet16_address.append(now_address)


#それぞれのサブネットごとに確認時刻、サーバアドレス、応答結果のリストを作成
for idx in range(len(subnet24_address)):
    str_newlist_subnet = 'address_list_sub24_' + str(idx) + ' = []'
    str_newlist_time = 'time_list_sub24_' + str(idx) + ' = []'
    str_newlist_ping = 'ping_list_sub24_' + str(idx) + ' = []'
    exec(str_newlist_subnet)
    exec(str_newlist_time)
    exec(str_newlist_ping)
for idx in range(len(subnet16_address)):
    str_newlist_subnet = 'address_list_sub16_' + str(idx) + ' = []'
    str_newlist_time = 'time_list_sub16_' + str(idx) + ' = []'
    str_newlist_ping = 'ping_list_sub16_' + str(idx) + ' = []'
    exec(str_newlist_subnet)
    exec(str_newlist_time)
    exec(str_newlist_ping)

for ii in range(len(NETWORKLOG_ADDRESS)):

    now_address = NETWORKLOG_ADDRESS[ii]

    if now_address[-2:] == '24':

        now_address_24 = now_address
        now_address_24 = now_address_24.replace('/24','')
        now_address_24 = now_address_24.split('.')
        del now_address_24[3]
        now_address_24 = '.'.join(now_address_24)

        for jj in range(len(subnet24_address)):
            if now_address_24 == subnet24_address[jj]:

                str_makelist_subnet = 'address_list_sub24_' + str(jj) + '.append(\'' + now_address + '\')'
                str_makelist_time = 'time_list_sub24_' + str(jj) + \
                                    '.append(datetime.datetime.strptime(str(' + NETWORKLOG_TIME[ii] + '), \'%Y%m%d%H%M%S\'))'
                if NETWORKLOG_PING[ii].isdecimal():
                    str_makelist_ping = 'ping_list_sub24_' + str(jj) + '.append(' + NETWORKLOG_PING[ii] + ')'
                else:
                    str_makelist_ping = 'ping_list_sub24_' + str(jj) + '.append(float(\'nan\'))'
                exec(str_makelist_subnet)
                exec(str_makelist_time)
                exec(str_makelist_ping)

    if now_address[-2:] == '16':

        now_address_16 = now_address
        now_address_16 = now_address_16.replace('/16','')
        now_address_16 = now_address_16.split('.')
        del now_address_16[2:]
        now_address_16 = '.'.join(now_address_16)

        for jj in range(len(subnet16_address)):
            if now_address_16 == subnet16_address[jj]:

                str_makelist_subnet = 'address_list_sub16_' + str(jj) + '.append(\'' + now_address + '\')'
                str_makelist_time = 'time_list_sub16_' + str(jj) + \
                                    '.append(datetime.datetime.strptime(str(' + NETWORKLOG_TIME[ii] + '), \'%Y%m%d%H%M%S\'))'
                if NETWORKLOG_PING[ii].isdecimal():
                    str_makelist_ping = 'ping_list_sub16_' + str(jj) + '.append(' + NETWORKLOG_PING[ii] + ')'
                else:
                    str_makelist_ping = 'ping_list_sub16_' + str(jj) + '.append(float(\'nan\'))'
                exec(str_makelist_subnet)
                exec(str_makelist_time)
                exec(str_makelist_ping)


#プレフィックス長==24のサブネットの応答結果を評価
for idx_net in range(len(subnet24_address)):

    timeoutcounter = []
    now_subnet_address_list = []
    now_idx_address_in_subnet = 0

    datetime_first_timeout = []
    datetime_last_timeout = []

    frag_condition_1 = 1

    now_name_address = subnet24_address[idx_net]
    print('サブネットアドレス：' + now_name_address + '.XXX')

    now_address_list = []
    str_nowaddresslist = 'now_address_list = address_list_sub24_' + str(idx_net)
    exec(str_nowaddresslist)

    now_ping_list = []
    str_nowpinglist = 'now_ping_list = ping_list_sub24_' + str(idx_net)
    exec(str_nowpinglist)

    now_time_list = []
    str_nowtimelist = 'now_time_list = time_list_sub24_' + str(idx_net)
    exec(str_nowtimelist)

    totalnum_ping = len(now_ping_list)

    now_ping = []

    # 故障の判定
    for idx_ping in range(totalnum_ping):

        now_ping = now_ping_list[idx_ping]
        now_address = now_address_list[idx_ping]

        if not now_address in now_subnet_address_list:
            now_subnet_address_list.append(str(now_address))
            timeoutcounter.append(0)
            now_idx_address_in_subnet = len(now_subnet_address_list) - 1
        else:
            now_idx_address_in_subnet = now_subnet_address_list.index(str(now_address))

        if math.isnan(now_ping):

            timeoutcounter[now_idx_address_in_subnet] = timeoutcounter[now_idx_address_in_subnet] + 1

            if datetime_first_timeout == []:

                for ll in range(len(now_subnet_address_list)):

                    if not timeoutcounter[ll] >= N:
                        break

                    if ll == len(now_subnet_address_list) - 1:
                        datetime_first_timeout = now_time_list[idx_ping]
                    
        else:

            for ll in range(len(now_subnet_address_list)):

                if not timeoutcounter[ll] >= N:
                    break

                if ll == len(now_subnet_address_list) - 1:

                    datetime_last_timeout = now_time_list[idx_ping]

                    if frag_condition_1:
                        print('・以下の期間でサブネットの故障が確認されました。')
                        frag_condition_1 = 0

                    print('　' + datetime_first_timeout.strftime('%Y/%m/%d %H:%M:%S') + \
                            ' ~ ' + datetime_last_timeout.strftime('%Y/%m/%d %H:%M:%S'))

            datetime_first_timeout = []
            datetime_last_timeout = []
            timeoutcounter[now_idx_address_in_subnet] = 0
            
    if frag_condition_1:
        print('・対象のサブネットで故障は確認されませんでした。')

print('\n')


#プレフィックス長==16のサブネットの応答結果を評価
for idx_net in range(len(subnet16_address)):

    timeoutcounter = []
    now_subnet_address_list = []
    now_idx_address_in_subnet = 0

    datetime_first_timeout = []
    datetime_last_timeout = []

    frag_condition_1 = 1

    now_name_address = subnet16_address[idx_net]
    print('サブネットアドレス：' + now_name_address + '.XXX.XXX')

    now_address_list = []
    str_nowaddresslist = 'now_address_list = address_list_sub16_' + str(idx_net)
    exec(str_nowaddresslist)

    now_ping_list = []
    str_nowpinglist = 'now_ping_list = ping_list_sub16_' + str(idx_net)
    exec(str_nowpinglist)

    now_time_list = []
    str_nowtimelist = 'now_time_list = time_list_sub16_' + str(idx_net)
    exec(str_nowtimelist)

    totalnum_ping = len(now_ping_list)

    now_ping = []

    # 故障の判定
    for idx_ping in range(totalnum_ping):

        now_ping = now_ping_list[idx_ping]
        now_address = now_address_list[idx_ping]

        if not now_address in now_subnet_address_list:
            now_subnet_address_list.append(str(now_address))
            timeoutcounter.append(0)
            now_idx_address_in_subnet = len(now_subnet_address_list) - 1
        else:
            now_idx_address_in_subnet = now_subnet_address_list.index(str(now_address))

        if math.isnan(now_ping):

            timeoutcounter[now_idx_address_in_subnet] = timeoutcounter[now_idx_address_in_subnet] + 1

            if datetime_first_timeout == []:

                for ll in range(len(now_subnet_address_list)):

                    if not timeoutcounter[ll] >= N:
                        break

                    if ll == len(now_subnet_address_list) - 1:
                        datetime_first_timeout = now_time_list[idx_ping]
                    
        else:

            for ll in range(len(now_subnet_address_list)):

                if not timeoutcounter[ll] >= N:
                    break

                if ll == len(now_subnet_address_list) - 1:

                    datetime_last_timeout = now_time_list[idx_ping]

                    if frag_condition_1:
                        print('・以下の期間でサブネットの故障が確認されました。')
                        frag_condition_1 = 0

                    print('　' + datetime_first_timeout.strftime('%Y/%m/%d %H:%M:%S') + \
                            ' ~ ' + datetime_last_timeout.strftime('%Y/%m/%d %H:%M:%S'))

            datetime_first_timeout = []
            datetime_last_timeout = []
            timeoutcounter[now_idx_address_in_subnet] = 0

    if frag_condition_1:
        print('・対象のサブネットで故障は確認されませんでした。')

    
print('\n')
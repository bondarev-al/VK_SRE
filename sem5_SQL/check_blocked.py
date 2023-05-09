import psycopg2
import sys
import re
import ipaddress

script_name=sys.argv[0]
find=""

def show_examples():
    print(f'(Example: python3 {script_name} 13.32.12.23)')
    print(f'(Example: python3 {script_name} -d website_for_check.com)')

# Обработка переданных позиционных параметров
if ( len(sys.argv) == 3 ) and ( sys.argv[1] == "-d") :
    domain = sys.argv[2]
    find = "domain"
elif len(sys.argv) == 2:
    if re.fullmatch('^([12]?\d{1,2}\.){3}[12]?\d{1,2}$', sys.argv[1]):
        ip = sys.argv[1]
        find = "ip"
    else:
        print(f"Error: '{sys.argv[1]}' it's not ip.")
        show_examples()
        exit(1)
else:
    print('Error: Enter ip or domain name for check.')
    show_examples()
    exit(1)

# Подключение к базе данных
conn = psycopg2.connect("dbname=block_ip user=alexander password=1234 host=localhost") 
cur = conn.cursor() 

if find == "ip":
    # Проверка ip на блокировку
    ip_regular_exp = "'(^|\|)"+ip+"($|\|)'"
    cur.execute(f"SELECT * from blocked_ip where ip ~ {ip_regular_exp}")
    res_check_ip = cur.fetchall()

    # Проверка не заблокирована ли подсеть ip
    half_ip = re.findall("^\d{1,3}\.\d{1,3}\.", ip)[0]
    ip_subnet_regular_exp = "'(^|\|)"+half_ip+"[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}($|\|)'"
    cur.execute(f"SELECT * from blocked_ip where ip ~ {ip_subnet_regular_exp}")
    list_check_subnet = cur.fetchall()
    for subnet_record in list_check_subnet:
        subnets = re.findall("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}", subnet_record[0])
        for subnet in subnets:
            ip_subnet = ipaddress.ip_network(subnet)
            ipv4 = ipaddress.ip_address(ip)
            # Если ip в подсети, то добавление записи об этом в итоговую сводку поиска
            if ipv4 in ip_subnet:
                res_check_ip.append(subnet_record)

    # Вывод информации о блокировке
    if len(res_check_ip) > 0:
        reply = input(f"'{ip}' - blocked. Show results with this ip?[yes/no]: ")
        if ( reply == 'yes' ) or ( reply == 'y'):
            for x in res_check_ip:
                print(x)
    else:
        print(f"'{ip}' - OK. It's not blocked.")
elif find == "domain":
    # Проверка доменного имени на блокировку
    domain_regular_exp="'^(\*\.)?"+domain+"$'"
    cur.execute(f"SELECT * from blocked_ip where domain ~ {domain_regular_exp}")
    res_check_domain = cur.fetchall()

    # Вывод информации о блокировке домена
    if len(res_check_domain) > 0:
        reply = input(f"'{domain}' - blocked. Show results with this domain?[yes/no]: ")
        if ( reply == 'yes' ) or ( reply == 'y'):
            for x in res_check_domain:
                print(x)
    else:
        print(f"'{domain}' - OK. It's not blocked.")

cur.close();
conn.close();
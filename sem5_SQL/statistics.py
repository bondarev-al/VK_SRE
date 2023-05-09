import psycopg2
import sys

script_name=sys.argv[0]

# Подключение к базе данных
conn = psycopg2.connect("dbname=block_ip user=alexander password=1234 host=localhost") 
cur = conn.cursor() 

print(f'{script_name}: statistics for blocked websites:')

# Подсчет числа записей в БД
cur.execute("SELECT COUNT(*) from blocked_ip")
res = cur.fetchall()[0][0]
print(f'Number of records - {res}')

# Подсчет числа уникальных наборов ip
cur.execute("SELECT ip from blocked_ip GROUP BY ip")
res = cur.fetchall()
print(f'Number of unique set of ip - {len(res)}')

# Подсчет числа уникальных доменов
cur.execute("SELECT domain from blocked_ip GROUP BY domain")
res = cur.fetchall()
print(f'Number of unique domain - {len(res)}')

# Подсчет числа уникальных решений суда
cur.execute("SELECT decree from blocked_ip GROUP BY decree")
res = cur.fetchall()
print(f'Number of unique decree - {len(res)}')

cur.close();
conn.close();
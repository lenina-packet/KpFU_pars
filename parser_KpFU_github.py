import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup as BS

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
}

KFU_ping = "https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_faculty=47&p_speciality=1416&p_inst=0&p_typeofstudy=1"
KFU_pi = "https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_faculty=9&p_speciality=1084&p_inst=0&p_typeofstudy=1"
KFU_pmi = "https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_faculty=9&p_speciality=166&p_inst=0&p_typeofstudy=1"
KFU_pm = "https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_faculty=9&p_speciality=559&p_inst=0&p_typeofstudy=1"
KFU_mat_and_komp = "https://abiturient.kpfu.ru/entrant/abit_entrant_originals_list?p_open=&p_faculty=5&p_speciality=358&p_inst=0&p_typeofstudy=1"

KFU = [("Программная инженерия (КФУ)", KFU_ping), ("Прикладная информатика (КФУ)", KFU_pi), \
        ("Прикладная математика и информатика (КФУ)", KFU_pmi), ("Прикладная математика (КФУ)", KFU_pm), \
            ("Математика и комп.науки (КФУ)" , KFU_mat_and_komp)]
KFU_info_students = [] 

def get_html(url, params = None):
    session = HTMLSession()
    r = session.get(url)
    return r

def parse(URL):
    html = get_html(URL)
    if html.status_code == 200:
        soup = BS(html.text, 'lxml')
        tables = get_tables(soup)
        return get_content(soup, tables)
    else:
        print("Ошибка!")

def get_tables(soup):
    tables_lgot = soup.find_all('table', id = "t_lgota")
    out_tbls = [x for x in tables_lgot]
    tables_control = soup.find_all('table', id = "t_common")
    for x in tables_control: out_tbls.append(x)
    return out_tbls


def parse_abits(soup):
    info = []
    abits = soup.find_all('tr', style = "font-weight:normal;")
    for abit in abits:
        tds = abit.find_all('td', align = "left")
        for snils in tds:
            snils_number = snils.text.replace('\n','')
        flags = abit.find_all('td')
        ball = []
        soglasies = []
        for tf in flags:
            buffer = tf.text.replace('\n','')
            if buffer in ['да', 'нет']:
                soglasies.append(buffer)
            elif buffer.isdigit():
                ball.append(int(buffer))
        info.append((snils_number, soglasies[-2], soglasies[-1], ball[-1]))
    abits = soup.find_all('tr', style = "font-weight:bold;")
    for abit in abits:
        tds = abit.find_all('td', align = "left")
        for snils in tds:
            snils_number = snils.text.replace('\n','')
        flags = abit.find_all('td')
        ball = []
        soglasies = []
        for tf in flags:
            buffer = tf.text.replace('\n','')
            if buffer in ['да', 'нет']:
                soglasies.append(buffer)
            elif buffer.isdigit():
                ball.append(int(buffer))
        info.append((snils_number, soglasies[-2], soglasies[-1], ball[-1]))
    return info

def get_content(soup, tables):
    info = []
    info_priem = soup.find('p', align = "center")
    info_priem = info_priem.find('b')
    for inf in info_priem:
            inf_nabor = inf.text.replace('\n','')
    lgot_counts = inf_nabor.split()
    counts = round(int(lgot_counts[2].replace(",", "")))
    lgot_counts = round(int(lgot_counts[2].replace(",", "")) * 0.1)
    for x in tables:
        if x != tables[-1]:
            info.append([lgot_counts, parse_abits(x)])
        else:
            info.append([counts, parse_abits(x)])
    return (info, inf_nabor)
    
def input_inf(URLS):
    for x in URLS:
        print("Сбор информации из", x[0])
        KFU_info_students.append([x[0], parse(x[1])[0], parse(x[1])[1]])

def search_mest():
    print("Введите номер вашего СНИЛСа:")
    search_snils = input()
    print("Введите суммарный балл в данном вузе:")
    ball = int(input())
    for x in KFU_info_students:
        flag = False
        print(x[0])
        f = open(x[0] + ".txt", "w", encoding="utf8")
        f.write(x[2] + "\n")
        count_lg = 0
        for elements in x[1]:
            if elements != x[1][-1]:
                cnt_lgts = 0
                counts = elements[0]
                elements[1].sort(key = lambda x: (x[1], x[2], x[3]))
                for y in elements[1]:
                    s = str(y[0]) + " " + str(y[1]) + " " +str(y[2]) + " " + str(y[3]) + "\n"
                    f.write(s)
                    if y[1] == "да" and y[2] == "да":
                        cnt_lgts += 1
                if cnt_lgts > counts:
                    count_lg += counts
                else:
                    count_lg += cnt_lgts
            else:
                id_sogl, id_original = count_lg, count_lg
                elements[1].sort(key = lambda x: (x[1], x[2], x[3]))
                for y in elements[1]:
                    s = str(y[0]) + " " + str(y[1]) + " " + str(y[2]) + " " + str(y[3]) + "\n"
                    f.write(s)
                    if y[1] == "да" and y[3] >= ball:
                        id_sogl += 1
                        if y[2] == "да":
                            id_original += 1
                        print(y)
                    if y[0] == search_snils:
                        id_sogl += 1;  id_original += 1
                        print("СНИЛС: ", search_snils, "Позиция, если сдашь согласие + оригинал: ", id_original)
                        print("СНИЛС: ", search_snils, "Позиция, если сдашь согласие: ", id_sogl)
                        print("Занято льготных мест:", count_lg)
                        flag = True
                        break
        print("*************************")
        f.close()  
input_inf(KFU)                
search_mest()
    
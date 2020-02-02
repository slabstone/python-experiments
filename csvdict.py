import codecs
import csv

# запись списка словарей в CSV-таблицу
def write_list(file, list, mode='a', header=None):
    with codecs.open(file, mode, 'utf-8') as f:
        if header:
            fieldnames = header
        else:
            # список ключей словаря записывается в качестве заголовка таблицы
            fieldnames = list[0].keys()
        
        # создание таблицы
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # запись списка в таблицу
        writer.writerows(list)
            
# чтение списка словарей из CSV-таблицы
def read_list(file):
    with codecs.open(file, 'r', 'utf-8') as f:
        reader = csv.DictReader(f, fieldnames=None)
        list = []
        for row in reader:
            list.append(dict(row))  # type(row) == OrderedDict
        
        return list

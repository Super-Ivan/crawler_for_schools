import requests
import re
import xlwt
import xlrd
from urllib import parse as parse


def get_page(url):
    crawler = requests.session()
    page = crawler.get(url).content
    page_data = page.decode()
    return page_data


def get_table():
    data = xlrd.open_workbook('schools.xls')
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    return table, nrows, ncols


def get_url(word):
    url = 'http://baike.baidu.com/item/{}'.format(parse.quote(word))
    return url


def get_schools_list(table, begin, end):
    schools = []
    for i in range(begin, end):
        schools.append(table.col(0)[i].value)
    return schools


def get_schools_dict(schools_list):
    schools = {}
    schools_not_changed = []

    for school in schools_list:
        url = get_url(school)
        page_data = get_page(url)

        new_names = re.findall(
            '更名[为\：]([\“\”\《\》\u4e00-\u9fa5]*?大学|[\“\”\《\》\u4e00-\u9fa5]*?学院|[\“\”\《\》\u4e00-\u9fa5]*?学校)', page_data)
        original_names = re.findall(
            '([\“\”\《\》\u4e00-\u9fa5]*?大学|[\“\”\《\》\u4e00-\u9fa5]*?学院|[\“\”\《\》\u4e00-\u9fa5]*?学校)[\“\”\《\》\u4e00-\u9fa5]*?更名', page_data)
        first_name = re.findall(
            '原名[为\：]([\“\”\《\》\u4e00-\u9fa5]*?大学|[\“\”\《\》\u4e00-\u9fa5]*?学院|[\“\”\《\》\u4e00-\u9fa5]*?学校)', page_data)

        names = new_names + original_names + first_name

        if len(names) != 0:
            schools.setdefault(school, set())
            for name in names:
                schools[school] |= {name}

        else:
            print(school, '从未更名')
            schools_not_changed.append(school)

    return schools, schools_not_changed


def compare(school_original_list, schools_new_dict):
    schools_changed = []
    for school_original in school_original_list:
        for school_new in schools_new_dict:

            for school_new_name in schools_new_dict[school_new]:
                if school_original in school_new_name:
                    print(
                        'one school be found:', school_original, '->', school_new, '\n')
                    schools_changed.append((school_original, school_new))
    return schools_changed


if __name__ == '__main__':
    original_end = 1
    table, nrows, ncols = get_table()
    school_original_list = get_schools_list(table, 1, original_end)
    schools_new_list = get_schools_list(table, original_end, nrows)
    schools_new_dict, schools_not_changed = get_schools_dict(schools_new_list)

    print('\nget the school_original_list:', len(school_original_list))
    print('get the schools_new_list:', len(schools_new_list))
    print('get the schools_new_dict:', len(schools_new_dict), '\n')

    schools_changed = compare(school_original_list, schools_new_dict)

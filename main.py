import requests
from env import get_data_from_env
from statistics import mean
from terminaltables import SingleTable

HH_VACANCIES_URL = 'https://api.hh.ru/vacancies/'
SUPER_JOB_URL = 'https://api.superjob.ru/2.0/vacancies/'
TOP_PROGRAMMING_LANGUAGES = ["Kotlin",
                             "Go",
                             "Javascript",
                             "Typescript",
                             "Python",
                             "Java",
                             "PHP",
                             "Swift",
                             "C++",
                             "C#"]


def get_hh_total_count_for_vancancy(vacancy_name):
    params = {'text': vacancy_name,
              'area': 1,
              'period': 30,
              'clusters': 'true',
              'per_page': 0
              }
    response = requests.get(HH_VACANCIES_URL,
                            params=params)
    response.raise_for_status()
    return response.json()


def get_hh_vancancy_average_salary(vacancy_name, pages_count):
    vacancies_pages_result = []
    for page_number in range(pages_count):
        params = {'text': vacancy_name,
                  'area': 1,
                  'period': 30,
                  'per_page': 100,
                  'page': page_number}
        response = requests.get(HH_VACANCIES_URL,
                                params=params)
        response.raise_for_status()
        vacancies_pages_result.append(response.json())
    vacancies_processed = 0
    vacancies_salary = []
    for vacancies_page in vacancies_pages_result:
        for vacancy in vacancies_page['items']:
            if vacancy['salary'] is not None:
                if vacancy['salary']['currency'] == "RUR":
                    salary_from = 0 if vacancy['salary']['from'] is None \
                        else vacancy['salary']['from']
                    salary_to = 0 if vacancy['salary']['to'] is None \
                        else vacancy['salary']['to']
                    vacancies_salary.append(get_average_salary(salary_from,
                                                               salary_to))
                    vacancies_processed += 1
    return vacancies_processed, int(mean(vacancies_salary))


def get_hh_programers_statistic():
    hh_total = []
    for prog_language in TOP_PROGRAMMING_LANGUAGES:
        vacancy_name = f'программист {prog_language}'
        vacancies_found = get_hh_total_count_for_vancancy(
            vacancy_name).get('found')
        vacancies_processed, average_salary = get_hh_vancancy_average_salary(
            vacancy_name, pages_count=10)
        hh_total.append([prog_language,
                        vacancies_found,
                        vacancies_processed,
                        average_salary])
    return(hh_total)


def get_sj_programers_statistic():
    super_job_secret_key = get_data_from_env("secret_key")
    headers = {
        "X-Api-App-Id": super_job_secret_key}
    super_job_total = []
    for prog_language in TOP_PROGRAMMING_LANGUAGES:
        vacancy_name = f'программист {prog_language}'
        params = {'keyword': vacancy_name,
                  'town': 'Москва',
                  'period': 30,
                  'count': 100}
        response = requests.get(SUPER_JOB_URL,
                                headers=headers,
                                params=params)
        response.raise_for_status()
        average_salaries = []
        vacancies_processed = 0
        for item in response.json()['objects']:
            if (item['payment_from'] != 0 and
                item['payment_to'] != 0 and
                item['currency'] == 'rub'):
                    vacancies_processed += 1
                    average_salaries.append(get_average_salary(
                        item['payment_from'], item['payment_to']))
        if (response.json()['total'] != 0 and vacancies_processed != 0):
            super_job_total.append([prog_language,
                                    response.json()['total'],
                                    vacancies_processed,
                                    int(mean(average_salaries))])
    return super_job_total


def get_average_salary(salary_from, salary_to):
    average_salary = 0
    if salary_from != 0 and salary_to != 0:
        average_salary = (salary_from+salary_to)/2
    if salary_from != 0 and salary_to == 0:
        average_salary = salary_from*1.2
    if salary_to != 0 and salary_from == 0:
        average_salary = salary_to*0.8
    return int(average_salary)


def print_table(languages_data, title):
    rows_titles = ['Язык программирования',
                   'Вакансий найдено',
                   'Вакансий обработано',
                   'Средняя зарплата']
    table_data = []
    table_data.append(rows_titles)
    for language_data in languages_data:
        table_data.append(language_data)
    table_instance = SingleTable(table_data, title)
    print(table_instance.table)


def main():
    print_table(get_hh_programers_statistic(), 'Headhunter Moscow')
    print_table(get_sj_programers_statistic(), 'SuperJob Moscow')


if __name__ == '__main__':
    main()

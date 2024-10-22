import time
import requests
from loguru import logger
import pandas as pd
from openpyxl import load_workbook
from datetime import datetime
from multiprocessing import Process


def request_post(storeID):
    json_schema = {
        "query": "query Query($storeId: Int!, $slug: String!, $attributes:[AttributeFilter], $filters: [FieldFilter], "
                 "$from: Int!, $size: Int!, $sort: InCategorySort, $in_stock: Boolean, $eshop_order: Boolean, "
                 "$is_action: Boolean, $priceLevelsOnline: Boolean) { category (storeId: $storeId, slug: $slug, "
                 "inStock: $in_stock, eshopAvailability: $eshop_order, isPromo: $is_action, priceLevelsOnline: "
                 "$priceLevelsOnline) { id name slug parent_id meta { description h1 title keywords } disclaimer "
                 "description { top main bottom } breadcrumbs { category_type id name parent_id parent_slug slug } "
                 "promo_banners { id image name category_ids type sort_order url is_target_blank analytics { name "
                 "category brand type start_date end_date } } dynamic_categories(from: 0, size: 9999) { slug name id "
                 "category_type dynamic_product_settings { attribute_id max_value min_value slugs type } } filters { "
                 "facets { key total filter { id hru_filter_slug is_hru_filter is_filter name display_title is_list "
                 "is_main text_filter is_range category_id category_name values { slug text total } } } } total "
                 "prices { max min } pricesFiltered { max min } products(attributeFilters: $attributes, from: $from, "
                 "size: $size, sort: $sort, fieldFilters: $filters) { health_warning limited_sale_qty id slug name "
                 "name_highlight article new_status main_article main_article_slug is_target category_id category { "
                 "name } url images pick_up rating icons { id badge_bg_colors rkn_icon caption type is_only_for_sales "
                 "caption_settings { colors text } sort image_svg description end_date start_date status } "
                 "manufacturer { name } packing { size type } stocks { value text scale eshop_availability "
                 "prices_per_unit { old_price offline { price old_price type offline_discount offline_promo } price "
                 "is_promo levels { count price } online_levels { count price discount } discount } prices { price "
                 "is_promo old_price offline { old_price price type offline_discount offline_promo } levels { count "
                 "price } online_levels { count price discount } discount } } } argumentFilters { eshopAvailability "
                 "inStock isPromo priceLevelsOnline } } }",
        "variables": {
            "isShouldFetchOnlyProducts": True,
            "slug": "ovoshchi",
            "storeId": int(storeID),
            "sort": "default",
            "size": 9999,
            "from": 0,
            "filters": [{"field": "main_article", "value": "0"}],
            "attributes": [],
            "in_stock": True,  # True = Только овощи в наличии в магазине, False = все овощи
            "eshop_order": False
        }
    }
    response = requests.post('https://api.metro-cc.ru/products-api/graph',
                             headers={'Content-Type': 'application/json'},
                             json=json_schema)
    return response


def parsing_ovoshchi(shops):
    data_xlsx = {'id': [],
                 'Название': [],
                 'Ссылка': [],
                 'Регулярная цена': [],
                 'Промо цена': [],
                 'Бренд': []}

    for storeID in shops.keys():
        address_shop = shops[storeID]

        [data_xlsx[key].append(f"Магазин по адресу: {address_shop}" if key == 'Ссылка' else '') for key in
         data_xlsx.keys()]  # Добавляет в центральный столбец название магазина

        logger.info(f"Получаем овощи(в наличии) из магазина {address_shop} ")
        response = request_post(storeID)
        if response.status_code != 200:
            logger.critical(f"Error response: {response.status_code}")
            logger.info(f"Ожидание повторного запроса 5 секунд")
            time.sleep(5)
            while response.status_code != 200:
                response = request_post(storeID)
                if response.status_code != 200:
                    logger.critical(f"Error response: {response.status_code}")
                    logger.info(f"Ожидание повторного запроса 5 секунд")
                    time.sleep(5)
        logger.success("Данные получены успешно")
        response = response.json()
        total_type_products = 0
        for item in response['data']['category']['products']:
            data_xlsx['id'].append(item['id'])
            data_xlsx['Название'].append(item['name'])
            data_xlsx['Ссылка'].append('https://online.metro-cc.ru' + item['url'])
            if item['stocks'][0]['prices']['is_promo']:
                data_xlsx['Регулярная цена'].append(item['stocks'][0]['prices']['old_price'])
                data_xlsx['Промо цена'].append(item['stocks'][0]['prices']['price'])
            else:
                data_xlsx['Регулярная цена'].append(item['stocks'][0]['prices']['price'])
                data_xlsx['Промо цена'].append('Акции нет')
            data_xlsx['Бренд'].append(item['manufacturer']['name'])
            total_type_products += 1
        logger.info(f"Колличество типов овощей(в наличии) = {total_type_products}")
        [data_xlsx[key].append(f"Колличество овощей = {total_type_products}" if key == 'Ссылка' else '') for key in
         data_xlsx.keys()]  # Добавляем в конце строку Кол-во все типов овощей в наличии
        [data_xlsx[key].append(' ') for key in data_xlsx.keys()]  # Добавляет пустую строку, для лучшей читаемости
    return data_xlsx


def save_to_xlsx(data_xlsx, path_doc):
    df = pd.DataFrame.from_dict(data_xlsx)
    df.to_excel(path_doc, index=False, engine='openpyxl')


# Чисто для лучшей читаемости Эксельки
def optimization_width_column(path_doc):
    workbook = load_workbook(path_doc)
    sheet = workbook.active
    column_widths = {
        'A': 10,
        'B': 50,
        'C': 70,
        'D': 17,
        'E': 15,
        'F': 30,
    }
    for column, width in column_widths.items():
        sheet.column_dimensions[column].width = width
    workbook.save(path_doc)


def multi_start(shops, city_name):
    data_piter = parsing_ovoshchi(shops)
    logger.info(f"Сохраняем в xlsx")
    path_doc = f'Овощи {city_name}.xlsx'  # Изменить для сохранения в другую папку и с другим названием
    save_to_xlsx(data_piter, path_doc)
    logger.info(f"Оптимизируем ширину столбцов")
    optimization_width_column(path_doc)


if __name__ == '__main__':
    start_time_job = datetime.now()
    # Все магазины в г.Москва
    id_address_shop_moskov = {
        '10': 'Ул. Ленинградское шоссе, д. 71Г (м. Речной вокзал)',
        '11': 'Ул. Пр-т Мира, д. 211, стр. 1 (м. Ростокино)',
        '12': 'Ул. Дорожная, д. 1, корп. 1 (м. Южная)',
        '13': 'Ул. Рябиновая, д. 59 (м. Аминьевская)',
        '14': 'Ул. Дмитровское шоссе, д. 165Б (м. Физтех)',
        '17': 'Ул. Маршала Прошлякова, д. 14 (м. Строгино)',
        '18': 'Ул. 104 км МКАД, д. 6 (м. Щелковская)',
        '19': 'Ул. Шоссейная, д. 2Б (м. Печатники)',
        '49': 'П. Московский, кв-л 34, д. 3, стр. 1',
        '308': 'Ул. Складочная, д. 1, стр. 1 (м. Савеловская)',
        '356': 'Ул. 1-я Дубровская, д. 13А, стр. 1 (м. Дубровка)',
        '363': 'Ул. Боровское шоссе, д. 10А (м. Боровское шоссе)',
    }
    # Все магазины в г.Санкт-Петербург
    id_address_shop_piter = {
        '15': 'Ул. Комендантский пр-т, д. 3, лит. А (м. Комендантский пр-т)',
        '16': 'Ул. Пр-т Косыгина, д. 4, лит. А (м. Ладожская)',
        '20': 'Ул. Пулковское шоссе, д. 23, лит. A (м. Звездная)',
    }
    data = [[id_address_shop_moskov, 'г.Москва'], [id_address_shop_piter, 'г.Санкт-Петербург']]

    processes = []
    for id_address_shop, name in data:
        logger.success(f"Парсим магазины {name}")
        process = Process(target=multi_start, args=(id_address_shop, name))
        process.start()
        processes.append(process)

    for process in processes:
        process.join()

    logger.success(f"Документы готовы")
    finish_time_job = datetime.now()
    job_time = finish_time_job - start_time_job
    logger.success(f"Время работы составило {job_time}")

import pandas as pd


def list_sales_to_exel(list_orders: list):
    dict_stat = {"№ п/п": [], "Дата": [], "Кем создана": [], "Описание": [], "Контакты": [], "Статус": [], "Исполнитель": [], "Стоимость": []}
    i = 0
    for order in list_orders:
        i += 1
        dict_stat["№ п/п"].append(i)
        dict_stat["Дата"].append(order[1])
        dict_stat["Кем создана"].append(order[2])
        dict_stat["Описание"].append(order[3])
        dict_stat["Контакты"].append(order[4])
        dict_stat["Статус"].append(order[7])
        dict_stat["Исполнитель"].append(order[7])
        dict_stat["Стоимость"].append(order[9])
    df_stat = pd.DataFrame(dict_stat)
    with pd.ExcelWriter(path='./order.xlsx', engine='xlsxwriter') as writer:
        df_stat.to_excel(writer, sheet_name=f'Статистика', index=False)


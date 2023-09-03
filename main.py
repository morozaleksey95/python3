# streamlit run main.py

import pickle
from pathlib import Path
import streamlit_authenticator as stauth  # pip install streamlit-authenticator

import streamlit as st
import datetime
import httpx
import pandas as pd

from st_pages import Page, add_page_title, show_pages

st.set_page_config(page_title="-Ae_help-", page_icon=":bar_chart:", layout="wide")


def auth():
    # --- Пользователи ---
    names = ["Admin", "Admin2"]
    usernames = ["admin", "admin2"]

    # Загружаем хэш паролей
    file_path = Path(__file__).parent / "hashed_pw.pkl"
    with file_path.open("rb") as file:
        hashed_passwords = pickle.load(file)

    authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
                                        "-Ae_help-", "Ae_help", cookie_expiry_days=30)

    name, authentication_status, username = authenticator.login("Login", "main")

    return authenticator, name, authentication_status, username


def redirect_button(url: str, text: str = None, color="#FD504D"):
    st.markdown(
        f"""
    <a href="{url}" target="_blank">
        <div style="
            display: inline-block;
            padding: 0.5em 1em;
            color: #FFFFFF;
            background-color: {color};
            border-radius: 3px;
            text-decoration: none;">
            {text}
        </div>
    </a>
    """,
        unsafe_allow_html=True
    )


def get_orders(start_date, stop_date):
    try:
        url = 'http://www.corp.safaripark25.ru/test/api/rest.php'
        params_for_orders = {'key': 'D7rj6KIyTvf6rhfXbbBU02AjSXYshVykmQFCRlAb',
                             'username': 'admin',
                             'password': '241717',
                             'action': 'select',  # Метод
                             'entity_id': 28,  # раздел
                             'select_fields': '242,247,275,270,271,272,273,285,286,293,294,346,394,395,396,397,398,399,400,401,480,481',
                             'limit': 0,
                             'filters[242]': str(start_date) + ',' + str(stop_date),

                             }
        r = httpx.post(url, data=params_for_orders)
        r = r.json()
        print(r)
        return r['data']
    except:
        return 0


def get_products(id):
    # параметры для запроса
    try:
        url = 'http://www.corp.safaripark25.ru/test/api/rest.php'
        params_for_products = {'key': 'D7rj6KIyTvf6rhfXbbBU02AjSXYshVykmQFCRlAb',
                               'username': 'admin',
                               'password': '241717',
                               'action': 'select',  # метод - выборка
                               'entity_id': 29,  # сущность
                               'select_fields': '254,255,260,263,515',  # поля выборки
                               'limit': 0,  # при 0 получим все записи
                               # фильтрация
                               'parent_item_id': id,  # указать по какому заказу запрос

                               }

        r = httpx.post(url, data=params_for_products)
        r = r.json()
        return r['data']
    except:
        return 0


def find_order_tel(tel_find):
    # параметры для запроса
    try:
        url = 'http://www.corp.safaripark25.ru/test/api/rest.php'
        params_for_orders = {'key': 'D7rj6KIyTvf6rhfXbbBU02AjSXYshVykmQFCRlAb',
                             'username': 'admin',
                             'password': '241717',
                             'action': 'select',  # Метод
                             'entity_id': 28,  # раздел
                             'select_fields': '242,247,275,270,271,272,273,285,286,293,294,346,394,395,396,397,398,399,400,401,480,481',
                             'limit': 0,
                             'filters[270]': tel_find

                             }
        r = httpx.post(url, data=params_for_orders)
        r = r.json()
        return r['data']

    except:
        return 0


def main():
    authenticator, name, authentication_status, username = auth()
    if authentication_status == False:
        st.error("Неверный логин или пароль")
    if authentication_status == None:
        st.warning("Войдите в приложение")

    if authentication_status:
        nav = st.sidebar.container()
        nav.info('-Ae_help-')
        page = nav.selectbox(
            'Выбрать раздел',
            ('Статистика', 'Заявки', 'Калькулятор'))
        authenticator.logout("Выйти", "sidebar")

        container = st.container()
        if page == 'Статистика':
            container.info('Статистика')
            start_date = st.date_input("от ", datetime.datetime.now())
            stop_date = st.date_input("до ", datetime.datetime.now())
            if st.button("Просмотреть"):
                orders = get_orders(start_date, stop_date)
                if orders != [] or orders != 0:
                    df = pd.DataFrame([], columns=['Дата',
                                                   'Тип',
                                                   'Адрес',
                                                   'Доставка',
                                                    'Сумма',
                                                   'Доход',
                                                   '%',
                                                   ], dtype=object)
                    for row in orders:
                        index = len(df.index) + 1
                        df.loc[index, 'Дата'] = row['242']
                        df.loc[index, 'Тип'] = row['294']
                        df.loc[index, 'Адрес'] = row['271']
                        df.loc[index, 'Доставка'] = row['285']
                        df.loc[index, 'Сумма'] = row['286']
                        df.loc[index, 'Доход'] = row['346']
                        df.loc[index, '%'] = row['394']

                    st.dataframe(df)

                    df['Доход'] = df['Доход'].map(lambda x: x.lstrip('+-').rstrip(' ₽'))
                    df['Доход'] = df['Доход'].astype(float)


                    df['Сумма'] = df['Сумма'].map(lambda x: x.lstrip('+-').rstrip(' ₽'))
                    df['Сумма'] = df['Сумма'].astype(int)


                    st.metric(label='В кассе', value=df['Сумма'].sum(), delta='₽')
                    st.metric(label='Чистыми', value=df['Доход'].sum(), delta='₽')




        elif page == 'Заявки':
            container.info('История заявок')
            start_date = st.date_input("от ", datetime.datetime.now())
            stop_date = st.date_input("до ", datetime.datetime.now())
            with st.expander("Фильтры"):
                type = st.multiselect(
                    'Тип заявки:',
                    ['Доставка', 'Самовывоз', 'Покупка', ],
                    ['Доставка', 'Самовывоз', 'Покупка', ])
                status = st.multiselect(
                    'Заказчик',
                    ['Положительный', 'Нежелательный', 'VIP', 'Представитель организации'],
                    ['Положительный', 'Нежелательный', 'VIP', 'Представитель организации'])
                number = st.number_input('Номер телефона', value=9)

            if st.button("Выполнить запрос"):

                if len(str(number)) > 1:
                    orders = find_order_tel(number)
                else:
                    orders = get_orders(start_date, stop_date)
                if orders != [] or orders != 0:

                    for row in orders:
                        if type.count(row['294']):  # если фильтра по типу заказа
                            if status.count(row['480']):  # если фильтр по статусу клиента
                                tab1, tab2, = st.tabs(["Заявка", "Товары", ])
                                with tab1:
                                    st.write(row['294'], row['242'])
                                    st.write('Заказчик: ', row['396'], '(', row['395'][0:1], ')')

                                    if row['270'] != '':  # если телефон не пуст
                                        tel = row['247'] + ' +7' + row['270']
                                        url = 'https://api.whatsapp.com/send?phone=7' + row['270']
                                        redirect_button(url, tel)

                                        if row['294'] == 'Доставка':
                                            st.write('Доставили по адресу: ', row['271'], '(', row['285'], ')')

                                        st.write('Повод: ', row['399'], row['400'], '(', row['401'], ')')
                                        st.write('Кому подарок: ', row['398'], '(', row['397'], ')')

                                        st.write('Клиент:', row['480'], ' - ', row['481'])
                                        pay = 'Оплачено ' + row['275']
                                        st.metric(label=pay, value=row['286'], delta=row['394'])

                                    with tab2:
                                        df = pd.DataFrame([], columns=['Товар',
                                                                       'Цена',
                                                                       'Кол-во',
                                                                       'Сумма',
                                                                       '%',
                                                                       ], dtype=object)

                                        products = get_products(row['id'])

                                        for row in products:
                                            index = len(df.index) + 1
                                            df.loc[index, 'Товар'] = row['254']
                                            df.loc[index, 'Цена'] = row['255']
                                            df.loc[index, 'Кол-во'] = row['260']
                                            df.loc[index, 'Сумма'] = row['263']
                                            df.loc[index, '%'] = row['515']

                                        st.dataframe(df)

                                    st.divider()

                st.toast('Это все заказы')

        if page == 'Калькулятор':
            balloon_volume = st.number_input('Вместимость балона', value=5700, step=100)
            hellium = st.number_input('Цена баллона 40 л.', value=28000, step=1000)
            ballon = st.number_input('Закупочная цена шара ₽', value=100, step=50)
            size = st.number_input('Вместимость шара в м*3', value=15, step=5)
            price = st.number_input('Цена продажи в ₽', value=500, step=50)
            if st.button("Расчитать"):
                price_of_1 = int(hellium) / balloon_volume
                sebestoimost = int(ballon) +  price_of_1 * size
                dohod = price - sebestoimost
                procent = dohod / price * 100

                st.write('Себестоимость шара ', int(sebestoimost), '₽')
                st.write('Чистый доход  ', int(dohod), '₽')
                st.write('С ', price, '₽ вы получите',  int(procent), '% чистой прибыли')




main()

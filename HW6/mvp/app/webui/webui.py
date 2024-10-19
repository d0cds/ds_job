import streamlit as st
import requests
import extra_streamlit_components as stx
from datetime import datetime, timedelta
from auth.jwt_handler import decode_access_token
import time

# Основной адрес API
API_URL = "http://app:8080"

# Функция для работы с куками
@st.cache_resource(experimental_allow_widgets=True)
def get_cookie_manager():
    return stx.CookieManager()

# Инициализация cookie_manager
cookie_manager = get_cookie_manager()

def set_token(token):
    cookie_manager.set("token", token, expires_at=datetime.now() + timedelta(minutes=30))

def get_token():
    return cookie_manager.get("token")

def remove_token():
    cookie_manager.delete("token")

# Инициализация session_state
def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Главная"
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

# Функция для выполнения запросов к API с токеном
def api_request(method, endpoint, data=None):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    url = f"{API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")
        
        response.raise_for_status()  # Вызовет исключение 
        return response
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("Сессия истекла. Пожалуйста, войдите снова.")
            remove_token()
            st.session_state.logged_in = False
            st.session_state.current_page = "Вход"
            st.rerun()
        else:
            st.error(f"Ошибка API: {e}")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка запроса: {e}")
        return None


# Страница входа в систему
def login_page():
    st.title("Вход в систему")
    username = st.text_input("Имя пользователя", key="login_username")
    password = st.text_input("Пароль", type="password", key="login_password")
    login_button = st.button("Войти")
    if login_button:
        response = api_request("POST", "/user/login", {"username": username, "password": password})
        if response and response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user_id = data.get("user_id")
            username = data.get("username")
            set_token(token)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_id = user_id
            st.session_state.current_page = "Личный кабинет"
            st.success("Вход выполнен успешно")
            st.rerun()
        else:
            st.error("Ошибка входа")



# Страница регистрации
def register_page():
    st.title("Регистрация")
    username = st.text_input("Имя пользователя", key="register_username")
    password = st.text_input("Пароль", type="password", key="register_password")
    register_button = st.button("Зарегистрироваться")

    if register_button:
        response = api_request("POST", "/user/register", {"username": username, "password": password})
        if response and response.status_code == 200:
            st.success("Регистрация выполнена успешно")
            st.session_state.current_page = login_page
            st.session_state.logged_in = False
            st.rerun()
        else:
            st.error("Ошибка регистрации")
    

# личный кабинет
def dashboard_page():
    #st.title("Личный кабинет")
    if not st.session_state.logged_in or not st.session_state.user_id:
        st.error("Необходимо войти систему")
        st.session_state.current_page = register_page
        st.rerun()
        return

    st.write("# Прогноз зарплаты на основании Ваших навыков")
    st.write(f"### Добро пожаловать, {st.session_state.username}!")

    # Отображение текущего баланса
    response = api_request("GET", f"/balance/{st.session_state.user_id}")
    if response and response.status_code == 200:
        balance = response.json().get("balance")
        st.write(f"Ваш текущий баланс: {balance} койнов")
    else:
        st.error("Ошибка получения текущего баланса")

    # Создание колонок
    col11, col22 = st.columns(2)
    # Заполнение первой колонки
    with col11:
        job_type = st.selectbox("Выберите направление специализации:",
                                ("Аналитик данных", "Инженер по обработке данных",
                                "ML инженер", "Администратор БД", "BI-аналитик")
                                )
    with col22:
        location_type = st.selectbox("Выберите регион:",
                                        ('Любой', 'Алтайский край', 'Амурская область', 'Архангельская область', 'Астраханская область', 'Белгородская область', 'Брянская область',
                                        'Владимирская область', 'Волгоградская область', 'Вологодская область', 'Воронежская область', 'Город Севастополь', 'Донецкая Народная Республика',
                                        'Еврейская автономная область', 'Забайкальский край', 'Запорожская область', 'Ивановская область', 'Иркутская область', 'Кабардино-Балкарская Республика',
                                        'Калининградская область', 'Калужская область', 'Камчатский край', 'Карачаево-Черкесская Республика', 'Кемеровская область - Кузбасс',
                                        'Кировская область', 'Костромская область', 'Краснодарский край', 'Красноярский край', 'Курганская область', 'Курская область', 'Ленинградская область',
                                        'Липецкая область',  'Луганская Народная Республика', 'Магаданская область', 'Москва', 'Московская область', 'Мурманская область',
                                        'Ненецкий автономный округ', 'Нижегородская область', 'Новгородская область', 'Новосибирская область', 'Омская область', 'Оренбургская область',
                                        'Орловская область',  'Пензенская область', 'Пермский край', 'Приморский край', 'Псковская область', 'Республика Адыгея (Адыгея)',
                                        'Республика Алтай', 'Республика Башкортостан', 'Республика Бурятия', 'Республика Дагестан', 'Республика Ингушетия', 'Республика Калмыкия',
                                        'Республика Карелия', 'Республика Коми', 'Республика Крым', 'Республика Марий Эл',
                                        'Республика Мордовия', 'Республика Саха (Якутия)', 'Республика Северная Осетия - Алания', 'Республика Татарстан (Татарстан)',
                                        'Республика Тыва', 'Республика Хакасия', 'Ростовская область', 'Рязанская область', 'Самарская область', 'Санкт-Петербург',
                                        'Саратовская область', 'Сахалинская область', 'Свердловская область', 'Смоленская область', 'Ставропольский край', 'Тамбовская область',
                                        'Тверская область', 'Томская область', 'Тульская область', 'Тюменская область', 'Удмуртская Республика', 'Ульяновская область',
                                        'Хабаровский край', 'Ханты-Мансийский автономный округ - Югра', 'Херсонская область', 'Челябинская область', 'Чеченская Республика',
                                        'Чувашская Республика - Чувашия', 'Чукотский автономный округ', 'Ямало-Ненецкий автономный округ', 'Ярославская область')
                                        )
    # Создание колонок
    col1, col2 = st.columns(2)
    # Заполнение первой колонки
    with col1:
        #st.subheader("Выберите уровень квалификации:")
        qual_type = st.selectbox("Выберите уровень квалификаци:",
                                 ("Junior", "Middle", "Senior")
                                )
    # Заполнение второй колонки
    with col2:
        # Выбор типа занятости
        #st.subheader("Выберите тип занятости:")
        employment_type = st.selectbox("Выберите тип занятости:",
                                        ("Full-time", "Remote", "Temporary", "Part-time")
                                        )
    
    #st.header("Навыки")
    skills = st.text_input("Введите ваши навыки (через запятую):")
    st.write(f"Ваши навыки: {skills}")
    input_data = {'name_job':job_type,
                  'type_busy':employment_type, 
                  'qualification': qual_type,
                  'location':location_type, 
                  'skills':skills}
    # Отправка данных для предсказания
    #st.subheader("Запрос предсказания")
    if st.button("Предсказать"):
        response = api_request("POST", "/prediction",
                               {"input_data": input_data})
        if response and response.status_code == 200:
            with st.spinner("Ожидайте"):
                time.sleep(5)
                c = 0
                while c<1:
                    response = api_request("GET", "/history/")
                    if response and response.status_code == 200:
                            history = response.json()
                            if history:
                                st.write(f" ## Ваша прогнозируемая зарплата: {history.get('output_data', 'Нет данных')}")
                                break                        
                            else:
                                c=+1


# Главная страница
def main_page():
    st.title('''Вас приветсвует "Зарплатный компас"
                    ''')
    st.write("""
    Прежде чем воспользоваться функционалом сервиса:
    - Пройдите регистрацию
    - Войдите в систему и получите доступ к прогнозированию зарплаты.
    """)

# Основной поток работы приложения
def main():
    initialize_session_state()
    
    st.sidebar.title("Меню")
    token = get_token()
    
    if token:
        try:
            decoded_token = decode_access_token(token)
            if decoded_token:
                st.session_state.logged_in = True
                st.session_state.username = decoded_token.get("sub_name")
                st.session_state.user_id = decoded_token.get("sub_id")
                st.sidebar.write(f"Приветсвую, {st.session_state.username}!")
            else:
                raise ValueError("Invalid token")
        except Exception as e:
            st.error(f"Ошибка проверки токена: {e}")
            st.session_state.logged_in = False
            remove_token()
    else:
        st.session_state.logged_in = False

    # Настраиваем навигацию в зависимости от статуса входа
    if st.session_state.logged_in:
        pages = {
            "Главная": main_page,
            "Личный кабинет": dashboard_page,
        }
        
        if st.sidebar.button("Выйти", key="logout_button"):
            remove_token()
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_id = None
            st.session_state.current_page = "Главная"
            st.rerun()
    else:
        pages = {"Главная": main_page, "Вход": login_page, "Регистрация": register_page}

    # Обновляем навигацию в боковой панели
    page = st.sidebar.radio("Перейти к", list(pages.keys()), key="navigation")
    
    if page != st.session_state.current_page:
        st.session_state.current_page = page

    # Отображаем текущую страницу
    if st.session_state.current_page in pages:
        pages[st.session_state.current_page]()
    else:
        st.error(f"Ошибка: страница '{st.session_state.current_page}' не найдена")
        main_page()

    # Проверяем, нужно ли перезагрузить страницу
    if st.session_state.current_page != page:
        st.rerun()

if __name__ == "__main__":
    main()
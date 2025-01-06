from sklearn.cluster import KMeans
import numpy as np

#это неправильное ML
def train_model(session, user_id, habit_id):
    times = session.query(func.extract('hour', Execution.execution_time))\
        .filter(Execution.user_id == user_id, Execution.habit_id == habit_id).all()
    times = np.array(times).reshape(-1, 1)

    model = KMeans(n_clusters=1)
    model.fit(times)
    return model

def predict_time(model):
    return model.cluster_centers_[0][0]


from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import numpy as np


# Функция для извлечения времени выполнения привычки
def extract_time_features(events):
    time_features = []
    for event in events:
        execution_time = event.execution_time
        # Преобразуем datetime в число секунд с начала дня
        seconds_since_midnight = (
                    execution_time - execution_time.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        time_features.append(seconds_since_midnight)
    return np.array(time_features).reshape(-1, 1)


# Функция для предсказания времени напоминания с использованием машинного обучения
def predict_reminder_time_using_ml(session, habit_id):
    event_dao = EventDAO(session)
    events = event_dao.get_events_for_habit(habit_id)

    if not events:
        return "Нет данных о выполнении привычки."

    # Собираем данные
    X = extract_time_features(events)

    # Обучаем модель
    model = LinearRegression()
    model.fit(X, X)  # Для упрощения обучаем на тех же данных, можно модифицировать

    # Предсказанное время (например, на 30 минут позже времени выполнения)
    predicted_seconds = model.predict(np.array([[X[-1][0] + 30 * 60]]))  # Предсказание на 30 минут вперед

    # Преобразуем секунды обратно в формат времени
    predicted_time = datetime(1, 1, 1) + timedelta(seconds=predicted_seconds[0][0])
    return predicted_time.time().strftime("%H:%M")


# Пример использования
habit_id = 1  # ID привычки
reminder_time = predict_reminder_time_using_ml(session, habit_id)
print(f"Время напоминания: {reminder_time}")

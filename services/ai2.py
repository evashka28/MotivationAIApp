from datetime import datetime, time
from typing import List
from core.db import Session
import numpy as np
from sklearn.cluster import KMeans

from dao.event_dao import EventDAO

#вот это правильное ML

def get_event_hours(events: List["Event"]) -> np.ndarray:
    """
    Функция извлекает из списка Event часы (с учетом минут),
    чтобы затем использовать их в алгоритмах машинного обучения.
    Например, 09:30 = 9.5, 16:15 = 16.25 и т.д.
    """
    #print(events)
    hours = []
    for e in events:
        dt = e.execution_time  # это datetime
        hour_float = dt.hour + dt.minute / 60.0
        hours.append(hour_float)
    return np.array(hours).reshape(-1, 1)


def find_best_notification_time(events: List["Event"], n_clusters: int = 3) -> time:
    """
    Функция, которая находит "лучшее время" уведомления на основе исторических данных.
    1. Собирает у событий (Event) часы выполнения привычки.
    2. Делает кластеризацию (KMeans) по часам выполнения.
    3. Определяет, какой кластер самый большой.
    4. Возвращает время (час:минуты) из центра этого кластера.

    :param events: список событий для одной привычки.
    :param n_clusters: количество кластеров (регулируется экспериментально).
    :return: объекты time (час:минуты) — ориентировочное "лучшее время" уведомления.
    """

    if not events:
        # Если нет исторических данных, просто возвращаем None или какое-то дефолтное значение
        return None

    # Преобразуем времена выполнения в числовой формат
    X = get_event_hours(events)

    # Обучаем KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(X)

    # Определим метки (к какому кластеру принадлежит каждая точка) и посчитаем размер каждого кластера
    labels = kmeans.labels_
    unique_labels, counts = np.unique(labels, return_counts=True)

    # Находим самый большой кластер
    max_label = unique_labels[np.argmax(counts)]

    # Центр самого крупного кластера (по сути, "среднее" в этом кластере)
    best_cluster_center = kmeans.cluster_centers_[max_label][0]

    # Преобразуем число вида 9.5 обратно в часы и минуты
    best_hour = int(best_cluster_center)  # целая часть — часы
    best_minute = int(round((best_cluster_center - best_hour) * 60))  # дробная часть * 60 — минуты

    # Валидация границ (на всякий случай)
    best_hour = max(0, min(23, best_hour))
    best_minute = max(0, min(59, best_minute))

    return time(hour=best_hour, minute=best_minute)


def predict_notification_time_for_habit(event_dao: "EventDAO", habit_id: int) -> time:
    """
    Функция, которая берёт из DAO все события по одной привычке,
    а затем вычисляет "лучшее время" с помощью find_best_notification_time.
    """
    # Получаем все события для данной привычки
    events = event_dao.get_by_habit_id(habit_id)
    print(events)

    # Находим оптимальное время
    best_time = find_best_notification_time(events, n_clusters=3)
    return best_time


if __name__ == "__main__":
    """
    Пример использования. Предположим, что у вас уже есть созданный session SQLAlchemy
    и соответствующий EventDAO.
    """
    # from your_database import SessionLocal
    session = Session()
    event_dao = EventDAO(session)

    habit_id = 1  # некий id привычки
    best_time = predict_notification_time_for_habit(event_dao, habit_id)
    print("Лучшее время для уведомления:", best_time)
    pass

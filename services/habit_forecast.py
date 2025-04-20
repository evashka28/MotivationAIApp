import pandas as pd
from datetime import date, timedelta
from sqlalchemy.orm import Session
from prophet import Prophet
from models import Event, Habit
from services.giga_client import GigaChatClient


class HabitTimeSeriesBuilder:
    def __init__(self, session: Session):
        self.session = session

    def get_event_dates(self, habit_id: int, start_date: date, end_date: date) -> pd.DataFrame:
        """Получает даты выполнения привычки"""
        events = self.session.query(Event).filter(
            Event.habit_id == habit_id,
            Event.execution_time >= start_date,
            Event.execution_time <= end_date
        ).all()

        return pd.DataFrame({
            'ds': [e.execution_time.date() for e in events]
        })

    def build_time_series(self, habit_id: int, start_date: date = None, end_date: date = None) -> pd.DataFrame:
        """Создаёт бинарный временной ряд для Prophet"""
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=90)

        full_dates = pd.DataFrame({
            'ds': pd.date_range(start=start_date, end=end_date)
        })

        events_df = self.get_event_dates(habit_id, start_date, end_date)

        full_dates['y'] = full_dates['ds'].isin(events_df['ds']).astype(int)

        return full_dates


class HabitFailurePredictor:
    def __init__(self):
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False
        )

    def fit(self, df: pd.DataFrame):
        self.model.fit(df)

    def predict(self, days_ahead: int = 7) -> pd.DataFrame:
        future = self.model.make_future_dataframe(periods=days_ahead)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


class HabitForecastService:
    def __init__(self, session: Session, decline_threshold: float = 0.3, client_id: str = None, client_secret: str = None):
        print(f"[DEBUG] client_id={client_id}, client_secret={client_secret}")
        self.session = session
        self.builder = HabitTimeSeriesBuilder(session)
        self.predictor = HabitFailurePredictor()
        self.decline_threshold = decline_threshold
        if client_id and client_secret:
            print("[DEBUG] Creating GigaChatClient with:", client_id, client_secret)
            self.giga = GigaChatClient(client_id, client_secret)
        else:
            print("[DEBUG] GigaChatClient not created (no credentials)")
            self.giga = None

    def get_habit_info(self, habit_id: int):
        habit = self.session.query(Habit).filter(Habit.id == habit_id).first()
        return habit.create_at, habit.repeat  # created_at должен быть datetime/date

    def get_grace_period_days(self, repeat: str) -> int:
        grace_mapping = {
            "1 раз в день": 7,
            "2 раза в день": 7,
            "1 раз в неделю": 21,
            "2 раза в неделю": 14,
            "3 раза в неделю": 14,
            "1 раз в месяц": 60
        }
        return grace_mapping.get(repeat, 14)  # По умолчанию 14 дней

    def is_habit_declining(self, habit_id: int, days_ahead: int = 7) -> bool:
        create_at, repeat = self.get_habit_info(habit_id)
        days_since_creation = (date.today() - create_at.date()).days
        grace_period = self.get_grace_period_days(repeat)

        print(f"Привычка создана {create_at}, повтор: {repeat}, прошло дней: {days_since_creation}, grace: {grace_period}")
        if days_since_creation < grace_period:
            print("Привычка слишком новая, прогноз не выполняется.")
            return False

        ts_df = self.builder.build_time_series(habit_id)
        print("Построен временной ряд")
        print(ts_df.tail(10))

        if ts_df['y'].sum() == 0:
            return True

        self.predictor.fit(ts_df)
        forecast = self.predictor.predict(days_ahead)
        mean_future_yhat = forecast.tail(days_ahead)['yhat'].mean()

        print(f"Среднее yhat: {mean_future_yhat}")
        return mean_future_yhat < self.decline_threshold

    def generate_alternatives(self, habit_id: int) -> list[str]:
        if not self.giga:
            return []

        habit = self.session.query(Habit).filter(Habit.id == habit_id).first()
        if not habit:
            return []

        print(f"Habit: id={habit.id}, name={habit.name}, description={habit.description}")
        print("Calling GigaChatClient for:", habit.name)
        return self.giga.generate_alternative_habits(habit.name, habit.description)


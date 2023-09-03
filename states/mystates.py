from telebot.handler_backends import State, StatesGroup

class MyStates(StatesGroup):
    start = State()
    history = State()
    city = State()
    destination = State()
    arrival_date = State()
    departure_date = State()
    amount_hotels = State()
    photo = State()
    amount_photo = State()
    done = State()





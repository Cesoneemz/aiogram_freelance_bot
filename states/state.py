from aiogram.dispatcher.filters.state import State, StatesGroup


class IdOrURl(StatesGroup):
    wait_for_id_or_url = State()


class LoadCsv(StatesGroup):
    wait_for_csv = State()


class SetMaxRequestPerDay(StatesGroup):
    wait_for_request_int = State()


class EditSystemMessages(StatesGroup):
    wait_for_id = State()
    wait_fot_new_message = State()

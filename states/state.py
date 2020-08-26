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


class AddAdmin(StatesGroup):
    wait_for_admin_id = State()


class DeleteAdmin(StatesGroup):
    wait_for_admin_id_delete = State()

class SetNewCountRequestToUser(StatesGroup):
    wait_for_username = State()
    wait_for_count = State()


class Mailing(StatesGroup):
    wait_for_text = State()


class ClearDatabase(StatesGroup):
    yesno_prompt = State()


class SetNewRowsCount(StatesGroup):
    wait_for_count = State()

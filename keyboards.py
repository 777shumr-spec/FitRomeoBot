from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard(has_access: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔐 Запросити доступ", callback_data="request_access")

    if has_access:
        builder.button(text="💪 Мої групи", callback_data="my_groups")

    builder.adjust(1)
    return builder.as_markup()


def groups_keyboard(groups: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for group in groups:
        group_id = str(group.get("group_id", ""))
        group_name = str(group.get("group_name", "Без назви"))
        builder.button(
            text=group_name,
            callback_data=f"group:{group_id}"
        )

    builder.button(text="⬅️ Назад", callback_data="back_to_start")
    builder.adjust(1)
    return builder.as_markup()


def subgroups_keyboard(group_id: str, subgroups: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for subgroup in subgroups:
        subgroup_id = str(subgroup.get("subgroup_id", ""))
        subgroup_name = str(subgroup.get("subgroup_name", "Без назви"))
        builder.button(
            text=subgroup_name,
            callback_data=f"subgroup:{group_id}:{subgroup_id}"
        )

    builder.button(text="⬅️ До груп", callback_data="my_groups")
    builder.adjust(1)
    return builder.as_markup()


def videos_keyboard(group_id: str, subgroup_id: str, videos: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for video in videos:
        video_id = str(video.get("video_id", ""))
        title = str(video.get("video_title", "Відео"))
        builder.button(
            text=title,
            callback_data=f"video:{group_id}:{subgroup_id}:{video_id}"
        )

    builder.button(text="⬅️ До вправ", callback_data=f"back_to_group:{group_id}")
    builder.adjust(1)
    return builder.as_markup()


def video_action_keyboard(group_id: str, subgroup_id: str, video_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Переглянув",
        callback_data=f"watched:{group_id}:{subgroup_id}:{video_id}"
    )
    builder.button(
        text="🏁 Виконав",
        callback_data=f"done:{group_id}:{subgroup_id}:{video_id}"
    )
    builder.adjust(1)
    return builder.as_markup()

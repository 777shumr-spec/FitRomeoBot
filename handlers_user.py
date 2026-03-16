from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from keyboards import (
    groups_keyboard,
    start_keyboard,
    subgroups_keyboard,
    video_action_keyboard,
    videos_keyboard,
)
from sheets_api import (
    create_access_request,
    get_allowed_groups,
    get_subgroups_by_group,
    get_user_status,
    get_videos_by_subgroup,
    upsert_user,
    write_log,
)

router = Router()

WELCOME_TEXT = (
    "Вітаю тебе, якщо ти читаєш це, то ти майже обраний, "
    "і зараз тобі потрібно зробити лише маленький крок до великої перемоги!\n\n"
    "Натискай запросити доступ до цінного контенту, за допомогою якого "
    "ти точно досягнеш результату!"
)


def _has_access(status_result: dict) -> bool:
    result = status_result.get("result", {})
    return result.get("status") == "active"


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    upsert_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        first_name=message.from_user.first_name or "",
        last_name=message.from_user.last_name or "",
    )

    status_result = get_user_status(message.from_user.id)
    has_access = _has_access(status_result)

    await message.answer(
        WELCOME_TEXT,
        reply_markup=start_keyboard(has_access=has_access)
    )


@router.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery) -> None:
    status_result = get_user_status(callback.from_user.id)
    has_access = _has_access(status_result)

    await callback.message.edit_text(
        WELCOME_TEXT,
        reply_markup=start_keyboard(has_access=has_access)
    )
    await callback.answer()


@router.callback_query(F.data == "request_access")
async def cb_request_access(callback: CallbackQuery) -> None:
    upsert_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        first_name=callback.from_user.first_name or "",
        last_name=callback.from_user.last_name or "",
    )

    create_access_request(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        first_name=callback.from_user.first_name or "",
        last_name=callback.from_user.last_name or "",
    )

    await callback.message.answer(
        "✅ Запит на доступ відправлено адміну.\n"
        "Очікуй підтвердження."
    )
    await callback.answer("Запит відправлено")


@router.callback_query(F.data == "my_groups")
async def cb_my_groups(callback: CallbackQuery) -> None:
    result = get_allowed_groups(callback.from_user.id).get("result", {})
    status = result.get("status")
    groups = result.get("groups", [])

    if status != "active":
        await callback.answer("У тебе ще немає активного доступу", show_alert=True)
        return

    if not groups:
        await callback.answer("Немає доступних груп", show_alert=True)
        return

    await callback.message.edit_text(
        "💪 Обери групу м'язів:",
        reply_markup=groups_keyboard(groups)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("group:"))
async def cb_group(callback: CallbackQuery) -> None:
    _, group_id = callback.data.split(":", 1)

    subgroups = get_subgroups_by_group(group_id).get("items", [])

    if not subgroups:
        await callback.answer("У цій групі поки немає вправ", show_alert=True)
        return

    await callback.message.edit_text(
        "Оберіть підгрупу:",
        reply_markup=subgroups_keyboard(group_id, subgroups)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back_to_group:"))
async def cb_back_to_group(callback: CallbackQuery) -> None:
    _, group_id = callback.data.split(":", 1)

    subgroups = get_subgroups_by_group(group_id).get("items", [])

    if not subgroups:
        await callback.answer("У цій групі поки немає вправ", show_alert=True)
        return

    await callback.message.edit_text(
        "Оберіть підгрупу:",
        reply_markup=subgroups_keyboard(group_id, subgroups)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("subgroup:"))
async def cb_subgroup(callback: CallbackQuery) -> None:
    _, group_id, subgroup_id = callback.data.split(":", 2)

    videos = get_videos_by_subgroup(subgroup_id).get("items", [])

    if not videos:
        await callback.answer("У цій підгрупі поки немає відео", show_alert=True)
        return

    await callback.message.edit_text(
        "🎬 Обери відео:",
        reply_markup=videos_keyboard(group_id, subgroup_id, videos)
    )
    await callback.answer()

@router.message(F.video)
async def debug_video_file_id(message: Message) -> None:
    if message.chat.id != -5122927435:
        return

    file_id = message.video.file_id
    await message.answer(f"VIDEO_FILE_ID:\n{file_id}")


@router.callback_query(F.data.startswith("video:"))
async def cb_video(callback: CallbackQuery) -> None:
    _, group_id, subgroup_id, video_id = callback.data.split(":", 3)

    videos = get_videos_by_subgroup(subgroup_id).get("items", [])
    video = next((v for v in videos if str(v.get("video_id")) == str(video_id)), None)

    if not video:
        await callback.answer("Відео не знайдено", show_alert=True)
        return

    file_id = str(video.get("telegram_file_id", "")).strip()
    title = str(video.get("video_title", "Відео")).strip()
    description = str(video.get("description", "")).strip()

    if not file_id:
        await callback.answer("У відео відсутній file_id", show_alert=True)
        return

    caption_parts = [f"🎬 {title}"]
    if description:
        caption_parts.append(description)

    await callback.message.answer_video(
        video=file_id,
        caption="\n\n".join(caption_parts),
        protect_content=True,
        reply_markup=video_action_keyboard(group_id, subgroup_id, video_id)
    )

    write_log(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        group_id=group_id,
        subgroup_id=subgroup_id,
        video_id=video_id,
        action="opened"
    )

    await callback.answer()

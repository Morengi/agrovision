import asyncio
import base64
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.crud import content_item as content_item_crud
from app.crud import content_item_image as image_crud
from app.crud import course as course_crud
from app.crud import photocase as photocase_crud
from app.crud import tag as tag_crud
from app.crud import topic as topic_crud
from app.crud import user as user_crud
from app.db.base import async_session_maker
from app.models.content_item import ContentItemType
from app.models.user import UserRole

settings = get_settings()

SEED_USERS = [
    {
        "email": "admin@agrovision.ru",
        "password": settings.seed_admin_password,
        "full_name": "Админ Платформы",
        "role": UserRole.admin,
    },
    {
        "email": "moderator@agrovision.ru",
        "password": settings.seed_moderator_password,
        "full_name": "Модератор Курсов",
        "role": UserRole.moderator,
    },
    {
        "email": "student@agrovision.ru",
        "password": settings.seed_student_password,
        "full_name": "Студент Тестовый",
        "role": UserRole.student,
    },
]

# A tiny valid solid-colour JPEG, reused as a stand-in for real field photos —
# real course content gets uploaded through the admin panel.
_PLACEHOLDER_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgICAgMCAgIDAwMDBAYEBAQEBAgGBgUGCQgKCgkICQkKDA8MCgsOCwkJDRENDg8QEBEQ"
    "CgwSExIQEw8QEBD/2wBDAQMDAwQDBAgEBAgQCwkLEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQ"
    "EBD/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAj/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAA"
    "AAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCdABmX/9k="
)


async def _save_placeholder_image(subdir: str) -> str:
    target_dir = Path(settings.media_root) / "images" / subdir
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4()}.jpg"
    (target_dir / filename).write_bytes(base64.b64decode(_PLACEHOLDER_JPEG_B64))
    return f"/media/images/{subdir}/{filename}"


async def seed() -> None:
    async with async_session_maker() as db:
        users_by_email = {}
        for entry in SEED_USERS:
            existing = await user_crud.get_by_email(db, entry["email"])
            if existing is not None:
                print(f"[seed] {entry['email']} already exists, skipping")
                users_by_email[entry["email"]] = existing
                continue
            user = await user_crud.create_user(
                db,
                email=entry["email"],
                password=entry["password"],
                full_name=entry["full_name"],
                role=entry["role"],
            )
            users_by_email[entry["email"]] = user
            print(f"[seed] created {entry['role'].value}: {entry['email']} / {entry['password']}")

        admin = users_by_email["admin@agrovision.ru"]

        existing_course = await course_crud.get_by_slug(db, "diagnostika-bolezney-tomata")
        if existing_course is not None:
            print("[seed] demo course already exists, skipping")
            return

        tomato_tag = await tag_crud.create_tag(db, "Томат")
        disease_tag = await tag_crud.create_tag(db, "Болезнь")
        nutrition_tag = await tag_crud.create_tag(db, "Дефицит питания")

        course = await course_crud.create_course(
            db,
            title="Диагностика болезней томата",
            description="Учимся распознавать типичные проблемы томата по фото: на какие признаки смотреть, "
            "как отличить похожие симптомы друг от друга и что делать дальше для уточнения диагноза.",
            price=0,
            tag_ids=[tomato_tag.id, disease_tag.id],
            created_by=admin.id,
        )
        await course_crud.update_course(db, course, is_published=True)

        topic1 = await topic_crud.create_topic(
            db,
            course_id=course.id,
            title="Признаки фитофтороза",
            description="Как отличить фитофтороз от других проблем",
            order_index=None,
        )
        lecture1 = await content_item_crud.create_content_item(
            db,
            topic_id=topic1.id,
            type=ContentItemType.text_lecture,
            title="Как распознать фитофтороз",
            order_index=None,
            text_body=(
                "Фитофтороз обычно начинается с нижних листьев и распространяется вверх по растению.\n\n"
                "Ключевые признаки: бурые пятна неправильной формы с более светлым влажным налётом по краю "
                "(особенно заметен утром или после дождя), быстрое потемнение и усыхание листа целиком.\n\n"
                "Типичная ошибка — спутать фитофтороз с обычным увяданием от жары: при увядании пятен и налёта "
                "нет, лист просто теряет тургор и восстанавливается к вечеру."
            ),
        )
        for _ in range(3):
            path = await _save_placeholder_image(str(lecture1.id))
            await image_crud.add_image(db, content_item_id=lecture1.id, image_path=path)

        case1 = await content_item_crud.create_content_item(
            db,
            topic_id=topic1.id,
            type=ContentItemType.photocase,
            title="Определите проблему по фото",
            order_index=None,
            text_body=None,
        )
        for _ in range(3):
            path = await _save_placeholder_image(str(case1.id))
            await image_crud.add_image(db, content_item_id=case1.id, image_path=path)
        await content_item_crud.update_content_item(
            db,
            case1,
            key_signs="Бурые пятна неправильной формы со светлым влажным налётом по краю, начинаются с нижних "
            "листьев и распространяются вверх.",
            next_steps="Проверить влажность и вентиляцию в теплице, осмотреть соседние растения на предмет "
            "распространения, при подтверждении — обработать фунгицидом и удалить поражённые листья.",
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case1.id,
            label="Фитофтороз",
            is_correct=True,
            explanation="Верно! Форма пятен, влажный налёт по краю и распространение снизу вверх — классический фитофтороз.",
            order_index=None,
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case1.id,
            label="Дефицит калия",
            is_correct=False,
            explanation="Не совсем — дефицит калия даёт равномерный краевой ожог листа без влажного налёта.",
            order_index=None,
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case1.id,
            label="Бактериальная пятнистость",
            is_correct=False,
            explanation="Не совсем — бактериальная пятнистость даёт мелкие водянистые пятна без светлого налёта по краю.",
            order_index=None,
        )

        topic2 = await topic_crud.create_topic(
            db,
            course_id=course.id,
            title="Дефицит азота",
            description="Признаки азотного голодания томата",
            order_index=None,
        )
        lecture2 = await content_item_crud.create_content_item(
            db,
            topic_id=topic2.id,
            type=ContentItemType.text_lecture,
            title="Признаки дефицита азота",
            order_index=None,
            text_body=(
                "Нижние листья желтеют равномерно от центра к краю, черешки становятся тонкими и вытягиваются.\n\n"
                "В отличие от дефицита калия, при азотном голодании края листа не буреют — пожелтение равномерное "
                "по всей пластинке, а не только по краю."
            ),
        )
        for _ in range(3):
            path = await _save_placeholder_image(str(lecture2.id))
            await image_crud.add_image(db, content_item_id=lecture2.id, image_path=path)

        case2 = await content_item_crud.create_content_item(
            db,
            topic_id=topic2.id,
            type=ContentItemType.photocase,
            title="Определите проблему по фото",
            order_index=None,
            text_body=None,
        )
        for _ in range(3):
            path = await _save_placeholder_image(str(case2.id))
            await image_crud.add_image(db, content_item_id=case2.id, image_path=path)
        await content_item_crud.update_content_item(
            db,
            case2,
            key_signs="Равномерное пожелтение нижних листьев от центра к краю, тонкие вытянутые черешки, "
            "отставание в росте.",
            next_steps="Провести подкормку азотным удобрением, проверить pH почвы (при низком pH азот хуже "
            "усваивается), через 5-7 дней оценить динамику по новым листьям.",
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case2.id,
            label="Дефицит азота",
            is_correct=True,
            explanation="Верно! Равномерное пожелтение нижних листьев и тонкие черешки — типичное азотное голодание.",
            order_index=None,
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case2.id,
            label="Дефицит железа",
            is_correct=False,
            explanation="Не совсем — при дефиците железа желтеют в первую очередь верхние молодые листья, а жилки остаются зелёными.",
            order_index=None,
        )
        await photocase_crud.create_option(
            db,
            content_item_id=case2.id,
            label="Переувлажнение",
            is_correct=False,
            explanation="Не совсем — при переувлажнении листья желтеют вместе с признаками загнивания корней и общим увяданием.",
            order_index=None,
        )

        print(f"[seed] created demo course '{course.title}' with 2 topics, tag: {nutrition_tag.name}")


if __name__ == "__main__":
    asyncio.run(seed())

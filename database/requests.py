from database.models import async_session
from database.models import InformationAboutUser, Task

from sqlalchemy import select, update, delete


async def set_information_about_user(tg_id, data):
    async with async_session() as session:
        user = await session.scalar(select(InformationAboutUser).where(InformationAboutUser.tg_id == tg_id))

        if not user:
            session.add(InformationAboutUser(tg_id=tg_id, name=data['name'],
                                             time=data['time_to_message'], sity=data['city']))
            await session.commit()
        else:
            session.update(InformationAboutUser(tg_id=tg_id, name=data['name'],
                                                time=data['time_to_message'], sity=data['city'].capitalize()))
            await session.commit()
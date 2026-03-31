"""Seed sample herb data for development."""
import asyncio

from sqlalchemy import select

from app.database import async_session_factory, engine, Base
from app.models.herb import Herb


SAMPLE_HERBS = [
    {"name_cn": "黄芪", "name_pinyin": "Huang Qi", "category": "补气药", "nature": "温", "flavor": ["甘"], "efficacy": "补气升阳，固表止汗，利水消肿，生津养血，行滞通痹，托毒排脓，敛疮生肌。"},
    {"name_cn": "人参", "name_pinyin": "Ren Shen", "category": "补气药", "nature": "平", "flavor": ["甘", "苦"], "efficacy": "大补元气，复脉固脱，补脾益肺，生津养血，安神益智。"},
    {"name_cn": "甘草", "name_pinyin": "Gan Cao", "category": "补气药", "nature": "平", "flavor": ["甘"], "efficacy": "补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药。"},
    {"name_cn": "当归", "name_pinyin": "Dang Gui", "category": "补血药", "nature": "温", "flavor": ["甘", "辛"], "efficacy": "补血活血，调经止痛，润肠通便。"},
    {"name_cn": "熟地黄", "name_pinyin": "Shu Di Huang", "category": "补血药", "nature": "温", "flavor": ["甘"], "efficacy": "补血滋阴，益精填髓。"},
    {"name_cn": "金银花", "name_pinyin": "Jin Yin Hua", "category": "清热药", "nature": "寒", "flavor": ["甘"], "efficacy": "清热解毒，疏散风热。"},
    {"name_cn": "黄连", "name_pinyin": "Huang Lian", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "清热燥湿，泻火解毒。"},
    {"name_cn": "黄芩", "name_pinyin": "Huang Qin", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "清热燥湿，泻火解毒，止血，安胎。"},
    {"name_cn": "麻黄", "name_pinyin": "Ma Huang", "category": "解表药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "发汗散寒，宣肺平喘，利水消肿。"},
    {"name_cn": "桂枝", "name_pinyin": "Gui Zhi", "category": "解表药", "nature": "温", "flavor": ["辛", "甘"], "efficacy": "发汗解肌，温通经脉，助阳化气，平冲降逆。"},
    {"name_cn": "柴胡", "name_pinyin": "Chai Hu", "category": "解表药", "nature": "凉", "flavor": ["辛", "苦"], "efficacy": "疏散退热，疏肝解郁，升举阳气。"},
    {"name_cn": "白术", "name_pinyin": "Bai Zhu", "category": "补气药", "nature": "温", "flavor": ["甘", "苦"], "efficacy": "健脾益气，燥湿利水，止汗，安胎。"},
    {"name_cn": "茯苓", "name_pinyin": "Fu Ling", "category": "利水渗湿药", "nature": "平", "flavor": ["甘"], "efficacy": "利水渗湿，健脾，宁心。"},
    {"name_cn": "川芎", "name_pinyin": "Chuan Xiong", "category": "活血化瘀药", "nature": "温", "flavor": ["辛"], "efficacy": "活血行气，祛风止痛。"},
    {"name_cn": "丹参", "name_pinyin": "Dan Shen", "category": "活血化瘀药", "nature": "凉", "flavor": ["苦"], "efficacy": "活血祛瘀，通经止痛，清心除烦，凉血消痈。"},
    {"name_cn": "陈皮", "name_pinyin": "Chen Pi", "category": "理气药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "理气健脾，燥湿化痰。"},
    {"name_cn": "半夏", "name_pinyin": "Ban Xia", "category": "化痰止咳平喘药", "nature": "温", "flavor": ["辛"], "efficacy": "燥湿化痰，降逆止呕，消痞散结。"},
    {"name_cn": "枸杞子", "name_pinyin": "Gou Qi Zi", "category": "补阴药", "nature": "平", "flavor": ["甘"], "efficacy": "滋补肝肾，益精明目。"},
    {"name_cn": "大黄", "name_pinyin": "Da Huang", "category": "泻下药", "nature": "寒", "flavor": ["苦"], "efficacy": "泻下攻积，清热泻火，凉血解毒，逐瘀通经，利湿退黄。"},
    {"name_cn": "附子", "name_pinyin": "Fu Zi", "category": "温里药", "nature": "热", "flavor": ["辛", "甘"], "efficacy": "回阳救逆，补火助阳，散寒止痛。"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for data in SAMPLE_HERBS:
            result = await session.execute(select(Herb).where(Herb.name_cn == data["name_cn"]))
            if result.scalar_one_or_none():
                continue
            session.add(Herb(**data))
        await session.commit()
        print(f"Seeded {len(SAMPLE_HERBS)} sample herbs.")


if __name__ == "__main__":
    asyncio.run(seed())

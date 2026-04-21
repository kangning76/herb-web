"""Seed sample herb data for development."""
import asyncio

from sqlalchemy import select

from app.database import async_session_factory, engine, Base
from app.models.herb import Herb


SAMPLE_HERBS = [
    # ── 解表药 (7) ──────────────────────────────────────────────────────
    {"name_cn": "麻黄", "name_pinyin": "Ma Huang", "category": "解表药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "发汗散寒，宣肺平喘，利水消肿。"},
    {"name_cn": "桂枝", "name_pinyin": "Gui Zhi", "category": "解表药", "nature": "温", "flavor": ["辛", "甘"], "efficacy": "发汗解肌，温通经脉，助阳化气，平冲降逆。"},
    {"name_cn": "柴胡", "name_pinyin": "Chai Hu", "category": "解表药", "nature": "凉", "flavor": ["辛", "苦"], "efficacy": "疏散退热，疏肝解郁，升举阳气。"},
    {"name_cn": "紫苏", "name_pinyin": "Zi Su", "category": "解表药", "nature": "温", "flavor": ["辛"], "efficacy": "解表散寒，行气宽中，安胎，解鱼蟹毒。"},
    {"name_cn": "防风", "name_pinyin": "Fang Feng", "category": "解表药", "nature": "温", "flavor": ["辛", "甘"], "efficacy": "祛风解表，胜湿止痛，止痉。"},
    {"name_cn": "薄荷", "name_pinyin": "Bo He", "category": "解表药", "nature": "凉", "flavor": ["辛"], "efficacy": "疏散风热，清利头目，利咽透疹，疏肝行气。"},
    {"name_cn": "荆芥", "name_pinyin": "Jing Jie", "category": "解表药", "nature": "温", "flavor": ["辛"], "efficacy": "祛风解表，透疹消疮，止血。"},

    # ── 清热药 (7) ──────────────────────────────────────────────────────
    {"name_cn": "金银花", "name_pinyin": "Jin Yin Hua", "category": "清热药", "nature": "寒", "flavor": ["甘"], "efficacy": "清热解毒，疏散风热。"},
    {"name_cn": "黄连", "name_pinyin": "Huang Lian", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "清热燥湿，泻火解毒。"},
    {"name_cn": "黄芩", "name_pinyin": "Huang Qin", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "清热燥湿，泻火解毒，止血，安胎。"},
    {"name_cn": "连翘", "name_pinyin": "Lian Qiao", "category": "清热药", "nature": "凉", "flavor": ["苦"], "efficacy": "清热解毒，消肿散结，疏散风热。"},
    {"name_cn": "栀子", "name_pinyin": "Zhi Zi", "category": "清热药", "nature": "寒", "flavor": ["苦"], "efficacy": "泻火除烦，清热利湿，凉血解毒。"},
    {"name_cn": "石膏", "name_pinyin": "Shi Gao", "category": "清热药", "nature": "寒", "flavor": ["甘", "辛"], "efficacy": "清热泻火，除烦止渴。"},
    {"name_cn": "知母", "name_pinyin": "Zhi Mu", "category": "清热药", "nature": "寒", "flavor": ["甘", "苦"], "efficacy": "清热泻火，滋阴润燥。"},
    # ── 泻下药 (3) ──────────────────────────────────────────────────────
    {"name_cn": "大黄", "name_pinyin": "Da Huang", "category": "泻下药", "nature": "寒", "flavor": ["苦"], "efficacy": "泻下攻积，清热泻火，凉血解毒，逐瘀通经，利湿退黄。"},
    {"name_cn": "芒硝", "name_pinyin": "Mang Xiao", "category": "泻下药", "nature": "寒", "flavor": ["苦", "咸"], "efficacy": "泻下通便，润燥软坚，清火消肿。"},
    {"name_cn": "火麻仁", "name_pinyin": "Huo Ma Ren", "category": "泻下药", "nature": "平", "flavor": ["甘"], "efficacy": "润肠通便。"},

    # ── 祛风湿药 (4) ────────────────────────────────────────────────────
    {"name_cn": "独活", "name_pinyin": "Du Huo", "category": "祛风湿药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "祛风除湿，通痹止痛。"},
    {"name_cn": "威灵仙", "name_pinyin": "Wei Ling Xian", "category": "祛风湿药", "nature": "温", "flavor": ["辛", "咸"], "efficacy": "祛风除湿，通络止痛，消骨鲠。"},
    {"name_cn": "秦艽", "name_pinyin": "Qin Jiao", "category": "祛风湿药", "nature": "平", "flavor": ["辛", "苦"], "efficacy": "祛风湿，清湿热，止痹痛，退虚热。"},
    {"name_cn": "木瓜", "name_pinyin": "Mu Gua", "category": "祛风湿药", "nature": "温", "flavor": ["酸"], "efficacy": "舒筋活络，和胃化湿。"},

    # ── 化湿药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "藿香", "name_pinyin": "Huo Xiang", "category": "化湿药", "nature": "温", "flavor": ["辛"], "efficacy": "芳香化浊，和中止呕，发表解暑。"},
    {"name_cn": "苍术", "name_pinyin": "Cang Zhu", "category": "化湿药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "燥湿健脾，祛风散寒，明目。"},
    {"name_cn": "厚朴", "name_pinyin": "Hou Po", "category": "化湿药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "燥湿消痰，下气除满。"},
    {"name_cn": "砂仁", "name_pinyin": "Sha Ren", "category": "化湿药", "nature": "温", "flavor": ["辛"], "efficacy": "化湿开胃，温脾止泻，理气安胎。"},

    # ── 利水渗湿药 (4) ──────────────────────────────────────────────────
    {"name_cn": "茯苓", "name_pinyin": "Fu Ling", "category": "利水渗湿药", "nature": "平", "flavor": ["甘"], "efficacy": "利水渗湿，健脾，宁心。"},
    {"name_cn": "泽泻", "name_pinyin": "Ze Xie", "category": "利水渗湿药", "nature": "寒", "flavor": ["甘"], "efficacy": "利水渗湿，泄热。"},
    {"name_cn": "薏苡仁", "name_pinyin": "Yi Yi Ren", "category": "利水渗湿药", "nature": "凉", "flavor": ["甘"], "efficacy": "利水渗湿，健脾止泻，除痹，清热排脓。"},
    {"name_cn": "车前子", "name_pinyin": "Che Qian Zi", "category": "利水渗湿药", "nature": "寒", "flavor": ["甘"], "efficacy": "清热利尿通淋，渗湿止泻，明目，祛痰。"},

    # ── 温里药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "附子", "name_pinyin": "Fu Zi", "category": "温里药", "nature": "热", "flavor": ["辛", "甘"], "efficacy": "回阳救逆，补火助阳，散寒止痛。"},
    {"name_cn": "干姜", "name_pinyin": "Gan Jiang", "category": "温里药", "nature": "热", "flavor": ["辛"], "efficacy": "温中散寒，回阳通脉，温肺化饮。"},
    {"name_cn": "肉桂", "name_pinyin": "Rou Gui", "category": "温里药", "nature": "热", "flavor": ["辛", "甘"], "efficacy": "补火助阳，散寒止痛，温通经脉，引火归元。"},
    {"name_cn": "吴茱萸", "name_pinyin": "Wu Zhu Yu", "category": "温里药", "nature": "热", "flavor": ["辛", "苦"], "efficacy": "散寒止痛，降逆止呕，助阳止泻。"},

    # ── 理气药 (5) ──────────────────────────────────────────────────────
    {"name_cn": "陈皮", "name_pinyin": "Chen Pi", "category": "理气药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "理气健脾，燥湿化痰。"},
    {"name_cn": "木香", "name_pinyin": "Mu Xiang", "category": "理气药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "行气止痛，健脾消食。"},
    {"name_cn": "香附", "name_pinyin": "Xiang Fu", "category": "理气药", "nature": "平", "flavor": ["辛", "苦"], "efficacy": "疏肝解郁，理气宽中，调经止痛。"},
    {"name_cn": "枳实", "name_pinyin": "Zhi Shi", "category": "理气药", "nature": "温", "flavor": ["辛", "苦", "酸"], "efficacy": "破气消积，化痰散痞。"},
    {"name_cn": "青皮", "name_pinyin": "Qing Pi", "category": "理气药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "疏肝破气，消积化滞。"},

    # ── 消食药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "山楂", "name_pinyin": "Shan Zha", "category": "消食药", "nature": "温", "flavor": ["酸", "甘"], "efficacy": "消食健胃，行气散瘀，化浊降脂。"},
    {"name_cn": "麦芽", "name_pinyin": "Mai Ya", "category": "消食药", "nature": "平", "flavor": ["甘"], "efficacy": "行气消食，健脾开胃，回乳消胀。"},
    {"name_cn": "神曲", "name_pinyin": "Shen Qu", "category": "消食药", "nature": "温", "flavor": ["辛", "甘"], "efficacy": "消食和胃。"},
    {"name_cn": "莱菔子", "name_pinyin": "Lai Fu Zi", "category": "消食药", "nature": "平", "flavor": ["辛", "甘"], "efficacy": "消食除胀，降气化痰。"},

    # ── 驱虫药 (3) ──────────────────────────────────────────────────────
    {"name_cn": "使君子", "name_pinyin": "Shi Jun Zi", "category": "驱虫药", "nature": "温", "flavor": ["甘"], "efficacy": "杀虫消积。"},
    {"name_cn": "槟榔", "name_pinyin": "Bing Lang", "category": "驱虫药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "杀虫消积，行气利水，截疟。"},
    {"name_cn": "南瓜子", "name_pinyin": "Nan Gua Zi", "category": "驱虫药", "nature": "平", "flavor": ["甘"], "efficacy": "杀虫。"},

    # ── 止血药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "三七", "name_pinyin": "San Qi", "category": "止血药", "nature": "温", "flavor": ["甘", "苦"], "efficacy": "散瘀止血，消肿定痛。"},
    {"name_cn": "白及", "name_pinyin": "Bai Ji", "category": "止血药", "nature": "凉", "flavor": ["苦", "甘", "酸"], "efficacy": "收敛止血，消肿生肌。"},
    {"name_cn": "艾叶", "name_pinyin": "Ai Ye", "category": "止血药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "温经止血，散寒止痛，调经安胎。"},
    {"name_cn": "蒲黄", "name_pinyin": "Pu Huang", "category": "止血药", "nature": "平", "flavor": ["甘"], "efficacy": "止血，化瘀，通淋。"},

    # ── 活血化瘀药 (6) ──────────────────────────────────────────────────
    {"name_cn": "川芎", "name_pinyin": "Chuan Xiong", "category": "活血化瘀药", "nature": "温", "flavor": ["辛"], "efficacy": "活血行气，祛风止痛。"},
    {"name_cn": "丹参", "name_pinyin": "Dan Shen", "category": "活血化瘀药", "nature": "凉", "flavor": ["苦"], "efficacy": "活血祛瘀，通经止痛，清心除烦，凉血消痈。"},
    {"name_cn": "桃仁", "name_pinyin": "Tao Ren", "category": "活血化瘀药", "nature": "平", "flavor": ["苦", "甘"], "efficacy": "活血祛瘀，润肠通便，止咳平喘。"},
    {"name_cn": "红花", "name_pinyin": "Hong Hua", "category": "活血化瘀药", "nature": "温", "flavor": ["辛"], "efficacy": "活血通经，散瘀止痛。"},
    {"name_cn": "益母草", "name_pinyin": "Yi Mu Cao", "category": "活血化瘀药", "nature": "凉", "flavor": ["辛", "苦"], "efficacy": "活血调经，利尿消肿，清热解毒。"},
    {"name_cn": "延胡索", "name_pinyin": "Yan Hu Suo", "category": "活血化瘀药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "活血，行气，止痛。"},

    # ── 化痰止咳平喘药 (5) ──────────────────────────────────────────────
    {"name_cn": "半夏", "name_pinyin": "Ban Xia", "category": "化痰止咳平喘药", "nature": "温", "flavor": ["辛"], "efficacy": "燥湿化痰，降逆止呕，消痞散结。"},
    {"name_cn": "川贝母", "name_pinyin": "Chuan Bei Mu", "category": "化痰止咳平喘药", "nature": "凉", "flavor": ["苦", "甘"], "efficacy": "清热润肺，化痰止咳，散结消痈。"},
    {"name_cn": "桔梗", "name_pinyin": "Jie Geng", "category": "化痰止咳平喘药", "nature": "平", "flavor": ["辛", "苦"], "efficacy": "宣肺，利咽，祛痰，排脓。"},
    {"name_cn": "杏仁", "name_pinyin": "Xing Ren", "category": "化痰止咳平喘药", "nature": "温", "flavor": ["苦"], "efficacy": "降气止咳平喘，润肠通便。"},
    {"name_cn": "紫苑", "name_pinyin": "Zi Wan", "category": "化痰止咳平喘药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "润肺下气，消痰止咳。"},

    # ── 安神药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "酸枣仁", "name_pinyin": "Suan Zao Ren", "category": "安神药", "nature": "平", "flavor": ["甘", "酸"], "efficacy": "养心补肝，宁心安神，敛汗，生津。"},
    {"name_cn": "远志", "name_pinyin": "Yuan Zhi", "category": "安神药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "安神益智，祛痰开窍，消散痈肿。"},
    {"name_cn": "柏子仁", "name_pinyin": "Bai Zi Ren", "category": "安神药", "nature": "平", "flavor": ["甘"], "efficacy": "养心安神，润肠通便，止汗。"},
    {"name_cn": "合欢皮", "name_pinyin": "He Huan Pi", "category": "安神药", "nature": "平", "flavor": ["甘"], "efficacy": "解郁安神，活血消肿。"},

    # ── 平肝息风药 (4) ──────────────────────────────────────────────────
    {"name_cn": "天麻", "name_pinyin": "Tian Ma", "category": "平肝息风药", "nature": "平", "flavor": ["甘"], "efficacy": "息风止痉，平抑肝阳，祛风通络。"},
    {"name_cn": "钩藤", "name_pinyin": "Gou Teng", "category": "平肝息风药", "nature": "凉", "flavor": ["甘"], "efficacy": "息风定惊，清热平肝。"},
    {"name_cn": "决明子", "name_pinyin": "Jue Ming Zi", "category": "平肝息风药", "nature": "凉", "flavor": ["甘", "苦", "咸"], "efficacy": "清热明目，润肠通便。"},
    {"name_cn": "石决明", "name_pinyin": "Shi Jue Ming", "category": "平肝息风药", "nature": "寒", "flavor": ["咸"], "efficacy": "平肝潜阳，清肝明目。"},

    # ── 开窍药 (3) ──────────────────────────────────────────────────────
    {"name_cn": "麝香", "name_pinyin": "She Xiang", "category": "开窍药", "nature": "温", "flavor": ["辛"], "efficacy": "开窍醒神，活血通经，消肿止痛。"},
    {"name_cn": "冰片", "name_pinyin": "Bing Pian", "category": "开窍药", "nature": "凉", "flavor": ["辛", "苦"], "efficacy": "开窍醒神，清热止痛。"},
    {"name_cn": "石菖蒲", "name_pinyin": "Shi Chang Pu", "category": "开窍药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "开窍豁痰，醒神益智，化湿开胃。"},

    # ── 补气药 (7) ──────────────────────────────────────────────────────
    {"name_cn": "黄芪", "name_pinyin": "Huang Qi", "category": "补气药", "nature": "温", "flavor": ["甘"], "efficacy": "补气升阳，固表止汗，利水消肿，生津养血，行滞通痹，托毒排脓，敛疮生肌。"},
    {"name_cn": "人参", "name_pinyin": "Ren Shen", "category": "补气药", "nature": "平", "flavor": ["甘", "苦"], "efficacy": "大补元气，复脉固脱，补脾益肺，生津养血，安神益智。"},
    {"name_cn": "甘草", "name_pinyin": "Gan Cao", "category": "补气药", "nature": "平", "flavor": ["甘"], "efficacy": "补脾益气，清热解毒，祛痰止咳，缓急止痛，调和诸药。"},
    {"name_cn": "白术", "name_pinyin": "Bai Zhu", "category": "补气药", "nature": "温", "flavor": ["甘", "苦"], "efficacy": "健脾益气，燥湿利水，止汗，安胎。"},
    {"name_cn": "党参", "name_pinyin": "Dang Shen", "category": "补气药", "nature": "平", "flavor": ["甘"], "efficacy": "补中益气，健脾益肺，养血生津。"},
    {"name_cn": "山药", "name_pinyin": "Shan Yao", "category": "补气药", "nature": "平", "flavor": ["甘"], "efficacy": "补脾养胃，生津益肺，补肾涩精。"},
    {"name_cn": "大枣", "name_pinyin": "Da Zao", "category": "补气药", "nature": "温", "flavor": ["甘"], "efficacy": "补中益气，养血安神，缓和药性。"},

    # ── 补血药 (5) ──────────────────────────────────────────────────────
    {"name_cn": "当归", "name_pinyin": "Dang Gui", "category": "补血药", "nature": "温", "flavor": ["甘", "辛"], "efficacy": "补血活血，调经止痛，润肠通便。"},
    {"name_cn": "熟地黄", "name_pinyin": "Shu Di Huang", "category": "补血药", "nature": "温", "flavor": ["甘"], "efficacy": "补血滋阴，益精填髓。"},
    {"name_cn": "白芍", "name_pinyin": "Bai Shao", "category": "补血药", "nature": "凉", "flavor": ["苦", "酸"], "efficacy": "养血调经，敛阴止汗，柔肝止痛，平抑肝阳。"},
    {"name_cn": "阿胶", "name_pinyin": "E Jiao", "category": "补血药", "nature": "平", "flavor": ["甘"], "efficacy": "补血滋阴，润燥，止血。"},
    {"name_cn": "何首乌", "name_pinyin": "He Shou Wu", "category": "补血药", "nature": "温", "flavor": ["甘", "苦"], "efficacy": "补肝肾，益精血，乌须发，强筋骨，化浊降脂。"},

    # ── 补阴药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "枸杞子", "name_pinyin": "Gou Qi Zi", "category": "补阴药", "nature": "平", "flavor": ["甘"], "efficacy": "滋补肝肾，益精明目。"},
    {"name_cn": "麦冬", "name_pinyin": "Mai Dong", "category": "补阴药", "nature": "凉", "flavor": ["甘", "苦"], "efficacy": "养阴生津，润肺清心。"},
    {"name_cn": "沙参", "name_pinyin": "Sha Shen", "category": "补阴药", "nature": "凉", "flavor": ["甘"], "efficacy": "养阴清肺，益胃生津。"},
    {"name_cn": "玉竹", "name_pinyin": "Yu Zhu", "category": "补阴药", "nature": "平", "flavor": ["甘"], "efficacy": "养阴润燥，生津止渴。"},

    # ── 补阳药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "鹿茸", "name_pinyin": "Lu Rong", "category": "补阳药", "nature": "温", "flavor": ["甘", "咸"], "efficacy": "壮肾阳，益精血，强筋骨，调冲任，托疮毒。"},
    {"name_cn": "淫羊藿", "name_pinyin": "Yin Yang Huo", "category": "补阳药", "nature": "温", "flavor": ["辛", "甘"], "efficacy": "补肾阳，强筋骨，祛风湿。"},
    {"name_cn": "杜仲", "name_pinyin": "Du Zhong", "category": "补阳药", "nature": "温", "flavor": ["甘"], "efficacy": "补肝肾，强筋骨，安胎。"},
    {"name_cn": "肉苁蓉", "name_pinyin": "Rou Cong Rong", "category": "补阳药", "nature": "温", "flavor": ["甘", "咸"], "efficacy": "补肾阳，益精血，润肠通便。"},

    # ── 收涩药 (4) ──────────────────────────────────────────────────────
    {"name_cn": "五味子", "name_pinyin": "Wu Wei Zi", "category": "收涩药", "nature": "温", "flavor": ["酸", "甘"], "efficacy": "收敛固涩，益气生津，补肾宁心。"},
    {"name_cn": "乌梅", "name_pinyin": "Wu Mei", "category": "收涩药", "nature": "平", "flavor": ["酸"], "efficacy": "敛肺止咳，涩肠止泻，安蛔止痛，生津止渴。"},
    {"name_cn": "山茱萸", "name_pinyin": "Shan Zhu Yu", "category": "收涩药", "nature": "温", "flavor": ["酸"], "efficacy": "补益肝肾，收涩固脱。"},
    {"name_cn": "莲子", "name_pinyin": "Lian Zi", "category": "收涩药", "nature": "平", "flavor": ["甘", "酸"], "efficacy": "补脾止泻，止带，益肾涩精，养心安神。"},

    # ── 涌吐药 (2) ──────────────────────────────────────────────────────
    {"name_cn": "常山", "name_pinyin": "Chang Shan", "category": "涌吐药", "nature": "寒", "flavor": ["辛", "苦"], "efficacy": "涌吐痰饮，截疟。"},
    {"name_cn": "瓜蒂", "name_pinyin": "Gua Di", "category": "涌吐药", "nature": "寒", "flavor": ["苦"], "efficacy": "涌吐痰食，祛湿退黄。"},

    # ── 外用药 (3) ──────────────────────────────────────────────────────
    {"name_cn": "硫磺", "name_pinyin": "Liu Huang", "category": "外用药", "nature": "温", "flavor": ["酸"], "efficacy": "外用解毒杀虫疗疮，内服补火助阳通便。"},
    {"name_cn": "雄黄", "name_pinyin": "Xiong Huang", "category": "外用药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "解毒杀虫，燥湿祛痰，截疟。"},
    {"name_cn": "蛇床子", "name_pinyin": "She Chuang Zi", "category": "外用药", "nature": "温", "flavor": ["辛", "苦"], "efficacy": "杀虫止痒，燥湿，温肾壮阳。"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        added = 0
        for data in SAMPLE_HERBS:
            result = await session.execute(select(Herb).where(Herb.name_cn == data["name_cn"]))
            if result.scalar_one_or_none():
                continue
            session.add(Herb(**data))
            added += 1
        await session.commit()
        print(f"Seeded {added} new herbs (total in seed list: {len(SAMPLE_HERBS)}).")


if __name__ == "__main__":
    asyncio.run(seed())

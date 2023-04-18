from dataclasses import dataclass
from typing import List

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_ids: List[int]
    use_redis: bool

@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str

@dataclass
class Other:
    payments_token: str

@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    other: Other

def load_config(path: str):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS")
        ),
        db=DbConfig(
            host=env.str("DB_HOST"),
            password=env.str("DB_PASS"),
            user=env.str("DB_USER"),
            database=env.str("DB_NAME")
        ),
        other=Other(
            payments_token=env.str("PAYMENTS_TOKEN")
        )
    )
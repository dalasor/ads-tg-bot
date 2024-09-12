from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    BOT_TOKEN: str
    ADS_TOKEN: str


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            BOT_TOKEN=env('BOT_TOKEN'),
            ADS_TOKEN=env('ADS_TOKEN')
        )
    )

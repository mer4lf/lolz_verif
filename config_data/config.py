from dataclasses import dataclass
from environs import Env


@dataclass
class DatabaseConfig:
    database: str  # �^}азвание баз�^k данн�^k�^e
    db_host: str  # URL-ад�^`е�^a баз�^k данн�^k�^e
    db_user: str  # Username пол�^lзова�^bел�^o баз�^k данн�^k�^e
    db_password: str  # �^=а�^`ол�^l к базе данн�^k�^e


@dataclass
class TgBot:
    token: str  # Токен дл�^o до�^a�^b�^cпа к �^bелег�^`ам-бо�^b�^c
    admin_ids: list[int]  # Спи�^aок id админи�^a�^b�^`а�^bо�^`ов бо�^bа




@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig


def load_config(path: str | None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            admin_ids=list(map(int, env.list('ADMIN_IDS')))),
        db=DatabaseConfig(
            database=env('DATABASE'),
            db_host=env('DB_HOST'),
            db_user=env('DB_USER'),
            db_password=env('DB_PASSWORD'))
    )


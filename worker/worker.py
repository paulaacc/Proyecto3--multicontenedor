import os
import json
import time
from datetime import datetime, timezone

import redis
import psycopg2
from pymongo import MongoClient


def retry(fn, name):
    while True:
        try:
            return fn()
        except Exception as e:
            print(f"[worker] esperando {name}: {e}", flush=True)
            time.sleep(2)


def connect_redis():
    c = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
    c.ping()
    return c


def connect_pg():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS votes (
                         voter_id VARCHAR(64) PRIMARY KEY,
                         vote VARCHAR(50) NOT NULL)""")
    return conn


def connect_mongo():
    client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"), serverSelectionTimeoutMS=3000)
    client.admin.command("ping")
    return client["auditoria"]["eventos"]


def main():
    rds = retry(connect_redis, "redis")
    pg = retry(connect_pg, "postgresql")
    audit = retry(connect_mongo, "mongodb")
    print("[worker] conectado a Redis, PostgreSQL y MongoDB", flush=True)

    while True:
        item = rds.blpop("votes", timeout=5)
        if not item:
            continue
        data = json.loads(item[1])
        with pg.cursor() as cur:
            cur.execute(
                """INSERT INTO votes (voter_id, vote) VALUES (%s, %s)
                   ON CONFLICT (voter_id) DO UPDATE SET vote = EXCLUDED.vote""",
                (data["voter_id"], data["vote"]),
            )
        audit.insert_one({**data, "procesado": datetime.now(timezone.utc)})
        print(f"[worker] voto procesado: {data}", flush=True)


if __name__ == "__main__":
    main()

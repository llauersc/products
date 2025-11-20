from typing import Any


class SessionMaker:
    def __init__(self, db):
        self.db = db

    def session(self):
        return Session(self.db)


class Session:
    def __init__(self, db) -> None:
        self._db = db
        self.conn: Any = None

    async def __aenter__(self):
        self.conn = await self._db.connect()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.conn.rollback()
            await self.conn.close()
        await self.conn.commit()
        await self.conn.close()

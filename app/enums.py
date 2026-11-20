from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "new"
    PUBLISHED = "published"


class SyncStatus(StrEnum):
    IDLE = "idle"
    SUCCESS = "success"
    ERROR = "error"
from enum import Enum


class Status(Enum):
    WORKING = "working"
    TEST = "testing"
    SHUTDOWN = "preparing to shut down"

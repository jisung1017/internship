from enum import Enum


class MenuTag(str, Enum):
    NEW = "NEW"
    RECOMMEND = "RECOMMEND"
    SEASONAL = "SEASONAL"
    SIGNATURE = "SIGNATURE"
    BEST = "BEST"
from enum import Enum


class BandType(str, Enum):
    COVER_BAND = "Cover Band"
    TRIBUTE_BAND = "Tribute Band"
    ORIGINALS_ONLY = "Originals Only"
    ORIGINALS_AND_COVERS = "Originals and Covers"
    OTHER = "Other"

import warnings
from enum import Enum

from pydantic import BaseModel, Field


class ComplaintType(Enum):
    """Enum for complaint types"""

    LOST_ITEM = "1"  # Lost Item Report
    FOUND_ITEM = "2"  # Found Item Report


class ArticleType(Enum):
    """Enum for article types"""

    DRIVING_LICENSE = "Driving License"
    PASSPORT = "Passport"  # Currently not in use, but may be used in future
    PAN_CARD = "PAN Card"
    AADHAR_CARD = "Aadhar Card"
    VOTER_ID = "Voter ID Card"
    RATION_CARD = "Ration Card"
    EDUCATIONAL_DOCUMENT = "Educational Document"
    OTHER_DOCUMENTS = "Other Documents"
    MOBILE = "Mobile"  # Currently not in use, but may be used in future

    # Define as class variable

    def __init__(self, value):
        _DEPRECATED_TYPES = {"PASSPORT", "MOBILE"}
        """Initialize and check for deprecation."""
        # Use self.__class__ to access the class attribute
        if self.name in _DEPRECATED_TYPES:
            warnings.warn(
                f"The article type '{self.value}' is deprecated and may not be\
                     supported in the future.",
                DeprecationWarning,
                stacklevel=2,
            )

    @classmethod
    def _missing_(cls, value):
        """Handle lookup by value and ensure deprecation warning is \
            triggered."""
        for member in cls:
            if member.value == value:
                return member
        raise ValueError(f"{value} is not a valid {cls.__name__}")


class SearchParams(BaseModel):
    """Model for search parameters"""

    complaint_type: ComplaintType = Field(default=ComplaintType.LOST_ITEM)
    article_type: ArticleType = Field(default=ArticleType.OTHER_DOCUMENTS)
    article_desc: str = Field(default="")
    page: int = Field(default=1)

    def to_dict(self):
        """Convert model to dictionary with string values for URL parameters"""
        return {
            "complaint_type": self.complaint_type.value,
            "article_type": self.article_type.value,
            "article_desc": self.article_desc,
            "page": str(self.page),
        }

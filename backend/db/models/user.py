from sqlalchemy import (VARCHAR, Boolean, CheckConstraint, Column, ForeignKey,
                        Integer, String, Text)
from sqlalchemy.orm import Mapped, relationship

from db import constants

from .base import BaseModel


class PagePermission(BaseModel):
    """Page permission table"""

    core = Column(
        Integer,
        CheckConstraint("core >= 0 AND core <= 2"),
        nullable=False,
        default=0,
        doc="Semantic Core",
    )
    ads = Column(
        Integer,
        CheckConstraint("ads >= 0 AND ads <= 2"),
        nullable=False,
        default=0,
        doc="Advertising",
    )
    daypart = Column(
        Integer,
        CheckConstraint("daypart >= 0 AND daypart <= 2"),
        nullable=False,
        default=0,
        doc="Dayparting",
    )
    voice = Column(
        Integer,
        CheckConstraint("voice >= 0 AND voice <= 2"),
        nullable=False,
        default=0,
        doc="Share of voice",
    )
    ppc_auto = Column(
        Integer,
        CheckConstraint("ppc_auto >= 0 AND ppc_auto <= 2"),
        nullable=False,
        default=0,
        doc="PPC Automation",
    )
    ppc_audit = Column(
        Integer,
        CheckConstraint("ppc_audit >= 0 AND ppc_audit <= 2"),
        nullable=False,
        default=0,
        doc="PPC Audit",
    )
    alerts = Column(
        Integer,
        CheckConstraint("alerts >= 0 AND alerts <= 2"),
        nullable=False,
        default=0,
        doc="Alerts",
    )

    def __repr__(self):
        return (
            "core: {}, ads: {}, daypart: {}, voice: {}, ppc_auto: {}, ppc_audit: {}, alerts: {}"
        ).format(
            self.core,
            self.ads,
            self.daypart,
            self.voice,
            self.ppc_auto,
            self.ppc_audit,
            self.alerts,
        )

    def __str__(self):
        return (
            "core: {}, ads: {}, daypart: {}, voice: {}, ppc_auto: {}, ppc_audit: {}, alerts: {}"
        ).format(
            self.core,
            self.ads,
            self.daypart,
            self.voice,
            self.ppc_auto,
            self.ppc_audit,
            self.alerts,
        )


class Group(BaseModel):
    """Group table"""

    creator_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="Group creator id",
    )
    name = Column(String(length=40), doc="User name")

    def __repr__(self):
        return f"Group: <ID{self.id}:{self.name}>"

    def __str__(self):
        return f"Group: <ID{self.id}:{self.name}>"


class GroupUserPerms(BaseModel):
    """Group user permission table"""

    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="User id",
    )
    group_id = Column(
        Integer,
        ForeignKey("group.id", ondelete="CASCADE"),
        nullable=False,
        doc="Group id",
    )
    page_perm_id = Column(
        Integer,
        ForeignKey("page_permission.id", ondelete="CASCADE"),
        unique=True,
        doc="Page permission id",
    )
    role = Column(
        VARCHAR,
        nullable=False,
        default=constants.GroupRole.USER.value,
        doc="Type of User in current group",
    )
    page_perms: Mapped[PagePermission] = relationship(
        "PagePermission", uselist=False, lazy="joined"
    )
    group: Mapped[Group] = relationship("Group", uselist=False, lazy="subquery")


class User(BaseModel):
    """User table"""

    email = Column(String, unique=True, nullable=False, doc="Unique email address")
    password = Column(String, nullable=False, doc="Hashed password")
    name = Column(String(length=40), doc="User name")
    is_active = Column(
        Boolean, default=True, nullable=False, doc="Is user active in system"
    )
    is_superuser = Column(
        Boolean, default=False, nullable=False, doc="Is user superuser in system"
    )
    is_staff = Column(
        Boolean, default=False, nullable=False, doc="Is user staff in system"
    )
    current_group_id = Column(
        Integer,
        ForeignKey("group.id", ondelete="SET NULL"),
        doc="Current group id",
    )
    group_info: Mapped[GroupUserPerms] = relationship(
        "GroupUserPerms",
        primaryjoin="GroupUserPerms.user_id == User.id",
        backref="user",
    )

    def __repr__(self):
        return f"User: <ID{self.id}:{self.email}>"

    def __str__(self):
        return f"User: <ID{self.id}:{self.email}>"


class AmazonAccount(BaseModel):
    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        doc="Owner id",
    )
    group_id = Column(
        Integer,
        ForeignKey("group.id", ondelete="CASCADE"),
        nullable=False,
        doc="Group id",
    )
    profile_id = Column(String(length=50), doc="Profile ID on Amazon")
    country = Column(VARCHAR(length=25), doc="Country code. Example: US")
    region = Column(VARCHAR(length=25), doc="Amazon region. Example: na")
    currency = Column(VARCHAR(length=25), doc="Currency code. Example: USD")
    time_zone = Column(String(length=50), doc="Time zone. Example: America/Los_Angeles")
    marketplace_id = Column(String(length=100), doc="Marketplace ID on Amazon")
    amz_acc_id = Column(String(length=256), doc="Account ID on Amazon")
    acc_type = Column(String(length=50), doc="Account type. Example: seller")
    origin_name = Column(String(length=256), doc="Origin name from Amazon")
    custom_name = Column(String(length=256), doc="Name inside ScaleAnalyzer")
    sp_api_refresh_token = Column(Text())
    ads_api_refresh_token = Column(Text())

"""
Schema داخلی برای Opportunity - مستقل از منبع داده

این schema فرمت استاندارد داخلی ماست.
همه منابع (Greenhouse, Lever, OpenAlex) باید به این فرمت تبدیل شوند.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OpportunityBase(BaseModel):
    """
    فیلدهای مشترک بین همه schema های Opportunity
    """
    title: str = Field(..., description="عنوان فرصت شغلی/تحصیلی")
    description: str | None = Field(None, description="توضیحات کامل (متن ساده)")
    type: str = Field(..., description="نوع فرصت: job, phd, postdoc, etc")
    url: str = Field(..., description="لینک اصلی آگهی")
    deadline: date | None = Field(None, description="مهلت اعلام")
    posted_at: datetime | None = Field(None, description="تاریخ انتشار")


class OpportunityIngest(OpportunityBase):
    """
    Schema میانی — خروجی آداپترها قبل از رسیدن به دیتابیس.

    اینجا هنوز organization_id (UUID) نداریم چون هنوز رکورد Organization
    در دیتابیس ساخته نشده. به‌جاش organization_name رو نگه می‌داریم تا
    در مرحله‌ی لود به دیتابیس، سازمان پیدا/ساخته بشه و UUID واقعی بگیره.
    """
    organization_name: str = Field(..., description="نام سازمان از منبع خام")
    external_id: str = Field(..., description="شناسه در منبع خارجی (مثلاً ID در Greenhouse)")
    source: str = Field(..., description="منبع داده: greenhouse, lever, openalex, etc")


class OpportunityCreate(OpportunityBase):
    """
    Schema برای ساخت Opportunity جدید
    
    این schema زمانی استفاده می‌شود که می‌خواهیم یک Opportunity جدید
    از منبع خارجی (Greenhouse, Lever, ...) ایجاد کنیم.
    """
    organization_id: UUID = Field(..., description="شناسه سازمان")
    external_id: str = Field(..., description="شناسه در منبع خارجی (مثلاً ID در Greenhouse)")
    source: str = Field(..., description="منبع داده: greenhouse, lever, openalex, etc")

    model_config = ConfigDict(from_attributes=True)


class OpportunityResponse(OpportunityBase):
    """
    Schema برای نمایش Opportunity به کاربر (در API Response)
    
    این شامل فیلدهای اضافی است که بعد از ذخیره در دیتابیس اضافه می‌شوند.
    """
    id: UUID = Field(..., description="شناسه یکتا در دیتابیس")
    organization_id: UUID = Field(..., description="شناسه سازمان")
    external_id: str = Field(..., description="شناسه در منبع خارجی")
    source: str = Field(..., description="منبع داده")
    created_at: datetime = Field(..., description="زمان ایجاد در سیستم ما")

    model_config = ConfigDict(from_attributes=True)

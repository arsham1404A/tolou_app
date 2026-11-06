import jdatetime
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Audition, GalleryPhoto, Play, Reservation, Script

User = get_user_model()


# ۱. فرم ثبت‌نام اعضا با تایید تولد خورشیدی
class CustomUserCreationForm(forms.ModelForm):
    birth_day = forms.IntegerField(
        label="روز تولد (شمسی)",
        min_value=1,
        max_value=31,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "مثلاً ۱۵"}
        ),
    )
    birth_month = forms.IntegerField(
        label="ماه تولد (شمسی)",
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "مثلاً ۸"}
        ),
    )
    birth_year = forms.IntegerField(
        label="سال تولد (شمسی)",
        min_value=1300,
        max_value=1450,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "مثلاً ۱۳۸۵"}
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "role",
            "phone_number",
        ]

    def clean(self):
        cleaned_data = super().clean()
        day = cleaned_data.get("birth_day")
        month = cleaned_data.get("birth_month")
        year = cleaned_data.get("birth_year")

        if day and month and year:
            try:
                jdatetime.date(year, month, day)
            except ValueError:
                raise ValidationError(
                    "تاریخ تولد وارد شده معتبر نیست (به تعداد روزهای ماه دقت کنید)."
                )
        return cleaned_data


# ۲. فرم ایجاد/ویرایش نمایشنامه (Play)
class PlayCreateForm(forms.ModelForm):
    class Meta:
        model = Play
        fields = [
            "title",
            "poster",
            "teaser",
            "short_description",
            "full_description",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "short_description": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "full_description": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
        }


# ۳. فرم آپلود تصویر در گالری/آرشیو (GalleryPhoto)
class ActorArchiveUploadForm(forms.ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = ["album", "image", "caption"]
        widgets = {
            "album": forms.Select(attrs={"class": "form-select"}),
            "caption": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "توضیح کوتاه عکس",
                }
            ),
        }


# ۴. فرم ثبت درخواست رزرو اجرا (Reservation)
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "full_name",
            "phone",
            "province",
            "city",
            "address",
            "sound_capacity",
            "light_capacity",
            "play_title",
            "offered_price",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "province": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "sound_capacity": forms.Select(attrs={"class": "form-select"}),
            "light_capacity": forms.Select(attrs={"class": "form-select"}),
            "play_title": forms.Select(attrs={"class": "form-select"}),
            "offered_price": forms.TextInput(attrs={"class": "form-control"}),
        }
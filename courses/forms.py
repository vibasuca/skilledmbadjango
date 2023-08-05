# forms.py

from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            "title",
            "slug",
            "description",
            "max_students",
            "difficulty_level",
            "is_public",
            "enable_qa",
            "language",
            "category",
            "price",
            "discount_price",
            "thumbnail",
            "instructors",
            "attachments",
            "what_will_i_learn",
            "target_audience",
            "duration",
            "materials_included",
            "requirements",
            "tags",
            "prerequisite_courses",
        )

    # def __init__(self, *args, **kwargs):
    #     super(ProductForm, self).__init__(*args, **kwargs)

    #     # Customize the field widgets or querysets if needed
    #     self.fields["category"].widget.attrs.update({"class": "custom-select"})
    #     self.fields["tags"].widget.attrs.update({"class": "custom-select"})

    #     # Optionally, you can limit the choices for the category field or tags field
    #     self.fields["category"].queryset = Category.objects.all()
    #     self.fields["tags"].queryset = Tag.objects.all()

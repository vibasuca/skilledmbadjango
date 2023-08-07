import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import F
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import CourseForm
from .models import *


@require_POST
@login_required
def create_course(request):
    course = Course.objects.create(user=request.user, title="New Course")
    return redirect("courses:update_course", pk=course.pk)


@login_required
def update_course(request, pk):
    course = get_object_or_404(Course, user=request.user, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            instance = form.save()
            if "submit_for_review" in request.POST:
                instance.published_at = timezone.now()
            else:
                instance.published_at = None
            instance.save()

            return redirect("courses:update_course", pk=instance.pk)
    else:
        form = CourseForm(instance=course)

    context = {"form": form, "course": course}
    return render(request, "courses/update_course.html", context)


@require_POST
@login_required
def create_topic(request, course_pk):
    """
    Returns following error on failure:
    {
        "error": {
            "title": [
                "This field is required."
            ]
        }
    }
    """
    course = get_object_or_404(Course, user=request.user, pk=course_pk)
    title = request.POST.get("title", "")
    summary = request.POST.get("summary", "")

    sort_order = course.topics.count() + 1
    topic = Topic(
        course=course,
        title=title,
        summary=summary,
        sort_order=sort_order,
    )

    # Validate the topic instance before saving
    try:
        topic.full_clean()
        topic.save()
        return JsonResponse({"message": "Topic created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


@require_POST
@login_required
def update_topic(request, pk):
    """
    Returns following error on failure:
    {
        "error": {
            "title": [
                "This field is required."
            ]
        }
    }
    """
    topic = get_object_or_404(Topic, pk=pk, course__user=request.user)
    course = topic.course
    title = request.POST.get("title", "")
    summary = request.POST.get("summary", "")
    sort_order = int(request.POST.get("sort_order"))

    # Shift the sort_order of other topics if needed
    if sort_order > topic.sort_order:
        topics = course.topics.filter(
            sort_order__gt=topic.sort_order, sort_order__lte=sort_order
        )
        topics.update(sort_order=F("sort_order") - 1)

    elif sort_order < topic.sort_order:
        topics = course.topics.filter(
            sort_order__lt=topic.sort_order, sort_order__gte=sort_order
        )
        topics.update(sort_order=F("sort_order") + 1)

    topic.title = title
    topic.summary = summary
    topic.sort_order = sort_order

    # Validate the topic instance before saving
    try:
        topic.full_clean()
        topic.save()
        return JsonResponse({"message": "Topic created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


@login_required
def list_topics(request, course_pk):
    course = get_object_or_404(Course, user=request.user, pk=course_pk)
    topics = course.topics.all()

    # Convert topic queryset to a list of dictionaries
    topic_list = [
        {
            "id": topic.id,
            "title": topic.title,
            "summary": topic.summary,
            "sort_order": topic.sort_order,
        }
        for topic in topics
    ]

    return JsonResponse({"topics": topic_list})


@require_POST
@login_required
def create_lesson(request, topic_pk):
    """
    Returns following error on failure:
    {
        "error": {
            "title": [
                "This field is required."
            ]
        }
    }
    """
    topic = get_object_or_404(Topic, course__user=request.user, pk=topic_pk)
    data = json.loads(request.body)
    title = data.get("title", "")
    content = data.get("content", "")
    feature_image = data.get("feature_image")
    if feature_image:
        feature_image = Media.objects.get(pk=int(feature_image), user=request.user)
    attachments = data.get("attachments")
    if attachments:
        attachments = Media.objects.filter(pk__in=attachments, user=request.user)
    enable_preview = data.get("enable_preview")

    lesson = Lesson(
        title=title,
        content=content,
        feature_image=feature_image,
        enable_preview=enable_preview,
    )

    # Validate the lesson instance before saving
    try:
        lesson.full_clean()
        lesson.save()
        if attachments:
            lesson.attachments.set(attachments)
        sort_order = topic.items.count() + 1
        TopicItem.objects.create(topic=topic, lesson=lesson, sort_order=sort_order)
        return JsonResponse({"message": "Lesson created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


@login_required
def list_topic_items(request, topic_pk):
    topic = get_object_or_404(Topic, course__user=request.user, pk=topic_pk)
    topic_items = topic.items.all()

    # Convert topic queryset to a list of dictionaries
    topic_items_list = []
    for topic_item in topic_items:
        item = json.loads(serializers.serialize("json", [topic_item]))[0]["fields"]
        item["id"] = topic_item.pk

        if topic_item.lesson:
            lesson = json.loads(serializers.serialize("json", [topic_item.lesson]))[0][
                "fields"
            ]
            lesson["id"] = topic_item.lesson.pk

            if topic_item.lesson.feature_image:
                feature_image = json.loads(
                    serializers.serialize("json", [topic_item.lesson.feature_image])
                )[0]["fields"]
                feature_image["id"] = topic_item.lesson.feature_image.pk
                lesson["feature_image"] = feature_image

            attachments = topic_item.lesson.attachments.all()
            attachments = json.loads(serializers.serialize("json", attachments))
            attachments_serialized = []
            for attachment in attachments:
                att = attachment["fields"]
                att["id"] = attachment["pk"]
                attachments_serialized.append(att)
            lesson["attachments"] = attachments_serialized

            item["lesson"] = lesson

        elif topic_item.assignment:
            item["lesson"] = {
                "id": topic_item.assignment.id,
                "title": topic_item.assignment.title,
                "summary": topic_item.assignment.summary,
                "attachments": topic_item.assignment.attachments.values_list(
                    "id", flat=True
                ),
                "time_limit": topic_item.assignment.time_limit,
                "time_limit_unit": topic_item.assignment.time_limit_unit,
                "total_points": topic_item.assignment.total_points,
                "min_pass_points": topic_item.assignment.min_pass_points,
                "max_file_uploads": topic_item.assignment.max_file_uploads,
                "file_size_limit": topic_item.assignment.file_size_limit,
            }
        topic_items_list.append(item)

    return JsonResponse({"data": topic_items_list})


@require_POST
@login_required
def update_lesson(request, pk):
    """
    Returns following error on failure:
    {
        "error": {
            "title": [
                "This field is required."
            ]
        }
    }
    """
    user = request.user
    lesson = get_object_or_404(Lesson, pk=pk, topic_item__topic__course__user=user)
    topic_item = lesson.topic_item
    topic = topic_item.topic

    data = json.loads(request.body)
    title = data.get("title", "")
    content = data.get("content", "")
    feature_image = data.get("feature_image")
    if feature_image:
        feature_image = Media.objects.get(pk=feature_image, user=user)
    attachments = data.get("attachments")
    if attachments:
        attachments = Media.objects.filter(pk__in=attachments, user=user)
    enable_preview = data.get("enable_preview")
    sort_order = data.get("sort_order")

    lesson.title = title
    lesson.content = content
    lesson.feature_image = feature_image
    lesson.enable_preview = enable_preview

    # Validate the lesson instance before saving
    try:
        lesson.full_clean()
        lesson.save()
        lesson.attachments.set(attachments)

        # Shift the sort_order of other topic items if needed
        if sort_order > topic_item.sort_order:
            topic_items = topic.items.filter(
                sort_order__gt=topic_item.sort_order, sort_order__lte=sort_order
            )
            topic_items.update(sort_order=F("sort_order") - 1)

        elif sort_order < topic_item.sort_order:
            topic_items = topic.items.filter(
                sort_order__lt=topic_item.sort_order, sort_order__gte=sort_order
            )
            topic_items.update(sort_order=F("sort_order") + 1)

        topic_item.sort_order = sort_order
        topic_item.save()

        return JsonResponse({"message": "Lesson updated successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)

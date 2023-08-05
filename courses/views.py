from django.contrib.auth.decorators import login_required
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
    topic = get_object_or_404(Topic, pk=pk)
    course = topic.course
    if course.user != request.user:
        raise Http404()

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

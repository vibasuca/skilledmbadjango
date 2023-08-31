import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from quizzes.models import Quiz, Question, Option
from .forms import CourseForm
from .models import *
from .serializers import *


def index(request):
    approved_courses = Course.objects.exclude(approved_at=None)
    context = {
        "courses": approved_courses,
    }
    return render(request, "index.html", context)


def course_details(request, pk, slug):
    course = get_object_or_404(Course, pk=pk, approved_at__isnull=False)
    related_courses = course.user.courses.exclude(pk=course.pk).exclude(
        approved_at=None
    )[:3]
    enrollment = None
    if request.user.is_authenticated:
        enrollment = Enrollment.objects.filter(course=course, user=request.user).first()
    context = {
        "course": course,
        "related_courses": related_courses,
        "enrollment": enrollment,
    }
    return render(request, "sitePages/courseDetails.html", context)


@login_required
def enroll_course(request, course_pk):
    course = get_object_or_404(Course, pk=course_pk, approved_at__isnull=False)
    if request.method != "POST":
        return redirect("courses:course_details", pk=course.pk, slug=course.slug)

    Enrollment.objects.get_or_create(course=course, user=request.user)
    messages.success(request, "You have successfully enrolled in this course.")
    return redirect("courses:course_details", pk=course.pk, slug=course.slug)


@login_required
def list_courses_published(request):
    published = request.user.courses.exclude(approved_at=None)
    pending = request.user.courses.exclude(published_at=None).filter(approved_at=None)
    draft = request.user.courses.filter(published_at=None)
    context = {
        "courses": published,
        "publish_count": published.count(),
        "pending_count": pending.count(),
        "draft_count": draft.count(),
    }
    return render(request, "courses/course_list.html", context)


@login_required
def list_courses_pending(request):
    published = request.user.courses.exclude(approved_at=None)
    pending = request.user.courses.exclude(published_at=None).filter(approved_at=None)
    draft = request.user.courses.filter(published_at=None)
    context = {
        "courses": pending,
        "publish_count": published.count(),
        "pending_count": pending.count(),
        "draft_count": draft.count(),
    }
    return render(request, "courses/course_list.html", context)


@login_required
def list_courses_draft(request):
    published = request.user.courses.exclude(approved_at=None)
    pending = request.user.courses.exclude(published_at=None).filter(approved_at=None)
    draft = request.user.courses.filter(published_at=None)
    context = {
        "courses": draft,
        "publish_count": published.count(),
        "pending_count": pending.count(),
        "draft_count": draft.count(),
    }
    return render(request, "courses/course_list.html", context)


@require_POST
@login_required
def create_course(request):
    course = Course.objects.create(user=request.user, title="New Course")
    redirect_url = f"/courses/update-course/{course.pk}/"
    return JsonResponse({"success": True, "redirect_url": redirect_url})


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
            instance.approved_at = None
            instance.save()

            return redirect("courses:update_course", pk=instance.pk)
    else:
        form = CourseForm(instance=course)

    context = {
        "form": form,
        "course": course,
        "categories": CourseCategory.objects.all(),
        "tags": CourseTag.objects.all(),
    }
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
    serializer = CreateTopicSerializer(data=request.POST, context={"course": course})
    if serializer.is_valid():
        topic = serializer.save()
        return JsonResponse({"message": "Topic created successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


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
    serializer = UpdateTopicSerializer(instance=topic, data=request.POST)
    if serializer.is_valid():
        topic = serializer.save()
        return JsonResponse({"message": "Topic updated successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@login_required
def list_topics(request, course_pk):
    course = get_object_or_404(Course, user=request.user, pk=course_pk)
    topics = course.topics.all()
    topics = topics.values("id", "title", "summary", "sort_order")
    return JsonResponse({"topics": list(topics)})


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
    serializer = CreateLessonSerializer(
        data=data, context={"topic": topic, "user": request.user}
    )
    if serializer.is_valid():
        lesson = serializer.save()
        return JsonResponse({"message": "Lesson created successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@login_required
def list_topic_items(request, topic_pk):
    topic = get_object_or_404(Topic, course__user=request.user, pk=topic_pk)
    topic_items = topic.items.all()
    serializer = ListTopicItemSerializer(topic_items, many=True)
    return JsonResponse({"data": serializer.data})


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
    data = json.loads(request.body)
    serializer = UpdateLessonSerializer(
        instance=lesson, data=data, context={"user": user}
    )
    if serializer.is_valid():
        lesson = serializer.save()
        return JsonResponse({"message": "Lesson updated successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def create_assignment(request, topic_pk):
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
    serializer = CreateAssignmentSerializer(
        data=data, context={"topic": topic, "user": request.user}
    )
    if serializer.is_valid():
        assignment = serializer.save()
        return JsonResponse({"message": "Assignment created successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def update_assignment(request, pk):
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
    assignment = get_object_or_404(
        Assignment, pk=pk, topic_item__topic__course__user=user
    )
    data = json.loads(request.body)
    serializer = UpdateAssignmentSerializer(
        instance=assignment, data=data, context={"user": user}
    )
    if serializer.is_valid():
        assignment = serializer.save()
        return JsonResponse({"message": "Assignment updated successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def create_quiz(request, topic_pk):
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
    serializer = CreateQuizSerializer(data=data, context={"topic": topic})
    if serializer.is_valid():
        quiz = serializer.save()
        return JsonResponse(
            {"data": serializer.data, "message": "Quiz created successfully."}
        )
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def update_quiz(request, pk):
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
    quiz = get_object_or_404(Quiz, pk=pk, topic_item__topic__course__user=user)
    data = json.loads(request.body)
    serializer = UpdateQuizSerializer(instance=quiz, data=data)
    if serializer.is_valid():
        quiz = serializer.save()
        return JsonResponse(
            {"data": serializer.data, "message": "Quiz updated successfully."}
        )
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def create_question(request, quiz_pk):
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
    quiz = get_object_or_404(
        Quiz, pk=quiz_pk, topic_item__topic__course__user=request.user
    )
    data = json.loads(request.body)
    serializer = CreateQuestionSerializer(data=data, context={"quiz": quiz})
    if serializer.is_valid():
        question = serializer.save()
        return JsonResponse(
            {"data": serializer.data, "message": "Question created successfully."}
        )
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def update_question(request, pk):
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
    question = get_object_or_404(
        Question, pk=pk, quiz__topic_item__topic__course__user=request.user
    )
    data = json.loads(request.body)
    serializer = UpdateQuestionSerializer(instance=question, data=data)
    if serializer.is_valid():
        question = serializer.save()
        return JsonResponse({"message": "Question updated successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@login_required
def list_questions(request, quiz_pk):
    quiz = get_object_or_404(
        Quiz, pk=quiz_pk, topic_item__topic__course__user=request.user
    )
    questions = quiz.questions.all()
    serializer = ListQuestionSerializer(questions, many=True)
    return JsonResponse({"data": list(serializer.data)})


@require_POST
@login_required
def create_option(request, question_pk):
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
    question = get_object_or_404(
        Question, pk=question_pk, quiz__topic_item__topic__course__user=request.user
    )
    data = json.loads(request.body)
    serializer = CreateOptionSerializer(
        data=data, context={"question": question, "user": request.user}
    )
    if serializer.is_valid():
        option = serializer.save()
        return JsonResponse({"message": "Option created successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@require_POST
@login_required
def update_option(request, pk):
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
    option = get_object_or_404(
        Option, pk=pk, question__quiz__topic_item__topic__course__user=request.user
    )
    data = json.loads(request.body)
    serializer = UpdateOptionSerializer(
        instance=option, data=data, context={"user": request.user}
    )
    if serializer.is_valid():
        option = serializer.save()
        return JsonResponse({"message": "Option updated successfully."})
    return JsonResponse({"error": serializer.errors}, status=400)


@login_required
def list_options(request, question_pk):
    question = get_object_or_404(
        Question, pk=question_pk, quiz__topic_item__topic__course__user=request.user
    )
    options = question.options.all()
    serializer = ListOptionSerializer(options, many=True)
    return JsonResponse({"data": serializer.data})

import json
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import F
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from quizzes.models import Quiz, Question, Option
from .forms import CourseForm
from .models import *


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
            instance.save()

            return redirect("courses:update_course", pk=instance.pk)
        print(form.errors)
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
        return JsonResponse({"message": "Topic updated successfully."})
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
            assignment = json.loads(
                serializers.serialize("json", [topic_item.assignment])
            )[0]["fields"]
            assignment["id"] = topic_item.assignment.pk

            attachments = topic_item.assignment.attachments.all()
            attachments = json.loads(serializers.serialize("json", attachments))
            attachments_serialized = []
            for attachment in attachments:
                att = attachment["fields"]
                att["id"] = attachment["pk"]
                attachments_serialized.append(att)
            assignment["attachments"] = attachments_serialized

            item["assignment"] = assignment

        elif topic_item.quiz:
            quiz = json.loads(serializers.serialize("json", [topic_item.quiz]))[0][
                "fields"
            ]
            quiz["id"] = topic_item.quiz.pk

            item["quiz"] = quiz

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
    title = data.get("title", "")
    summary = data.get("summary", "")
    time_limit = data.get("time_limit")
    time_limit_unit = data.get("time_limit_unit")
    total_points = data.get("total_points")
    min_pass_points = data.get("min_pass_points")
    max_file_uploads = data.get("max_file_uploads")
    file_size_limit = data.get("file_size_limit")

    attachments = data.get("attachments")
    if attachments:
        attachments = Media.objects.filter(pk__in=attachments, user=request.user)

    assignment = Assignment(
        title=title,
        summary=summary,
        time_limit=time_limit,
        time_limit_unit=time_limit_unit,
        total_points=total_points,
        min_pass_points=min_pass_points,
        max_file_uploads=max_file_uploads,
        file_size_limit=file_size_limit,
    )

    # Validate the assignment instance before saving
    try:
        assignment.full_clean()
        assignment.save()
        if attachments:
            assignment.attachments.set(attachments)

        sort_order = topic.items.count() + 1
        TopicItem.objects.create(
            topic=topic, assignment=assignment, sort_order=sort_order
        )
        return JsonResponse({"message": "Assignment created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    topic_item = assignment.topic_item
    topic = topic_item.topic

    data = json.loads(request.body)
    title = data.get("title", "")
    summary = data.get("summary", "")
    time_limit = data.get("time_limit")
    time_limit_unit = data.get("time_limit_unit")
    total_points = data.get("total_points")
    min_pass_points = data.get("min_pass_points")
    max_file_uploads = data.get("max_file_uploads")
    file_size_limit = data.get("file_size_limit")

    attachments = data.get("attachments")
    if attachments:
        attachments = Media.objects.filter(pk__in=attachments, user=user)

    sort_order = data.get("sort_order")

    assignment.title = title
    assignment.summary = summary
    assignment.time_limit = time_limit
    assignment.time_limit_unit = time_limit_unit
    assignment.total_points = total_points
    assignment.min_pass_points = min_pass_points
    assignment.max_file_uploads = max_file_uploads
    assignment.file_size_limit = file_size_limit

    # Validate the assignment instance before saving
    try:
        assignment.full_clean()
        assignment.save()
        assignment.attachments.set(attachments)

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

        return JsonResponse({"message": "Assignment updated successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    title = data.get("title", "")
    summary = data.get("summary", "")
    time_limit = data.get("time_limit")
    time_limit_unit = data.get("time_limit_unit")
    hide_time_display = data.get("hide_time_display")
    feedback_mode = data.get("feedback_mode")
    max_attempts_allowed = data.get("max_attempts_allowed")
    passing_percentage = data.get("passing_percentage")
    max_questions = data.get("max_questions")
    auto_start = data.get("auto_start")
    hide_question_no = data.get("hide_question_no")
    short_ans_char_limit = data.get("short_ans_char_limit")
    long_ans_char_limit = data.get("long_ans_char_limit")

    quiz = Quiz(
        title=title,
        summary=summary,
        time_limit=time_limit,
        time_limit_unit=time_limit_unit,
        hide_time_display=hide_time_display,
        feedback_mode=feedback_mode,
        max_attempts_allowed=max_attempts_allowed,
        passing_percentage=passing_percentage,
        max_questions=max_questions,
        auto_start=auto_start,
        hide_question_no=hide_question_no,
        short_ans_char_limit=short_ans_char_limit,
        long_ans_char_limit=long_ans_char_limit,
    )

    # Validate the assignment instance before saving
    try:
        quiz.full_clean()
        quiz.save()

        sort_order = topic.items.count() + 1
        TopicItem.objects.create(topic=topic, quiz=quiz, sort_order=sort_order)
        return JsonResponse({"message": "Quiz created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    topic_item = quiz.topic_item
    topic = topic_item.topic

    data = json.loads(request.body)
    title = data.get("title", "")
    summary = data.get("summary", "")
    time_limit = data.get("time_limit")
    time_limit_unit = data.get("time_limit_unit")
    hide_time_display = data.get("hide_time_display")
    feedback_mode = data.get("feedback_mode")
    max_attempts_allowed = data.get("max_attempts_allowed")
    passing_percentage = data.get("passing_percentage")
    max_questions = data.get("max_questions")
    auto_start = data.get("auto_start")
    hide_question_no = data.get("hide_question_no")
    short_ans_char_limit = data.get("short_ans_char_limit")
    long_ans_char_limit = data.get("long_ans_char_limit")

    sort_order = data.get("sort_order")

    quiz.title = title
    quiz.summary = summary
    quiz.time_limit = time_limit
    quiz.time_limit_unit = time_limit_unit
    quiz.hide_time_display = hide_time_display
    quiz.feedback_mode = feedback_mode
    quiz.max_attempts_allowed = max_attempts_allowed
    quiz.passing_percentage = passing_percentage
    quiz.max_questions = max_questions
    quiz.auto_start = auto_start
    quiz.hide_question_no = hide_question_no
    quiz.short_ans_char_limit = short_ans_char_limit
    quiz.long_ans_char_limit = long_ans_char_limit

    # Validate the quiz instance before saving
    try:
        quiz.full_clean()
        quiz.save()

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

        return JsonResponse({"message": "Quiz updated successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    title = data.get("title", "")
    description = data.get("description", "")
    type = data.get("type")
    answer_required = data.get("answer_required")
    randomize_options = data.get("randomize_options")
    points = data.get("points")
    display_points = data.get("display_points")
    tf_correct_answer = data.get("tf_correct_answer")
    tf_true_first = data.get("tf_true_first")
    fb_question_title = data.get("fb_question_title", "")
    fb_correct_answer = data.get("fb_correct_answer", "")

    sort_order = quiz.questions.count() + 1
    question = Question(
        quiz=quiz,
        title=title,
        description=description,
        type=type,
        answer_required=answer_required,
        randomize_options=randomize_options,
        points=points,
        display_points=display_points,
        tf_correct_answer=tf_correct_answer,
        tf_true_first=tf_true_first,
        fb_question_title=fb_question_title,
        fb_correct_answer=fb_correct_answer,
        sort_order=sort_order,
    )

    # Validate the assignment instance before saving
    try:
        question.full_clean()
        question.save()

        return JsonResponse({"message": "Question created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    title = data.get("title", "")
    description = data.get("description", "")
    type = data.get("type")
    answer_required = data.get("answer_required")
    randomize_options = data.get("randomize_options")
    points = data.get("points")
    display_points = data.get("display_points")
    tf_correct_answer = data.get("tf_correct_answer")
    tf_true_first = data.get("tf_true_first")
    fb_question_title = data.get("fb_question_title", "")
    fb_correct_answer = data.get("fb_correct_answer", "")

    sort_order = data.get("sort_order")

    question.title = title
    question.description = description
    question.type = type
    question.answer_required = answer_required
    question.randomize_options = randomize_options
    question.points = points
    question.display_points = display_points
    question.tf_correct_answer = tf_correct_answer
    question.tf_true_first = tf_true_first
    question.fb_question_title = fb_question_title
    question.fb_correct_answer = fb_correct_answer

    # Validate the question instance before saving
    try:
        question.full_clean()
        question.save()

        # Shift the sort_order of other questions if needed
        if sort_order > question.sort_order:
            questions = question.quiz.questions.filter(
                sort_order__gt=question.sort_order, sort_order__lte=sort_order
            )
            questions.update(sort_order=F("sort_order") - 1)

        elif sort_order < question.sort_order:
            questions = question.quiz.questions.filter(
                sort_order__lt=question.sort_order, sort_order__gte=sort_order
            )
            questions.update(sort_order=F("sort_order") + 1)

        question.sort_order = sort_order
        question.save()

        return JsonResponse({"message": "Question updated successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


@login_required
def list_questions(request, quiz_pk):
    quiz = get_object_or_404(
        Quiz, pk=quiz_pk, topic_item__topic__course__user=request.user
    )
    questions = quiz.questions.all()
    questions = questions.values(
        "id",
        "title",
        "description",
        "type",
        "answer_required",
        "randomize_options",
        "points",
        "display_points",
        "tf_correct_answer",
        "tf_true_first",
        "fb_question_title",
        "fb_correct_answer",
        "sort_order",
    )
    return JsonResponse({"data": list(questions)})


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
    title = data.get("title", "")
    image = data.get("image")
    if image:
        image = Media.objects.get(pk=image, user=request.user)
    display_format = data.get("display_format")
    o_correct_order = data.get("o_correct_order")
    m_matched_ans_title = data.get("m_matched_ans_title", "")
    is_correct = data.get("is_correct")

    sort_order = question.options.count() + 1
    option = Option(
        question=question,
        title=title,
        image=image,
        display_format=display_format,
        o_correct_order=o_correct_order,
        m_matched_ans_title=m_matched_ans_title,
        is_correct=is_correct,
        sort_order=sort_order,
    )

    # Validate the assignment instance before saving
    try:
        option.full_clean()
        option.save()

        return JsonResponse({"message": "Option created successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


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
    title = data.get("title", "")
    image = data.get("image")
    if image:
        image = Media.objects.get(pk=image, user=request.user)
    display_format = data.get("display_format")
    o_correct_order = data.get("o_correct_order")
    m_matched_ans_title = data.get("m_matched_ans_title", "")
    is_correct = data.get("is_correct")

    sort_order = data.get("sort_order")

    option.title = title
    option.image = image
    option.display_format = display_format
    option.o_correct_order = o_correct_order
    option.m_matched_ans_title = m_matched_ans_title
    option.is_correct = is_correct

    # Validate the option instance before saving
    try:
        option.full_clean()
        option.save()

        # Shift the sort_order of other options if needed
        if sort_order > option.sort_order:
            options = option.question.options.filter(
                sort_order__gt=option.sort_order, sort_order__lte=sort_order
            )
            options.update(sort_order=F("sort_order") - 1)

        elif sort_order < option.sort_order:
            options = option.question.options.filter(
                sort_order__lt=option.sort_order, sort_order__gte=sort_order
            )
            options.update(sort_order=F("sort_order") + 1)

        option.sort_order = sort_order
        option.save()

        return JsonResponse({"message": "Option updated successfully."})
    except ValidationError as e:
        errors = dict(e)
        return JsonResponse({"error": errors}, status=400)


@login_required
def list_options(request, question_pk):
    question = get_object_or_404(
        Question, pk=question_pk, quiz__topic_item__topic__course__user=request.user
    )
    options = question.options.all()
    options = options.values(
        "id",
        "title",
        "image",
        "display_format",
        "o_correct_order",
        "m_matched_ans_title",
        "is_correct",
        "sort_order",
    )
    return JsonResponse({"data": list(options)})

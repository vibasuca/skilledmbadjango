import json
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Question, Option, Answer, Attempt


@require_POST
@login_required
def mark_answer(request, attempt_pk):
    attempt = get_object_or_404(Attempt, pk=attempt_pk, quiz__user=request.user)
    question_pk = request.POST.get("question_id")
    answers = attempt.answers.filter(attempt=attempt, question__pk=question_pk)
    status = request.POST.get("status")
    answers.update(status=status)
    return JsonResponse({"success": True})


@require_POST
@login_required
def submit_answer(request, attempt_pk):
    """
    Request Format:
    {
        "answers": [
            {
                "question_id": 1,
                "option_id": 1,
                "tf_answer": true,
                "answer_text": "Answer text",
                "o_answer_order": 1
            },
            ...
        ]
    }
    Errors on failure:
    {
        "error": [
            {
                "question": [
                    "This field is required."
                ]
            },
            null,
            ...
        ]
    }
    """
    attempt = get_object_or_404(Attempt, pk=attempt_pk, user=request.user)
    data = json.loads(request.body)
    answers = data.get("answers")
    answer_instances = []
    errors = []
    has_errors = False
    for answer in answers:
        question = Question.objects.get(pk=answer.get("question_id"))
        option = Option.objects.filter(pk=answer.get("option_id")).first()
        answer_instance = Answer(
            attempt=attempt,
            question=question,
            option=option,
            tf_answer=answer.get("tf_answer"),
            answer_text=answer.get("answer_text"),
            o_answer_order=answer.get("o_answer_order"),
        )

        # Validate the instance before saving
        try:
            answer_instance.full_clean()
            answer_instances.append(answer_instance)
            errors.append(None)
        except ValidationError as e:
            error = dict(e)
            errors.append(error)
            has_errors = True

    if has_errors:
        return JsonResponse({"error": errors}, status=400)

    question.answers.filter(attempt=attempt).delete()
    for answer_instance in answer_instances:
        answer_instance.save()

    return JsonResponse({"message": "Answer submitted successfully."})


# @login_required
# def fetch_answers(request, attempt_pk):
#     attempt = get_object_or_404(Attempt, pk=attempt_pk, user=request.user)
#     questions = attempt.quiz.questions.all()
#     answers = []
#     for question in questions:
#         answer = attempt.answers.filter(question=question).first()
#         if answer:
#             answers.append(answer)
#         else:
#             answers.append(None)
#     return JsonResponse({"answers": answers})

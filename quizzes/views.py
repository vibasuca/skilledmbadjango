from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Question, Answer


@require_POST
@login_required
def mark_answer(request, pk):
    answer = get_object_or_404(
        Answer,
        pk=pk,
        question__quiz__topic_item__topic__course__user=request.user,
    )
    answer.status = request.POST.get("status")
    answer.save()
    return JsonResponse({"success": True})

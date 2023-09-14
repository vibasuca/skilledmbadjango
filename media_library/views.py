from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import *


@login_required
def upload_media(request):
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
    if request.method == "POST" and request.FILES.get("file"):
        user = request.user
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        alt_text = request.POST.get("alt_text", "")
        caption = request.POST.get("caption", "")

        media = Media(
            user=user,
            file=request.FILES["file"],
            title=title,
            description=description,
            alt_text=alt_text,
            caption=caption,
        )

        # Validate the media instance before saving
        try:
            media.full_clean()
            media.save()
            return JsonResponse({"message": "Media uploaded successfully."})
        except ValidationError as e:
            errors = dict(e)
            return JsonResponse({"error": errors}, status=400)

    return JsonResponse(
        {"error": "Invalid request. Make sure to include a file."}, status=400
    )


@login_required
def list_media(request):
    """
    Can filter like this: ?month=7&year=2023&q=hello
    """
    # Get the month, year, and search query from the query parameters (if provided)
    month = request.GET.get("month")
    year = request.GET.get("year")
    search_query = request.GET.get("q", "")

    # Filter media based on the month and year (if provided)
    media_queryset = Media.objects.filter(user=request.user)
    if month and year:
        media_queryset = media_queryset.filter(
            created_at__year=year, created_at__month=month
        )

    # Perform a case-insensitive search based on both file name and title
    if search_query:
        media_queryset = media_queryset.filter(
            Q(file__icontains=search_query) | Q(title__icontains=search_query)
        )

    # Convert media queryset to a list of dictionaries
    media_list = [
        {
            "id": media.id,
            "file": media.file.url,
            "thumbnail": media.thumbnail.url,
            "title": media.title,
            "description": media.description,
            "alt_text": media.alt_text,
            "caption": media.caption,
            "size": media.get_size(),
            "created_at": media.created_at,
        }
        for media in media_queryset
    ]

    return JsonResponse({"media": media_list})


@login_required
def update_media(request, media_id):
    media = get_object_or_404(Media, id=media_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        alt_text = request.POST.get("alt_text")
        caption = request.POST.get("caption")

        # Update the media object
        media.title = title
        media.description = description
        media.alt_text = alt_text
        media.caption = caption

        try:
            media.full_clean()  # Run model validation (e.g., field length, content, etc.)
            media.save()  # Save the changes if the validation is successful
            return JsonResponse({"message": "Media updated successfully."})
        except ValidationError as e:
            errors = dict(e)
            return JsonResponse({"error": errors}, status=400)

    return JsonResponse(
        {"error": "Invalid request method or media not found."}, status=400
    )


@login_required
def read_media(request, media_id):
    media = get_object_or_404(Media, id=media_id, user=request.user)
    return JsonResponse(
        {
            "id": media.id,
            "file": media.file.url,
            "thumbnail": media.thumbnail.url,
            "title": media.title,
            "description": media.description,
            "alt_text": media.alt_text,
            "caption": media.caption,
            "created_at": media.created_at,
        }
    )

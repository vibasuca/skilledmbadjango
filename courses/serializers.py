from rest_framework import serializers
from django.db.models import F
from quizzes.models import Quiz, Question, Option
from .models import *
from .utils import shift_items


class CreateTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("id", "title", "summary")

    def create(self, validated_data):
        course = self.context["course"]
        sort_order = course.topics.count() + 1
        instance = self.Meta.model.objects.create(
            course=course, sort_order=sort_order, **validated_data
        )
        return instance


class UpdateTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ("id", "title", "summary", "sort_order")

    def update(self, instance, validated_data):
        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(sort_order, instance, instance.course.topics)
        return super().update(instance, validated_data)


class CreateLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "content",
            "feature_image",
            "attachments",
            "enable_preview",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["feature_image"].queryset = self.context["user"].media.all()
        self.fields["attachments"].queryset = self.context["user"].media.all()

    def create(self, validated_data):
        topic = self.context["topic"]
        sort_order = topic.items.count() + 1
        attachments = validated_data.pop("attachments", [])
        lesson = self.Meta.model.objects.create(**validated_data)
        lesson.attachments.set(attachments)
        TopicItem.objects.create(topic=topic, lesson=lesson, sort_order=sort_order)

        return lesson


class UpdateLessonSerializer(serializers.ModelSerializer):
    sort_order = serializers.IntegerField(min_value=1, required=False)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "content",
            "feature_image",
            "attachments",
            "enable_preview",
            "sort_order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["feature_image"].queryset = self.context["user"].media.all()
        self.fields["attachments"].queryset = self.context["user"].media.all()

    def update(self, instance, validated_data):
        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(
                sort_order, instance.topic_item, instance.topic_item.topic.items
            )
        attachments = validated_data.pop("attachments", [])
        lesson = super().update(instance, validated_data)
        lesson.attachments.set(attachments)
        return lesson


class MediaSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = (
            "id",
            "file",
            "title",
            "description",
            "alt_text",
            "caption",
            "size",
            "created_at",
        )

    def get_size(self, obj):
        return obj.get_size()


class LessonSerializer(serializers.ModelSerializer):
    feature_image_data = MediaSerializer(source="feature_image", read_only=True)
    attachments_data = MediaSerializer(source="attachments", read_only=True, many=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "content",
            "feature_image",
            "feature_image_data",
            "attachments",
            "attachments_data",
            "enable_preview",
        )


class AssignmentSerializer(serializers.ModelSerializer):
    attachments_data = MediaSerializer(source="attachments", read_only=True, many=True)
    time_limit_hours = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "summary",
            "attachments",
            "attachments_data",
            "time_limit",
            "time_limit_hours",
            "time_limit_unit",
            "total_points",
            "min_pass_points",
            "max_file_uploads",
            "file_size_limit",
        )

    def get_time_limit_hours(self, obj):
        value = obj.time_limit
        total_seconds = value.total_seconds()
        total_hours = int(total_seconds // 3600)
        remaining_minutes = int((total_seconds % 3600) // 60)
        return total_hours


class QuizSerializer(serializers.ModelSerializer):
    time_limit_hours = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "summary",
            "time_limit",
            "time_limit_hours",
            "time_limit_unit",
            "hide_time_display",
            "feedback_mode",
            "max_attempts_allowed",
            "passing_percentage",
            "max_questions",
            "auto_start",
            "hide_question_no",
            "short_ans_char_limit",
            "long_ans_char_limit",
            "created_at",
            "updated_at",
        )

    def get_time_limit_hours(self, obj):
        value = obj.time_limit
        total_seconds = value.total_seconds()
        total_hours = int(total_seconds // 3600)
        remaining_minutes = int((total_seconds % 3600) // 60)
        return total_hours


class ListTopicItemSerializer(serializers.ModelSerializer):
    lesson_data = LessonSerializer(source="lesson", read_only=True)
    assignment_data = AssignmentSerializer(source="assignment", read_only=True)
    quiz_data = QuizSerializer(source="quiz", read_only=True)

    class Meta:
        model = TopicItem
        fields = (
            "id",
            "sort_order",
            "lesson",
            "lesson_data",
            "assignment",
            "assignment_data",
            "quiz",
            "quiz_data",
        )


class CreateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "summary",
            "attachments",
            "time_limit",
            "time_limit_unit",
            "total_points",
            "min_pass_points",
            "max_file_uploads",
            "file_size_limit",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachments"].queryset = self.context["user"].media.all()

    def create(self, validated_data):
        topic = self.context["topic"]
        sort_order = topic.items.count() + 1
        attachments = validated_data.pop("attachments", [])
        assignment = self.Meta.model.objects.create(**validated_data)
        assignment.attachments.set(attachments)
        TopicItem.objects.create(
            topic=topic, assignment=assignment, sort_order=sort_order
        )
        return assignment


class UpdateAssignmentSerializer(serializers.ModelSerializer):
    sort_order = serializers.IntegerField(min_value=1, required=False)

    class Meta:
        model = Assignment
        fields = (
            "id",
            "title",
            "summary",
            "attachments",
            "time_limit",
            "time_limit_unit",
            "total_points",
            "min_pass_points",
            "max_file_uploads",
            "file_size_limit",
            "sort_order",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["attachments"].queryset = self.context["user"].media.all()

    def update(self, instance, validated_data):
        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(
                sort_order, instance.topic_item, instance.topic_item.topic.items
            )
        attachments = validated_data.pop("attachments", [])
        assignment = super().update(instance, validated_data)
        assignment.attachments.set(attachments)
        return assignment


class CreateQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "summary",
            "time_limit",
            "time_limit_unit",
            "hide_time_display",
            "feedback_mode",
            "max_attempts_allowed",
            "passing_percentage",
            "max_questions",
            "auto_start",
            "hide_question_no",
            "short_ans_char_limit",
            "long_ans_char_limit",
            "topic_item",
        )
        extra_kwargs = {"topic_item": {"read_only": True}}

    def create(self, validated_data):
        topic = self.context["topic"]
        sort_order = topic.items.count() + 1
        quiz = self.Meta.model.objects.create(**validated_data)
        TopicItem.objects.create(topic=topic, quiz=quiz, sort_order=sort_order)

        return quiz


class UpdateQuizSerializer(serializers.ModelSerializer):
    sort_order = serializers.IntegerField(min_value=1, required=False)

    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "summary",
            "time_limit",
            "time_limit_unit",
            "hide_time_display",
            "feedback_mode",
            "max_attempts_allowed",
            "passing_percentage",
            "max_questions",
            "auto_start",
            "hide_question_no",
            "short_ans_char_limit",
            "long_ans_char_limit",
            "sort_order",
            "topic_item",
        )
        extra_kwargs = {"topic_item": {"read_only": True}}

    def update(self, instance, validated_data):
        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(
                sort_order, instance.topic_item, instance.topic_item.topic.items
            )
        return super().update(instance, validated_data)


class CreateQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
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
        )

    def create(self, validated_data):
        quiz = self.context["quiz"]
        sort_order = quiz.questions.count() + 1
        instance = self.Meta.model.objects.create(
            quiz=quiz, sort_order=sort_order, **validated_data
        )
        return instance


class UpdateQuestionSerializer(serializers.ModelSerializer):
    sort_order = serializers.IntegerField(min_value=1, required=False)
    correct_options = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Question
        fields = (
            "id",
            "title",
            "description",
            "type",
            "answer_required",
            "randomize_options",
            "points",
            "display_points",
            "sort_order",
            "tf_correct_answer",
            "tf_true_first",
            "fb_question_title",
            "fb_correct_answer",
            "correct_options",
        )

    def update(self, instance, validated_data):
        # Update correct options
        correct_options = validated_data.pop("correct_options", [])
        if correct_options:
            type = validated_data.get("type")
            instance.options.filter(type=type).update(is_correct=False)
            instance.options.filter(id__in=correct_options, type=type).update(
                is_correct=True
            )

        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(sort_order, instance, instance.quiz.questions)
        return super().update(instance, validated_data)


class CreateOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = (
            "id",
            "title",
            "image",
            "display_format",
            "is_correct",
            "type",
            "m_matched_ans_title",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].queryset = self.context["user"].media.all()

    def create(self, validated_data):
        question = self.context["question"]
        sort_order = question.options.count() + 1
        instance = self.Meta.model.objects.create(
            question=question, sort_order=sort_order, **validated_data
        )
        return instance


class UpdateOptionSerializer(serializers.ModelSerializer):
    sort_order = serializers.IntegerField(min_value=1)

    class Meta:
        model = Option
        fields = (
            "id",
            "title",
            "image",
            "display_format",
            "is_correct",
            "sort_order",
            "type",
            "m_matched_ans_title",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].queryset = self.context["user"].media.all()

    def update(self, instance, validated_data):
        # Shift sort order of others if necessary
        sort_order = validated_data.get("sort_order")
        if sort_order:
            shift_items(sort_order, instance, instance.question.options)
        return super().update(instance, validated_data)


class ListOptionSerializer(serializers.ModelSerializer):
    image_data = MediaSerializer(source="image", read_only=True)

    class Meta:
        model = Option
        fields = (
            "id",
            "title",
            "image",
            "image_data",
            "display_format",
            "is_correct",
            "sort_order",
            "type",
            "m_matched_ans_title",
        )


class ListQuestionSerializer(serializers.ModelSerializer):
    options_data = ListOptionSerializer(source="options", read_only=True, many=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "title",
            "description",
            "type",
            "answer_required",
            "randomize_options",
            "points",
            "display_points",
            "sort_order",
            "tf_correct_answer",
            "tf_true_first",
            "fb_question_title",
            "fb_correct_answer",
            "options",
            "options_data",
        )

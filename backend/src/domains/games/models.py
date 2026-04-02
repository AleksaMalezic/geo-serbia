from math import atan2, cos, radians, sin, sqrt

from tortoise import fields
from tortoise.models import Model


class GameSession(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="game_sessions")
    total_score = fields.FloatField(default=0)
    rounds_played = fields.FloatField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "game_sessions"


class Round(Model):
    id = fields.IntField(pk=True)
    session = fields.ForeignKeyField("models.GameSession", related_name="rounds")
    location = fields.ForeignKeyField("models.Location", related_name="rounds")
    guessed_latitude = fields.FloatField()
    guessed_longitude = fields.FloatField()
    distance_km = fields.FloatField()
    base_score = fields.FloatField(default=0)
    hint_penalty_percent = fields.FloatField(default=0)
    hints_used_count = fields.IntField(default=0)
    score = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "rounds"

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius = 6371
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return radius * c

    @staticmethod
    def calculate_score(distance_km: float) -> float:
        if distance_km < 1:
            return 5000
        if distance_km < 5:
            return 4000 - (distance_km * 200)
        if distance_km < 20:
            return 3000 - (distance_km * 50)
        if distance_km < 100:
            return 2000 - (distance_km * 10)
        return max(0, 1000 - distance_km * 2)


class UserSkillProfile(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="skill_profile", unique=True)
    skill_rating = fields.FloatField(default=52)
    recent_avg_distance_km = fields.FloatField(default=0)
    recent_avg_points = fields.FloatField(default=0)
    consistency_index = fields.FloatField(default=0)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_skill_profile"


class LocationDifficultyProfile(Model):
    id = fields.IntField(pk=True)
    location = fields.ForeignKeyField("models.Location", related_name="difficulty_profile", unique=True)
    difficulty_rating = fields.FloatField(default=50)
    global_avg_distance_km = fields.FloatField(default=0)
    global_avg_points = fields.FloatField(default=0)
    attempt_count = fields.IntField(default=0)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "location_difficulty_profile"


class AdaptiveDecisionLog(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="adaptive_decisions")
    mode = fields.CharField(max_length=20, default="adaptive")
    chosen_band = fields.CharField(max_length=20, default="normal")
    fallback_used = fields.BooleanField(default=False)
    candidate_pool_size = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "adaptive_decision_log"

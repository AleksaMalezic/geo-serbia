from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "token_blacklist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "jti" VARCHAR(128) NOT NULL UNIQUE,
    "token_type" VARCHAR(20) NOT NULL,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_token_black_jti_6fe842" ON "token_blacklist" ("jti");
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(100) NOT NULL UNIQUE,
    "email" VARCHAR(100) NOT NULL UNIQUE,
    "hashed_password" VARCHAR(255) NOT NULL,
    "is_admin" BOOL NOT NULL DEFAULT False,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "locations" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "image_url" VARCHAR(200),
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "is_approved" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "adaptive_decision_log" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "mode" VARCHAR(20) NOT NULL DEFAULT 'adaptive',
    "chosen_band" VARCHAR(20) NOT NULL DEFAULT 'normal',
    "fallback_used" BOOL NOT NULL DEFAULT False,
    "candidate_pool_size" INT NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "game_sessions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "total_score" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "rounds_played" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "location_difficulty_profile" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "difficulty_rating" DOUBLE PRECISION NOT NULL DEFAULT 50,
    "global_avg_distance_km" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "global_avg_points" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "attempt_count" INT NOT NULL DEFAULT 0,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT NOT NULL REFERENCES "locations" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "rounds" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "guessed_latitude" DOUBLE PRECISION NOT NULL,
    "guessed_longitude" DOUBLE PRECISION NOT NULL,
    "distance_km" DOUBLE PRECISION NOT NULL,
    "score" DOUBLE PRECISION NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "location_id" INT NOT NULL REFERENCES "locations" ("id") ON DELETE CASCADE,
    "session_id" INT NOT NULL REFERENCES "game_sessions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user_skill_profile" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "skill_rating" DOUBLE PRECISION NOT NULL DEFAULT 52,
    "recent_avg_distance_km" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "recent_avg_points" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "consistency_index" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
    "cjcB5eQF82IR9yenn4H5Y6Dek="
)

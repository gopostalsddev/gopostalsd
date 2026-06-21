"""Backfill auth schema for legacy SQLite databases

Revision ID: f3a5c1d8e9b0
Revises: b6dd5b87b433
Create Date: 2026-06-20 03:16:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3a5c1d8e9b0'
down_revision = 'b6dd5b87b433'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(column['name'] == column_name for column in inspector.get_columns(table_name))


def _has_index(inspector, table_name, index_name):
    return any(index['name'] == index_name for index in inspector.get_indexes(table_name))


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if 'roles' in tables:
        with op.batch_alter_table('roles', schema=None) as batch_op:
            if not _has_column(inspector, 'roles', 'permissions'):
                batch_op.add_column(sa.Column('permissions', sa.JSON(), nullable=True))
            if not _has_column(inspector, 'roles', 'is_system_role'):
                batch_op.add_column(sa.Column('is_system_role', sa.Boolean(), nullable=False, server_default=sa.false()))
            if not _has_column(inspector, 'roles', 'created_at'):
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
            if not _has_column(inspector, 'roles', 'updated_at'):
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))

    if 'users' in tables:
        with op.batch_alter_table('users', schema=None) as batch_op:
            if not _has_column(inspector, 'users', 'email'):
                batch_op.add_column(sa.Column('email', sa.String(length=120), nullable=True))
            if not _has_column(inspector, 'users', 'password_hash'):
                batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=True))
            if not _has_column(inspector, 'users', 'status'):
                batch_op.add_column(sa.Column('status', sa.String(length=32), nullable=False, server_default='PENDING_VERIFICATION'))
            if not _has_column(inspector, 'users', 'email_verified'):
                batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.false()))
            if not _has_column(inspector, 'users', 'email_verified_at'):
                batch_op.add_column(sa.Column('email_verified_at', sa.DateTime(), nullable=True))
            if not _has_column(inspector, 'users', 'last_login'):
                batch_op.add_column(sa.Column('last_login', sa.DateTime(), nullable=True))
            if not _has_column(inspector, 'users', 'failed_login_attempts'):
                batch_op.add_column(sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
            if not _has_column(inspector, 'users', 'locked_until'):
                batch_op.add_column(sa.Column('locked_until', sa.DateTime(), nullable=True))
            if not _has_column(inspector, 'users', 'created_at'):
                batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
            if not _has_column(inspector, 'users', 'updated_at'):
                batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))

        if _has_column(inspector, 'users', 'email_address'):
            op.execute("""
                UPDATE users
                SET email = lower(email_address)
                WHERE email IS NULL AND email_address IS NOT NULL
            """)

        inspector = sa.inspect(bind)
        if not _has_index(inspector, 'users', 'ix_users_email'):
            op.create_index('ix_users_email', 'users', ['email'], unique=True)

    if 'permissions' not in tables:
        op.create_table(
            'permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('resource', sa.String(length=50), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    if 'user_sessions' not in tables:
        op.create_table(
            'user_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('session_token', sa.String(length=255), nullable=False),
            sa.Column('refresh_token', sa.String(length=255), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('last_accessed', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('refresh_token'),
            sa.UniqueConstraint('session_token')
        )

    if 'password_reset_tokens' not in tables:
        op.create_table(
            'password_reset_tokens',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('token', sa.String(length=255), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('used', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('token')
        )

    if 'email_verification_tokens' not in tables:
        op.create_table(
            'email_verification_tokens',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('token', sa.String(length=255), nullable=False),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('used', sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('token')
        )

    if 'oauth_accounts' not in tables:
        op.create_table(
            'oauth_accounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('provider', sa.String(length=50), nullable=False),
            sa.Column('provider_user_id', sa.String(length=255), nullable=False),
            sa.Column('provider_email', sa.String(length=120), nullable=True),
            sa.Column('access_token', sa.Text(), nullable=True),
            sa.Column('refresh_token', sa.Text(), nullable=True),
            sa.Column('token_expires_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('provider', 'provider_user_id', name='_provider_user_uc')
        )

    inspector = sa.inspect(bind)
    if 'user_sessions' in inspector.get_table_names():
        if not _has_index(inspector, 'user_sessions', 'ix_user_sessions_session_token'):
            op.create_index('ix_user_sessions_session_token', 'user_sessions', ['session_token'], unique=True)
        if not _has_index(inspector, 'user_sessions', 'ix_user_sessions_refresh_token'):
            op.create_index('ix_user_sessions_refresh_token', 'user_sessions', ['refresh_token'], unique=True)

    if 'password_reset_tokens' in inspector.get_table_names() and not _has_index(inspector, 'password_reset_tokens', 'ix_password_reset_tokens_token'):
        op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)

    if 'email_verification_tokens' in inspector.get_table_names() and not _has_index(inspector, 'email_verification_tokens', 'ix_email_verification_tokens_token'):
        op.create_index('ix_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True)


def downgrade():
    # Intentionally left as a no-op; this migration upgrades legacy local SQLite
    # environments in-place and is not safely reversible without data loss.
    pass

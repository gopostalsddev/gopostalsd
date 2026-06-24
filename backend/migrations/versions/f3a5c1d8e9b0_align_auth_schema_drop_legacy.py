"""Align auth schema and drop legacy user columns

Revision ID: f3a5c1d8e9b0
Revises: b6dd5b87b433
Create Date: 2026-06-21 22:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'f3a5c1d8e9b0'
down_revision = 'b6dd5b87b433'
branch_labels = None
depends_on = None


def _has_column(inspector, table_name, column_name):
    return any(column['name'] == column_name for column in inspector.get_columns(table_name))


def _has_index(inspector, table_name, index_name):
    return any(index['name'] == index_name for index in inspector.get_indexes(table_name))


def _has_table(inspector, table_name):
    return table_name in inspector.get_table_names()


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if _has_table(inspector, 'roles'):
        role_columns = {column['name'] for column in inspector.get_columns('roles')}
        if 'permissions' not in role_columns:
            op.add_column('roles', sa.Column('permissions', sa.JSON(), nullable=True))
        if 'is_system_role' not in role_columns:
            op.add_column(
                'roles',
                sa.Column('is_system_role', sa.Boolean(), nullable=False, server_default=sa.false()),
            )
        if 'created_at' not in role_columns:
            op.add_column(
                'roles',
                sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            )
        if 'updated_at' not in role_columns:
            op.add_column(
                'roles',
                sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            )

    inspector = sa.inspect(bind)
    if _has_table(inspector, 'users'):
        user_columns = {column['name'] for column in inspector.get_columns('users')}

        if 'email' not in user_columns:
            op.add_column('users', sa.Column('email', sa.String(length=120), nullable=True))
        if 'password_hash' not in user_columns:
            op.add_column('users', sa.Column('password_hash', sa.String(length=255), nullable=True))
        if 'status' not in user_columns:
            op.add_column(
                'users',
                sa.Column('status', sa.String(length=32), nullable=False, server_default='pending_verification'),
            )
        if 'email_verified' not in user_columns:
            op.add_column(
                'users',
                sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.false()),
            )
        if 'email_verified_at' not in user_columns:
            op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
        if 'last_login' not in user_columns:
            op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
        if 'failed_login_attempts' not in user_columns:
            op.add_column(
                'users',
                sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'),
            )
        if 'locked_until' not in user_columns:
            op.add_column('users', sa.Column('locked_until', sa.DateTime(), nullable=True))
        if 'created_at' not in user_columns:
            op.add_column(
                'users',
                sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            )
        if 'updated_at' not in user_columns:
            op.add_column(
                'users',
                sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            )

        if 'email_address' in user_columns:
            op.execute(sa.text("""
                UPDATE users
                SET email = lower(email_address)
                WHERE (email IS NULL OR email = '') AND email_address IS NOT NULL
            """))

        if 'creation_date' in user_columns and 'created_at' in user_columns:
            op.execute(sa.text("""
                UPDATE users
                SET created_at = creation_date
                WHERE created_at IS NULL AND creation_date IS NOT NULL
            """))

        op.execute(sa.text("""
            UPDATE users
            SET status = lower(status)
            WHERE status IS NOT NULL AND status <> lower(status)
        """))

        if 'shipping_address_id' in user_columns:
            op.alter_column('users', 'shipping_address_id', nullable=True)
        if 'billing_address_id' in user_columns:
            op.alter_column('users', 'billing_address_id', nullable=True)

        inspector = sa.inspect(bind)
        if _has_column(inspector, 'users', 'email'):
            op.alter_column('users', 'email', nullable=False)

        if not _has_index(inspector, 'users', 'ix_users_email'):
            op.create_index('ix_users_email', 'users', ['email'], unique=True)

        inspector = sa.inspect(bind)
        if _has_index(inspector, 'users', 'ix_users_email_address'):
            op.drop_index('ix_users_email_address', table_name='users')
        if _has_column(inspector, 'users', 'email_address'):
            op.drop_column('users', 'email_address')
        if _has_column(inspector, 'users', 'creation_date'):
            op.drop_column('users', 'creation_date')

    inspector = sa.inspect(bind)
    if not _has_table(inspector, 'permissions'):
        op.create_table(
            'permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('resource', sa.String(length=50), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )

    inspector = sa.inspect(bind)
    if not _has_table(inspector, 'user_sessions'):
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
            sa.UniqueConstraint('session_token'),
        )

    inspector = sa.inspect(bind)
    if not _has_table(inspector, 'password_reset_tokens'):
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
            sa.UniqueConstraint('token'),
        )

    inspector = sa.inspect(bind)
    if not _has_table(inspector, 'oauth_accounts'):
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
            sa.UniqueConstraint('provider', 'provider_user_id', name='_provider_user_uc'),
        )

    inspector = sa.inspect(bind)
    if not _has_table(inspector, 'email_verification_tokens'):
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
            sa.UniqueConstraint('token'),
        )

    inspector = sa.inspect(bind)
    if _has_table(inspector, 'user_sessions'):
        if not _has_index(inspector, 'user_sessions', 'ix_user_sessions_session_token'):
            op.create_index('ix_user_sessions_session_token', 'user_sessions', ['session_token'], unique=True)
        if not _has_index(inspector, 'user_sessions', 'ix_user_sessions_refresh_token'):
            op.create_index('ix_user_sessions_refresh_token', 'user_sessions', ['refresh_token'], unique=True)
    if _has_table(inspector, 'password_reset_tokens') and not _has_index(
        inspector, 'password_reset_tokens', 'ix_password_reset_tokens_token'
    ):
        op.create_index('ix_password_reset_tokens_token', 'password_reset_tokens', ['token'], unique=True)
    if _has_table(inspector, 'email_verification_tokens') and not _has_index(
        inspector, 'email_verification_tokens', 'ix_email_verification_tokens_token'
    ):
        op.create_index(
            'ix_email_verification_tokens_token', 'email_verification_tokens', ['token'], unique=True
        )

    inspector = sa.inspect(bind)
    if _has_table(inspector, 'accounts'):
        op.drop_table('accounts')
    if _has_table(inspector, 'hashing_algorithms'):
        op.drop_table('hashing_algorithms')


def downgrade():
    pass

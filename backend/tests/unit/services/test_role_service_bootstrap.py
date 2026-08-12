from server.config import database as db
from server.models.auth import Permission, Role
from server.services.role_service import RoleService


def test_default_role_bootstrap_repairs_partial_state(app):
    with app.app_context():
        db.session.add(
            Role(
                name="CustomStaff",
                description="Pre-existing non-system role",
                permissions=[],
                is_system_role=False,
            )
        )
        db.session.add(
            Permission(
                name="products.read",
                description="Pre-existing permission",
                resource="products",
                action="read",
            )
        )
        db.session.commit()

        service = RoleService()
        service._initialize_default_roles()
        service._initialize_default_roles()

        names = {role.name for role in Role.query.all()}
        assert {"Admin", "RegisteredCustomer", "GuestCustomer"} <= names
        assert "CustomStaff" in names
        assert Permission.query.filter_by(name="products.read").count() == 1
        assert Permission.query.count() == 19

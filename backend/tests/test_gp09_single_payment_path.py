"""GP-09 proves there is only one reachable public charging lifecycle."""

import ast
import inspect
from pathlib import Path
import textwrap

from server.routes.payment_routes import PaymentProcessResource


def test_legacy_payment_route_returns_gone_before_any_business_work():
    source = textwrap.dedent(inspect.getsource(PaymentProcessResource.post))
    function = ast.parse(source).body[0]
    executable = [
        statement for statement in function.body
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
    ]

    assert isinstance(executable[0], ast.Return)
    rendered = ast.unparse(executable[0])
    assert "PAYMENT_ROUTE_RETIRED" in rendered
    assert "410" in rendered


def test_frontend_uses_order_payment_endpoint_not_retired_bypass():
    frontend = Path(__file__).resolve().parents[2] / "frontend" / "src"
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in frontend.rglob("*")
        if path.suffix in {".js", ".jsx", ".ts", ".tsx"}
    )

    assert "/payments/process" not in sources
    assert "/payment`" in sources or "/payment'" in sources or '/payment"' in sources


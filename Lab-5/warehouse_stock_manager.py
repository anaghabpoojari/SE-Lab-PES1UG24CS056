"""Manage warehouse inventory and demonstrate safe stock operations."""

from __future__ import annotations

import ast
import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

LOGGER = logging.getLogger(__name__)
AUDIT_FILE = Path("warehouse_audit.log")
STOCK_FILE = Path("warehouse.json")

warehouse_stock: dict[str, int] = {}


class InventoryError(ValueError):
    """Raised when an inventory operation would create invalid stock data."""


def _validate_sku(sku: str) -> str:
    """Validate and return a non-empty string SKU."""
    if not isinstance(sku, str) or not sku.strip():
        raise InventoryError("SKU must be a non-empty string.")
    return sku.strip()


def _validate_quantity(qty: int, *, allow_zero: bool = False) -> int:
    """Validate an integer stock quantity."""
    if isinstance(qty, bool) or not isinstance(qty, int):
        raise InventoryError("Quantity must be an integer.")
    if qty < 0 or (qty == 0 and not allow_zero):
        raise InventoryError("Quantity must be positive.")
    return qty


def add_stock(sku: str, qty: int, history: list[str] | None = None) -> None:
    """Add a positive quantity of stock and optionally record the action."""
    sku = _validate_sku(sku)
    qty = _validate_quantity(qty)
    warehouse_stock[sku] = warehouse_stock.get(sku, 0) + qty
    if history is not None:
        history.append(f"{datetime.now().isoformat(timespec='seconds')}: Received {qty} units of {sku}")


def remove_stock(sku: str, qty: int) -> None:
    """Remove stock, rejecting unknown SKUs and insufficient quantities."""
    sku = _validate_sku(sku)
    qty = _validate_quantity(qty)
    if sku not in warehouse_stock:
        raise InventoryError(f"Unknown SKU: {sku}")
    if qty > warehouse_stock[sku]:
        raise InventoryError(
            f"Insufficient stock for {sku}: available {warehouse_stock[sku]}, requested {qty}."
        )
    warehouse_stock[sku] -= qty
    if warehouse_stock[sku] == 0:
        del warehouse_stock[sku]


def get_stock(sku: str) -> int:
    """Return stock for a SKU, raising a clear error if it is unknown."""
    sku = _validate_sku(sku)
    try:
        return warehouse_stock[sku]
    except KeyError as exc:
        raise InventoryError(f"Unknown SKU: {sku}") from exc


def sku_checksum(sku: str) -> str:
    """Return a short fingerprint for a printed bin label."""
    return hashlib.sha256(sku.encode("utf-8")).hexdigest()[:6]


def load_stock(file_path: str | Path = STOCK_FILE) -> None:
    """Load stock from JSON after validating its structure and values."""
    global warehouse_stock
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as stock_file:
            loaded: Any = json.load(stock_file)
    except (OSError, json.JSONDecodeError) as exc:
        raise InventoryError(f"Could not load stock from {path}: {exc}") from exc

    if not isinstance(loaded, dict):
        raise InventoryError("Stock file must contain a JSON object.")

    validated: dict[str, int] = {}
    for sku, qty in loaded.items():
        valid_sku = _validate_sku(sku)
        if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
            raise InventoryError(f"Invalid quantity for SKU {valid_sku!r}.")
        validated[valid_sku] = qty
    warehouse_stock = validated


def save_stock(file_path: str | Path = STOCK_FILE) -> None:
    """Save the current inventory as readable JSON."""
    path = Path(file_path)
    try:
        with path.open("w", encoding="utf-8") as stock_file:
            json.dump(warehouse_stock, stock_file, indent=2, sort_keys=True)
            stock_file.write("\n")
    except OSError as exc:
        raise InventoryError(f"Could not save stock to {path}: {exc}") from exc


def print_report() -> None:
    """Print each SKU and its quantity with a short checksum."""
    print("Warehouse Stock Report")
    for sku, quantity in sorted(warehouse_stock.items()):
        print(f"{sku} -> {quantity} units [chk: {sku_checksum(sku)}]")


def check_reorder(threshold: int = 10) -> list[str]:
    """Return SKUs with stock below a positive reorder threshold."""
    threshold = _validate_quantity(threshold)
    return sorted(sku for sku, qty in warehouse_stock.items() if qty < threshold)


def _evaluate_formula(formula: str, current: int) -> int | float:
    """Evaluate a limited arithmetic formula without executing arbitrary code."""
    allowed_binary_ops = {
        ast.Add: lambda left, right: left + right,
        ast.Sub: lambda left, right: left - right,
        ast.Mult: lambda left, right: left * right,
        ast.Div: lambda left, right: left / right,
        ast.FloorDiv: lambda left, right: left // right,
        ast.Mod: lambda left, right: left % right,
        ast.Pow: lambda left, right: left**right,
    }
    allowed_unary_ops = {ast.UAdd: lambda value: value, ast.USub: lambda value: -value}

    def evaluate(node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.Name) and node.id == "current":
            return current
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_binary_ops:
            left = evaluate(node.left)
            right = evaluate(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 10:
                raise InventoryError("Exponent magnitude must not exceed 10.")
            return allowed_binary_ops[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_unary_ops:
            return allowed_unary_ops[type(node.op)](evaluate(node.operand))
        raise InventoryError("Formula contains an unsupported expression.")

    try:
        expression = ast.parse(formula, mode="eval")
        result = evaluate(expression)
    except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
        raise InventoryError(f"Invalid adjustment formula: {exc}") from exc
    if not isinstance(result, (int, float)) or isinstance(result, bool):
        raise InventoryError("Formula must produce a number.")
    if not result >= 0 or result > 2**53:
        raise InventoryError("Adjusted stock must be between 0 and 2^53.")
    if isinstance(result, float) and not result.is_integer():
        raise InventoryError("Adjusted stock must be a whole number.")
    return int(result)


def apply_adjustment(sku: str, formula: str, password: str) -> None:
    """Apply a safe arithmetic adjustment after checking configured credentials."""
    expected_password = os.environ.get("WAREHOUSE_SUPERVISOR_PASSWORD")
    if not expected_password:
        raise InventoryError(
            "Set WAREHOUSE_SUPERVISOR_PASSWORD before using supervisor adjustments."
        )
    if password != expected_password:
        raise InventoryError("Supervisor authentication failed.")

    sku = _validate_sku(sku)
    current = warehouse_stock.get(sku, 0)
    adjusted = _evaluate_formula(formula, current)
    if adjusted == 0:
        warehouse_stock.pop(sku, None)
    else:
        warehouse_stock[sku] = adjusted

    try:
        with AUDIT_FILE.open("a", encoding="utf-8") as audit_file:
            audit_file.write(
                f"adjusted {sku} to {adjusted} using {formula!r} at "
                f"{datetime.now().isoformat(timespec='seconds')}\n"
            )
    except OSError as exc:
        LOGGER.warning("Stock adjustment succeeded, but audit logging failed: %s", exc)


def main() -> None:
    """Run a small, self-contained demonstration of inventory operations."""
    demo_history: list[str] = []
    warehouse_stock.clear()
    add_stock("WID-001", 40, demo_history)
    add_stock("WID-002", 4, demo_history)
    add_stock("WID-404", 15, demo_history)
    remove_stock("WID-001", 12)

    try:
        remove_stock("GHOST-9", 1)
    except InventoryError as exc:
        print(f"Stock removal rejected: {exc}")
    try:
        remove_stock("WID-001", 500)
    except InventoryError as exc:
        print(f"Stock removal rejected: {exc}")

    print("WID-002 stock:", get_stock("WID-002"))
    print("Needs reorder:", check_reorder())

    demo_password = os.environ.get("WAREHOUSE_SUPERVISOR_PASSWORD")
    if demo_password:
        apply_adjustment("WID-002", "current + 25", demo_password)
    else:
        print("Supervisor adjustment skipped: set WAREHOUSE_SUPERVISOR_PASSWORD to enable it.")

    save_stock()
    load_stock()
    print_report()
    print("Stock audit complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
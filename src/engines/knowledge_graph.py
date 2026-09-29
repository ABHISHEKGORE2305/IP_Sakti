"""
Relational Knowledge Graph (left_to_do.md item 11 / Gap Analysis row 10).

    Product -> Ingredient -> Biological Resource -> TK -> Regulation
             -> IP Type -> Authority -> Jurisdiction

Rather than a graph database over a fabricated entity/relation schema
(there is no curated ingredient/biological-resource dataset in this
corpus, and inventing statutory facts about specific plants would risk
exactly the hallucination this platform's guardrails exist to prevent —
see guardrails/confidence.py, agents/citation_agent.py), this module
builds the graph FROM the outputs of the already-verified deterministic
engines (classifier.py, tk_engine.py, abs_engine.py) that this
codebase's test suite (test_engines.py) already covers. Every edge here
traces back to a specific field in one of those engines' return
contracts — nothing is asserted here that wasn't already asserted (and
tested) there.

The `ingredient` / `biological_resource` nodes are the one place a
free-text label is accepted from the caller — they are rendered as
provided, not looked up or fact-checked, since no such reference data
exists yet in this system.
"""

from engines.classifier import classify_product
from engines.tk_engine import analyze_tk_patentability
from engines.abs_engine import analyze_abs_compliance


def _node(node_id: str, kind: str, label: str, **extra) -> dict:
    return {"id": node_id, "kind": kind, "label": label, **extra}


def _edge(source: str, target: str, relation: str) -> dict:
    return {"source": source, "target": target, "relation": relation}


def build_graph(
    jurisdiction: str = "India",
    ingredient: str | None = None,
    biological_resource: str | None = None,
    classification_inputs: dict | None = None,
    tk_inputs: dict | None = None,
    abs_inputs: dict | None = None,
) -> dict:
    """
    Build a multi-hop graph rooted at "Product", branching through
    whichever of classification / TK / ABS facts the caller supplies.
    Every argument is optional — pass only what's known, and the graph
    covers only those hops (no branch is fabricated to fill a gap).

    Returns {"nodes": [...], "edges": [...]} — plain dicts, JSON-ready.
    """

    nodes: list[dict] = []
    edges: list[dict] = []

    product_id = "product"
    nodes.append(_node(product_id, "Product", "Ayurvedic Product / Formulation"))

    last_ip_source = product_id

    if ingredient:
        ing_id = "ingredient"
        nodes.append(_node(ing_id, "Ingredient", ingredient))
        edges.append(_edge(product_id, ing_id, "contains"))
        last_ip_source = ing_id

        if biological_resource:
            res_id = "biological_resource"
            nodes.append(_node(res_id, "BiologicalResource", biological_resource))
            edges.append(_edge(ing_id, res_id, "sourced_from"))

    # --- Classification branch: Product -> Category -> Regulator / Licensing / IP options ---
    if classification_inputs:
        try:
            result = classify_product(**classification_inputs)
        except (TypeError, ValueError) as exc:
            result = {"error": str(exc)}

        if "error" not in result:
            cat_id = "classification"
            nodes.append(_node(cat_id, "Classification", result["label"], statutory_basis=result["statutory_basis"]))
            edges.append(_edge(product_id, cat_id, "classified_as"))

            reg_id = "regulator"
            nodes.append(_node(reg_id, "Authority", result["primary_regulator"]))
            edges.append(_edge(cat_id, reg_id, "regulated_by"))

            for i, route in enumerate(result.get("licensing_route", [])):
                route_id = f"licensing_route_{i}"
                nodes.append(_node(route_id, "LicensingRoute", route))
                edges.append(_edge(cat_id, route_id, "requires"))

            for regime, note in result.get("ip_regimes", {}).items():
                ip_id = f"ip_{regime}"
                nodes.append(_node(ip_id, "IPType", regime.replace("_", " ").title(), note=note))
                edges.append(_edge(cat_id, ip_id, "ip_option"))

    # --- TK branch: Ingredient/Product -> Section 3(p)/(e)/(d)/2(1)(j) findings -> IP risk ---
    if tk_inputs:
        try:
            result = analyze_tk_patentability(**tk_inputs)
        except (TypeError, ValueError) as exc:
            result = {"error": str(exc)}

        if "error" not in result:
            for i, finding in enumerate(result["findings"]):
                tk_id = f"tk_finding_{i}"
                nodes.append(
                    _node(
                        tk_id,
                        "TKFinding",
                        finding["section"],
                        risk=finding["risk"],
                        note=finding["finding"],
                    )
                )
                edges.append(_edge(last_ip_source, tk_id, "patent_issue"))

    # --- ABS branch: Product -> entity/activity -> required NBA/SBB approvals ---
    if abs_inputs:
        try:
            result = analyze_abs_compliance(**abs_inputs)
        except (TypeError, ValueError) as exc:
            result = {"error": str(exc)}

        if "error" not in result:
            entity = result["entity_classification"]
            abs_id = "abs_obligation"
            nodes.append(
                _node(
                    abs_id,
                    "ABSObligation",
                    entity["governing_section"],
                    finding=entity["finding"],
                )
            )
            edges.append(_edge(last_ip_source, abs_id, "abs_obligation"))

            for i, item in enumerate(result["compliance_checklist"]):
                cl_id = f"abs_checklist_{i}"
                nodes.append(_node(cl_id, "ComplianceStep", item))
                edges.append(_edge(abs_id, cl_id, "requires"))

    # --- Jurisdiction root ---
    jur_id = "jurisdiction"
    nodes.append(_node(jur_id, "Jurisdiction", jurisdiction))
    edges.append(_edge(product_id, jur_id, "governed_in"))

    return {"nodes": nodes, "edges": edges}

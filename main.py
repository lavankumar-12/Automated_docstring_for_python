"""Automated Docstring Generator & Validator.

This module provides tools to extract metadata from Python files using AST,
generate docstrings in multiple styles (Google, NumPy, reST), and validate
compliance with PEP-257 using pydocstyle.
"""
import ast
import argparse
import sys
import io
import tomllib
import os
from pydocstyle import check
from pydocstyle.violations import conventions

class DocstringGenerator:
    """Generates docstrings in various styles: Google, NumPy, reST."""
    
    def __init__(self, style="google"):
        """Initializes the generator with a specific style."""
        self.style = style.lower()

    def generate(self, info):
        """Generates a docstring for a given function or class metadata."""
        if info["type"] == "function":
            if self.style == "google":
                return self._generate_google_func(info)
            elif self.style == "numpy":
                return self._generate_numpy_func(info)
            elif self.style == "rest":
                return self._generate_rest_func(info)
        elif info["type"] == "class":
            return self._generate_class_doc(info)
        return ""

    def _generate_google_func(self, info):
        """Generates a Google-style docstring for a function."""
        doc = f'"""{info["name"]} function.\n\n'
        if info["params"]:
            doc += "Args:\n"
            for p, t in info["params"]:
                type_hint = f" ({t})" if t else ""
                doc += f"    {p}{type_hint}: Description for {p}.\n"
        
        if info["yields"]:
            doc += "\nYields:\n"
            doc += "    Description of the yielded values.\n"
        elif info["returns"]:
            doc += "\nReturns:\n"
            type_hint = f"{info['return_type']}: " if info['return_type'] else ""
            doc += f"    {type_hint}Description of the return value.\n"

        if info["raises"]:
            doc += "\nRaises:\n"
            for r in sorted(list(info["raises"])):
                doc += f"    {r}: Description for {r}.\n"
        
        doc += '"""'
        return doc

    def _generate_numpy_func(self, info):
        """Generates a NumPy-style docstring for a function."""
        doc = f'"""{info["name"]} function.\n\n'
        if info["params"]:
            doc += "Parameters\n----------\n"
            for p, t in info["params"]:
                type_hint = f" : {t}" if t else ""
                doc += f"{p}{type_hint}\n    Description for {p}.\n"
        
        if info["yields"]:
            doc += "\nYields\n------\n"
            doc += "Description of the yielded values.\n"
        elif info["returns"]:
            doc += "\nReturns\n-------\n"
            type_hint = f"{info['return_type']}\n" if info['return_type'] else ""
            doc += f"{type_hint}    Description of the return value.\n"

        if info["raises"]:
            doc += "\nRaises\n------\n"
            for r in sorted(list(info["raises"])):
                doc += f"{r}\n    Description for {r}.\n"
        
        doc += '"""'
        return doc

    def _generate_rest_func(self, info):
        """Generates a reST-style docstring for a function."""
        doc = f'"""{info["name"]} function.\n\n'
        for p, t in info["params"]:
            doc += f":param {p}: Description for {p}.\n"
            if t:
                doc += f":type {p}: {t}\n"
        
        if info["yields"]:
            doc += "\n:yields: Description of the yielded values.\n"
        elif info["returns"]:
            doc += f"\n:returns: Description of the return value.\n"
            if info['return_type']:
                doc += f":rtype: {info['return_type']}\n"

        if info["raises"]:
            for r in sorted(list(info["raises"])):
                doc += f":raises {r}: Description for {r}.\n"
        
        doc += '"""'
        return doc

    def _generate_class_doc(self, info):
        """Generates a docstring for a class."""
        doc = f'"""{info["name"]} class.\n\n'
        if info["attributes"]:
            if self.style == "google":
                doc += "Attributes:\n"
                for attr in info["attributes"]:
                    doc += f"    {attr}: Description.\n"
            elif self.style == "numpy":
                doc += "Attributes\n----------\n"
                for attr in info["attributes"]:
                    doc += f"{attr}\n    Description.\n"
            else: # rest
                for attr in info["attributes"]:
                    doc += f":ivar {attr}: Description.\n"
        doc += '"""'
        return doc


def extract_metadata(source_code):
    """Extracts metadata for functions and classes using AST."""
    tree = ast.parse(source_code)
    nodes_info = []

    # Module level docstring
    # Find the maximum line number to cover the entire file
    max_line = 1
    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            max_line = max(max_line, getattr(node, 'end_lineno', node.lineno))

    nodes_info.append({
        "type": "module",
        "name": "Module",
        "lineno": 1,
        "end_lineno": max_line,
        "has_docstring": ast.get_docstring(tree) is not None
    })

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            info = {
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, 'end_lineno', node.lineno),
                "params": [],
                "return_type": None,
                "returns": False,
                "yields": False,
                "raises": set(),
                "has_docstring": ast.get_docstring(node) is not None
            }
            
            # Params and type hints
            for arg in node.args.args:
                arg_name = arg.arg
                if arg_name in ('self', 'cls'):
                    continue
                type_hint = None
                if arg.annotation:
                    type_hint = ast.unparse(arg.annotation)
                info["params"].append((arg_name, type_hint))
            
            if node.returns:
                info["return_type"] = ast.unparse(node.returns)

            # Analyze function body
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Return) and subnode.value:
                    info["returns"] = True
                if isinstance(subnode, (ast.Yield, ast.YieldFrom)):
                    info["yields"] = True
                if isinstance(subnode, ast.Raise):
                    if subnode.exc:
                        if isinstance(subnode.exc, ast.Call):
                            if hasattr(subnode.exc.func, 'id'):
                                info["raises"].add(subnode.exc.func.id)
                            elif isinstance(subnode.exc.func, ast.Attribute):
                                info["raises"].add(subnode.exc.func.attr)
                        elif isinstance(subnode.exc, ast.Name):
                            info["raises"].add(subnode.exc.id)

            nodes_info.append(info)

        elif isinstance(node, ast.ClassDef):
            info = {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                "end_lineno": getattr(node, 'end_lineno', node.lineno),
                "attributes": [],
                "has_docstring": ast.get_docstring(node) is not None,
            }
            # Class attributes (simple detection)
            for subnode in node.body:
                if isinstance(subnode, ast.Assign):
                    for target in subnode.targets:
                        if isinstance(target, ast.Name):
                            info["attributes"].append(target.id)
                elif isinstance(subnode, ast.AnnAssign):
                    if isinstance(subnode.target, ast.Name):
                        info["attributes"].append(subnode.target.id)
            
            nodes_info.append(info)

    return nodes_info


def load_config():
    """Loads configuration from pyproject.toml."""
    default_config = {
        "min_coverage": 80.0,
        "default_style": "google",
        "validation_enabled": True
    }
    
    if os.path.exists("pyproject.toml"):
        try:
            with open("pyproject.toml", "rb") as f:
                data = tomllib.load(f)
                config = data.get("tool", {}).get("docstring_generator", {})
                return {**default_config, **config}
        except Exception as e:
            print(f"Warning: Could not read pyproject.toml ({e}). Using defaults.")
    
    return default_config


def validate_docstrings(file_path, select=None, ignore=None):
    """Validates docstrings using pydocstyle with selective rules."""
    violations = []
    try:
        errors = list(check([file_path], select=select, ignore=ignore))
        for error in errors:
            violations.append({
                "code": error.code,
                "message": error.message,
                "line": error.line,
                "short_desc": error.short_desc
            })
    except Exception as e:
        print(f"Validation error: {e}")
    return violations


def run(file_path, style="google", validate=False):
    """Main execution logic for Milestone-2."""
    with open(file_path, "r", encoding="utf-8") as f:
        source_code = f.read()
    
    nodes = extract_metadata(source_code)
    generator = DocstringGenerator(style=style)
    
    generated_docs = []
    for node in nodes:
        if not node["has_docstring"]:
            generated_docs.append({
                "name": node["name"],
                "type": node["type"],
                "docstring": generator.generate(node)
            })

    # Coverage metrics
    total_funcs = sum(1 for n in nodes if n["type"] == "function")
    total_classes = sum(1 for n in nodes if n["type"] == "class")
    doc_funcs = sum(1 for n in nodes if n["type"] == "function" and n["has_docstring"])
    doc_classes = sum(1 for n in nodes if n["type"] == "class" and n["has_docstring"])
    has_mod_doc = any(n["type"] == "module" and n["has_docstring"] for n in nodes)
    
    total = total_funcs + total_classes + 1 # +1 for module
    documented = doc_funcs + doc_classes + (1 if has_mod_doc else 0)
    
    report = {
        "total_functions": total_funcs,
        "total_classes": total_classes,
        "documented_functions": doc_funcs,
        "documented_classes": doc_classes,
        "has_module_doc": has_mod_doc,
        "total": total,
        "with_doc": documented,
        "missing": total - documented,
        "coverage_percentage": (documented / total * 100) if total > 0 else 100,
        "compliance": "PASS",
        "compliance_percentage": 100.0,
        "violations": []
    }
    
    if validate:
        # Pydocstyle conventions implementation
        select_codes = None
        if style == "google":
            select_codes = list(conventions.google)
        elif style == "numpy":
            select_codes = list(conventions.numpy)
        
        violations = validate_docstrings(file_path, select=select_codes)
        report["violations"] = violations
        
        if violations:
            report["compliance"] = "FAIL"
            # Calculate how many entities have violations
            entities_with_violations = set()
            for v in violations:
                for node in nodes:
                    if node["lineno"] <= v["line"] <= node["end_lineno"]:
                        entities_with_violations.add(node["name"])
                        break
            
            compliant_entities = total - len(entities_with_violations)
            report["compliance_percentage"] = (compliant_entities / total * 100) if total > 0 else 100.0
            
    return generated_docs, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Docstring Generator & Validator - Milestone 3")
    parser.add_argument("file", help="Python file path")
    parser.add_argument("--style", choices=["google", "numpy", "rest"], help="Docstring style (overrides config)")
    parser.add_argument("--validate", action="store_true", help="Run PEP 257 validation (overrides config)")
    parser.add_argument("--check-only", action="store_true", help="Exit with non-zero if requirements not met")
    
    args = parser.parse_args()
    
    config = load_config()
    style = args.style if args.style else config["default_style"]
    validate = args.validate or config["validation_enabled"]
    min_cov = config["min_coverage"]

    docs, report = run(args.file, style=style, validate=validate)

    print("\n" + "="*40)
    print(f"DOCSTRING TOOL RESULTS FOR: {args.file}")
    print("="*40)

    if not args.check_only:
        print("\n--- Generated Docstrings ---")
        if not docs:
            print("Everything is already documented!")
        else:
            for d in docs:
                print(f"\n[{d['type'].capitalize()}: {d['name']}]")
                print(d['docstring'])

    print("\n--- Docstring Coverage & Compliance Report ---")
    print(f"Total Functions          : {report['total_functions']}")
    print(f"Total Classes            : {report['total_classes']}")
    print(f"Documented (Total)       : {report['with_doc']} / {report['total']}")
    print(f"Coverage Percentage      : {report['coverage_percentage']:.2f}% (Threshold: {min_cov}%)")
    print(f"PEP-257 Compliance       : {report['compliance']}")
    print(f"Compliance Percentage    : {report['compliance_percentage']:.2f}%")
    print(f"Total Violations         : {len(report['violations'])}")

    if (args.validate or validate) and report['violations']:
        print("\n--- Validation Errors (pydocstyle) ---")
        for v in report['violations']:
            print(f"Line {v['line']} [{v['code']}]: {v['message']}")

    print("\n" + "="*40)

    # CI/Hook checks
    failed = False
    if report['coverage_percentage'] < min_cov:
        print(f"ERROR: Coverage {report['coverage_percentage']:.2f}% is below threshold {min_cov}%")
        failed = True
    
    if validate and report['compliance'] == "FAIL":
        print("ERROR: PEP-257 validation failed!")
        failed = True
    
    if failed:
        if args.check_only:
            sys.exit(1)
        else:
            print("Status: FAILED (Commit would be blocked in pre-commit hook)")
    else:
        print("Status: PASSED")

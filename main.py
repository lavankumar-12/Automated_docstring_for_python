import ast
import argparse
import sys
import io
from pydocstyle import check

class DocstringGenerator:
    """Generates docstrings in various styles: Google, NumPy, reST."""
    
    def __init__(self, style="google"):
        self.style = style.lower()

    def generate(self, info):
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

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            info = {
                "type": "function",
                "name": node.name,
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


def validate_docstrings(file_path):
    """Validates docstrings using pydocstyle."""
    violations = []
    try:
        errors = list(check([file_path]))
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
    
    total = total_funcs + total_classes
    documented = doc_funcs + doc_classes
    
    report = {
        "total_functions": total_funcs,
        "total_classes": total_classes,
        "documented_functions": doc_funcs,
        "documented_classes": doc_classes,
        "total": total,
        "with_doc": documented,
        "missing": total - documented,
        "coverage_percentage": (documented / total * 100) if total > 0 else 100,
        "compliance": "PASS",
        "violations": []
    }
    
    if validate:
        violations = validate_docstrings(file_path)
        report["violations"] = violations
        if violations:
            report["compliance"] = "FAIL"
            
    return generated_docs, report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Docstring Generator & Validator - Milestone 2")
    parser.add_argument("file", help="Python file path")
    parser.add_argument("--style", choices=["google", "numpy", "rest"], default="google", help="Docstring style")
    parser.add_argument("--validate", action="store_true", help="Run PEP 257 validation")
    
    args = parser.parse_args()

    docs, report = run(args.file, style=args.style, validate=args.validate)

    print("\n" + "="*40)
    print(f"MILESTONE-2 RESULTS FOR: {args.file}")
    print("="*40)

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
    print(f"Coverage Percentage      : {report['coverage_percentage']:.2f}%")
    print(f"PEP-257 Compliance       : {report['compliance']}")

    if args.validate and report['violations']:
        print("\n--- Validation Errors (pydocstyle) ---")
        for v in report['violations']:
            print(f"Line {v['line']} [{v['code']}]: {v['message']}")

    print("\n" + "="*40)

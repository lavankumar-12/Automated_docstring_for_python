import ast
import argparse


def read_source_code(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_functions(source_code):
    tree = ast.parse(source_code)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "params": [arg.arg for arg in node.args.args],
                "has_docstring": ast.get_docstring(node) is not None
            })
    return functions


def generate_docstring(func):
    doc = f'''"""
Function: {func["name"]}
Parameters:
'''
    for p in func["params"]:
        doc += f"    {p}\n"
    doc += '"""\n'
    return doc


def generate_report(functions):
    total = len(functions)
    with_doc = sum(1 for f in functions if f["has_docstring"])
    missing = total - with_doc

    return {
        "total": total,
        "with_doc": with_doc,
        "missing": missing
    }


def run(file_path):
    source_code = read_source_code(file_path)
    functions = extract_functions(source_code)

    generated_docs = []
    for f in functions:
        if not f["has_docstring"]:
            generated_docs.append(generate_docstring(f))

    report = generate_report(functions)
    return generated_docs, report


# -------- CLI PART --------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Docstring Generator - Milestone 1")
    parser.add_argument("file", help="Python file path")
    args = parser.parse_args()

    docs, report = run(args.file)

    print("\n--- Generated Docstrings ---\n")
    for d in docs:
        print(d)

    print("\n--- Docstring Coverage Report ---")
    print(f'Total functions/methods : {report["total"]}')
    print(f'With docstrings        : {report["with_doc"]}')
    print(f'Missing docstrings     : {report["missing"]}')

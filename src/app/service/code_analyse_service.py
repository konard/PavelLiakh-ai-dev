import os
import json
from tree_sitter import Language, Parser
from pydantic import BaseModel
from typing import List, Dict, Optional


class Method(BaseModel):
    method: str
    args: List[str]


class ClassStructure(BaseModel):
    methods: List[Method]
    attributes: List[str]


class FileStructure(BaseModel):
    imports: List[str]
    classes: Dict[str, ClassStructure]
    functions: Dict[str, List[str]]


class ProjectStructure(BaseModel):
    files: Dict[str, FileStructure]


class ProjectAnalyzer:
    def __init__(
        self, 
        language_lib_path='build/my-languages.so'
    ):
        if not os.path.exists(language_lib_path):
            raise FileNotFoundError(
                f"{language_lib_path} not found. Please run 'poetry run build-grammar' first."
            )
        self.language = Language(language_lib_path, 'python')
        self.parser = Parser()
        self.parser.set_language(self.language)

    def analyze_file_structure(self, file_path) -> FileStructure:
        with open(file_path, "rb") as f:
            source = f.read()

        tree = self.parser.parse(source)
        root_node = tree.root_node

        imports = []
        classes = {}
        functions = {}

        def traverse(node, current_class=None):

            if node.type in ["import_statement", "import_from_statement"]:
                import_text = source[node.start_byte : node.end_byte].decode()
                imports.append(import_text)

            elif node.type == "class_definition":
                class_name = node.child_by_field_name("name").text.decode()
                classes[class_name] = ClassStructure(methods=[], attributes=[])
                for class_child in node.children:
                    traverse(class_child, current_class=class_name)

            elif node.type == "function_definition":
                func_name = node.child_by_field_name("name").text.decode()
                params = node.child_by_field_name("parameters")
                args = [
                    param.text.decode()
                    for param in params.children
                    if param.type == "identifier"
                ]
                method = Method(method=func_name, args=args)
                if current_class:
                    classes[current_class].methods.append(method)
                else:
                    functions[func_name] = args

            elif node.type == "assignment" and current_class:
                var_name_node = node.child_by_field_name("left")
                if var_name_node:
                    var_name = source[var_name_node.start_byte : var_name_node.end_byte].decode()
                    classes[current_class].attributes.append(var_name)

            for child in node.children:
                traverse(child, current_class=current_class)

        traverse(root_node)

        return FileStructure(imports=imports, classes=classes, functions=functions)


    def analyze_project_structure(self, project_root) -> ProjectStructure:
        project_summary = {}
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_root)
                    file_structure = self.analyze_file_structure(full_path)
                    project_summary[rel_path] = file_structure

        return ProjectStructure(files=project_summary)


    def save_project_structure(self, project_root, output_path):
        project_structure = self.analyze_project_structure(project_root)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(project_structure, f, indent=2, ensure_ascii=False)

        print(f"Project structure saved to {output_path}")


if __name__ == "__main__":
    analyzer = ProjectAnalyzer()
    project_root = "/Users/uvauchok/bot-project/ai-dev/src"
    file_path = "/Users/uvauchok/bot-project/ai-dev/src/app/service/development_service.py"

    structure = analyzer.analyze_project_structure(project_root)
    file_structure = analyzer.analyze_file_structure(file_path)

    # Output structure to console in JSON format
    print(file_structure.model_dump_json(indent=2, exclude_none=True))
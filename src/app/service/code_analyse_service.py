import os
import json
from tree_sitter import Language, Parser

class ProjectAnalyzer:
    def __init__(self, language_lib_path='build/my-languages.so', languages=['tree-sitter-python']):
        self.language_lib_path = language_lib_path
        self.languages = languages

        if not os.path.exists(self.language_lib_path):
            Language.build_library(self.language_lib_path, self.languages)

        self.language = Language(self.language_lib_path, 'python')
        self.parser = Parser()
        self.parser.set_language(self.language)

    def analyze_file_structure(self, file_path):

        with open(file_path, 'rb') as f:
            source = f.read()

        tree = self.parser.parse(source)
        root_node = tree.root_node

        structure = {
            'imports': [],
            'classes': {},
            'functions': {},
        }

        def traverse(node, current_class=None):

            if node.type == 'import_statement' or node.type == 'import_from_statement':
                import_text = source[node.start_byte:node.end_byte].decode()
                structure['imports'].append(import_text)

            elif node.type == 'class_definition':
                class_name = node.child_by_field_name('name').text.decode()
                structure['classes'][class_name] = {
                    'methods': [],
                    'attributes': []
                }
                for class_child in node.children:
                    traverse(class_child, current_class=class_name)

            elif node.type == 'function_definition':
                func_name = node.child_by_field_name('name').text.decode()
                params = node.child_by_field_name('parameters')
                args = [param.text.decode() for param in params.children if param.type == 'identifier']
                if current_class:
                    structure['classes'][current_class]['methods'].append({
                        'method': func_name,
                        'args': args
                    })
                else:
                    structure['functions'][func_name] = args

            elif node.type == 'assignment' and current_class:
                var_name_node = node.child_by_field_name('left')
                if var_name_node:
                    var_name = source[var_name_node.start_byte:var_name_node.end_byte].decode()
                    structure['classes'][current_class]['attributes'].append(var_name)

            for child in node.children:
                traverse(child, current_class=current_class)

        traverse(root_node)
        return structure

    def analyze_project_structure(self, project_root):
        project_summary = {}
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, project_root)
                    project_summary[rel_path] = self.analyze_file_structure(full_path)
        return project_summary

    def save_project_structure(self, project_root, output_path):
        project_structure = self.analyze_project_structure(project_root)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(project_structure, f, indent=2, ensure_ascii=False)

        print(f'Project structure saved to {output_path}')

if __name__ == '__main__':
    analyzer = ProjectAnalyzer()
    project_root = '/Users/uvauchok/bot-project/ai-dev/src'
    
    structure = analyzer.analyze_project_structure(project_root)
    
    # Output structure to console in JSON format
    print(json.dumps(structure, indent=2, ensure_ascii=False))
    
    # (optional) save to JSON file
    # analyzer.save_project_structure(project_root, 'project_structure.json')

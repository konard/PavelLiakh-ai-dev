from tree_sitter import Language
import os

def main():
    grammar_dir = os.path.join(os.path.dirname(__file__), '../vendor/tree-sitter-python')
    build_dir = os.path.join(os.path.dirname(__file__), '../build')
    os.makedirs(build_dir, exist_ok=True)
    
    lib_path = os.path.join(build_dir, 'my-languages.so')
    
    if not os.path.exists(lib_path):
        Language.build_library(
            lib_path,
            [grammar_dir]
        )
        print(f'Grammar built at {lib_path}')
    else:
        print('Grammar already built.')

if __name__ == '__main__':
    main()

import os
import distutils.dir_util
import argparse
import shutil

import markdown

def kebab_to_title_case(s: str) -> str:
  """Convert kebab-case string to Title Case string
  
  Args:
    s (str): The kebab-cased string to convert
  
  Returns:
    str: The Title Cased string
  
  """
  return s.replace("-", " ").title()

def copy_static_files(src: str, dst: str):
  """Copy static files from src/ to dst/.

  Copies static files from the src directory to the dst directory. A static
  file is any file that is not in the recipes/ directory, does not have
  a .md extension, or is not the _header.html or _footer.html.
  
  Args:
    src (str): The source directory
    dst (str): The destination directory
  
  """
  for file in os.listdir(src):
    file_path_src = os.path.join(src, file)
    file_path_dst = os.path.join(dst, file)
    fn, fe = os.path.splitext(file)
    if not os.path.isdir(file_path_src) and fe != '.md' and not fn.startswith('_') :
      shutil.copy(file_path_src, file_path_dst)
    elif os.path.isdir(file_path_src) and 'recipes' not in file_path_src:
      distutils.dir_util.copy_tree(file_path_src, file_path_dst)


def write_index(src_dir: str, dst_dir: str, title: str, content: str):
  """Write the index.html file of the static site.
  
  Inject alphabetized list of recipes from the files in the recipes dir in between the 
  _header.html and _footer.html.

  Args:
    src_dir (str): The source directory containing markdown files
    dst_dir (str): The destination directory of the static site
    title   (str): The title of the site
    content (str): The main content of the index.html

  """
  header_path = os.path.join(src_dir, '_header.html')
  footer_path = os.path.join(src_dir, '_footer.html')
  file_path = os.path.join(dst_dir, 'index.html')

  with open(file_path, 'w', encoding='utf-8', ) as fout:
  
    # Write Header
    with open(header_path, 'r', encoding='utf-8', ) as fin: 
      fout.write(fin.read().replace('<title></title>', f'<title>{title}</title>'))
    
    # Write content
    fout.write(content)

    with open(footer_path, 'r', encoding='utf-8') as fin:
      fout.write(fin.read())


def write_file(src_dir: str, dst_dir: str, title: str, recipe_name: str, content: str):
  """Write a recipe file for the static site.
  
  Inject converted markdown of a recipe in between the _header.html and _footer.html.

  Args:
    src_dir     (str): The source directory containing markdown files
    dst_dir     (str): The destination directory of the static site
    title       (str): The title of the site.
    recipe_name (str): The name of the current recipe in kebab-case
    content     (str): The main content of the index.html.

  """
  header_path = os.path.join(src_dir, '_header.html')
  footer_path = os.path.join(src_dir, '_footer.html')
  file_path = os.path.join(dst_dir, recipe_name)
  if not os.path.exists(file_path):
    os.mkdir(file_path)

  with open(os.path.join(file_path, 'index.html'), 'w', encoding='utf-8', ) as fout:
  
    # Write header
    with open(header_path, 'r', encoding='utf-8', ) as fin: 
      fout.write(fin.read().replace('<title></title>', f'<title>{title} | {kebab_to_title_case(os.path.basename(recipe_name))}</title>'))
    
    # Write content
    fout.write(content)

    # Write footer
    with open(footer_path, 'r', encoding='utf-8') as fin:
      fout.write(fin.read())


# Set up argument parsisng
parser = argparse.ArgumentParser(description="A simple SSG written in Python.")
parser.add_argument('src', help="The source code folder")
parser.add_argument('dst', help="The destination folder")
parser.add_argument('title', help="The title for your site")
args = parser.parse_args()

# Create dst dir
if not os.path.exists(args.dst):
  os.mkdir(args.dst)

# Step 1: Copy over static files
copy_static_files(args.src, args.dst)

# Step 2: Create the index.html
## TODO: Generate title and description of index from src/index.md
## Write index content
### Title
index_title = '<h1>Recipes</h1>'

### Put sorted list of recipes in the content
recipes = os.listdir(os.path.join(args.src, 'recipes'))
sorted_recipes = sorted(recipes)
#### Make each recipe name an li
recipes_li = map(lambda s: f'<li><a href="/recipes/{s[:-3]}">{kebab_to_title_case(s[:-3])}</a></li>\n', sorted_recipes)
#### Wrap li's in ul
recipes_ul = f'<ul id="recipe-list">\n{"".join(recipes_li)}</ul>'

### Create a searchable input
search_box = '<input type="text" id="search" onkeyup="filterRecipes()" placeholder="Search" autocomplete="off">'

### Write the content to index.html 
index_content = f'{index_title}\n{search_box}\n{recipes_ul}\n'
write_index(args.src, args.dst, args.title, index_content)

# Step 3: Generate html files from markdown
## Create recipes directory in dst
if not os.path.exists(os.path.join(args.dst, 'recipes')):
  os.mkdir(os.path.join(args.dst, 'recipes'))
## Get md contents of recipe file
for recipe in recipes:
  with open(os.path.join(args.src, 'recipes', recipe)) as fin:
    html = markdown.markdown(fin.read())
    write_file(args.src, args.dst, args.title, os.path.join('recipes', recipe.replace('.md', '')), html)






"""Prepare static output for a GitHub Pages project URL."""
from pathlib import Path
import argparse, re, shutil

parser = argparse.ArgumentParser()
parser.add_argument('--base-path', required=True)
parser.add_argument('--origin', required=True)
args = parser.parse_args()
base = '/' + args.base_path.strip('/')
root = Path(__file__).resolve().parents[1]
output = root / 'pages-output'
if output.exists():
    shutil.rmtree(output)
shutil.copytree(root / 'dist', output)
for file in output.rglob('*'):
    if file.suffix not in {'.html', '.css', '.js'}:
        continue
    content = file.read_text().replace('/assets/', base + '/assets/')
    if file.suffix == '.html':
        def prefix_link(match):
            path = match[2]
            if path.startswith(base + '/'):
                return match[0]
            return match[1] + base + path
        content = re.sub(r'((?:href|src|poster)=["\'])(/(?!/)[^"\']*)', prefix_link, content)
    content = content.replace('https://swingora-recreation.muhirwa250.chatgpt.site', args.origin.rstrip('/') + base)
    file.write_text(content)
# GitHub's custom not-found file must live at the project root.
shutil.copyfile(output / '404' / 'index.html', output / '404.html')
(output / '.nojekyll').touch()
print('Prepared GitHub Pages output:', output)

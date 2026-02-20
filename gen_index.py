import os
import sys
from datetime import datetime

SKIP_DIRS = {'.git', '__pycache__', 'node_modules', '.svn'}
SKIP_FILES = {'gen_index.py',  '.gitignore'}
INDEX_FILE = 'indexx.html'
metrika = '''
<!-- Yandex.Metrika counter -->
<script type="text/javascript">
    (function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=106700083', 'ym');

    ym(106700083, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});
</script>
<noscript><div><img src="https://mc.yandex.ru/watch/106700083" style="position:absolute; left:-9999px;" alt="" /></div></noscript>
<!-- /Yandex.Metrika counter -->
'''


def format_size(size):
    for unit in ('B', 'KB', 'MB', 'GB'):
        if size < 1024:
            return f'{size:.0f} {unit}' if unit == 'B' else f'{size:.1f} {unit}'
        size /= 1024
    return f'{size:.1f} TB'


def generate_index(dirpath, rootpath):
    entries = os.scandir(dirpath)

    dirs = []
    files = []

    for e in sorted(entries, key=lambda x: x.name.lower()):
        if e.name == INDEX_FILE:
            continue
        if e.name in SKIP_FILES:
            continue
        if e.is_dir(follow_symlinks=False):
            if e.name not in SKIP_DIRS:
                dirs.append(e)
        else:
            files.append(e)

    rel = os.path.relpath(dirpath, rootpath)
    is_root = (rel == '.')
    title = 'Index of /' if is_root else f'Index of /{rel.replace(os.sep, "/")}'

    rows = []

    if not is_root:
        rows.append('<tr><td><a href="../indexx.html">[Parent Directory]</a></td><td>-</td><td>-</td></tr>')

    for d in dirs:
        rows.append(
            f'<tr>'
            f'<td><a href="{d.name}/indexx.html">{d.name}/</a></td>'
            f'<td>-</td>'
            f'<td>Directory</td>'
            f'</tr>'
        )

    for f in files:
        stat = f.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
        size = format_size(stat.st_size)
        rows.append(
            f'<tr>'
            f'<td><a href="{f.name}">{f.name}</a></td>'
            f'<td>{mtime}</td>'
            f'<td>{size}</td>'
            f'</tr>'
        )


    html = f"""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
{metrika}
<title>{title}</title>
</head>
<body>
<h1>{title}</h1>
<hr>
<table>
<tr>
  <th align="left">Name</th>
  <th align="left">Last Modified</th>
  <th align="left">Size</th>
</tr>
<tr><td colspan="3"><hr></td></tr>
{''.join(rows)}
<tr><td colspan="3"><hr></td></tr>
</table>
</body>
</html>
"""

    index_path = os.path.join(dirpath, INDEX_FILE)
    with open(index_path, 'w', encoding='utf-8') as fp:
        fp.write(html)

    print(f'Written: {index_path}')


def walk(rootpath):
    for dirpath, dirnames, _ in os.walk(rootpath):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        generate_index(dirpath, rootpath)


if __name__ == '__main__':
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    root = os.path.abspath(root)
    print(f'Generating indexes in: {root}')
    walk(root)
    print('Done.')

#!/usr/bin/env python3
import os
import argparse
from datetime import datetime

def format_size(size):
    """Форматирует размер файла"""
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f} KB"
    else:
        return f"{size/(1024*1024):.2f} MB"

def format_date(timestamp):
    """Форматирует дату как в старых листингах"""
    return datetime.fromtimestamp(timestamp).strftime('%d-%b-%Y %H:%M')

def generate_index_html(directory, output_file='index.html', root_dir=None):
    """
    Генерирует index.html в классическом стиле 90-х - начала 2000-х
    """
    
    if root_dir is None:
        root_dir = directory
    
    # Получаем абсолютный путь к каталогу
    target_dir = os.path.abspath(directory)
    
    # Получаем относительный путь от корневого каталога
    rel_path = os.path.relpath(target_dir, root_dir)
    if rel_path == '.':
        rel_path = ''
    
    # Получаем список файлов и подкаталогов
    items = []
    try:
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if item == output_file:
                continue
                
            is_dir = os.path.isdir(item_path)
            try:
                size = os.path.getsize(item_path) if not is_dir else 0
                mod_time = os.path.getmtime(item_path)
                
                items.append({
                    'name': item,
                    'is_dir': is_dir,
                    'size': size,
                    'mod_time': mod_time,
                    'path': item_path
                })
            except (OSError, PermissionError):
                continue
                
    except PermissionError:
        print(f"Нет доступа к {target_dir}")
        return
    except FileNotFoundError:
        print(f"Каталог {target_dir} не найден")
        return
    
    # Сортируем
    items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
    
    # Генерируем HTML в стиле старого доброго веба
    html_content = f'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=windows-1251">
    <title>Index of /{rel_path.replace(os.sep, '/')}</title>
    <style type="text/css">
        body {{
            background-color: #FFFFFF;
            color: #000000;
            font-family: 'Times New Roman', Times, serif;
            margin: 20px;
        }}
        h1 {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        pre {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 16px;
            margin: 0;
        }}
        a {{
            color: #0000EE;
            text-decoration: none;
        }}
        a:visited {{
            color: #551A8B;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        table {{
            border: 0;
            width: 100%;
        }}
        td {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 16px;
            padding: 2px 5px;
        }}
        th {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 16px;
            font-weight: bold;
            text-align: left;
            background-color: #CCCCCC;
            padding: 3px 5px;
        }}
        .dir {{
            color: #0000EE;
        }}
        .file {{
            color: #0000EE;
        }}
        .size {{
            text-align: right;
            padding-right: 20px;
        }}
        .date {{
            text-align: left;
        }}
        hr {{
            border: 1px solid #000000;
            margin: 20px 0;
        }}
        .footer {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 14px;
            color: #666666;
        }}
        .parent-link {{
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <h1>Index of /{rel_path.replace(os.sep, '/')}</h1>
    
    <table>
    <tr>
        <th colspan="3">[ICO]</th>
        <th>Name</th>
        <th>Last modified</th>
        <th>Size</th>
        <th>Description</th>
    </tr>
'''
    
    # Добавляем родительский каталог (иконка PARENTDIR)
    if target_dir != os.path.dirname(target_dir) and target_dir != root_dir:
        html_content += f'''    <tr>
        <td colspan="3"><img src="/icons/back.gif" alt="[PARENTDIR]"></td>
        <td><a href="../{output_file}">Parent Directory</a></td>
        <td class="date"> </td>
        <td class="size"> </td>
        <td> </td>
    </tr>
'''
    
    # Добавляем все элементы
    for item in items:
        if item['is_dir']:
            # Создаем index.html в подкаталоге
            generate_index_html(item['path'], output_file, root_dir)
            
            # Иконка для папки
            icon = "folder.gif"
            alt = "[DIR]"
            display_name = item['name'] + "/"
            size_display = " "
            link = f"{item['name']}/{output_file}"
        else:
            # Определяем иконку по расширению
            ext = os.path.splitext(item['name'])[1].lower()
            if ext in ['.txt', '.log']:
                icon = "text.gif"
                alt = "[TXT]"
            elif ext in ['.jpg', '.jpeg', '.gif', '.png', '.bmp']:
                icon = "image2.gif"
                alt = "[IMG]"
            elif ext in ['.htm', '.html']:
                icon = "html.gif"
                alt = "[HTML]"
            elif ext in ['.zip', '.rar', '.7z', '.gz']:
                icon = "compressed.gif"
                alt = "[ZIP]"
            elif ext in ['.exe', '.com', '.bat']:
                icon = "binary.gif"
                alt = "[EXE]"
            else:
                icon = "unknown.gif"
                alt = "[   ]"
            
            display_name = item['name']
            size_display = format_size(item['size'])
            link = item['name']
        
        html_content += f'''    <tr>
        <td colspan="3"><img src="/icons/{icon}" alt="{alt}"></td>
        <td><a href="{link}" class="dir">{display_name}</a></td>
        <td class="date">{format_date(item['mod_time'])}</td>
        <td class="size">{size_display}</td>
        <td> </td>
    </tr>
'''
    
    dir_count = sum(1 for item in items if item['is_dir'])
    file_count = len(items) - dir_count
    
    html_content += f'''    </table>
    
    <hr>
    <pre>Apache/1.3.41 Server at localhost Port 80</pre>
    
    <div class="footer">
        {dir_count} directories, {file_count} files<br>
        <i>Generated: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}</i>
    </div>
</body>
</html>'''
    
    # Записываем в файл
    output_path = os.path.join(target_dir, output_file)
    try:
        with open(output_path, 'w', encoding='windows-1251', errors='replace') as f:
            f.write(html_content)
        print(f"✓ {output_path}")
    except PermissionError:
        print(f"✗ Нет прав для записи в {output_path}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

def create_icons_directory(root_dir):
    """Создает директорию с иконками и базовыми иконками"""
    icons_dir = os.path.join(root_dir, 'icons')
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
        print(f"Создана директория для иконок: {icons_dir}")
        
        # Создаем простые HTML-иконки (так как настоящие картинки не можем создать)
        icons = {
            'back.gif': '[UP]',
            'folder.gif': '[DIR]',
            'text.gif': '[TXT]',
            'image2.gif': '[IMG]',
            'html.gif': '[HTML]',
            'compressed.gif': '[ZIP]',
            'binary.gif': '[EXE]',
            'unknown.gif': '[?]'
        }
        
        for icon_name, content in icons.items():
            icon_path = os.path.join(icons_dir, icon_name)
            with open(icon_path, 'w') as f:
                f.write(f'<span style="font-family: monospace;">{content}</span>')
        
        print("Созданы текстовые заглушки для иконок")

def main():
    parser = argparse.ArgumentParser(description='Генератор index.html в стиле Apache 1.3')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Корневой каталог')
    parser.add_argument('-o', '--output', default='index.html',
                       help='Имя выходного файла')
    
    args = parser.parse_args()
    
    root_dir = os.path.abspath(args.directory)
    
    print("=" * 50)
    print("Генератор старых индексов (стиль Apache/1.3)")
    print("=" * 50)
    print(f"Каталог: {root_dir}")
    print(f"Выходной файл: {args.output}")
    print("-" * 50)
    
    # Создаем директорию с иконками
    create_icons_directory(root_dir)
    
    # Запускаем генерацию
    generate_index_html(root_dir, args.output, root_dir)
    
    print("-" * 50)
    print("Готово! Файлы index.html созданы во всех папках.")
    print("Примечание: Для полноценной работы нужны настоящие иконки")
    print(f"в папке {os.path.join(root_dir, 'icons')}")

if __name__ == '__main__':
    main()
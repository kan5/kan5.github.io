import os

def delete_index_html_simple(root_dir='.'):
    for root, dirs, files in os.walk(root_dir):
        if 'index.html' in files:
            os.remove(os.path.join(root, 'index.html'))

# Использование для текущей директории:
delete_index_html_simple()

# Или для конкретной директории:
# delete_index_html_simple('/путь/к/папке')
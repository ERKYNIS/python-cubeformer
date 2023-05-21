import pip
import os

print('\n[Cubeформер] Загрузка презентации и главного файла проекта...\n')

try:
    import requests
except ModuleNotFoundError:
    pip.main(['install', 'requests'])
    import requests

if not os.path.exists('start.py'):
    with open('start.py', 'wb') as handler:
        handler.write(requests.get('https://www.dropbox.com/s/2yq1fdvtb81fe0e/'
                                   'start.py?dl=1').content)

if not os.path.exists('Cubeформер.pptx'):
    with open('Cubeформер.pptx', 'wb') as handler:
        handler.write(requests.get('https://www.dropbox.com/scl/fi/k1tg8yh5tm0lh0kcgxtqv/'
                                   'Cube.pptx?dl=1&rlkey=197sizr6dh3f6e7ou7qgagwot').content)

print('[?] Запустите файл start.py, чтобы запустить игру.'
      '\n\n[!] Данный файл будет автоматически удалён.')
input('Нажмите "Enter".')
os.remove('install.py')

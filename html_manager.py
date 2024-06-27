from bs4 import BeautifulSoup
import os

def add_iframe(url):
    file_path = "C:/Users/luffy/.node-red/visualization_page/charts_page.html"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
    except FileNotFoundError:
        print('Fichier introuvable : ', file_path)
        return
    
    iframe_container = soup.find('div', class_='iframe-container')
    if not iframe_container:
        print('Div iframe-container non trouvée')
        return

    # Ajout d'un iframe avec des styles inline
    new_iframe = soup.new_tag('iframe', src=url)
    iframe_container.append(new_iframe)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

def remove_iframe(url):
    file_path = "C:/Users/luffy/.node-red/visualization_page/charts_page.html"
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
    except FileNotFoundError:
        print('Fichier introuvable')
        return
    
    iframe_container = soup.find('div', class_='iframe-container')
    if not iframe_container:
        print('Div iframe-container non trouvée')
        return

    iframes = iframe_container.find_all('iframe')
    for iframe in iframes:
        if iframe and iframe.has_attr('src') and url in iframe['src']:
            src = iframe['src']
            iframe.decompose()
            if os.path.exists(src) and os.path.isfile(src):
                try:
                    os.remove(src)
                except FileNotFoundError:
                    print('Fichier introuvable : ', src)
            print('iframe supprimée')
            break
    else:
        print('iframe non trouvée')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

if __name__ == '__main__':
    # Example usage
    add_iframe('http://127.0.0.1:8051/')
    remove_iframe('http://127.0.0.1:8051/')

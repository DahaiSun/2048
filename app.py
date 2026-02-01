import webview
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    # Locate index.html
    html_file = resource_path('index.html')
    
    # Create the window
    # Width 450 is good for the mobile-first design of 2048
    window = webview.create_window(
        title='Word2048 Enhanced', 
        url=html_file, 
        width=450, 
        height=850, 
        resizable=True
    )
    
    # Start the GUI loop
    webview.start()

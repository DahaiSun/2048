import zipfile
import os

def zip_project():
    source_files = [
        'index.html',
        'styles.css',
        'game.js',
        'vocabulary.js',
        'oxford_vocabulary.js',
        'bgm.mp3',
        'icon.png',
        'manifest.json',
        'sw.js'
    ]
    
    source_dirs = ['words']
    output_filename = 'Word2048_Android_Source.zip'

    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for file in source_files:
            if os.path.exists(file):
                print(f"Adding {file}...")
                zipf.write(file)
            else:
                print(f"Warning: {file} not found!")

        # Add directories
        for folder in source_dirs:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    print(f"Adding {file_path}...")
                    zipf.write(file_path)

    print(f"Created {output_filename} successfully!")

if __name__ == '__main__':
    zip_project()

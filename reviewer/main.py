from .groq import analyze_code_with_groq
from .github_api import post_comment
import os
import gc
import time

def get_files(repo_path, extensions=None):
    """
    Obtiene los archivos del repositorio que coincidan con las extensiones especificadas.

    Args:
        repo_path (str): Ruta del repositorio.
        extensions (list, optional): Lista de extensiones de archivo a incluir (por ejemplo, ['.py', '.js']).

    Returns:
        list: Lista de rutas de archivos que coinciden con las extensiones.
    """
    if extensions is None:
        extensions = ['.py']

    files = []
    for root, _, files_in_dir in os.walk(repo_path):
        for file in files_in_dir:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 10 * 1024 * 1024: 
                    print(f"Skipping large file: {file_path}")
                    continue
                files.append(file_path)
    return files

def clean_console():
    """
    Limpia la consola dependiendo del sistema operativo.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def run_code_review():
    """
    Ejecuta el proceso de revisión de código para los archivos especificados en el repositorio.
    """
    repo_path = input("Enter the path to the repository (default: current directory): ").strip()
    if not repo_path:
        repo_path = "."

    extensions = input("Enter file extensions to include (comma-separated, e.g., .py,.js,.html): ").strip()

    lang = input("Select language for code review (1 for English, 2 for Spanish): ").strip()
    if lang == "1":
        language = False    
    elif lang == "2":
        language = True
    else:
        print("Invalid selection. Defaulting to English.")
        language = False

    if not extensions:
        extensions = ".py"
    extensions = [ext.strip() for ext in extensions.split(",")]

    files_to_review = get_files(repo_path, extensions)

    for file_path in files_to_review:
        with open(file_path, 'r', encoding='utf-8') as file:
            code = file.read()

        try:
            print("Loading...")
            pause(3)

            print("--------------------------------------------------")
            review = analyze_code_with_groq(code, file_path, language)
        except Exception as e:
            print(f"ERROR ({e}): {e.args}")
            exit()

        if os.path.exists(file_path) == False:
            os.mkdir("./output")

        output_file = f"./output/{os.path.basename(file_path)}_{'es' if language else 'en'}_review.md"
        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Code Review for {file_path}\n\n")
            md_file.write(review)
        print(f"Review for {file_path} has been saved to {output_file}")

        post_comment(review)

        del code
        del review
        gc.collect()
        print("Finished processing file:", file_path)
        print("--------------------------------------------------")

def pause(timer: int = 2):
    """
    Pausa la ejecución del programa por una cantidad de segundos.

    Args:
        timer (int, optional): Número de segundos a pausar (por defecto 2).
    """
    time.sleep(timer)
    

def ask_to_exit() -> bool:
    """
    Pregunta al usuario si desea salir del programa.

    Returns:
        bool: True si el usuario desea salir, False en caso contrario.
    """
    salida = input("Do you want to exit? (y/n)")

    if salida == "y":
        return True
    else:
        return False


def main():
    """
    Bloque principal del programa.
    """
    
    exit = False

    while exit != True:
        clean_console()
        print("""
            ░█████╗░░█████╗░██████╗░███████╗░██╗░░░░░░░██╗██╗░██████╗███████╗
            ██╔══██╗██╔══██╗██╔══██╗██╔════╝░██║░░██╗░░██║██║██╔════╝██╔════╝
            ██║░░╚═╝██║░░██║██║░░██║█████╗░░░╚██╗████╗██╔╝██║╚█████╗░█████╗░░
            ██║░░██╗██║░░██║██║░░██║██╔══╝░░░░████╔═████║░██║░╚═══██╗██╔══╝░░
            ╚█████╔╝╚█████╔╝██████╔╝███████╗░░╚██╔╝░╚██╔╝░██║██████╔╝███████╗
            ░╚════╝░░╚════╝░╚═════╝░╚══════╝░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░╚══════╝

            ██████╗░███████╗██╗░░░██╗██╗███████╗░██╗░░░░░░░██╗███████╗██████╗░
            ██╔══██╗██╔════╝██║░░░██║██║██╔════╝░██║░░██╗░░██║██╔════╝██╔══██╗
            ██████╔╝█████╗░░╚██╗░██╔╝██║█████╗░░░╚██╗████╗██╔╝█████╗░░██████╔╝
            ██╔══██╗██╔══╝░░░╚████╔╝░██║██╔══╝░░░░████╔═████║░██╔══╝░░██╔══██╗
            ██║░░██║███████╗░░╚██╔╝░░██║███████╗░░╚██╔╝░╚██╔╝░███████╗██║░░██║
            ╚═╝░░╚═╝╚══════╝░░░╚═╝░░░╚═╝╚══════╝░░░╚═╝░░░╚═╝░░╚══════╝╚═╝░░╚═╝
            """)
        
        run_code_review()
        exit = ask_to_exit()


if __name__ == "__main__":
    main()
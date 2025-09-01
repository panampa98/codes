import os
from pathlib import Path

def get_folder_size(path: Path) -> int:
    """Calcula el tamaño total de una carpeta."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
            except Exception:
                pass  # Archivos bloqueados o inaccesibles
    return total_size

def to_MB(size_in_bytes: int) -> str:
    """Convierte bytes a MB con 2 decimales."""
    return f"{round(size_in_bytes / (1024 * 1024), 2)} MB"

def main():
    # Ruta a analizar
    input_path = Path(r"C:\Users\USER\Documents")

    if not input_path.exists():
        print(f"❌ Ruta no encontrada: {input_path}")
        return

    if input_path.is_file():
        size = input_path.stat().st_size
        print(f"Tamaño del archivo '{input_path.name}': {to_MB(size)}")
    elif input_path.is_dir():
        print(f"Tamaños de archivos y subcarpetas en: {input_path}\n")
        folder_sizes = []
        for item in input_path.iterdir():
            if item.is_dir():
                size = get_folder_size(item)
            elif item.is_file():
                size = item.stat().st_size
            folder_sizes.append((item.name, size))
        folder_sizes.sort(key=lambda x: x[1], reverse=True)
        for name, size in folder_sizes:
            print(f"{name:<30} {to_MB(size):>10}")
    else:
        print("La ruta no es un archivo ni una carpeta válida.")

if __name__ == "__main__":
    main()

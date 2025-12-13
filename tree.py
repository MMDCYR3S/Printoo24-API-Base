import os

def show_directory_tree(path, indent=0):
    try:
        items = os.listdir(path)
    except PermissionError:
        print(" " * indent + f"[Access Denied]: {path}")
        return

    for item in items:
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            print(" " * indent + f"📁 {item}")
            show_directory_tree(item_path, indent + 4)
        else:
            print(" " * indent + f"📄 {item}")

if __name__ == "__main__":
    target_path = input("Enter the target directory path: ").strip()
    if not os.path.exists(target_path):
        print("❌ The specified path does not exist!")
    else:
        print(f"\nDirectory structure for: {target_path}\n")
        show_directory_tree(target_path)

import os
import platform
import shutil
import subprocess
import time
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def clear_screen():
    """Clears the terminal screen based on the operating system."""
    if platform.system() == 'Windows':
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # For Linux/macOS

def display_welcome():
    """Displays a welcome message with credits."""
    clear_screen()
    border = Fore.MAGENTA + "=" * 60
    welcome_msg = Fore.CYAN + Style.BRIGHT + "\n       WELCOME TO THE DARK_PAK HEX EDITOR & REPACKER\n"
    credit_msg = Fore.YELLOW + "                      Developed by Darshan\n"
    print(border)
    print(welcome_msg)
    print(credit_msg)
    print(border)
    time.sleep(2)

# =================== CONFIGURATION ===================
# Base directory for DARK_PAK (update if needed)
dark_mods_dir = Path("/storage/emulated/0/DARK_PAK/UNPACK_REPACK")
# Folder with original .pak files (should contain game_patch_3.7.0.19766.pak)
paks_dir = dark_mods_dir / "PAKS"
# Folder with unpacked and repacked files
unpack_repack_dir = dark_mods_dir / "UNPACK"
# Executable script path (assumed to be in home/DARK_PAK as an example)
executable_script = Path.home() / "DARK_PAK" / "DARKSIDE"

# =================== HEX EDITING FUNCTIONS ===================
def search_index(hex_code, index_data):
    """
    Search for the given hex code in the index data and return the corresponding index.
    """
    for line in index_data:
        parts = line.split(" | ")  # Split the line by ' | ' to extract components
        if len(parts) >= 3 and parts[1].strip().lower() == hex_code.lower():
            index = parts[2].split(":")[1].strip()
            return index
    return None

def hex_edit(folder_path, skins, output_path, index_data):
    """Perform hex editing on files based on the skin pairs."""
    for i, (hex_code1, hex_code2) in enumerate(skins):
        index1 = search_index(hex_code1, index_data)
        index2 = search_index(hex_code2, index_data)

        if index1 and index2:
            print("")
            print(Fore.LIGHTCYAN_EX + f"Editing Skin Pair {i+1}: {Fore.YELLOW}{hex_code1} ►► {Fore.GREEN}{hex_code2}")
            print(Fore.LIGHTMAGENTA_EX + f"Index of {hex_code1}: {Fore.CYAN}{index1}")
            print(Fore.LIGHTMAGENTA_EX + f"Index of {hex_code2}: {Fore.CYAN}{index2}")
            print(Fore.LIGHTGREEN_EX + f"Repacking: {index1} ➤➤ {index2}")

            # Perform the hex editing for each pair
            search_bytes = bytes.fromhex(hex_code1)
            replace_byte1 = bytes.fromhex(index1)
            replace_byte2 = bytes.fromhex(index2)

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        repack_file_path = os.path.join(output_path, os.path.relpath(file_path, folder_path))
                        if os.path.exists(repack_file_path):
                            with open(repack_file_path, 'rb') as repack_file:
                                repack_data = repack_file.read()
                            if search_bytes in repack_data:
                                modified_data = repack_data.replace(replace_byte1, replace_byte2)
                                with open(repack_file_path, 'wb') as repack_file:
                                    repack_file.write(modified_data)
                                continue  
                        
                        with open(file_path, 'rb') as f:
                            data = f.read()
                        if search_bytes in data:
                            modified_data = data.replace(replace_byte1, replace_byte2)
                            relative_path = os.path.relpath(file_path, folder_path)
                            new_file_path = os.path.join(output_path, relative_path)
                            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                            with open(new_file_path, 'wb') as f:
                                f.write(modified_data)
                    except Exception as e:
                        print(Fore.RED + f"Error processing file {file_path}: {e}")
        else:
            print(Fore.RED + "One or both hex codes were not found in the index.")

# =================== REPACK FUNCTION (USING EXECUTABLE) ===================
def repakgamepach1(selected_file):
    """
    Repack edited files while keeping the original .pak file unchanged.
    This function uses the DARK_PAK folder structure.
    """
    pak_name = selected_file.stem
    repack_dir = unpack_repack_dir / pak_name / "repack"
    result_dir = unpack_repack_dir / pak_name / "result"

    if not repack_dir.exists():
        print(Fore.RED + f"No edited files found in the repack directory for {selected_file.name}.")
        return

    print(Fore.CYAN + f"Repacking {selected_file.name} while keeping the original safe...")

    # Ensure result directory exists  
    result_dir.mkdir(parents=True, exist_ok=True)

    # Paths  
    original_pak_file = paks_dir / selected_file.name
    copied_pak_file = repack_dir / selected_file.name
    result_pak_file = result_dir / selected_file.name

    # Step 1: Copy original .pak to repack folder  
    shutil.copy2(original_pak_file, copied_pak_file)
    print(Fore.BLUE + "Copied original file to repack folder.")

    # Step 2: Run repacking using the copied file  
    print(Fore.LIGHTGREEN_EX + "Repacking in progress...")
    subprocess.run([str(executable_script), "-a", "-r", str(copied_pak_file), str(repack_dir)])
    time.sleep(1)  # simple wait loop to simulate progress

    # Step 3: Move repacked .pak to result folder  
    if copied_pak_file.exists():
        shutil.move(copied_pak_file, result_pak_file)
        print(Fore.GREEN + f"Repacking completed! Modified .pak saved at {result_pak_file}.")
    else:
        print(Fore.RED + "Repacking failed! No file was created in the result folder.")
        return

    # Step 4: Delete temporary file if it still exists  
    if copied_pak_file.exists():
        os.remove(copied_pak_file)
        print(Fore.YELLOW + "Temporary file deleted from repack folder.")

    time.sleep(2)

def auto_repack():
    """
    Automatically triggers repacking for game_patch_3.7.0.19766.
    """
    target_pak = paks_dir / "game_patch_3.7.0.19766.pak"
    if not target_pak.exists():
        print(Fore.RED + f"{target_pak} not found. Repack aborted.")
        return
    print(Fore.LIGHTCYAN_EX + f"\nInitiating automatic repack for {target_pak.name} ...")
    repakgamepach1(target_pak)

# =================== MAIN MENU ===================
def main():
    display_welcome()
    
    # Path to the items index file  
    index_file = '/storage/emulated/0/DARK_PAK/Index.txt'

    # Load the index data from the file  
    try:
        with open(index_file, 'r') as f:
            index_data = f.readlines()
    except Exception as e:
        print(Fore.RED + f"Error reading index file: {e}")
        return

    while True:
        clear_screen()
        border = Fore.MAGENTA + "=" * 60
        print(border)
        print(Fore.CYAN + Style.BRIGHT + "              DARK_PAK HEX EDITOR & REPACKER")
        print(border)
        print(Style.BRIGHT + Fore.WHITE + "\n1. Enter SKIN HEX codes")
        print(Style.BRIGHT + Fore.WHITE + "2. EXIT")
        print(border)
        
        choice = input("\n" + Fore.LIGHTYELLOW_EX + "Enter your choice (1 or 2): ").strip()

        if choice == "1":
            clear_screen()
            print(Fore.LIGHTBLUE_EX + "\nEnter hex pairs (HexA,HexB). Type 'q' to finish:")
            bulk_input = []
            
            while True:
                line = input(Fore.WHITE + ">> ").strip()
                if line.lower() == 'q':  
                    if not bulk_input:
                        print(Fore.RED + "No valid skin pairs entered. Exiting.")
                        time.sleep(1.5)
                        return
                    break
                elif line:
                    bulk_input.append(line)

            # Split the bulk input into pairs  
            skins = [tuple(line.split(',')) for line in bulk_input]

            # Define folder paths for hex editing for game_patch_3.7.0.19766  
            folder_path = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19766/unpack/"
            output_path = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19766/repack/"

            # Perform hex editing  
            hex_edit(folder_path, skins, output_path, index_data)
            print(Fore.GREEN + "\nHex editing completed successfully.")

            # Automatically trigger repacking for game_patch_3.7.0.19766  
            auto_repack()
            input(Fore.LIGHTYELLOW_EX + "\nPress Enter to return to the main menu...")

        elif choice == "2":
            print(Fore.GREEN + "\nExiting. Thank you for using DARK_PAK!")
            time.sleep(1)
            break
        else:
            print(Fore.RED + "\nInvalid choice, please select 1 or 2.")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
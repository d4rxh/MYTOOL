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
    """Displays a welcome message with credits and tool name."""
    clear_screen()
    border = Fore.GREEN + "=" * 60
    tool_name = Fore.GREEN + Style.BRIGHT + "\n       X-suit entry emote tool\n"
    welcome_msg = Fore.GREEN + Style.BRIGHT + "       WELCOME TO THE ENTRY EMOTE TOOL BY DARSH\n"
    credit_msg = Fore.YELLOW + "                      Developed by Darshan\n"
    print(border)
    print(tool_name)
    print(welcome_msg)
    print(credit_msg)
    print(border)
    time.sleep(2)

################ CONFIGURATION ################

# Base directory for DARK_PAK (update if needed)
dark_mods_dir = Path("/storage/emulated/0/DARK_PAK/UNPACK_REPACK")

# Folder with original .pak files (should contain game_patch_3.7.0.19773.pak)
paks_dir = dark_mods_dir / "PAKS"

# Folder with unpacked and repacked files
unpack_repack_dir = dark_mods_dir / "UNPACK"

# Executable script path (assumed to be in home/DARK_PAK as an example)
executable_script = Path.home() / "DARK_PAK" / "DARKSIDE"

################ HEX EDITING FUNCTIONS ################

def hex_edit(folder_path, skins, output_path):
    """
    Perform hex editing on files based on the skin pairs.
    For each pair entered (HexA,HexB), the function replaces occurrences of HexA with HexB.
    If folder_path is a file, only that file will be processed.
    """
    folder_path = Path(folder_path)
    output_path = Path(output_path)

    if folder_path.is_file():
        # Process a single file
        output_file = output_path / folder_path.name
        try:
            with open(folder_path, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(Fore.YELLOW + f"Error reading file {folder_path}: {e}")
            return

        for i, (hex_code1, hex_code2) in enumerate(skins):
            try:
                search_bytes = bytes.fromhex(hex_code1.strip())
                replace_bytes = bytes.fromhex(hex_code2.strip())
            except ValueError as e:
                print(Fore.YELLOW + f"Invalid hex input: {e}")
                continue

            if search_bytes in data:
                data = data.replace(search_bytes, replace_bytes)
                print(Fore.GREEN + f"Editing Skin Pair {i+1}: {Fore.WHITE}{hex_code1} ►► {Fore.GREEN}{hex_code2}")
                print(Fore.GREEN + f"Replaced {hex_code1} with {hex_code2} in {folder_path.name}")
            else:
                print(Fore.YELLOW + f"Hex code {hex_code1} not found in {folder_path.name}.")

        # Write the modified data to the output file
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(data)
            print(Fore.GREEN + f"\nModified file saved as: {output_file}")
        except Exception as e:
            print(Fore.YELLOW + f"Error writing file {output_file}: {e}")

    else:
        # Process all files in the directory
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                except Exception as e:
                    print(Fore.YELLOW + f"Error reading file {file_path}: {e}")
                    continue

                for i, (hex_code1, hex_code2) in enumerate(skins):
                    try:
                        search_bytes = bytes.fromhex(hex_code1.strip())
                        replace_bytes = bytes.fromhex(hex_code2.strip())
                    except ValueError as e:
                        print(Fore.YELLOW + f"Invalid hex input: {e}")
                        continue

                    if search_bytes in data:
                        data = data.replace(search_bytes, replace_bytes)
                        print(Fore.GREEN + f"Editing Skin Pair {i+1}: {Fore.WHITE}{hex_code1} ►► {Fore.GREEN}{hex_code2}")
                        print(Fore.GREEN + f"Replaced {hex_code1} with {hex_code2} in {file}")
                    else:
                        print(Fore.YELLOW + f"Hex code {hex_code1} not found in {file}.")

                relative_path = os.path.relpath(file_path, folder_path)
                new_file_path = output_path / relative_path
                os.makedirs(new_file_path.parent, exist_ok=True)
                try:
                    with open(new_file_path, 'wb') as f:
                        f.write(data)
                except Exception as e:
                    print(Fore.YELLOW + f"Error writing file {new_file_path}: {e}")

################ REPACK FUNCTION (USING EXECUTABLE) ################

def repakgamepach1(selected_file):
    """
    Repack edited files while keeping the original .pak file unchanged.
    This function uses the DARK_PAK folder structure.
    """
    pak_name = selected_file.stem
    repack_dir = unpack_repack_dir / pak_name / "repack"
    result_dir = unpack_repack_dir / pak_name / "result"

    if not repack_dir.exists():
        print(Fore.YELLOW + f"No edited files found in the repack directory for {selected_file.name}.")
        return

    print(Fore.GREEN + f"Repacking {selected_file.name} while keeping the original safe...")

    # Ensure result directory exists
    result_dir.mkdir(parents=True, exist_ok=True)

    # Paths
    original_pak_file = paks_dir / selected_file.name
    copied_pak_file = repack_dir / selected_file.name
    result_pak_file = result_dir / selected_file.name

    # Step 1: Copy original .pak to repack folder
    shutil.copy2(original_pak_file, copied_pak_file)
    print(Fore.GREEN + "Copied original file to repack folder.")

    # Step 2: Run repacking using the copied file
    print(Fore.GREEN + "Repacking in progress...")
    subprocess.run([str(executable_script), "-a", "-r", str(copied_pak_file), str(repack_dir)])
    time.sleep(1)  # simple wait loop to simulate progress

    # Step 3: Move repacked .pak to result folder
    if copied_pak_file.exists():
        shutil.move(copied_pak_file, result_pak_file)
        print(Fore.GREEN + f"Repacking completed! Modified .pak saved at {result_pak_file}.")
    else:
        print(Fore.YELLOW + "Repacking failed! No file was created in the result folder.")
        return

    # Step 4: Delete temporary file if it still exists
    if copied_pak_file.exists():
        os.remove(copied_pak_file)
        print(Fore.YELLOW + "Temporary file deleted from repack folder.")

    time.sleep(2)

def auto_repack():
    """
    Automatically triggers repacking for game_patch_3.7.0.19773.
    """
    target_pak = paks_dir / "game_patch_3.7.0.19773.pak"
    if not target_pak.exists():
        print(Fore.YELLOW + f"{target_pak} not found. Repack aborted.")
        return
    print(Fore.GREEN + f"\nInitiating automatic repack for {target_pak.name} ...")
    repakgamepach1(target_pak)

################ MAIN MENU ################

def main():
    display_welcome()

    # Path to the items index file (if needed for other functionalities)
    index_file = '/storage/emulated/0/DARK_PAK/Index.txt'
    try:
        with open(index_file, 'r') as f:
            index_data = f.readlines()
    except Exception as e:
        print(Fore.YELLOW + f"Error reading index file: {e}")
        # Even if the index file is missing, we can proceed with hex editing
        index_data = []

    while True:
        clear_screen()
        border = Fore.GREEN + "=" * 60
        print(border)
        print(Fore.GREEN + Style.BRIGHT + "              ENTRY EMOTE TOOL BY DARSH")
        print(border)
        # Modified menu options
        print(Style.BRIGHT + Fore.WHITE + "\n1. MOD ANY ENTRY EMOTE")
        print(Style.BRIGHT + Fore.WHITE + "2. exit tool")
        print(border)

        choice = input("\n" + Fore.YELLOW + "Enter your choice (1 or 2): ").strip()    

        if choice == "1":
            clear_screen()
            print(Fore.GREEN + "\nEnter hex pairs (HexA,HexB). Type 'q' to finish:")
            bulk_input = []
                
            while True:
                line = input(Fore.WHITE + ">> ").strip()
                if line.lower() == 'q':
                    if not bulk_input:
                        print(Fore.YELLOW + "No valid skin pairs entered. Exiting.")
                        time.sleep(1.5)
                        return
                    break
                elif line:
                    bulk_input.append(line)

            # Parse the input into pairs (each should be in the format: HexA,HexB)
            try:
                skins = [tuple(line.split(',')) for line in bulk_input]
            except Exception as e:
                print(Fore.YELLOW + f"Error parsing input: {e}")
                time.sleep(2)
                continue

            # Define file path for hex editing for game_patch_3.7.0.19773
            # This single .dat file will be processed.
            folder_path = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19773/unpack/0026e939.dat"
            output_path = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19773/repack/"

            # Perform hex editing
            hex_edit(folder_path, skins, output_path)
            print(Fore.GREEN + "\nHex editing completed successfully.")

            # Automatically trigger repacking for game_patch_3.7.0.19773
            auto_repack()
            input(Fore.YELLOW + "\nPress Enter to return to the main menu...")

        elif choice == "2":
            print(Fore.GREEN + "\nExiting. Thank you for using ENTRY EMOTE TOOL BY DARSH!")
            time.sleep(1)
            break
        else:
            print(Fore.YELLOW + "\nInvalid choice, please select 1 or 2.")
            time.sleep(1.5)
    
    # Final credit message
    print(Fore.WHITE + "\nThis tool is made by DARSH")
    time.sleep(2)

if __name__ == "__main__":
    main()
import os
import requests
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from rich.progress import track

# Initialize Rich console
console = Console()

# File paths (update these if needed)
ORIGINAL_BINARY = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19773/unpack/0026c7f9.uasset"
MODIFIED_FOLDER = "/storage/emulated/0/DARK_PAK/UNPACK_REPACK/UNPACK/game_patch_3.7.0.19773/repack/"

# Pastebin API credentials and paste IDs (using your provided values)
PASTEBIN_API_KEY = "q5Cj4Yq8R-OCtelxRCwLbvZvoyKZfLyw"
PASTEBIN_USER_API_KEY = "a8bddbb5b1755c060c0f63a130bff66e"
XSUIT_PASTE_ID = "ZAn3bz4p"
OUTFITS_PASTE_ID = "hn0jReVN"

def clear_screen():
    """Clears the console screen."""
    console.clear()

def get_paste_content(paste_id, dev_key, user_key):
    """Fetch the raw content of a private Pastebin paste."""
    url = "https://pastebin.com/api/api_raw.php"
    data = {
        "api_dev_key": dev_key,
        "api_user_key": user_key,
        "api_option": "show_paste",
        "api_paste_key": paste_id
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error fetching paste: {response.status_code}")

def load_items_from_pastebin(paste_id, dev_key, user_key):
    """
    Load and parse items from the paste content.
    Expected format per line: Name: HexValue
    """
    content = get_paste_content(paste_id, dev_key, user_key)
    items = {}
    for line in content.splitlines():
        if ':' in line:
            name, hex_value = line.split(':', 1)
            items[name.strip()] = hex_value.strip()
    return items

def choose_multiple_items(items, prompt_text):
    """
    Displays a table of items and lets the user select multiple entries
    via comma-separated indices. Returns a dict of selected items.
    """
    table = Table(title=prompt_text, style="bold cyan", header_style="bold magenta")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    for idx, name in enumerate(items.keys(), start=1):
        table.add_row(str(idx), name)
    console.print(table)
    indices_input = Prompt.ask("[bold yellow]Enter comma separated indices[/bold yellow]")
    try:
        indices = [int(x.strip()) for x in indices_input.split(",")]
    except ValueError:
        console.print("[red]Invalid input. Please enter numbers separated by commas.[/red]")
        return None
    selected = {}
    for i in indices:
        if 1 <= i <= len(items):
            key = list(items.keys())[i - 1]
            selected[key] = items[key]
        else:
            console.print(f"[red]Index {i} is out of range.[/red]")
    return selected

def choose_replacement_for_xsuit(x_suit_name, outfits):
    """
    Prompts the user to search and select a replacement outfit for a given X-Suit.
    Returns a tuple (selected_outfit_name, outfit_hex).
    """
    console.print(Panel(f"Select replacement for [bold]{x_suit_name}[/bold]", style="green"))
    search_term = Prompt.ask("Enter search term for outfit (press Enter to list all)", default="").lower()
    if search_term:
        filtered_outfits = {name: hex_val for name, hex_val in outfits.items() if search_term in name.lower()}
        if not filtered_outfits:
            console.print("[red]No matching outfits found. Showing all outfits.[/red]")
            filtered_outfits = outfits
    else:
        filtered_outfits = outfits

    table = Table(title="Available Outfits", style="bold cyan", header_style="bold magenta")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    for idx, name in enumerate(filtered_outfits.keys(), start=1):
        table.add_row(str(idx), name)
    console.print(table)
    
    choice = Prompt.ask("Enter the index for replacement outfit")
    try:
        choice = int(choice)
        if 1 <= choice <= len(filtered_outfits):
            selected_name = list(filtered_outfits.keys())[choice - 1]
            return selected_name, filtered_outfits[selected_name]
        else:
            console.print("[red]Invalid choice number.[/red]")
            return None, None
    except ValueError:
        console.print("[red]Invalid input, please enter a number.[/red]")
        return None, None

def perform_replacements(replacements):
    """
    Reads the original binary file and applies multiple hex replacements.
    'replacements' is a list of tuples: (x_suit_name, x_hex, outfit_name, outfit_hex).
    A progress animation is displayed during processing.
    """
    with console.status("Processing hex replacements...", spinner="dots"):
        try:
            with open(ORIGINAL_BINARY, 'rb') as file:
                data = file.read()
            for rep in track(replacements, description="Replacing hex values...", style="green"):
                x_name, x_hex, outfit_name, outfit_hex = rep
                data = data.replace(bytes.fromhex(x_hex), bytes.fromhex(outfit_hex))
                time.sleep(0.2)  # simulate processing time for visual effect
            os.makedirs(MODIFIED_FOLDER, exist_ok=True)
            modified_file = os.path.join(MODIFIED_FOLDER, os.path.basename(ORIGINAL_BINARY))
            with open(modified_file, 'wb') as file:
                file.write(data)
            return modified_file
        except Exception as e:
            raise e

def mod_kill_message():
    """Main function for the MOD KILLMESSAGE option."""
    clear_screen()
    console.print(Panel("MOD KILLMESSAGE", style="bold magenta"))
    
    # Load X-Suits from Pastebin with loading animation
    with console.status("Loading X-Suits...", spinner="dots"):
        try:
            xsuits = load_items_from_pastebin(XSUIT_PASTE_ID, PASTEBIN_API_KEY, PASTEBIN_USER_API_KEY)
            xsuits = {k.replace(" (4-Star)", ""): v for k, v in xsuits.items()}
        except Exception as e:
            console.print(f"[red]Failed to load X-Suits: {e}[/red]")
            return
    
    # Load Outfits from Pastebin with loading animation
    with console.status("Loading Outfits...", spinner="dots"):
        try:
            outfits = load_items_from_pastebin(OUTFITS_PASTE_ID, PASTEBIN_API_KEY, PASTEBIN_USER_API_KEY)
        except Exception as e:
            console.print(f"[red]Failed to load Outfits: {e}[/red]")
            return

    # Allow user to select multiple X-Suits to replace
    selected_xsuits = choose_multiple_items(xsuits, "Select X-Suits to replace")
    if not selected_xsuits:
        console.print("[red]No valid X-Suits selected. Returning to main menu.[/red]")
        return

    # For each selected X-Suit, prompt for its individual replacement outfit
    replacements = []
    for x_suit_name, x_hex in selected_xsuits.items():
        replacement_name, replacement_hex = choose_replacement_for_xsuit(x_suit_name, outfits)
        if replacement_name is None:
            console.print(f"[red]Skipping {x_suit_name} due to invalid replacement selection.[/red]")
            continue
        replacements.append((x_suit_name, x_hex, replacement_name, replacement_hex))
    
    if not replacements:
        console.print("[red]No replacements selected. Returning to main menu.[/red]")
        return

    # Display a summary of the planned replacements
    summary_table = Table(title="Replacement Summary", style="bold cyan", header_style="bold magenta")
    summary_table.add_column("X-Suit", style="magenta")
    summary_table.add_column("Replacement Outfit", style="green")
    for rep in replacements:
        summary_table.add_row(rep[0], rep[2])
    console.print(summary_table)

    confirm = Prompt.ask("Confirm replacements? (y/n)", default="n")
    if confirm.lower() != "y":
        console.print("[yellow]Operation cancelled by user. Returning to main menu.[/yellow]")
        return

    # Perform the hex replacements with progress animation
    try:
        modified_file = perform_replacements(replacements)
        console.print(f"[green]Modified file saved to: {modified_file}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to perform hex replacements: {e}[/red]")

def main_menu():
    """Displays the main menu with options and handles user selection."""
    while True:
        clear_screen()
        menu_panel = Panel(
            "[bold cyan]1.[/bold cyan] MOD KILLMESSAGE\n"
            "[bold cyan]2.[/bold cyan] EXIT",
            title="[bold magenta] BEYONDBIRTHDAY[/bold magenta]",
            subtitle="Select an option",
            style="bold white",
        )
        console.print(menu_panel)
        choice = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]")
        if choice == "1":
            mod_kill_message()
            Prompt.ask("\nPress Enter to return to the main menu")
        elif choice == "2":
            console.print("[bold red]Exiting...[/bold red]")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()

import os
import re
from lxml import etree as ET

# Directory containing translation files
translation_dir = "./translations/"
translation_file_prefix = "translation_"
excluded_languages = {"en"}  # Exclude English from modification

# Function to load translations from a file
def load_translations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return ET.parse(file, parser=ET.XMLParser(remove_blank_text=False))

# Compare translations and return outdated ones
def find_outdated_translations(no_translations, en_translations):
    outdated = {}
    for no_text in no_translations.iter("text"):
        no_name = no_text.get("name")
        no_text_value = no_text.get("text")
        en_text = en_translations.find(f".//text[@name='{no_name}']")
        if en_text is not None and no_text_value != en_text.get("text"):
            outdated[no_name] = {
                "outdated_text": no_text_value,
                "updated_text": en_text.get("text"),
            }
    return outdated

# Update a specific translation file by fixing outdated translations
def update_translation_file(file_path, outdated_translations):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    modified = False

    # Regular expression to find <text name="..." text="..."/>
    text_pattern = r'<text\s+name="(?P<name>[^"]+)"\s+text="(?P<text>.*?)"\s*/>'

    def replace_text(line):
        nonlocal modified
        match = re.match(text_pattern, line, re.DOTALL)
        if match:
            name = match.group("name")
            current_text = match.group("text")
            if name in outdated_translations:
                outdated_info = outdated_translations[name]
                if current_text == outdated_info["outdated_text"]:
                    modified = True
                    # Replace only if current_text matches outdated_text exactly
                    return line.replace(current_text, outdated_info["updated_text"])
        return line

    updated_lines = [replace_text(line) for line in lines]

    # Write back the updated content if modified
    if modified:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)
        print(f"Updated translations saved to: {file_path}")

def main():
    # Load Norwegian and English translations
    no_file = os.path.join(translation_dir, "translation_no.xml")
    en_file = os.path.join(translation_dir, "translation_en.xml")

    no_tree = load_translations(no_file)
    en_tree = load_translations(en_file)

    no_texts = no_tree.find("texts")
    en_texts = en_tree.find("texts")

    # Find outdated translations
    outdated = find_outdated_translations(no_texts, en_texts)

    # Process all translation files, except English
    for file in os.listdir(translation_dir):
        if file.startswith(translation_file_prefix) and file.endswith(".xml"):
            language_code = file[len(translation_file_prefix):-4]
            if language_code in excluded_languages:
                continue  # Skip excluded languages like English

            file_path = os.path.join(translation_dir, file)
            update_translation_file(file_path, outdated)

    print("Outdated translations fixed.")

if __name__ == "__main__":
    main()

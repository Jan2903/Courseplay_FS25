import os
from lxml import etree as ET

# Directories and file prefixes
translation_dir = "./translations/"
output_dir = "./updated_translations/"
translation_file_prefix = "translation_"
excluded_languages = {"en", "de"}  # Exclude English and German from deletion

# Function to load translations from a file
def load_translations(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return ET.parse(file)

# Compare translations and return outdated ones
def find_outdated_translations(no_translations, en_translations):
    outdated = {}
    for no_text in no_translations.iter("text"):
        no_name = no_text.get("name")
        en_text = en_translations.find(f".//text[@name='{no_name}']")
        if en_text is not None and no_text.get("text") != en_text.get("text"):
            outdated[no_name] = no_text.get("text")
    return outdated

# Update other translation files by removing outdated translations
def update_translation_files(outdated_translations):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(translation_dir):
        if file.startswith(translation_file_prefix) and file.endswith(".xml"):
            language_code = file[len(translation_file_prefix):-4]
            if language_code in excluded_languages:
                continue

            file_path = os.path.join(translation_dir, file)
            tree = load_translations(file_path)
            root = tree.getroot()

            # Remove outdated translations
            texts = root.find("texts")
            for text in texts.findall("text"):
                if text.get("name") in outdated_translations:
                    texts.remove(text)

            # Save the updated file
            output_path = os.path.join(output_dir, file)
            tree.write(output_path, pretty_print=True, encoding="UTF-8", xml_declaration=True)
            print(f"Updated translations saved to: {output_path}")

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

    # Update other language files by removing outdated translations
    update_translation_files(outdated)

    print("Outdated translations fixed.")

if __name__ == "__main__":
    main()

import os
import re
from lxml import etree as ET

# Paths and configurations
TRANSLATION_DIR = './translations/'
LANGUAGES = [f"translation_{lang}.xml" for lang in ['br', 'cs', 'ct', 'cz', 'da', 'de', 'ea', 'en', 'es', 'fc', 'fi', 'fr', 'hu', 'it', 'jp', 'kr', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sv', 'tr', 'uk']]

def normalize_text(text):
    """Normalize text by collapsing extra whitespace but keeping line breaks."""
    if text:
        # Preserve line breaks and normalize spaces (remove leading/trailing)
        text = text.strip()  # remove any leading or trailing spaces
        text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces into one
    return text

def parse_xml(file_path):
    """Parse an XML file and return its root element."""
    try:
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.parse(file_path, parser)
        return tree.getroot(), tree
    except ET.XMLSyntaxError as e:
        print(f"Error parsing {file_path}: {e}")
        return None, None

def update_translations():
    """Main function to update translations."""
    # Parse the English and Norwegian translations
    en_file = os.path.join(TRANSLATION_DIR, 'translation_en.xml')
    no_file = os.path.join(TRANSLATION_DIR, 'translation_no.xml')

    en_root, _ = parse_xml(en_file)
    no_root, _ = parse_xml(no_file)

    if en_root is None or no_root is None:
        print("Error: Could not parse required files.")
        return

    # Find outdated translations in Norwegian
    outdated_translations = {}
    for en_text in en_root.iter('text'):
        name = en_text.get('name')
        en_value = normalize_text(en_text.get('text'))

        no_text = no_root.find(f"text[@name='{name}']")
        if no_text is not None:
            no_value = normalize_text(no_text.get('text'))

            # Debugging the comparison
            print(f"Comparing {name}:")
            print(f"EN: {en_value}")
            print(f"NO: {no_value}")
            
            if en_value != no_value:
                print(f"Outdated translation found: {name}")
                outdated_translations[name] = no_value

    if not outdated_translations:
        print("No outdated translations found.")
        return

    print(f"Outdated translations detected: {outdated_translations.keys()}")

    # Process each translation file
    for lang_file in LANGUAGES:
        lang_path = os.path.join(TRANSLATION_DIR, lang_file)
        if not os.path.isfile(lang_path):
            print(f"File not found: {lang_path}")
            continue

        print(f"Updating {lang_file}...")
        lang_root, tree = parse_xml(lang_path)

        if lang_root is None or tree is None:
            print(f"Failed to parse {lang_file}. Skipping.")
            continue

        updated = False
        for name, outdated_value in outdated_translations.items():
            lang_text = lang_root.find(f"text[@name='{name}']")
            if lang_text is not None:
                lang_value = lang_text.get('text')

                # Check if the translation is an exact match of the outdated one
                if normalize_text(lang_value) == normalize_text(outdated_value):
                    print(f" - Updating {name} in {lang_file}")
                    lang_text.set('text', en_root.find(f"text[@name='{name}']").get('text'))
                    updated = True

        if updated:
            tree.write(lang_path, pretty_print=True, xml_declaration=True, encoding='UTF-8')
            print(f"Updated {lang_file}")
        else:
            print(f"No changes required for {lang_file}.")

if __name__ == "__main__":
    update_translations()

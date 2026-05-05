import csv, time

import pywikibot


def add_text_to_beginning(page_title, text_to_add, summary_message):
    """
    Add a line of text at the beginning of a Wikipedia page.

    Args:
        page_title (str): The title of the page to edit
        text_to_add (str): The text to add at the beginning
        summary_message (str): Edit summary message
    """
    # Connect to the site (default is Wikipedia)
    site = pywikibot.Site('eu', 'wikipedia')  # Change 'en' for other language versions
    site.login()

    # Get the page
    page = pywikibot.Page(site, page_title)
    time.sleep(.5)
    try:
        # Get the current page text
        current_text = page.text
        if text_to_add in current_text and "{{Nagusia}}" in current_text:
            new_text = current_text.replace("{{Nagusia}}", "")
        elif text_to_add in current_text and text_to_add.replace("{{nagusia", "{{Nagusia") in current_text:
            new_text = current_text.replace(text_to_add, "")
        elif "{{Nagusia}}" in current_text:
            return 0
        elif text_to_add in current_text:
            return 0
        else:
            new_text = text_to_add + '\n' + current_text

        # Save the page with the new text
        page.text = new_text
        page.save(summary=summary_message)

        print(f"Successfully added text to '{page_title}'")
        time.sleep(.5)
        return 1
    except pywikibot.exceptions.NoPageError:
        print(f"Page '{page_title}' does not exist")
    except pywikibot.exceptions.LockedPageError:
        print(f"Page '{page_title}' is locked and cannot be edited")
    except Exception as e:
        print(f"An error occurred: {e}")


count = 0
with open("nagusia_candidates.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:

        if row['nagusia_onwiki'] == "None":
            print(row)
            count += add_text_to_beginning(
                page_title= row['cat_title'],
                text_to_add= "{{nagusia|" + row['nagusia_candidate'] + "}}",
                summary_message="Gehitu artikulu nagusia (artikuluaren izenburua = kategoriaren izena)"
            )

print(f"updated {count} articles.")
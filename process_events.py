import json
import os
import argparse
import datetime
import re

# import yaml  # Add this import for YAML handling
from collections import defaultdict  # Add this import for grouping events


def validate_and_format_date(subtitle):
    try:
        # Remove ordinal suffixes (e.g., "1st", "2nd", "3rd") from the date
        subtitle = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", subtitle)
        # Extract the first date in case of a date range (e.g., "7 January 2000 - 8 January 2000")
        first_date = subtitle.split(" - ")[0].strip()
        # Parse the date in the format "1 January 1999"
        parsed_date = datetime.datetime.strptime(first_date, "%d %B %Y")
        return parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date format in subtitle: {subtitle}")


def process_url(url):
    """Remove special characters from url and return a valid URL."""
    url = (
        url.replace(" ", "_")
        .replace("&", "")
        .replace("/", "")
        .replace("(", "")
        .replace(")", "")
        .replace("'", "")
        .replace('"', "")
        .lower()
    )
    return url


def update_hugo_menu(event_type, output_dir):
    """Update the Hugo menu configuration to include the event type and sub-type."""
    hugo_config_path = os.path.join(output_dir, "../hugo.yaml")
    # Split event type into main type and sub-type
    event_parts = event_type.split(" - ")
    main_type = process_url(event_parts[0])

    menu_entry = {"name": event_parts[0], "url": f"/{main_type}/", "weight": 1}

    # Load or create the hugo.yaml file
    if os.path.exists(hugo_config_path):
        with open(hugo_config_path, "r") as f:
            hugo_config = yaml.safe_load(f) or {}
    else:
        hugo_config = {}

    # Ensure the menu section exists
    menu = hugo_config.setdefault("menu", {})
    menu.setdefault("main", [])

    # Add main type to the menu
    if not any(entry.get("name") == event_parts[0] for entry in menu["main"]):
        menu["main"].append(menu_entry)
        print(f"Added main type '{event_parts[0]}' to the menu.")

    # Save the updated hugo.yaml
    with open(hugo_config_path, "w") as f:
        yaml.dump(hugo_config, f)


def clean_hugo_menu(output_dir):
    """Remove all menu items below the 'Search' item in the Hugo menu configuration."""
    hugo_config_path = os.path.join(output_dir, "../hugo.yaml")

    # Load or create the hugo.yaml file
    if os.path.exists(hugo_config_path):
        with open(hugo_config_path, "r") as f:
            hugo_config = yaml.safe_load(f) or {}
    else:
        hugo_config = {}

    # Ensure the menu section exists
    menu = hugo_config.setdefault("menu", {})
    menu.setdefault("main", [])

    # Remove all menu items below the "Search" item
    search_index = next(
        (i for i, entry in enumerate(menu["main"]) if entry.get("name") == "Search"),
        None,
    )
    if search_index is not None:
        menu["main"] = menu["main"][: search_index + 1]

    # Save the updated hugo.yaml
    with open(hugo_config_path, "w") as f:
        yaml.dump(hugo_config, f)


def generate_main_index(output_dir, grouped_events):
    """Generate an _index.md file listing all main types and sub-types with links."""
    content_dir = output_dir
    index_file = os.path.join(content_dir, "_index.md")

    # Collect main types and sub-types
    event_structure = defaultdict(set)
    for event_dir in grouped_events.keys():
        parts = event_dir.replace(output_dir, "").strip(os.sep).split(os.sep)
        if len(parts) == 1:
            event_structure[parts[0]].add(None)
        elif len(parts) == 2:
            event_structure[parts[0]].add(parts[1])

    # Write the _index.md file
    with open(index_file, "w") as f:
        f.write(f"---\n")
        f.write(f'title: "Event Types"\n')
        f.write(f"date: \"{datetime.datetime.now().strftime('%Y-%m-%d')}\"\n")
        f.write(f"---\n\n")
        f.write(f"# Event Types\n\n")
        for main_type, sub_types in sorted(event_structure.items()):
            main_type_title = main_type.replace("_", " ").title()
            f.write(f"## [{main_type_title}]({main_type}/)\n")
            for sub_type in sorted(sub_types):
                if sub_type:
                    sub_type_title = sub_type.replace("_", " ").title()
                    f.write(f"[{sub_type_title}]({main_type}/{sub_type}/) | ")
                else:
                    f.write(f"[{main_type.title()}]({main_type}/)")
            f.write("\n")

    # Write the sub-main index files
    for main_type, sub_types in sorted(event_structure.items()):
        main_type_dir = os.path.join(content_dir, main_type)
        if not os.path.exists(main_type_dir):
            continue
        sub_index_file = os.path.join(main_type_dir, "_index.md")
        with open(sub_index_file, "w") as f:
            f.write(f"---\n")
            f.write(f'title: "%s"\n' % main_type.replace("_", " ").title())
            f.write(f"date: \"{datetime.datetime.now().strftime('%Y-%m-%d')}\"\n")
            f.write(f"---\n\n")

            f.write(f"# {main_type.replace('_', ' ').title()}\n\n")
            for sub_type in sorted(sub_types):
                if sub_type:
                    sub_type_title = sub_type.replace("_", " ").title()
                    f.write(f"## [{sub_type_title}]({main_type}/{sub_type}/)\n")
                else:
                    f.write(f"## [{main_type.title()}]({main_type}/)\n")

    print(f"Main _index generated at {index_file}")


def generate_this_week(output_dir, event):
    """Writes an event to the /this-week/index.md"""
    os.makedirs(os.path.join(output_dir, "this-week"), exist_ok=True)
    output_file = os.path.join(output_dir, "this-week", "_index.md")
    with open(output_file, "a") as f:
        f.write(f"## {event['name']}\n")
        f.write(f"- **Date:** {event['subtitle']}\n")
        f.write(f"- **Location:** {event['address']}\n")
        # f.write(f"- **Telephone:** {event['telephone']}\n")
        # f.write(f"- **Email:** {event['email']}\n")
        # f.write(f"- **Event Type:** {event['event_type']}\n")
        # f.write(f"- **Organiser:** {event['organiser']}\n")
        if event["actions"]:
            f.write(f"- **More Info:** {event['actions'][0]['url']}\n\n")
        # else:
        # look up the organiser in EventOrganisers.csv and add the URL from the second column
        # with open("EventOrganisers.csv", "r") as csvfile:
        #     for line in csvfile:
        #         if event["organiser"] in line:
        #             url = line.split(",")[1].strip()
        #             f.write(f"- **More Info:** {url}\n\n")
        # Add the image URL if it doesn't contain "motorsport-uk-logo"
        if "motorsport-uk-logo" not in event["img_url"]:
            f.write(f"![Event Image]({event['img_url']})\n\n")


def process_events(input_file, output_dir):
    """Process Motorsport UK events for Hugo content generation."""

    # Clean the Hugo menu before processing events
    # clean_hugo_menu(output_dir)

    # Load the events data from the input JSON file
    with open(input_file, "r") as f:
        events = json.load(f)

    # Ensure the directories exist
    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing {len(events)} events...")

    # Group events by main type and sub-type
    grouped_events = defaultdict(list)

    # Process each event
    for event in events:
        info_list = event.get("info", [])
        if not isinstance(info_list, list):
            print(
                f"Warning: 'info' is not a list for event ID {event.get('id', 'Unknown')}. Skipping..."
            )
            continue

        event_type = next(
            (info["value"] for info in info_list if info.get("title") == "Event Type"),
            "Unknown",
        )
        # Split event type into main type and sub-type
        if " - " in event_type:
            event_parts = event_type.split(" - ")
            main_type = process_url(event_parts[0])
            sub_type = process_url(event_parts[1]) if len(event_parts) > 1 else None
        else:
            main_type = "other"
            event_parts = event_type.split(" (NCR")
            sub_type = process_url(event_parts[0])

        # Create directories for main type and sub-type
        event_dir = os.path.join(output_dir, main_type)
        if sub_type:
            event_dir = os.path.join(event_dir, sub_type)
        os.makedirs(event_dir, exist_ok=True)

        # Update the Hugo menu
        # update_hugo_menu(event_type, output_dir)

        # Add event to the grouped list
        grouped_events[event_dir].append(
            {
                "id": event["id"],
                "name": event["name"],
                "date": validate_and_format_date(event["subtitle"]),
                "address": event["address"],
                "telephone": event["telephone"],
                "email": event["email"],
                "event_type": event_type,
                "organiser": next(
                    (
                        info["value"]
                        for info in info_list
                        if info.get("title") == "Event Organiser"
                    ),
                    "Unknown",
                ),
                "img_url": event["img_url"],
                "actions": event["actions"],
            }
        )

        # check if date is in the next 7 days
        if validate_and_format_date(
            event["subtitle"]
        ) >= datetime.datetime.now().strftime("%Y-%m-%d"):
            generate_this_week(output_dir, event)

    # Write grouped events to _index.md files
    for event_dir, events in grouped_events.items():
        # Sort events by date
        events.sort(key=lambda e: e["date"])
        index_file = os.path.join(event_dir, "_index.md")
        with open(index_file, "w") as f:
            f.write(f"---\n")
            f.write(
                f'title: "%s"\n' % event_dir.split(os.sep)[-1].replace("_", " ").title()
            )
            f.write(f"date: \"{datetime.datetime.now().strftime('%Y-%m-%d')}\"\n")
            f.write(f"---\n\n")
            for event in events:
                f.write(f"## {event['name']}\n")
                f.write(f"- **Date:** {event['date']}\n")
                f.write(f"- **Location:** {event['address']}\n")
                # f.write(f"- **Telephone:** {event['telephone']}\n")
                # f.write(f"- **Email:** {event['email']}\n")
                # f.write(f"- **Event Type:** {event['event_type']}\n")
                f.write(f"- **Organiser:** {event['organiser']}\n")
                if event["actions"]:
                    base_url = (
                        event["actions"][0]["url"]
                        .replace("http://", "")
                        .replace("https://", "")
                    )
                    f.write(f"- **More Info:** [{base_url}](https://{base_url})\n\n")
                else:
                    # look up the organiser in EventOrganisers.csv and add the URL from the second column
                    with open("EventOrganisers.csv", "r") as csvfile:
                        for line in csvfile:
                            if event["organiser"] in line:
                                if "http" in line:
                                    url = line.split(", ")[1].strip()
                                else:
                                    url = "https://%s" % line.split(",")[1].strip()
                                organiser_name = line.split(",")[0].strip()
                                f.write(
                                    f"- **More Info:** [{organiser_name}]({url})\n\n"
                                )
                # Add the image URL if it doesn't contain "motorsport-uk-logo"
                if "motorsport-uk-logo" not in event["img_url"]:
                    f.write(f"![Event Image]({event['img_url']})\n\n")

    # Generate the main _index.md file
    generate_main_index(output_dir, grouped_events)

    print(f"Processed events saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Motorsport UK events for Hugo."
    )
    parser.add_argument("--input", required=True, help="Input JSON file")
    parser.add_argument(
        "--output", required=True, help="Output directory for Hugo content"
    )
    args = parser.parse_args()
    process_events(args.input, args.output)

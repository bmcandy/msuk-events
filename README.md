# Overview
This application scrapes the Motorsport UK events database and stores the events in a JSON file.  It uses this data to create a static web site, using Hugo.  The website has a separate page for each "Event Type" as described in the JSON returned from the API and each of these pages shows all the events in date order.  The event should have a link from the actions attribute for more information or, if this is an empty array for that event, it should use a lookup file EventOrganisers.csv, which matches the "Event Organiser" value and links to the appropriate site.

There is also a separate page that allows events to be queried directly from the API and filtered by the "Event Type" of the JSON returned from the API.

# References

## API
The events API is https://motorsportuk.sport80.com/api/public/events/locator/data?p=0&i=20&s=&l=&d=10&f=

It takes the following POST data:
* from_date: 2025-04-28 - the from date for events (inclusive)
* region: null - an integer representing the region. Doesn't appear to match any fields.
* to_date: 2025-04-30 - the to date for events (inclusive)
* event_type: 1 - An integer to define the event type (Events: 1, Courses: 3) not to be confused with "Event Type" in the returned JSON schema.

The variables in the URL are:
* p: Paginated results page number
* i: Number of results per page?
* s: Search string to pattern match.  Definitely matches the name attribute, not found anything else it matches.
* l: Location in postcode format, including a space.
* d: Distance from the location specified in miles.
* f: A filter ID?  Not sure how that works.

## JSON Schema
The API returns JSON that matches this schema.

* **`id`**: `"200753"` - A unique identifier for this event.
* **`is_event`**: `true` - A boolean value indicating that this record represents an event, rather than a training session or otherwise.
* **`name`**: `"DANIEL RICCIARDO SERIES CLUB"` - The official name of the event.
* **`subtitle`**: `"3rd May 2025 - 4th May 2025"` - Provides the dates of the event.
* **`subtitle_icon`**: `"mdi-calendar-outline"` -  Likely refers to an icon from the Material Design Icons set, suggesting a calendar icon to visually represent the dates.
* **`address`**: `"Llandow Kart Circuit, CF71 7PB"` - The physical address where the event is located.
* **`geolocation`**: `{ "lng": null, "lat": null }` - Contains the longitude (`lng`) and latitude (`lat`) of the event location. Not always provided for each event and is nearly always null.  Maybe always null.
* **`what3words`**: `null` -  A what3words address for the location, which isn't always provided and is sometime null.  Provided in this string format when not null: "\/\/\/incoming.cringes.professed"
* **`telephone`**: `"07437012982"` - The telephone number for contact related to the event.
* **`email`**: `"jaynemoore@danielricciardoseries.com"` - The email address for enquiries about the event.
* **`info`**: An array of objects, each providing specific details about the event:
    * `{ "title": "Type", "value": "Event" }` - Confirms the type of record.
    * `{ "title": "Status", "value": { "type": "label", "text": "Active", "icon": null, "style": "success", "tooltip": null, "dialog": null } }` - Indicates the event's status is "Active" and provides styling information (likely for display purposes, such as a green "success" label).
    * `{ "title": "Event Type", "value": "KX Arrive & Drive" }` - Specifies the particular type of event.  This is the attribute on which the website is categorised.  It is equivalent to the Motorsport Uk Discipline.
    * `{ "title": "Level", "value": "Certificate of Exemption" }` - Indicates the status of the event.  Usually Clubman, Interclub, National or International for competitive events.
    * `{ "title": "Entries On Platform", "value": "NO" }` - Suggests that entries for this event are not managed on the Motorsport UK Sport:80 platform.
    * `{ "title": "Event Organiser", "value": "DANIEL RICCIARDO SERIES" }` - Identifies the organizer of the event.  This will be used to lookup the organiser details and link to the website if nothing is specified in the actions attributes.
* **`actions`**: An array of objects, defining an associated web address.  This is often an empty array.
    * `{ "type": "external_url_button", "url": "www.danielricciardoseries.com", "text": "Website", "icon": "fa fa-browser", "style": null, "disabled": false, "confirmation_message": null, "default_table_row_action": false, "description": "Website DANIEL RICCIARDO SERIES CLUB" }` - Describes a button that will open the provided URL (`www.danielricciardoseries.com`) in a new tab. The button's text is "Website," it uses a "browser" icon (likely from Font Awesome).
* **`img_url`**: `"https:\/\/d7skausf3l8pb.cloudfront.net\/branding\/79a9db8b-b3a4-497d-bb64-c9c943483349\/copy-of-motorsport-uk-logo-1-672b92fc67532920507009.png"` - A URL pointing to an image for the event in the results.

## JSON Example
{

            "id": "200753",

            "is_event": true,

            "name": "DANIEL RICCIARDO SERIES CLUB",

            "subtitle": "3rd May 2025 - 4th May 2025",

            "subtitle_icon": "mdi-calendar-outline",

            "address": "Llandow Kart Circuit, CF71 7PB",

            "geolocation": {

                "lng": null,

                "lat": null

            },

            "what3words": null,

            "telephone": "07437012982",

            "email": "jaynemoore@danielricciardoseries.com",

            "info": [

                {

                    "title": "Type",

                    "value": "Event"

                },

                {

                    "title": "Status",

                    "value": {

                        "type": "label",

                        "text": "Active",

                        "icon": null,

                        "style": "success",

                        "tooltip": null,

                        "dialog": null

                    }

                },

                {

                    "title": "Event Type",

                    "value": "KX Arrive & Drive"

                },

                {

                    "title": "Level",

                    "value": "Certificate of Exemption"

                },

                {

                    "title": "Entries On Platform",

                    "value": "NO"

                },

                {

                    "title": "Event Organiser",

                    "value": "DANIEL RICCIARDO SERIES"

                }

            ],

            "actions": [

                {

                    "type": "external_url_button",

                    "url": "www.danielricciardoseries.com",

                    "text": "Website",

                    "icon": "fa fa-browser",

                    "style": null,

                    "disabled": false,

                    "confirmation_message": null,

                    "default_table_row_action": false,

                    "description": "Website DANIEL RICCIARDO SERIES CLUB"

                }

            ],

            "img_url": "https:\/\/d7skausf3l8pb.cloudfront.net\/branding\/79a9db8b-b3a4-497d-bb64-c9c943483349\/copy-of-motorsport-uk-logo-1-672b92fc67532920507009.png"

        }
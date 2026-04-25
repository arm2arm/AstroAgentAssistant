---
name: nextcloud-caldav-calendar-management
description: Create, read, update, and delete calendar events via Nextcloud CalDAV API. Includes auth patterns, calendar paths, and quirks for Nextcloud v29+.
version: 1.0.0
author: Hermes Agent
license: MIT
tags: [calendar, nextcloud, caldav]
---

# Nextcloud CalDAV Calendar Management

Manage calendars on a Nextcloud instance via the CalDAV WebDAV API.

## Credentials

Required:
- Username (e.g., `akhalatyan`)
- App Password (generated via Nextcloud → Settings → Security → Devices & sessions → Create new app password)
- Base URL: `https://cloud.aip.de/remote.php/dav/calendars/{username}/`

## Calendar Path Conventions

### Own calendars
URL: `https://{host}/remote.php/dav/calendars/{username}/{calendar-id}/`

Example: `pers%c3%b6nlich` for "Persönlich" (UTF-8 %-encoding required)

### Shared calendars (shared by others)
URL: `https://{host}/remote.php/dav/calendars/{username}/{shared-id}_shared_by_{owner}/`

Common shared calendars:
- `e-science_shared_by_agalkin` (eScience)
- `escience-holidays_shared_by_agalkin` (eScience Holidays)
- `4most_shared_by_agalkin` (4MOST)
- `punch4nfdi_shared_by_agalkin` (PUNCH4NFDI)
- `personal_shared_by_henke` (Harry)
- `mhd-out_shared_by_delstner` (mhd-out)
- `hpc-coffee-talk_shared_by_esacchi` (HPC coffee talk)

**Note:** Some shared calendars are read-only — writing may return HTTP 500 "Internal Server Error". Check with the owner for write permission.

## Authentication

HTTP Basic Auth:
```
-u "{username}:{app-password}"
```

Example:
```bash
curl -s -u "akhalatyan:Aac3Y-WTtq7-yCTq7-LQixM-2bzWz" \
  -X PROPFIND -H "Depth: 1" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/"
```

## Creating an Event (PUT)

### Minimal working iCal format (Nextcloud v29)

```bash
curl -s -u "{user}:{pass}" \
  -X PUT \
  -H "Content-Type: text/calendar; charset=UTF-8" \
  "https://cloud.aip.de/remote.php/dav/calendars/{user}/{calendar-id}/{filename}.ics" \
  -d 'BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Hermes Agent//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE-TIME:20260922T090000
DTEND;VALUE=DATE-TIME:20260923T180000
SUMMARY:Event Title
DESCRIPTION:Description text
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR'
```

### Key format rules

1. Use `VALUE=DATE-TIME` for DTSTART/DTEND (not plain `DTSTART:YYYYMMDDTHHMMSS`)
2. No `Z` suffix needed for local time (server infers timezone)
3. Include `PRODID`, `VERSION:2.0`, `BEGIN:VCALENDAR`/`END:VCALENDAR` wrapper
4. Filename must end in `.ics`
5. Use UTF-8 %-encoding for special chars in calendar IDs (e.g., `pers%c3%b6nlich`)

### Common pitfalls

- **HTTP 500 "Internal Server Error"**: Usually means write access denied (shared read-only calendar), malformed iCal, or wrong calendar ID
- **Missing UID or DTSTAMP**: Nextcloud requires a unique UID (and optional DTSTAMP) in the VEVENT; omitting them can cause silent failures.
- **Using `--upload-file`**: In some environments this can trigger server errors; prefer sending the iCal content with `-d` (as shown in the example) or ensure the file is correctly uploaded.

- **HTTP 204**: Success (no body)
- **HTTP 401**: Wrong credentials — try just the short username (e.g., `akhalatyan` not full email)
- **UID conflict**: If reusing a UID from another event, Nextcloud may deduplicate — generate a new UID or omit it and let Nextcloud generate one

## Querying Events (REPORT method — BROKEN on cloud.aip.de)

**⚠️ The CalDAV `REPORT` method with `<calendar-query>` consistently fails on cloud.aip.de** with HTTP 400/500 server errors, even when the XML is correctly formed. Do not rely on it.

### Workaround: PROPFIND + GET pattern

1. **List event files** with `PROPFIND Depth:1` and parse `<d:href>` tags.
2. **Filter by filename** for date patterns (e.g., `20260422`) to quickly find same-day events.
3. **For UUID-named events**, get ALL files via PROPFIND, then `GET` each one and parse DTSTART to match the target date.
4. **Python example** (preferred over curl for XML parsing):
```python
import requests, xml.etree.ElementTree as ET
auth = ("akhalatyan", "app-password")
resp = requests.request("PROPFIND", f"{base}/{calendar}/", auth=auth,
                        data=propfind_xml, headers={"Depth": "1"})
root = ET.fromstring(resp.text)
for resp_el in root.findall('.//{DAV:}response'):
    href = resp_el.find('{DAV:}href')
    if href is not None:
        print(href.text)  # -> /remote.php/dav/calendars/akhalatyan/cal/file.ics
```
5. **GET individual event files** to read DTSTART/SUMMARY/DESCRIPTION.

### Finding today's events (complete recipe)

```python
# Step 1: PROPFIND each calendar, collect .ics filenames
# Step 2: Filter filenames containing "20260422" for quick matches
# Step 3: For UUID-named events, GET each and parse DTSTART
# Step 4: Combine results from all owned + shared calendars
```

## Reading an Event

```bash
curl -s -u "{user}:{pass}" \
  "https://cloud.aip.de/remote.php/dav/calendars/{user}/{calendar-id}/{filename}.ics"
```

## Deleting an Event

```bash
curl -s -u "{user}:{pass}" -X DELETE \
  "https://cloud.aip.de/remote.php/dav/calendars/{user}/{calendar-id}/{filename}.ics"
```

## Listing Calendars (PROPFIND)

```bash
curl -s -u "{user}:{pass}" \
  -X PROPFIND -H "Depth: 1" \
  "https://cloud.aip.de/remote.php/dav/calendars/{user}/"
```

Response is XML — parse for `<d:displayname>` tags to find calendar IDs.

## MCP Server

Internal Kubernetes MCP server for documentation: `https://mcp-docs.kube.aip.de`
- Uses self-signed certificate (internal CA)
- Requires correct URL path (not just root)
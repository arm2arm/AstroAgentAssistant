---
name: nextcloud-caldav-agent
description: Access and manage calendars on cloud.aip.de Nextcloud via CalDAV. List, create, edit, and delete events in personal and shared calendars. Supports personal (Persoenlich, Students, Gabi, ADMIN) and shared read-only calendars (Harry/henke, eScience/4MOST/PUNCH4NFDI/agalkin, HPC coffee talk/esacchi).
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [productivity, calendar, nextcloud, caldav, events, scheduling]
    category: productivity
    related_skills: [google-workspace, hnralaya]
---

# Nextcloud CalDAV Agent

## When to Use
Use this skill to manage calendar events on the AIP Nextcloud instance (`cloud.aip.de`) from the terminal. Tasks include: listing calendars, checking events, creating events, editing reminders, and managing shared calendars.

## Credentials
- **URL**: `https://cloud.aip.de/remote.php/dav/calendars/<user>/`
- **User**: `akhalatyan`
- **Password**: Stored in Hermes memory — retrieve via session context.

## Personal Calendars (read-write)
- `Persoenlich` — personal events
- `Students`
- `Gabi`
- `ADMIN`

## Shared Calendars (read-only)
- `Harry/henke`
- `eScience/4MOST/PUNCH4NFDI/agalkin`
- `mhd-out/delstner`
- `HPC coffee talk/esacchi`

## Procedure

### 1. List calendars
```bash
curl -s -u "akhalatyan:$PASSWORD" \
  -X PROPFIND \
  -H "Depth: 1" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/"
```

### 2. List events in a calendar
```bash
curl -s -u "akhalatyan:$PASSWORD" \
  -X REPORT \
  -H "Depth: 1" \
  -H "Content-Type: application/xml; charset=utf-8" \
  -d '<?xml version="1.0" encoding="utf-8" ?>
<d:prop-sync xmlns:d="DAV:" xmlns:cs="http://calendarserver.org/ns/">
  <d:prop>
    <d:displayname/>
    <cs:getctag/>
    <d:resourcetype/>
  </d:prop>
</d:prop-sync>' \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/persoenlich/"
```

### 3. Create an event
```bash
curl -s -u "akhalatyan:$PASSWORD" \
  -X PUT \
  -H "Content-Type: text/plain; charset=utf-8" \
  -d "BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Team Meeting
DTSTART:20260415T100000Z
DTEND:20260415T110000Z
DESCRIPTION:Weekly sync
END:VEVENT
END:VCALENDAR" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/persoenlich/meeting-uid.ics"
```

### 4. Delete an event
```bash
curl -s -u "akhalatyan:$PASSWORD" \
  -X DELETE \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/persoenlich/meeting-uid.ics"
```

## Nextcloud Version Note
- Tested with Nextcloud v29+ — CalDAV endpoints follow RFC 4791.
- The `/remote.php/dav/calendars/<user>/<calendar>/` path format is stable.

## Pitfalls
- Shared calendars (Harry, eScience, HPC coffee talk, mhd-out) are **read-only** — PUT/DELETE will fail.
- Credentials must be passed via `-u "user:pass"` — do not use Bearer token auth on this endpoint.
- Calendar names with spaces or special characters must be URL-encoded.
- Always use the correct calendar path — personal calendars are under `akhalatyan/`, shared ones may be under different user paths.

## Verification
- PROPFIND returns calendar list with non-empty response.
- Events are created with correct DTSTART/DTEND.
- Deleted events no longer appear in subsequent listings.
---
name: nextcloud-caldav-agent
description: Access and manage calendars on cloud.aip.de Nextcloud via CalDAV. List, create, edit, and delete events in personal and shared calendars. Credentials are passed via environment variables — never hardcode them.
version: 1.0.0
author: AstroAgent / AIP
license: MIT
metadata:
  hermes:
    tags: [productivity, calendar, nextcloud, caldav, events, scheduling]
    category: productivity
    related_skills: [google-workspace, himalaya]
---

# Nextcloud CalDAV Agent

## When to Use
Use this skill to manage calendar events on the AIP Nextcloud instance (`cloud.aip.de`) from the terminal. Tasks include: listing calendars, checking events, creating events, editing reminders, and managing shared calendars.

## Required Environment Variables

| Variable | Description |
|---|---|
| `CALDAV_USER` | Nextcloud username |
| `CALDAV_PASS` | Nextcloud password |
| `CALDAV_BASE` | CalDAV base URL (e.g. `https://cloud.aip.de/remote.php/dav/calendars/`) |

Set them before use:
```bash
export CALDAV_USER="<your-username>"
export CALDAV_PASS="<your-password>"
export CALDAV_BASE="https://cloud.aip.de/remote.php/dav/calendars/"
```

## Calendar Paths

### Personal Calendars (read-write)
- `Persoenlich` — personal events
- `Students`
- `Gabi`
- `ADMIN`

### Shared Calendars (read-only)
- `Harry/henke`
- `eScience/4MOST/PUNCH4NFDI/agalkin`
- `mhd-out/delstner`
- `HPC coffee talk/esacchi`

## Procedure

### 1. List calendars
```bash
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X PROPFIND \
  -H "Depth: 1" \
  "${CALDAV_BASE}"
```

### 2. List events in a calendar
```bash
CALENDAR="persoenlich"
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
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
  "${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/"
```

### 3. Create an event
```bash
CALENDAR="persoenlich"
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
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
  "${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/meeting-uid.ics"
```

### 4. Delete an event
```bash
CALENDAR="persoenlich"
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X DELETE \
  "${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/meeting-uid.ics"
```

## Nextcloud Version Note
- Tested with Nextcloud v29+ — CalDAV endpoints follow RFC 4791.
- The path format `${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/` is stable.

## Pitfalls
- **Never hardcode credentials** in the SKILL.md — use `CALDAV_USER` and `CALDAV_PASS` environment variables.
- Shared calendars (Harry, eScience, HPC coffee talk, mhd-out) are **read-only** — PUT/DELETE will fail with 403.
- Credentials must be passed via `-u "${CALDAV_USER}:${CALDAV_PASS}"` — do not use Bearer token auth on this endpoint.
- Calendar names with spaces or special characters must be URL-encoded.
- Always use `${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/` — the calendar path always includes the authenticated user.

## Verification
- PROPFIND returns calendar list with non-empty response.
- Events are created with correct DTSTART/DTEND.
- Deleted events no longer appear in subsequent listings.
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

## Known Calendar Paths

Personal calendars (read-write) — URL-encode special characters:
- `persoenlich` → `pers%c3%b6nlich` (contains ö)
- `students` → `students`
- `gabi` → `gabi`
- `admin` → `admin`

Shared calendars (read-only):
- `personal_shared_by_henke` (Harry/Enke)
- `e-science_shared_by_agalkin`
- `4most_shared_by_agalkin`
- `escience-holidays_shared_by_agalkin`
- `mhd-out_shared_by_delstner`

## Procedure

### 1. List calendars
```bash
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X PROPFIND \
  -H "Accept: application/xml" \
  -H "Depth: 1" \
  "${CALDAV_BASE}"
```

### 2. List events in a calendar
```bash
# Calendar path must be URL-encoded — e.g. Persoenlich → pers%c3%b6nlich
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X PROPFIND \
  -H "Accept: application/xml" \
  -H "Depth: 1" \
  "${CALDAV_BASE}${CALDAV_USER}/pers%c3%b6nlich/"
```

### 3. Create an event
```bash
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X PUT \
  -H "Accept: application/xml" \
  -H "Content-Type: text/plain; charset=utf-8" \
  -d "BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Hermes Agent//EN
BEGIN:VEVENT
UID:unique-event-id-$(date +%Y%m%d)
DTSTART;VALUE=DATE-TIME:20260416T113000Z
DTEND;VALUE=DATE-TIME:20260416T123000Z
SUMMARY:Team Meeting
DESCRIPTION:Weekly sync
LOCATION:Zoom
END:VEVENT
END:VCALENDAR" \
  "${CALDAV_BASE}${CALDAV_USER}/pers%c3%b6nlich/unique-event-id.ics"
```

### 4. Delete an event
```bash
curl -s -u "${CALDAV_USER}:${CALDAV_PASS}" \
  -X DELETE \
  -H "Accept: application/xml" \
  "${CALDAV_BASE}${CALDAV_USER}/pers%c3%b6nlich/event-uid-to-delete.ics"
```

## Nextcloud Version Note
- Tested with Nextcloud v29+ — CalDAV endpoints follow RFC 4791.
- The path format `${CALDAV_BASE}${CALDAV_USER}/${CALENDAR}/` is stable.

## Pitfalls
- **Never hardcode credentials** — use `CALDAV_USER` and `CALDAV_PASS` environment variables.
- **Every curl call needs `-H "Accept: application/xml"`** — without it, PROPFIND returns HTML instead of XML (and the server may return 500).
- **Calendar paths must be URL-encoded in the URL** — `Persoenlich` must be `pers%c3%b6nlich`, `Students` → `students`, etc. Using the raw name in the URL causes 500 errors.
- **REPORT requests return 500 on this server** — use `PROPFIND -H "Depth: 1"` instead to list events.
- **Shared calendars** (Harry, eScience, 4MOST, HPC coffee talk, mhd-out) are **read-only** — PUT/DELETE will fail with 403.
- **No CSRF token needed** for Basic auth — the `-u` flag alone works. CSRF is only needed for session-based auth, not HTTP Basic.
- **DTSTART/DTEND must be in UTC** — always use UTC times (`YYYYMMDDTHHMMSSZ`) in VEVENT, or include `VALUE=DATE-TIME;TZID=Europe/Berlin:` with a VTIMEZONE block.
- **UID must be unique** — use a timestamp or UUID. Re-using the same UID overwrites the previous event.

## Verification
- PROPFIND returns calendar list with non-empty response.
- Events are created with correct DTSTART/DTEND.
- Deleted events no longer appear in subsequent listings.
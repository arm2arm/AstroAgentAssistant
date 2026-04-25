---
name: nextcloud-caldav-agent
category: productivity
description: Access and manage calendars on cloud.aip.de Nextcloud via CalDAV — listing, creating, editing, deleting events in personal and shared calendars.
triggers:
  - nextcloud calendar
  - cloud.aip.de calendar
  - caldav cloud
  - create event in calendar
  - nextcloud das calendar
---

# Nextcloud CalDAV — Agent Workflow

## Credentials
- Username: `akhalatyan`
- App Password: `Aac3Y-WTtq7-yCTq7-LQixM-2bzWz`
- CalDAV base: `https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/`

## Authentication
- Format: `curl -u "akhalatyan:TOKEN"` — **no email in username**
- The username is just `akhalatyan`, not `akhalatyan@aip.de`
- Auth failure returns generic `Internal Server Error` (SabreDAV 401 response) — not a real 500

## Known Calendar Slugs (URL paths)
- **Own**: `pers%c3%b6nlich` (Persönlich), `students`, `gabi`, `admin`, `contact_birthdays`
- **Shared (read-write)**: `e-science_shared_by_agalkin` (eScience — confirmed RW)
- **Shared (read-only)**: `escience-holidays_shared_by_agalkin`, `4most_shared_by_agalkin`, `punch4nfdi_shared_by_agalkin`, `personal_shared_by_henke` (Harry), `mhd-out_shared_by_delstner`, `hpc-coffee-talk_shared_by_esacchi`
- **Deck boards (VTODO)**: `app-generated--deck--board-*` (AIP Backup, Proxmox/Ovirt, CLUSTER, Todo, colab, Dashboard Dev, ai-infrastructure, IT-Service, EScience, IT-Service ToDo)
- **NOTE**: `escience_shared_by_agalkin` (WITHOUT hyphen) → 500 error. The correct slug has a hyphen: `e-science_shared_by_agalkin`

## Listing Calendars
```bash
curl -s -u "akhalatyan:TOKEN" -X PROPFIND -H "Depth: 1" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/"
```

## Creating Events
### Step 1: Test with minimal event first
```bash
curl -s -u "akhalatyan:TOKEN" -X PUT \
  -H "Content-Type: text/calendar; charset=UTF-8" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/pers%c3%b6nlich/test-event.ics" \
  -d 'BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Hermes//Test//EN
BEGIN:VEVENT
DTSTART:20260422T100000Z
DTEND:20260422T120000Z
SUMMARY:Test Event
END:VEVENT
END:VCALENDAR'
# Expect: HTTP 204 = success
```

### Step 2: Create real event
**Format**: Use `DTSTART;VALUE=DATE-TIME:` (with explicit VALUE=DATE-TIME parameter, local time, no Z suffix).
**Newlines in DESCRIPTION**: Use `\n` (backslash-n, iCalendar escaping).
**Test first**: Always test with a minimal event before creating the real one — if the test returns 204, the format is correct.

```bash
curl -s -u "akhalatyan:TOKEN" -X PUT \
  -H "Content-Type: text/calendar; charset=UTF-8" \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/pers%c3%b6nlich/event-id.ics" \
  -d 'BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Hermes Agent//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE-TIME:20260422T100000
DTEND;VALUE=DATE-TIME:20260422T120000
SUMMARY:Event Title
DESCRIPTION:Line 1\\nLine 2
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR'
# Expect: HTTP 204 = success
```

## Deleting Events
```bash
curl -s -u "akhalatyan:TOKEN" -X DELETE \
  "https://cloud.aip.de/remote.php/dav/calendars/akhalatyan/pers%c3%b6nlich/event-id.ics"
```

## Troubleshooting
| Problem | Cause | Fix |
|---------|-------|-----|
| 401 Internal Server Error | Wrong password/token | Generate fresh app password at Settings > Security > Devices & sessions |
| 500 on event creation | iCal syntax issue | Remove extra property parameters; use minimal `DTSTART;VALUE=DATE-TIME:` |
| Calendar not found | URL-encode special chars | ö → %c3%b6, ü → %c3%bc |
| Auth fails silently | Wrong username format | Use `akhalatyan` NOT `akhalatyan@aip.de` |

## Key Learnings (Trial & Error)
1. First API token (`-TgeTH-...` starting with dash) always returned 401 — only app passwords from Settings > Security > Devices & sessions work
2. `akhalatyan@aip.de` as username → 401. Must use just `akhalatyan`
3. `escience_shared_by_agalkin` → 500. Correct slug is `e-science_shared_by_agalkin` (hyphen matters)
4. `DTSTART;VALUE=DATE-TIME:20260422T100000` (local time, no Z) works correctly
5. Bare `DTSTART:20260422T100000Z` also works (UTC)
6. Always test with minimal event first — if 204, format is correct
---
name: aip-member-contact-retrieval
description: Retrieve phone number (and email) for a staff member of the Leibniz Institute for Astrophysics Potsdam (AIP) from the public website.
category: productivity
version: 1.0
---

## Goal
Obtain the official phone number (and optionally email) for a given AIP staff member.

## Prerequisites
- Internet access.
- The target person’s full name (as used on the AIP website).

## Steps
1. **Attempt direct table lookup**
   - Use `web_extract` on `https://www.aip.de/en/members/table/`.
   - Search the extracted markdown for the exact name (case‑insensitive).
   - If a table row containing the name is found, locate the **Phone** column (the table shows only the last digits; prepend the fixed prefix `+49 331 7499‑`).
   - Return the full phone number and, if present, the email username (append `@aip.de`).
2. **Fallback: search personal profile**
   - If the name is not found in the table, perform `web_search` with query `"<Name>" AIP`.
   - Take the first result whose URL contains `/members/` (e.g., `https://www.aip.de/members/<slug>/`).
   - `web_extract` that URL.
   - Parse the extracted content for a line like `Phone | **+49 331 7499 XYZ**` and extract the full number.
   - Also optionally extract the email line.
3. **Return result**
   - Provide the phone number in international format (`+49 331 7499 XYZ`).
   - Include the email if available.
   - Add a brief note that AIP’s policy forbids using these contacts for advertising/marketing.

## Pitfalls & Tips
- The members table only shows the last 3‑4 digits; always prepend the prefix `+49 331 7499‑`.
- Some profiles use a non‑standard email username; use the exact email shown.
- The table page may paginate; the `web_extract` result contains the entire table (292 entries) so regex search works.
- If multiple rows match (e.g., similar names), pick the one with the exact full name.

## Verification
- Verify that the extracted phone starts with `+49` and contains the expected number of digits after the country code.
- Ensure the email ends with `@aip.de`.

## Example
```
Input: "Arman Khalatyan"
Output:
Phone: +49 331 7499 528
Email: akhalatyannothing@aip.de
```

---

## Legal / Data‑Protection Note
AIP explicitly states: *"The use of telephone numbers and E‑mail addresses for advertising and marketing purposes is prohibited!"* Respect this policy when handling the data.

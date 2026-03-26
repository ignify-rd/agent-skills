# Postman Web — Navigation Guide

Browser-based Postman at `https://web.postman.co`. Used for executing API test cases and capturing response screenshots as evidence.

---

## Login handling

Navigate to `https://web.postman.co`. Take snapshot to detect state:

- If snapshot contains a **Login / Sign In form** → Postman requires authentication. Notify the user:
  > "Postman web requires login. Please log in to Postman in the browser, then confirm to continue."

  After user confirms, take snapshot again to verify login succeeded. If still on login screen → mark all test cases as ERROR: `"Postman not logged in"` and stop.

- If snapshot shows a **workspace / home page** → already logged in, proceed.

---

## Opening a new HTTP request tab

Once on the workspace, open a fresh request tab. Look in snapshot for one of:
- A **"+"** button in the tab bar (to open a new tab)
- A **"New"** button → then select **"HTTP Request"** from the popup

Click it. Wait for a request editor pane to appear (snapshot should show method dropdown + URL bar).

This single request tab is **reused for all test cases** — just update the fields for each case rather than opening a new tab each time.

---

## Configuring a request

### Method
Find the method dropdown (shows current method: GET, POST, etc.) in snapshot. Click it, then click the desired method from the list.

### URL
Find the URL input bar next to the method dropdown. Clear it (triple-click to select all) then type the new URL.

### Headers
1. Click the **"Headers"** tab below the URL bar.
2. Postman shows a table of key/value rows.
3. For each header to add: find the last empty Key cell, type the key, Tab to Value, type the value.
4. To **clear all previous headers**: before adding new ones, remove existing non-default rows (click the × on each row, or look for "Bulk Edit" mode to paste key:value lines directly).

### Body
1. Click the **"Body"** tab below the URL bar.
2. Select **"raw"** radio button.
3. Change the format dropdown (next to raw) to **"JSON"**.
4. In the text area: select all existing content (Ctrl+A), then type/paste the new body JSON.
5. If body is empty: select **"none"** radio button instead.

---

## Sending the request

Find the **"Send"** button (right side of URL bar). Click it.

After clicking Send:
- Use `mcp__playwright__browser_wait_for` to wait for the response panel to update. Look for:
  - A status code indicator (e.g., an element showing "200 OK")
  - The response body content area becoming non-empty
- Timeout: 15000ms (API calls may be slow)

If Send button is not clickable (grayed out) → take snapshot and report ERROR: `"Postman Send button not available — check URL and method fields"`.

---

## Reading the response

After response loads, take snapshot. In the response panel:

### Status code
Look for text matching the pattern `\d{3} [A-Z]` (e.g., "200 OK", "401 Unauthorized", "404 Not Found"). Extract the numeric part as an integer.

### Response body
- Click the **"Body"** tab in the response panel (if not already selected).
- Find the content area (code editor or text area) showing the response JSON/text.
- Read its text content from snapshot.

If response content is not readable from snapshot, use:
```
mcp__playwright__browser_evaluate(script="
  // attempt to read from Postman's response view
  const bodyEl = document.querySelector('[data-testid=\"response-body\"]')
    || document.querySelector('.response-body-container');
  return bodyEl ? bodyEl.innerText : null;
")
```

If still unreadable → mark result as ERROR: `"Could not read response from Postman UI"`.

---

## Taking the screenshot

Always screenshot the **full response view** (status + body visible):

```
mcp__playwright__browser_take_screenshot(
  type="png",
  filename="screenshots/{testId}_{yyyyMMdd_HHmmss}.png"
)
```

Ensure the response panel is visible and not collapsed before screenshotting.

---

## Handling multiple test cases in sequence

After the first Send:
- **Do NOT** open a new request tab for the next case.
- Simply update the method, URL, headers, and body fields in the same tab and click Send again.
- Clear headers from the previous case before adding new ones to avoid header accumulation.

---

## Troubleshooting

| Issue | Action |
|---|---|
| Postman shows "Request blocked by CORS" | The API doesn't allow browser requests; mark ERROR: "CORS blocked — API does not allow browser-origin requests" |
| Response body is empty / `null` | API returned no body; proceed with status-only validation |
| Postman shows a timeout or network error | Mark ERROR: "Postman request timeout / network error" (retry once after 3s) |
| Login session expired mid-execution | Pause, notify user to re-login, then re-run the current group from the beginning |
| Postman UI changes (element not found) | Use `mcp__playwright__browser_snapshot` to re-inspect the current UI and adapt selectors |

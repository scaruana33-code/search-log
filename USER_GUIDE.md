# Search Log: User Guide

This guide explains how to use Search Log day to day. You don't need to know how to code. Everything here is done by clicking around on the GitHub website, plus one optional step for viewing the dashboard on your Windows PC.

(For first-time technical setup, see [README.md](README.md). You have already done that part.)

---

## 1. What Search Log does

Search Log keeps track of your job applications for you.

Once a week, a robot on GitHub (called a **workflow** or **GitHub Action**):

1. Reads your recent Gmail and looks for job-related emails: application confirmations, interview invites, offers and rejections.
2. Adds or updates each job in a list stored in the file **`data/applications.json`**.
3. Emails you a **weekly summary** with the subject **"Your weekly job-search summary"**.

It only *reads* your Gmail. The only email it ever sends is that summary, and it goes to you.

---

## 2. The automatic Monday run

You don't have to do anything for this.

- **When:** every Monday at 13:00 UTC. That's about 8 AM (winter) or 9 AM (summer) US Eastern time.
- **What it scans:** the last **14 days** of Gmail. Two weeks rather than one means nothing slips through if a run is late or misses a week.
- **What you get:** the summary email in your Gmail inbox a few minutes after it runs.

If you get the email on Monday morning, everything is working.

---

## 3. Running it yourself (any time)

Use this if you want fresh numbers before Monday, or if a Monday run failed.

1. Go to **https://github.com/scaruana33-code/search-log** and sign in.
2. Click the **Actions** tab near the top of the page.
3. In the left-hand list, click **Weekly job-search refresh**.
4. On the right, click the grey **Run workflow** button. A small box drops down.
5. Leave **Branch: main** as it is.
6. In the box labelled **"Days of Gmail to scan (use e.g. 90 to backfill)"**, type a number of days:
   - **14** (the default): a normal catch-up. Use this almost every time.
   - **90**: a full backfill. Use it only if you think a lot was missed, for example after the workflow was broken for several weeks.
7. Click the green **Run workflow** button.
8. Wait a few seconds and refresh the page. A new run appears at the top of the list with a yellow dot (running).
   - A 14-day run takes about 1 to 3 minutes.
   - A 90-day run can take 10 minutes or more.
9. When it finishes, the dot turns into a **green check ✅** (worked) or a **red X ❌** (failed). If you see a red X, go to [Troubleshooting](#6-troubleshooting).

> **Tip:** It's safe to run it as often as you like. Running it twice won't create duplicate jobs.
>
> **Limit:** a single run reads at most about 500 emails. If a 90-day backfill seems to stop short, run it again with a smaller number, such as 45.

---

## 4. Where your results go

### The summary email
Look in Gmail for **"Your weekly job-search summary"**. It shows:
- how many applications you sent in the last 7 days
- how many interview events and offers you had
- for each source (ATS / LinkedIn / networking / recruiter), how often applications turned into interviews and offers
- the average number of interview rounds per application

### The data file
The full list lives in **`data/applications.json`** in the repository. To look at it:
1. On the repository's main page, click the **data** folder.
2. Click **applications.json**.

After each successful run you'll see a new entry called **"Weekly refresh"** in the repository's history. That is the robot saving the updated list. It only appears if something actually changed.

### The dashboard (optional, on your PC)
`index.html` is a dashboard that shows the same list as a table you can sort and edit. Because the repository is private, it has to be opened from your own computer:

1. On the repository's main page, click the green **Code** button, then **Download ZIP**.
2. Open your **Downloads** folder, right-click the ZIP and choose **Extract All…**, then click **Extract**.
3. Open the extracted folder (named `search-log-main`) so you can see `index.html` inside it.
4. Click in the **address bar** at the top of the File Explorer window, type `cmd` and press **Enter**. A black Command Prompt window opens, already in that folder.
5. Type this and press **Enter**:
   ```
   python -m http.server
   ```
6. Open your web browser and go to **http://localhost:8000**.
7. When you're done, close the Command Prompt window.

To see the newest data after a later run, download the ZIP again (steps 1 to 3) and repeat.

---

## 5. Keeping your own list (manual.csv)

Some things can't be read from email, such as LinkedIn's Archived tab, networking contacts, and recruiters who only use InMail. Your hand-kept list lives in **`data/manual.csv`**, and the robot always treats it as the truth. It never deletes or changes rows in that file.

To update it:

1. In the dashboard, make your changes (set each job's **Outcome**, add notes, add jobs with **+ Log application**).
2. Click **Export CSV**. A file is saved to your Downloads folder.
3. **Rename the file to `manual.csv` exactly.** See the Windows warning below first.
4. On GitHub, open the **data** folder, click **Add file** and then **Upload files**.
5. Drag `manual.csv` into the page, then click the green **Commit changes** button at the bottom. This replaces the old file.

### ⚠️ Windows file-name warning

Windows hides the end of file names (the ".csv" or ".json" part) by default. That can make a file *look* like `manual.csv` when it's really `manual.csv.csv` or `manual.csv.txt`, and then the robot won't find it.

Turn the real names on once and leave them on:
- **Windows 11:** in File Explorer click **View**, then **Show**, then tick **File name extensions**.
- **Windows 10:** in File Explorer click the **View** tab and tick **File name extensions**.

Now when you rename, make sure the name reads exactly `manual.csv`, with nothing extra on the end.

---

## 6. Troubleshooting

### First, find out what went wrong
1. Go to the **Actions** tab and click the run with the red X.
2. Click the box called **refresh**.
3. Click the step with the red X (usually **"Sync Gmail and email the summary"**) to open it.
4. Scroll to the bottom of the text and look for the words below.

### "invalid_grant" or "Token has been expired or revoked"
This is the most common problem. Google's permission for Search Log to read your Gmail (the **refresh token**) has stopped working. It happens if you changed your Google password, removed the app's access in your Google account, or haven't used it for about 6 months.

**Fix: get a new token and save it in GitHub.**

*Part A: get a new token on your PC*
1. You need the `client_secret.json` file you downloaded from Google Cloud during setup. If you can't find it, go to **console.cloud.google.com**, open **APIs & Services**, then **Credentials**, click your **Desktop app** client and download the JSON again. Save it in your **Downloads** folder as `client_secret.json`. Check it isn't really `client_secret.json.json` (see the [Windows warning](#️-windows-file-name-warning)).
2. Download the repository ZIP and extract it to your Downloads folder (see [the dashboard steps](#the-dashboard-optional-on-your-pc), steps 1 and 2).
3. Open the Start menu, type `cmd` and press **Enter**.
4. Type each line and press **Enter** after each one:
   ```
   cd Downloads\search-log-main
   pip install -r scripts\requirements.txt
   python scripts\get_refresh_token.py ..\client_secret.json
   ```
5. A browser window opens. Sign in with your Gmail account. If Google says the app is "unverified", click **Advanced** and then **Go to … (unsafe)**. It's your own app, so this is fine. Approve both permissions.
6. Back in the black window, three lines appear: `GOOGLE_CLIENT_ID=…`, `GOOGLE_CLIENT_SECRET=…` and `GOOGLE_REFRESH_TOKEN=…`. Usually only the last one has changed.

*Part B: save it in GitHub*
1. On the repository page, click **Settings** (top right of the tabs).
2. In the left menu, click **Secrets and variables**, then **Actions**.
3. Next to **GOOGLE_REFRESH_TOKEN**, click the **pencil ✏️** icon.
4. Paste in everything **after** the `=` sign. Don't include the `GOOGLE_REFRESH_TOKEN=` part or any spaces.
5. Click **Update secret**.
6. If the client ID or secret also changed, update **GOOGLE_CLIENT_ID** and **GOOGLE_CLIENT_SECRET** the same way.
7. Run the workflow by hand (section 3) with **14** days to check it works.

> 🔒 **Never paste these values into any file in the repository**, including the workflow file, a README or a note. Only put them in **Settings → Secrets and variables → Actions**. Anything saved in a file can be seen in the repository's history forever.

### "KeyError: 'GOOGLE_REFRESH_TOKEN'" (or CLIENT_ID / CLIENT_SECRET)
One of the three secrets is missing or misspelled. In **Settings → Secrets and variables → Actions**, make sure all three exist with exactly these names (capital letters, underscores):
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_REFRESH_TOKEN`

### "invalid_client" or "unauthorized_client"
The client ID or client secret in GitHub doesn't match Google Cloud. This happens if the secret was reset in Google Cloud. Download the JSON again (Part A, step 1), run Part A again, and update all three secrets.

### "rateLimitExceeded" or "Quota exceeded"
Gmail asked it to slow down, usually during a big 90-day backfill. Wait an hour and run it again, or use a smaller number of days.

### The run is green but I got no email
- Check Gmail's **Sent**, **Spam** and **All Mail** folders for "Your weekly job-search summary". It's sent from you to you, so Gmail sometimes files it oddly.
- Check the log: the last line of the "Sync Gmail" step should say `Summary email sent to …`.

### The Monday run didn't happen at all
- GitHub pauses scheduled workflows on repositories with no activity for 60 days. If the **Actions** tab shows a yellow banner saying the workflow is disabled, click **Enable workflow**.
- GitHub can run scheduled jobs up to an hour late on busy days. Check again later, or just run it by hand.

### A job shows the wrong company, stage or role
The robot guesses from email wording, so it isn't perfect. A few known quirks:
- Jobs from recruiter emails are sometimes named after the **recruiter** instead of the company.
- Odd subject lines can come out as **"Unknown role"**.

Fix these in the dashboard, then Export CSV and upload it as `manual.csv` (section 5). Your corrections will stick from then on.

---

## Quick reference

| I want to… | Do this |
|---|---|
| Update now | Actions → Weekly job-search refresh → Run workflow → `14` → Run workflow |
| Catch up after a long break | Same, but type `90` |
| See this week's numbers | Gmail: "Your weekly job-search summary" |
| See the full list | Repository → `data` → `applications.json`, or the dashboard |
| Save my own edits | Dashboard → Export CSV → rename to `manual.csv` → upload to `data` folder |
| Fix "invalid_grant" | Get a new token (section 6) → Settings → Secrets → update `GOOGLE_REFRESH_TOKEN` |

"""Tests for the email stage rules. Run: python -m unittest discover scripts"""
import tempfile
import unittest
from pathlib import Path

from sync_gmail import classify, load_manual, merge_manual, skip_sender, upsert

ME = "me@example.com"


class ClassifyTest(unittest.TestCase):
    def check(self, text, stage):
        self.assertEqual(classify(text), stage, text)

    def test_offer(self):
        self.check("We are pleased to offer you the position", "offer")

    def test_rejection(self):
        self.check("Unfortunately, we have decided to move forward with other candidates", "rejected")

    def test_final_round(self):
        self.check("Invitation: final round interview with the leadership team", "final")
        self.check("Onsite Interview - Global Program Manager", "final")
        self.check("We'd like to schedule a panel interview", "final")

    def test_on_site_job_description_is_not_final(self):
        # Workplace type in a job post or confirmation, not an interview stage.
        self.check("Thank you for applying. Location: New York (On-site)", "applied")
        self.check("This role is onsite 5 days a week. Your application was sent to Acme", "applied")
        self.assertIsNone(classify("New jobs for you: Program Manager, on-site, up to $300K/year"))

    def test_numbered_rounds(self):
        self.check("Second round interview availability", "round2")
        self.check("Round 3 with the VP", "round3")
        self.check("Phone screen with the hiring manager", "round1")

    def test_screen(self):
        self.check("Interview confirmation for Tuesday", "screen")
        self.check("Can we schedule a call this week?", "screen")

    def test_applied(self):
        self.check("Thank you for your application to Acme", "applied")

    def test_unrelated(self):
        self.assertIsNone(classify("Your weekly newsletter: World Series edition"))


class SkipSenderTest(unittest.TestCase):
    def test_own_mail(self):
        self.assertTrue(skip_sender("Me@Example.com", ME))

    def test_calendar_invites(self):
        self.assertTrue(skip_sender("calendar-notification@google.com", ME))

    def test_linkedin(self):
        self.assertFalse(skip_sender("jobs-noreply@linkedin.com", ME))
        self.assertTrue(skip_sender("inmail-hit-reply@linkedin.com", ME))
        self.assertTrue(skip_sender("newsletters-noreply@linkedin.com", ME))

    def test_employers(self):
        self.assertFalse(skip_sender("no-reply@us.greenhouse-mail.io", ME))
        self.assertFalse(skip_sender("breanah.alviz@pimco.com", ME))


MANUAL_CSV = """company,role,source,dateApplied,stage,stageDate,outcome,notes,peak
Con Edison,IT Vendor Manager,ats,10/13/2026,1st round,10/20/2026,ghosted,still interviewing per recruiter,
NY Times,Systems Analyst,ats,9/23/2026,rejected,10/14/2026,,,round2
Acme,PM,linkedin,9/01/2026,applied,,never heard back,,
Globex,Lead,ats,10/01/2026,not moving forward,10/05/2026,,,screen
"""


class ManualListTest(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        path = Path(d.name) / "manual.csv"
        path.write_text(MANUAL_CSV)
        self.rows = {r["company"]: r for r in load_manual(path)}

    def test_archived_but_still_interviewing_stays_active(self):
        r = self.rows["Con Edison"]
        self.assertEqual((r["stage"], r["outcome"], r["dateApplied"]), ("round1", None, "2026-10-13"))

    def test_outcomes_keep_the_furthest_stage(self):
        self.assertEqual((self.rows["NY Times"]["stage"], self.rows["NY Times"]["outcome"]), ("round2", "rejected"))
        self.assertEqual((self.rows["Acme"]["stage"], self.rows["Acme"]["outcome"]), ("applied", "ghosted"))
        self.assertEqual((self.rows["Globex"]["stage"], self.rows["Globex"]["outcome"]), ("screen", "disqualified"))

    def test_merge_keeps_your_rows_and_newer_email_rows(self):
        email = [
            {"company": "Con Edison Inc", "role": "Unknown role", "dateApplied": "2026-10-14", "stage": "applied"},
            {"company": "Myworkday", "role": "Next Steps", "dateApplied": "2026-09-05", "stage": "applied"},
            {"company": "Newco", "role": "PM", "dateApplied": "2026-10-30", "stage": "applied"},
        ]
        merged = merge_manual(email, list(self.rows.values()))
        self.assertEqual(sorted(a["company"] for a in merged), ["Acme", "Con Edison", "Globex", "NY Times", "Newco"])

    def test_email_never_changes_your_row(self):
        apps = list(self.rows.values())
        upsert(apps, "Con Edison", "", "ats", "2026-10-30", "rejected")
        upsert(apps, "ConEdison", "IT Vendor Manager", "ats", "2026-10-30", "offer")
        self.assertEqual(self.rows["Con Edison"]["stage"], "round1")
        self.assertIsNone(self.rows["Con Edison"]["outcome"])


if __name__ == "__main__":
    unittest.main()

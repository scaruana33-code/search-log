"""Tests for the email stage rules. Run: python -m unittest discover scripts"""
import unittest

from sync_gmail import classify, skip_sender

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


if __name__ == "__main__":
    unittest.main()

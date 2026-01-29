from odoo.tests.common import TransactionCase, tagged
from odoo.tools.mail import is_html_empty


@tagged("post_install", "-at_install")
class TestCleanEmailLayout(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({
            "name": "Test Partner",
            "email": "test@example.com",
        })

    def _render_layout(self, company):
        message = self.env["mail.message"].create({
            "model": "res.partner",
            "res_id": self.partner.id,
            "body": "<p>Hello</p>",
            "message_type": "notification",
            "subtype_id": self.env.ref("mail.mt_comment").id,
        })
        values = {
            "lang": "en_US",
            "company": company,
            "message": message,
            "record": self.partner,
            "record_name": "Test Record",
            "subtitles": ["Test Record"],
            "tracking_values": [],
            "model_description": "Contact",
            "author_user": self.env.user,
            "email_add_signature": False,
            "signature": "",
            "website_url": "http://example.com",
            "is_discussion": False,
            "is_html_empty": is_html_empty,
            "email_notification_force_header": False,
            "email_notification_allow_header": True,
            "email_notification_force_footer": True,
            "email_notification_allow_footer": True,
            "has_button_access": True,
            "button_access": {"url": "http://example.com", "title": "View"},
        }
        return self.env["ir.qweb"]._render("mail.mail_notification_layout", values)

    def _render_light_layout(self, company):
        message = self.env["mail.message"].create({
            "model": "res.partner",
            "res_id": self.partner.id,
            "body": "<p>Hello</p>",
            "message_type": "notification",
            "subtype_id": self.env.ref("mail.mt_comment").id,
        })
        values = {
            "lang": "en_US",
            "company": company,
            "message": message,
            "model_description": "Contact",
            "tracking_values": [],
            "has_button_access": True,
            "button_access": {"url": "http://example.com", "title": "View"},
        }
        return self.env["ir.qweb"]._render("mail.mail_notification_light", values)

    def test_layout_visible_by_default(self):
        company = self.env.company
        company.write({
            "hide_email_layout_parts": False,
            "phone": "081 1926",
            "email": "info@example.com",
            "website": "https://example.com",
        })
        html = self._render_layout(company)

        self.assertIn("Test Record", html)
        self.assertIn("My Company", html)
        self.assertIn("info@example.com", html)
        self.assertIn("Powered by", html)
        self.assertIn("<p>Hello</p>", html)

    def test_layout_hidden_when_flag_true(self):
        company = self.env.company
        company.write({
            "hide_email_layout_parts": True,
            "phone": "081 1926",
            "email": "info@example.com",
            "website": "https://example.com",
        })
        html = self._render_layout(company)

        self.assertNotIn("Test Record", html)
        self.assertIn("My Company", html)
        self.assertNotIn("info@example.com", html)
        self.assertNotIn("Powered by", html)
        self.assertNotIn("Unfollow", html)
        self.assertIn("<p>Hello</p>", html)

    def test_light_layout_visible_by_default(self):
        company = self.env.company
        company.write({
            "hide_email_layout_parts": False,
            "phone": "081 1926",
            "email": "info@example.com",
            "website": "https://example.com",
        })
        html = self._render_light_layout(company)

        self.assertIn("Test Partner", html)
        self.assertIn("My Company", html)
        self.assertIn("info@example.com", html)
        self.assertIn("Powered by", html)
        self.assertIn("<p>Hello</p>", html)

    def test_light_layout_hidden_when_flag_true(self):
        company = self.env.company
        company.write({
            "hide_email_layout_parts": True,
            "phone": "081 1926",
            "email": "info@example.com",
            "website": "https://example.com",
        })
        html = self._render_light_layout(company)

        self.assertNotIn("Test Partner", html)
        self.assertIn("My Company", html)
        self.assertNotIn("info@example.com", html)
        self.assertNotIn("Powered by", html)
        self.assertNotIn("Unfollow", html)
        self.assertIn("<p>Hello</p>", html)

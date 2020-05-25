# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
from urllib.parse import urljoin
from urllib.parse import urlencode


_logger = logging.getLogger(__name__)


class WebsiteFormApi(models.Model):
    _name = "website.form.api"
    _description = "Credit Applications"

    # company info
    name = fields.Text(string="Name*", required=True)
    # Address
    address = fields.Text(string="Address*", required=True)
    city = fields.Text(string="City*", required=True)
    state = fields.Text(string="State*", required=True)
    zip = fields.Text(string="Zip*", required=True)
    fein = fields.Text(string="FEIN*", required=True)
    # key company contacts
    # main purchase contact
    mp_name = fields.Text(string="Name")
    mp_email = fields.Text(string="Email")
    mp_phone = fields.Text("Phone")
    # accounts payable details
    ap_name = fields.Text("Name")
    ap_email = fields.Text("Email")
    ap_phone = fields.Text("Phone")
    # owner/ceo details
    owner_name = fields.Text("Name")
    owner_email = fields.Text("Email")
    owner_phone = fields.Text("Phone")
    # cfo details
    cfo_name = fields.Text("Name")
    cfo_email = fields.Text("Email")
    cfo_phone = fields.Text("Phone")

    # credit info
    credit_amt_req = fields.Text("Credit Amount")
    dnb_no = fields.Text("D and B Number")

    # Bank Reference and Payment Information
    bank_contact = fields.Text("Bank Contact*", required=True)
    bank_name = fields.Text("Bank Name*", required=True)
    bank_email = fields.Text("Bank Email*", required=True)
    bank_phone = fields.Text("Bank Phone*", required=True)

    # ACH / Wire Instruction *

    routing = fields.Char("Routing*", required=True)
    acc_no = fields.Text("Account No*", required=True)

    # Trade References
    trade_ref_ids = fields.One2many("trade.ref.lines", "form_id", "Trade Ref")
    mail_sent = fields.Boolean("Mail Sent")

    # send mail to users once credit application created
    def send_mail_credit_info(self):
        for record in self:
            recepient_users = self.env["res.users"].search(
                [("send_credit_info", "=", True)]
            )
            if recepient_users:
                email_to = "".join(
                    [user.partner_id.email + "," for user in recepient_users]
                )
                email_to = email_to[:-1]
                body = "<b> Yohooo!</b>"
                body += "</br>"
                body += "<p> We have a new contact applying for credit through our webform.If you have any questions related to this mail, you can contact Ha</p>"
                body += "</br>"
                body += "<p>Below is the link to the application in Odoo</p>"
                # to send mail on credit info creation
                base_url = self.env["ir.config_parameter"].get_param("web.base.url")
                query = {"db": self._cr.dbname}
                fragment = {
                    "model": "website.form.api",
                    "view_type": "form",
                    "id": record.id,
                }
                url = urljoin(
                    base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment))
                )
                text_link = _("""<a href="%s">%s</a> """) % (
                    url,
                    "VIEW CREDIT APPLICATION",
                )
                body += "<li> " + str(text_link) + "</li>"

                temp_id = self.env.ref("base_vph.email_template_for_credit_info")
                if temp_id:
                    base_url = self.env["ir.config_parameter"].get_param("web.base.url")
                    query = {"db": self._cr.dbname}
                    # email_from temporarily hardcoded once outgoing mail server
                    # configured will remove it
                    temp_id.write(
                        {
                            "body_html": body,
                            "email_to": email_to,
                            "email_from": "bhargavi1809@gmail.com",
                        }
                    )
                    values = temp_id.generate_email(record.id)
                    mail_mail_obj = self.env["mail.mail"]
                    msg_id = mail_mail_obj.create(values)
                    msg_id.send()
            record.mail_sent = True
            # record.message_post(body=body)
        return True

    # to create a record in credit info form through api call
    def create_rec(self, json_dict):
        for credit_info in json_dict.get("credit_info"):
            credit_amt_req = credit_info.get("credit_amt_req")
            dnb_no = credit_info.get("dnb_no")
        for bank_info in json_dict.get("bank_details"):
            bank_contact = bank_info.get("bank_contact")
            bank_name = bank_info.get("bank_name")
            bank_email = bank_info.get("bank_email")
            bank_phn = bank_info.get("bank_phone")
        for ach_info in json_dict.get("ach_info"):
            routing = ach_info.get("routing")
            acc_no = ach_info.get("acc_no")
        trade_list = []
        for trade_ref in json_dict.get("trade_ref_ids"):
            trade_dict = (
                0,
                0,
                {
                    "name": trade_ref.get("name"),
                    "cmpny": trade_ref.get("cmpny"),
                    "phone": trade_ref.get("phone"),
                    "email": trade_ref.get("email"),
                },
            )
            trade_list.append(trade_dict)

        web_from_id = self.create(
            {
                "name": json_dict.get("name"),
                "address": json_dict.get("address"),
                "city": json_dict.get("city"),
                "state": json_dict.get("state"),
                "zip": json_dict.get("zip"),
                "fein": json_dict.get("fein"),
                "mp_name": json_dict.get("mp_name"),
                "mp_email": json_dict.get("mp_email"),
                "mp_phone": json_dict.get("mp_phone"),
                "ap_name": json_dict.get("ap_name"),
                "ap_email": json_dict.get("ap_email"),
                "ap_phone": json_dict.get("ap_phone"),
                "owner_name": json_dict.get("owner_name"),
                "owner_email": json_dict.get("owner_email"),
                "owner_phone": json_dict.get("owner_phone"),
                "cfo_name": json_dict.get("cfo_name"),
                "cfo_email": json_dict.get("cfo_email"),
                "cfo_phone": json_dict.get("cfo_phone"),
                "credit_amt_req": credit_amt_req,
                "dnb_no": dnb_no,
                "bank_contact": bank_contact,
                "bank_name": bank_name,
                "bank_email": bank_email,
                "bank_phone": bank_phn,
                "routing": routing,
                "acc_no": acc_no,
                "trade_ref_ids": trade_list,
            }
        )
        return web_from_id

    # send mail when a credit apllication is created
    @api.model
    def create(self, vals):
        web_form_id = super(WebsiteFormApi, self).create(vals)
        web_form_id.send_mail_credit_info()
        return web_form_id


class TradeRefLines(models.Model):
    _name = "trade.ref.lines"
    _description = "Trade Ref Lines"
    form_id = fields.Many2one(
        "website.form.api",
        string="Form Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )

    name = fields.Text(string="Name", required=True)
    cmpny = fields.Text(string="Company")
    phone = fields.Text(string="Phone")
    email = fields.Text(string="Email", required=True)

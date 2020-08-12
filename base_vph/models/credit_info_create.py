# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging
from urllib.parse import urljoin
from urllib.parse import urlencode
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
from odoo.http import JsonRequest, Response
import json
from odoo.tools import ustr, consteq, frozendict, pycompat, unique
from odoo.tools import ustr, consteq, frozendict, pycompat, unique, date_utils

# inherit _json_response to return id in response
def _json_response(self, result=None, error=None):
    response = {"jsonrpc": "2.0", "id": self.jsonrequest.get("id")}

    if error is not None:
        response["error"] = error
    if result is not None:
        response["result"] = result
        if (
            result != False
            and isinstance(result, dict)
            and result.get("id")
            and isinstance(result.get("id"), int)
        ):
            response["id"] = result.get("id")

    mime = "application/json"
    body = json.dumps(response, default=date_utils.json_default)

    return Response(
        body,
        status=error and error.pop("http_status", 200) or 200,
        headers=[("Content-Type", mime), ("Content-Length", len(body))],
    )


JsonRequest._json_response = _json_response


class WebsiteFormApi(models.Model):
    _name = "website.form.api"
    _description = "Credit Applications"

    # company info
    name = fields.Char(string="Name*", required=True)
    # Address
    address = fields.Text(string="Address*", required=True)
    city = fields.Char(string="City*", required=True)
    state = fields.Char(string="State*", required=True)
    zip = fields.Char(string="Zip*", required=True)
    fein = fields.Char(string="FEIN*", required=True)
    # key company contacts
    # main purchase contact
    mp_name = fields.Char(string="Name")
    mp_email = fields.Char(string="Email")
    mp_phone = fields.Char("Phone")
    # accounts payable details
    ap_name = fields.Char("Name")
    ap_email = fields.Char("Email")
    ap_phone = fields.Char("Phone")
    # owner/ceo details
    owner_name = fields.Char("Name")
    owner_email = fields.Char("Email")
    owner_phone = fields.Char("Phone")
    # cfo details
    cfo_name = fields.Char("Name")
    cfo_email = fields.Char("Email")
    cfo_phone = fields.Char("Phone")

    # credit info
    credit_amt_req = fields.Text("Credit Amount")
    dnb_no = fields.Char("D and B Number")

    # Bank Reference and Payment Information
    bank_contact = fields.Char("Bank Contact*", required=True)
    bank_name = fields.Char("Bank Name*", required=True)
    bank_email = fields.Char("Bank Email*", required=True)
    bank_phone = fields.Char("Bank Phone*", required=True)

    # Trade References
    trade_ref_ids = fields.One2many("trade.ref.lines", "form_id", "Trade Ref")
    mail_sent = fields.Boolean("Mail Sent")

    # cannot delete credit application
    def unlink(self):
        raise UserError(
            _(
                "You cannot delete a Credit Application.Please contact your Administrator!!"
            )
        )
        return super(SaleOrder, self).unlink()

    # return url to odoo domain
    @api.model
    def get_website_url(self):
        # to send mail on credit info creation
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        query = {"db": self._cr.dbname}
        fragment = {"model": "website.form.api", "view_type": "form", "id": self.id}
        url = urljoin(base_url, "/web?%s#%s" % (urlencode(query), urlencode(fragment)))
        return url

    def send_mail_credit_info(self):
        """
        Send email to users once credit application created
        """
        for record in self:
            recepient_users = self.env["res.users"].search(
                [("send_credit_info", "=", True)]
            )
            if recepient_users:
                email_to = "".join(
                    [user.partner_id.email + "," for user in recepient_users]
                )
                email_to = email_to[:-1]

                # to send mail on credit info creation
                mail_template = self.env.ref("base_vph.email_template_for_credit_info")
                if mail_template:
                    mail_template.write(
                        {"email_to": email_to,}
                    )
                    values = mail_template.generate_email(record.id)
                    mail_obj = self.env["mail.mail"]
                    msg_id = mail_obj.create(values)
                    msg_id.send()
            record.mail_sent = True
            # record.message_post(body=body)

    # credit applications are not allowed to be copied
    def copy(self, default=None):
        default = default or {}
        res = super(WebsiteFormApi, self).copy(default)
        raise UserError(_("You are not allowed to copy the Credit Application!!"))
        return res

    def send_mail_to_main_purchase(self):
        """
        Send email to main purchase contact
        """
        for record in self:
            if record.mp_email:
                email_to = record.mp_email
                mail_template = self.env.ref(
                    "base_vph.email_template_main_purchase_contact"
                )
                if mail_template:
                    mail_template.write(
                        {"email_to": email_to,}
                    )
                    values = mail_template.generate_email(record.id)
                    mail_obj = self.env["mail.mail"]
                    msg_id = mail_obj.create(values)
                    msg_id.send()

    def create_record(self, data):
        """
        Creates a record in credit applications
        """

        credit_amt_req = None
        dnb_no = None
        for credit_info in data.get("credit_info"):
            credit_amt_req = credit_info.get("credit_amt_req")
            dnb_no = credit_info.get("dnb_no")

        bank_contact = None
        bank_name = None
        bank_email = None
        bank_phn = None
        for bank_info in data.get("bank_details"):
            bank_contact = bank_info.get("bank_contact")
            bank_name = bank_info.get("bank_name")
            bank_email = bank_info.get("bank_email")
            bank_phn = bank_info.get("bank_phone")

        trade_list = []
        for trade_ref in data.get("trade_ref_ids"):
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
                "name": data.get("name"),
                "address": data.get("address"),
                "city": data.get("city"),
                "state": data.get("state"),
                "zip": data.get("zip"),
                "fein": data.get("fein"),
                "mp_name": data.get("mp_name"),
                "mp_email": data.get("mp_email"),
                "mp_phone": data.get("mp_phone"),
                "ap_name": data.get("ap_name"),
                "ap_email": data.get("ap_email"),
                "ap_phone": data.get("ap_phone"),
                "owner_name": data.get("owner_name"),
                "owner_email": data.get("owner_email"),
                "owner_phone": data.get("owner_phone"),
                "cfo_name": data.get("cfo_name"),
                "cfo_email": data.get("cfo_email"),
                "cfo_phone": data.get("cfo_phone"),
                "credit_amt_req": credit_amt_req,
                "dnb_no": dnb_no,
                "bank_contact": bank_contact,
                "bank_name": bank_name,
                "bank_email": bank_email,
                "bank_phone": bank_phn,
                "trade_ref_ids": trade_list,
            }
        )
        return web_from_id

    # send mail when a credit apllication is created
    @api.model
    def create(self, vals):
        web_form_id = super(WebsiteFormApi, self).create(vals)
        web_form_id.send_mail_credit_info()
        web_form_id.send_mail_to_main_purchase()
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

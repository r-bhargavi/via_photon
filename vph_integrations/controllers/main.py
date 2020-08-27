# -*- coding: utf-8 -*-

from odoo import http, api, _
from odoo.http import request
import json
import base64
import werkzeug.wrappers

import ast
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController


# endpoint to get test results  from Blink
class OdooBlinkTestResults(http.Controller):
    @http.route(
        ["/api/data-pixel/testresults"],
        csrf=False,
        methods=["OPTIONS", "POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def get_test_results_blink(self, **kw):
        request_data = request.httprequest.data
        if request_data:
            dict_str = request_data.decode("UTF-8")
            mydata = ast.literal_eval(dict_str)
            json_data = repr(mydata).replace("'", '"')
            final_dictionary = json.loads(json_data)
            if not final_dictionary.get("workstation_id"):
                return "No WorkStation ID provided"
            if not final_dictionary.get("serial_number"):
                return "No Serial Number provided"
            if not final_dictionary.get("quality_check_id"):
                return "No Quality Check provided"
            if not final_dictionary.get("pass_fail"):
                return "No Test Results found"
            qc_id = (
                request.env["quality.check"]
                .sudo()
                .search(
                    [("id", "=", final_dictionary.get("quality_check_id"))], limit=1
                )
            )
            if qc_id:
                qc_id.sudo().write({"test_result_json": final_dictionary})
                state = "none"
                if final_dictionary.get("pass_fail") == "Pass":
                    state = "pass"
                if final_dictionary.get("pass_fail") == "Fail":
                    state = "fail"
                qc_id.sudo().write({"quality_state": state})
                message = {
                    "Success": "Test Results Saved Successfully",
                    "id": final_dictionary.get("quality_check_id"),
                }
                return message


# endpoint to integrate for Workorders bw Odoo and Blink
class OdooBlinkIntegrate(http.Controller):
    @http.route(
        ["/api/data-pixel/workorder"],
        csrf=False,
        methods=["OPTIONS", "POST"],
        type="json",
        auth="public",
        cors="*",
    )
    def send_workorder(self, **kw):
        request_data = request.httprequest.data
        if request_data:
            dict_str = request_data.decode("UTF-8")
            mydata = ast.literal_eval(dict_str)
            json_data = repr(mydata).replace("'", '"')

            final_dictionary = json.loads(json_data)
            if not final_dictionary.get("workstation_id"):
                return "No WorkStation ID provided"
            if not final_dictionary.get("workstation_model"):
                return "No WorkStation Model provided"
            # try:
            wo_resp = (
                request.env["mrp.workorder"].sudo().get_wo_details(final_dictionary)
            )

            if isinstance(wo_resp, dict):
                message = wo_resp
                return message
            else:
                return wo_resp

            # except Exception as e:
            #   return "Fetch details Failed from Odoo"

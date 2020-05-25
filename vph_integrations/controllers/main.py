# -*- coding: utf-8 -*-

from odoo import http, api, _
from odoo.http import request
import json
import base64
import werkzeug.wrappers

import ast
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController


class OdooBlinkIntegrate(http.Controller):
    @http.route(
        ["/api/data-pixel/workorder"], csrf=False, methods=["OPTIONS", "GET"], type="json", auth="public", cors='*'
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
            workstation_id=final_dictionary.get("workstation_id")
            #wo_id=request.env['mrp.workorder'].search([('workstation_id','=',workstation_id)],limit=1)
            #wo_id=True
            # sample json discussed with julien
            data ={
                "workorder_ref": "WO-1234",
                "part_number": "1238764865789",
                "serial_number": "1238764865789",
                "operator_number": "358",
                "hex_color_code": "#FF00FF",
                "nb_fibers": 12,
                "fiber_type": "PC",
                "connectorA_type": "LC",
                "connectorB_type": "MPO12",
                "connector_side ": "A",
                "connector_number": "2"
                }
            return data



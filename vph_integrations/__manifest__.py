# -*- coding: utf-8 -*-

###################################################################################
#
#    Copyright (C) 2020 Viaphoton, Inc.
#
###################################################################################

{
    "name": "Base Integrations for viaPhoton",
    "category": "Hidden",
    "author": "Technosavvy Infotech",
    "summary": "Custom",
    "version": "1.1",
    "description": """
THIS MODULE IS PROVIDED AS IS - INSTALLATION AT USERS' OWN RISK -
AUTHOR OF MODULE DOES NOT CLAIM ANY
RESPONSIBILITY FOR ANY BEHAVIOR ONCE INSTALLED.
        """,
    "depends": [
        "base_vph",
        "mrp",
        "quality_control",
        "mrp_account",
        "quality",
        "mrp_workorder",
        "mrp_plm",
    ],
    "data": ["security/ir.model.access.csv", "views/ir_ui_views.xml",],
    "installable": True,
}

"""CA1 Template definitions and schema."""

from typing import List, Dict, Any
from app.models.schemas import TemplateField


class CA1Template:
    """COREP CA1 - Own Funds template definition."""
    
    # CA1 template structure based on standard COREP
    # Simplified version focusing on key Own Funds components
    
    TEMPLATE_STRUCTURE = {
        "template_id": "CA1",
        "template_name": "Own Funds",
        "description": "Own funds composition",
        "columns": [
            {"code": "C0010", "label": "Amount"},
            {"code": "C0020", "label": "Of which: classified as equity under applicable accounting standards"}
        ],
        "rows": [
            # Common Equity Tier 1 (CET1) Capital: Instruments and reserves
            {"code": "R0010", "label": "Capital instruments and the related share premium accounts", "section": "CET1"},
            {"code": "R0030", "label": "Retained earnings", "section": "CET1"},
            {"code": "R0040", "label": "Accumulated other comprehensive income", "section": "CET1"},
            {"code": "R0050", "label": "Other reserves", "section": "CET1"},
            {"code": "R0060", "label": "Minority interests (amount allowed in consolidated CET1)", "section": "CET1"},
            
            # CET1 Capital before regulatory adjustments
            {"code": "R0070", "label": "Common Equity Tier 1 (CET1) capital before regulatory adjustments", "section": "CET1_SUBTOTAL", "is_calculated": True},
            
            # CET1 Capital: regulatory adjustments
            {"code": "R0080", "label": "Additional value adjustments", "section": "CET1_DEDUCTIONS"},
            {"code": "R0090", "label": "Intangible assets (net of related tax liability)", "section": "CET1_DEDUCTIONS"},
            {"code": "R0100", "label": "Deferred tax assets that rely on future profitability", "section": "CET1_DEDUCTIONS"},
            {"code": "R0130", "label": "Direct and indirect holdings of own CET1 instruments", "section": "CET1_DEDUCTIONS"},
            
            # Total regulatory adjustments
            {"code": "R0180", "label": "Total regulatory adjustments to CET1", "section": "CET1_DEDUCTIONS_TOTAL", "is_calculated": True},
            
            # CET1 Capital
            {"code": "R0200", "label": "Common Equity Tier 1 (CET1) capital", "section": "CET1_TOTAL", "is_calculated": True},
            
            # Additional Tier 1 (AT1) Capital
            {"code": "R0210", "label": "Capital instruments and the related share premium accounts", "section": "AT1"},
            {"code": "R0220", "label": "Amount of qualifying items referred to in Article 484 (4) CRR", "section": "AT1"},
            {"code": "R0230", "label": "Minority interests (amount allowed in consolidated AT1)", "section": "AT1"},
            
            # AT1 Capital before regulatory adjustments
            {"code": "R0240", "label": "Additional Tier 1 (AT1) capital before regulatory adjustments", "section": "AT1_SUBTOTAL", "is_calculated": True},
            
            # AT1 regulatory adjustments
            {"code": "R0250", "label": "Direct and indirect holdings of own AT1 instruments", "section": "AT1_DEDUCTIONS"},
            {"code": "R0270", "label": "Total regulatory adjustments to AT1 capital", "section": "AT1_DEDUCTIONS_TOTAL", "is_calculated": True},
            
            # AT1 Capital
            {"code": "R0280", "label": "Additional Tier 1 (AT1) capital", "section": "AT1_TOTAL", "is_calculated": True},
            
            # Tier 1 Capital
            {"code": "R0290", "label": "Tier 1 capital (T1 = CET1 + AT1)", "section": "T1_TOTAL", "is_calculated": True},
            
            # Tier 2 (T2) Capital
            {"code": "R0300", "label": "Capital instruments and the related share premium accounts", "section": "T2"},
            {"code": "R0310", "label": "Amount of qualifying items referred to in Article 484 (5) CRR", "section": "T2"},
            {"code": "R0320", "label": "Credit risk adjustments", "section": "T2"},
            {"code": "R0330", "label": "Minority interests (amount allowed in consolidated T2)", "section": "T2"},
            
            # T2 Capital before regulatory adjustments
            {"code": "R0340", "label": "Tier 2 (T2) capital before regulatory adjustments", "section": "T2_SUBTOTAL", "is_calculated": True},
            
            # T2 regulatory adjustments
            {"code": "R0350", "label": "Direct and indirect holdings of own T2 instruments", "section": "T2_DEDUCTIONS"},
            {"code": "R0360", "label": "Total regulatory adjustments to T2 capital", "section": "T2_DEDUCTIONS_TOTAL", "is_calculated": True},
            
            # T2 Capital
            {"code": "R0370", "label": "Tier 2 (T2) capital", "section": "T2_TOTAL", "is_calculated": True},
            
            # Total Capital
            {"code": "R0380", "label": "Total capital (TC = T1 + T2)", "section": "TOTAL_CAPITAL", "is_calculated": True},
        ]
    }
    
    @classmethod
    def get_empty_template(cls) -> List[TemplateField]:
        """Generate empty template structure."""
        
        fields = []
        for row in cls.TEMPLATE_STRUCTURE["rows"]:
            for col in cls.TEMPLATE_STRUCTURE["columns"]:
                field_code = f"{col['code']}_{row['code']}"
                fields.append(
                    TemplateField(
                        field_code=field_code,
                        row_code=row['code'],
                        col_code=col['code'],
                        label=f"{row['label']} - {col['label']}",
                        value=None,
                        data_type="numeric"
                    )
                )
        
        return fields
    
    @classmethod
    def get_field_info(cls, field_code: str) -> Dict[str, Any]:
        """Get information about a specific field."""
        
        # Parse field code (e.g., "C0010_R0010")
        parts = field_code.split("_")
        if len(parts) != 2:
            return None
        
        col_code, row_code = parts
        
        # Find row and column
        row_info = next((r for r in cls.TEMPLATE_STRUCTURE["rows"] if r["code"] == row_code), None)
        col_info = next((c for c in cls.TEMPLATE_STRUCTURE["columns"] if c["code"] == col_code), None)
        
        if not row_info or not col_info:
            return None
        
        return {
            "field_code": field_code,
            "row": row_info,
            "column": col_info,
            "is_calculated": row_info.get("is_calculated", False),
            "section": row_info.get("section", ""),
        }
    
    @classmethod
    def get_calculation_rules(cls) -> Dict[str, str]:
        """Get calculation rules for computed fields."""
        
        return {
            "R0070": "Sum of R0010 to R0060",  # CET1 before adjustments
            "R0180": "Sum of R0080 to R0130",  # Total CET1 adjustments
            "R0200": "R0070 - R0180",  # CET1 capital
            "R0240": "Sum of R0210 to R0230",  # AT1 before adjustments
            "R0270": "R0250",  # Total AT1 adjustments
            "R0280": "R0240 - R0270",  # AT1 capital
            "R0290": "R0200 + R0280",  # Tier 1 capital
            "R0340": "Sum of R0300 to R0330",  # T2 before adjustments
            "R0360": "R0350",  # Total T2 adjustments
            "R0370": "R0340 - R0360",  # T2 capital
            "R0380": "R0290 + R0370",  # Total capital
        }

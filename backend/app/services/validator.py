"""Validation service for COREP template fields."""

from app.models.schemas import TemplateField, ValidationIssue, ValidationSeverity
from app.services.ca1_template import CA1Template
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Validator:
    """Validates populated COREP template fields."""
    
    def __init__(self, template_id: str = "CA1"):
        """Initialize validator for specific template."""
        self.template_id = template_id
        if template_id == "CA1":
            self.template = CA1Template
        else:
            raise ValueError(f"Template {template_id} not supported")
    
    def validate_fields(self, fields: List[TemplateField]) -> List[ValidationIssue]:
        """
        Validate all populated fields.
        
        Returns:
            List of validation issues (errors and warnings)
        """
        
        issues = []
        
        # Create field lookup
        field_map = {f.field_code: f for f in fields}
        
        # 1. Type validation
        issues.extend(self._validate_types(fields))
        
        # 2. Required fields check
        issues.extend(self._check_required_fields(field_map))
        
        # 3. Business rules validation
        issues.extend(self._validate_business_rules(field_map))
        
        # 4. Range checks
        issues.extend(self._validate_ranges(fields))
        
        logger.info(f"Validation complete: {len(issues)} issues found")
        return issues
    
    def _validate_types(self, fields: List[TemplateField]) -> List[ValidationIssue]:
        """Validate data types."""
        
        issues = []
        
        for field in fields:
            if field.value is None:
                continue
            
            # Check numeric fields
            if field.data_type == "numeric":
                if not isinstance(field.value, (int, float)):
                    try:
                        float(field.value)
                    except (ValueError, TypeError):
                        issues.append(ValidationIssue(
                            field_code=field.field_code,
                            severity=ValidationSeverity.ERROR,
                            message=f"Expected numeric value but got: {type(field.value).__name__}",
                            suggestion="Provide a numeric value"
                        ))
        
        return issues
    
    def _check_required_fields(self, field_map: Dict[str, TemplateField]) -> List[ValidationIssue]:
        """Check if required fields are populated."""
        
        issues = []
        
        # Define required fields for CA1
        required_row_codes = [
            "R0200",  # CET1 capital (required)
            "R0280",  # AT1 capital
            "R0370",  # T2 capital
            "R0380",  # Total capital
        ]
        
        for row_code in required_row_codes:
            field_code = f"C0010_{row_code}"
            
            if field_code not in field_map or field_map[field_code].value is None:
                issues.append(ValidationIssue(
                    field_code=field_code,
                    severity=ValidationSeverity.WARNING,
                    message=f"Required field {row_code} is not populated",
                    suggestion="Ensure this field is calculated or provided"
                ))
        
        return issues
    
    def _validate_business_rules(self, field_map: Dict[str, TemplateField]) -> List[ValidationIssue]:
        """Validate business logic and calculations."""
        
        issues = []
        
        # Get calculation rules
        calc_rules = self.template.get_calculation_rules()
        
        # Validate key calculations
        # Example: CET1 capital = CET1 before adjustments - deductions
        if ("C0010_R0200" in field_map and field_map["C0010_R0200"].value and
            "C0010_R0070" in field_map and field_map["C0010_R0070"].value and
            "C0010_R0180" in field_map and field_map["C0010_R0180"].value):
            
            cet1 = float(field_map["C0010_R0200"].value)
            cet1_before = float(field_map["C0010_R0070"].value)
            deductions = float(field_map["C0010_R0180"].value)
            
            expected = cet1_before - deductions
            tolerance = abs(expected * 0.01)  # 1% tolerance
            
            if abs(cet1 - expected) > tolerance:
                issues.append(ValidationIssue(
                    field_code="C0010_R0200",
                    severity=ValidationSeverity.WARNING,
                    message=f"CET1 calculation mismatch. Expected {expected}, got {cet1}",
                    suggestion=f"CET1 should equal R0070 ({cet1_before}) - R0180 ({deductions})"
                ))
        
        # Validate Tier 1 = CET1 + AT1
        if ("C0010_R0290" in field_map and field_map["C0010_R0290"].value and
            "C0010_R0200" in field_map and field_map["C0010_R0200"].value and
            "C0010_R0280" in field_map and field_map["C0010_R0280"].value):
            
            t1 = float(field_map["C0010_R0290"].value)
            cet1 = float(field_map["C0010_R0200"].value)
            at1 = float(field_map["C0010_R0280"].value)
            
            expected = cet1 + at1
            tolerance = abs(expected * 0.01)
            
            if abs(t1 - expected) > tolerance:
                issues.append(ValidationIssue(
                    field_code="C0010_R0290",
                    severity=ValidationSeverity.ERROR,
                    message=f"Tier 1 calculation error. Expected {expected}, got {t1}",
                    suggestion=f"T1 must equal CET1 ({cet1}) + AT1 ({at1})"
                ))
        
        # Validate Total Capital = T1 + T2
        if ("C0010_R0380" in field_map and field_map["C0010_R0380"].value and
            "C0010_R0290" in field_map and field_map["C0010_R0290"].value and
            "C0010_R0370" in field_map and field_map["C0010_R0370"].value):
            
            total = float(field_map["C0010_R0380"].value)
            t1 = float(field_map["C0010_R0290"].value)
            t2 = float(field_map["C0010_R0370"].value)
            
            expected = t1 + t2
            tolerance = abs(expected * 0.01)
            
            if abs(total - expected) > tolerance:
                issues.append(ValidationIssue(
                    field_code="C0010_R0380",
                    severity=ValidationSeverity.ERROR,
                    message=f"Total Capital calculation error. Expected {expected}, got {total}",
                    suggestion=f"Total Capital must equal T1 ({t1}) + T2 ({t2})"
                ))
        
        return issues
    
    def _validate_ranges(self, fields: List[TemplateField]) -> List[ValidationIssue]:
        """Validate that values are within realistic ranges."""
        
        issues = []
        
        for field in fields:
            if field.value is None:
                continue
            
            # Check for negative values in capital fields (should be >= 0)
            if field.data_type == "numeric":
                try:
                    value = float(field.value)
                    
                    # Capital amounts should generally be positive
                    # Exception: Some deductions can be 0
                    if value < 0 and not field.row_code.startswith("R008"):  # Not deductions
                        issues.append(ValidationIssue(
                            field_code=field.field_code,
                            severity=ValidationSeverity.WARNING,
                            message=f"Unexpected negative value: {value}",
                            suggestion="Capital components should typically be positive"
                        ))
                    
                    # Check for unrealistically large values (> £10 trillion)
                    if value > 10_000_000_000_000:
                        issues.append(ValidationIssue(
                            field_code=field.field_code,
                            severity=ValidationSeverity.WARNING,
                            message=f"Unusually large value: {value:,.0f}",
                            suggestion="Please verify this amount is correct"
                        ))
                
                except (ValueError, TypeError):
                    pass  # Already caught in type validation
        
        return issues

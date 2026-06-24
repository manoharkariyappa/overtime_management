import frappe

def before_uninstall():

    custom_fields = [
        "Shift Type-custom_working_hours",
        "Attendance-custom_overtime_hours",
        "Attendance-custom_monthly_permission_hours",
        "Attendance-custom_laps_hours",
        "Salary Slip-custom_total_overtime_hours",
        "Salary Slip-custom_overtime_amount",
        "Salary Slip-custom_total_laps_hours",
        "Salary Slip-custom_holiday_working_days"
    ]

    for field in custom_fields:
        if frappe.db.exists("Custom Field", field):
            frappe.delete_doc("Custom Field", field, force=True)

    if frappe.db.exists("Salary Component", "Overtime"):
        frappe.delete_doc(
            "Salary Component",
            "Overtime",
            force=True
        )

    frappe.db.commit()
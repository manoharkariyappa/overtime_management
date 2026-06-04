import frappe

def calculate_overtime(doc, method=None):

    if not doc.shift or not doc.working_hours:
        doc.custom_overtime_hours = 0
        return

    shift_hours = frappe.db.get_value(
        "Shift Type",
        doc.shift,
        "custom_working_hours"
    ) or 9

    holiday_list = frappe.db.get_value(
        "Employee",
        doc.employee,
        "holiday_list"
    )

    is_holiday = False

    if holiday_list:
        is_holiday = frappe.db.exists(
            "Holiday",
            {
                "parent": holiday_list,
                "holiday_date": doc.attendance_date
            }
        )

    if is_holiday:
        doc.custom_overtime_hours = float(doc.working_hours)
    else:
        doc.custom_overtime_hours = max(
            0,
            float(doc.working_hours) - float(shift_hours)
        )
import frappe

def calculate_salary_overtime(doc, method=None):

    total_ot = frappe.db.sql("""
        SELECT COALESCE(SUM(custom_overtime_hours),0)
        FROM `tabAttendance`
        WHERE employee=%s
        AND attendance_date BETWEEN %s AND %s
        AND docstatus=1
    """, (
        doc.employee,
        doc.start_date,
        doc.end_date
    ))[0][0]

    doc.custom_total_overtime_hours = total_ot

    employee_shift = frappe.db.get_value(
        "Employee",
        doc.employee,
        "default_shift"
    )

    shift_hours = frappe.db.get_value(
        "Shift Type",
        employee_shift,
        "custom_working_hours"
    ) or 9

    basic_salary = 0

    for row in doc.earnings:
        if row.salary_component in ["Basic", "Basic+DA"]:
            basic_salary = row.amount
            break

    payment_days = doc.payment_days or 1

    daily_rate = basic_salary / payment_days

    hourly_rate = daily_rate / shift_hours

    overtime_amount = hourly_rate * total_ot

    doc.custom_overtime_amount = overtime_amount

    found = False

    for row in doc.earnings:
        if row.salary_component == "Overtime":
            row.amount = overtime_amount
            found = True
            break

    if not found and overtime_amount > 0:
        doc.append("earnings", {
            "salary_component": "Overtime",
            "amount": overtime_amount
        })
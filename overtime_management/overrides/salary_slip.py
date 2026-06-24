# import frappe

# def calculate_salary_overtime(doc, method=None):

#     total_ot = frappe.db.sql("""
#         SELECT COALESCE(SUM(custom_overtime_hours),0)
#         FROM `tabAttendance`
#         WHERE employee=%s
#         AND attendance_date BETWEEN %s AND %s
#         AND docstatus=1
#     """, (
#         doc.employee,
#         doc.start_date,
#         doc.end_date
#     ))[0][0]

#     doc.custom_total_overtime_hours = total_ot

#     employee_shift = frappe.db.get_value(
#         "Employee",
#         doc.employee,
#         "default_shift"
#     )

#     shift_hours = frappe.db.get_value(
#         "Shift Type",
#         employee_shift,
#         "custom_working_hours"
#     ) or 9

#     basic_salary = 0

#     for row in doc.earnings:
#         if row.salary_component in ["Basic", "Basic+DA"]:
#             basic_salary = row.amount
#             break

#     payment_days = doc.payment_days or 1

#     daily_rate = basic_salary / payment_days

#     hourly_rate = daily_rate / shift_hours

#     overtime_amount = hourly_rate * total_ot

#     doc.custom_overtime_amount = overtime_amount

#     found = False

#     for row in doc.earnings:
#         if row.salary_component == "Overtime":
#             row.amount = overtime_amount
#             found = True
#             break

#     if not found and overtime_amount > 0:
#         doc.append("earnings", {
#             "salary_component": "Overtime",
#             "amount": overtime_amount
#         })

# import frappe

# def calculate_salary_overtime(doc, method=None):

#     employee_shift = frappe.db.get_value(
#         "Employee",
#         doc.employee,
#         "default_shift"
#     )

#     shift_hours = frappe.db.get_value(
#         "Shift Type",
#         employee_shift,
#         "custom_working_hours"
#     ) or 9

#     # Total OT Hours
#     total_ot = frappe.db.sql("""
#         SELECT COALESCE(SUM(custom_overtime_hours), 0)
#         FROM `tabAttendance`
#         WHERE employee=%s
#         AND attendance_date BETWEEN %s AND %s
#         AND docstatus=1
#     """, (
#         doc.employee,
#         doc.start_date,
#         doc.end_date
#     ))[0][0]

#     total_laps = frappe.db.sql("""
#         SELECT COALESCE(SUM(custom_laps_hours), 0)
#         FROM `tabAttendance`
#         WHERE employee=%s
#         AND attendance_date BETWEEN %s AND %s
#         AND docstatus=1
#     """, (
#         doc.employee,
#         doc.start_date,
#         doc.end_date
#     ))[0][0]   
    
#     doc.custom_total_laps_hours = total_laps

#     # Approved Comp Off leaves during salary period
#     comp_off_days = frappe.db.sql("""
#         SELECT COALESCE(SUM(total_leave_days), 0)
#         FROM `tabLeave Application`
#         WHERE employee=%s
#         AND leave_type='Comp Off'
#         AND status='Approved'
#         AND from_date <= %s
#         AND to_date >= %s
#     """, (
#         doc.employee,
#         doc.end_date,
#         doc.start_date
#     ))[0][0]
                             
       
#     # Convert Comp Off days to hours
#     comp_off_hours = comp_off_days * shift_hours

#     # Deduct Comp Off hours from OT
#     payable_ot_hours = max(0, total_ot - comp_off_hours)

#     doc.custom_total_overtime_hours = payable_ot_hours

#     basic_salary = 0

#     for row in doc.earnings:
#         if row.salary_component in ["Basic", "Basic+DA"]:
#             basic_salary = row.amount
#             break

#     payment_days = doc.payment_days or 1

#     daily_rate = basic_salary / payment_days
#     hourly_rate = daily_rate / shift_hours

#     overtime_amount = hourly_rate * payable_ot_hours

#     doc.custom_overtime_amount = overtime_amount

#     found = False

#     for row in doc.earnings:
#         if row.salary_component == "Overtime":
#             row.amount = overtime_amount
#             found = True
#             break

#     if not found and overtime_amount > 0:
#         doc.append("earnings", {
#             "salary_component": "Overtime",
#             "amount": overtime_amount
#         })
import frappe


def calculate_salary_overtime(doc, method=None):
    # Force Working Days to 30
    doc.total_working_days = 30
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

    total_ot = frappe.db.sql("""
        SELECT COALESCE(SUM(custom_overtime_hours), 0)
        FROM `tabAttendance`
        WHERE employee=%s
        AND attendance_date BETWEEN %s AND %s
        AND docstatus=1
    """, (
        doc.employee,
        doc.start_date,
        doc.end_date
    ))[0][0]

    total_laps = frappe.db.sql("""
        SELECT COALESCE(SUM(custom_laps_hours), 0)
        FROM `tabAttendance`
        WHERE employee=%s
        AND attendance_date BETWEEN %s AND %s
        AND docstatus=1
    """, (
        doc.employee,
        doc.start_date,
        doc.end_date
    ))[0][0]

    # doc.custom_total_laps_hours = total_laps
    allowed_permission_hours = frappe.db.get_value(
       "Shift Type",
        employee_shift,
        "custom_monthly_permission_hours"
    ) or 0

    final_laps_hours = max(
       0,
       float(total_laps) - float(allowed_permission_hours)
    )

    doc.custom_total_laps_hours = final_laps_hours

    comp_off_days = frappe.db.sql("""
        SELECT COALESCE(SUM(total_leave_days), 0)
        FROM `tabLeave Application`
        WHERE employee=%s
        AND leave_type='Comp Off'
        AND status='Approved'
        AND from_date <= %s
        AND to_date >= %s
    """, (
        doc.employee,
        doc.end_date,
        doc.start_date
    ))[0][0]

    holiday_worked_days = frappe.db.sql("""
        SELECT COUNT(*)
        FROM `tabAttendance` a
        INNER JOIN `tabEmployee` e
            ON e.name = a.employee
        INNER JOIN `tabHoliday` h
            ON h.parent = e.holiday_list
            AND h.holiday_date = a.attendance_date
        WHERE a.employee=%s
        AND a.attendance_date BETWEEN %s AND %s
        AND a.status='Present'
        AND a.docstatus=1
    """, (
        doc.employee,
        doc.start_date,
        doc.end_date
    ))[0][0]

    doc.custom_holiday_working_days = max(
        0,
        holiday_worked_days - comp_off_days
    )

    payable_ot_hours = total_ot

    doc.custom_total_overtime_hours = payable_ot_hours

    basic_salary = 0

    for row in doc.earnings:
        if row.salary_component in ["Basic", "Basic+DA"]:
            basic_salary = row.amount
            break

    payment_days = doc.payment_days or 1

    daily_rate = basic_salary / payment_days
    hourly_rate = daily_rate / shift_hours

    overtime_amount = hourly_rate * payable_ot_hours

    doc.custom_overtime_amount = overtime_amount

    for row in doc.earnings:
        if row.salary_component == "Overtime":
            row.amount = overtime_amount
            break
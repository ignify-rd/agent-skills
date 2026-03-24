#!/usr/bin/env python3
"""
generate_field_skeleton.py — Pre-generate field test case skeleton from field metadata.

Usage:
    python generate_field_skeleton.py --field "Tên cấu hình SLA" --type textbox --maxLength 100 --required true
    python generate_field_skeleton.py --field "Ngày hiệu lực" --type datepicker --constraint ">= ngày hiện tại"
    python generate_field_skeleton.py --field "Trạng thái" --type combobox --apiEndpoint "/api/status"
    python generate_field_skeleton.py --field "Loại" --type simple_dropdown --values "A,B,C"
"""

import argparse
import sys
import re


def _fill(text, **kwargs):
    """Fill placeholders in template text."""
    for key, val in kwargs.items():
        text = text.replace(f"{{{key}}}", str(val))
    return text


def _indent(text, level=1, marker="    "):
    """Indent text by `level` levels of `marker`."""
    prefix = marker * level
    return "\n".join(f"{prefix}{line}" if line.strip() else line for line in text.splitlines())


# ─── Field Type Templates ────────────────────────────────────────────────────

def textbox(name, max_length=None, min_length=None, placeholder=None,
            required=False, allow_spaces=True, allow_special_chars=True,
            search_description=None, conditional_disabled=None, **kwargs):
    """Generate Textbox validate skeleton."""
    max_len = max_length or "N"
    max_minus = max_length - 1 if max_length and max_length > 1 else max_len
    max_plus = max_length + 1 if max_length else max_len

    lines = [f"### Kiểm tra textbox \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra hiển thị khi nhập 1 ký tự")
    lines.append(_indent("Hiển thị icon X xóa nhanh ký tự nhập"))

    lines.append("- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh ký tự nhập")
    lines.append(_indent("Clear data đã nhập ở textbox"))

    lines.append("- Kiểm tra khi nhập ký tự là số")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập ký tự chữ")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập ký tự đặc biệt")
    exp = "Hệ thống cho phép nhập" if allow_special_chars else "Hệ thống chặn không cho phép nhập"
    lines.append(_indent(exp))

    lines.append("- Kiểm tra khi nhập ký tự chữ có dấu (tiếng Việt)")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập SQL injection")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập unicode đặc biệt (tiếng Trung, Nhật, Hàn)")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    if search_description:
        lines.append("- Kiểm tra khi nhập 1 phần ký tự")
        lines.append(_indent(search_description))

    sp_exp = "Hệ thống cho phép nhập" if allow_spaces else "Hệ thống chặn không cho phép nhập"
    lines.append("- Kiểm tra khi nhập ký tự chứa space đầu/cuối")
    lines.append(_indent(sp_exp))

    sp_paste = "Hệ thống cho phép Paste" if allow_spaces else "Hệ thống chặn không cho phép Paste"
    lines.append("- Kiểm tra khi Paste ký tự chứa space đầu/cuối")
    lines.append(_indent(sp_paste))

    lines.append("- Kiểm tra khi nhập all space")
    lines.append(_indent(sp_exp))

    lines.append(f"- Kiểm tra khi nhập {max_minus} ký tự")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append(f"- Kiểm tra khi nhập {max_len} ký tự (maxLength)")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append(f"- Kiểm tra khi Paste {max_len} ký tự")
    lines.append(_indent("Hệ thống cho phép Paste"))

    lines.append(f"- Kiểm tra khi nhập {max_plus} ký tự (vượt maxLength)")
    lines.append(_indent(f'Hiển thị cảnh báo "{{warning_maxlength}}"'))

    if min_length:
        min_minus = min_length - 1 if min_length > 1 else 1
        lines.append(f"- Kiểm tra khi nhập {min_minus} ký tự (dưới minLength={min_length})")
        lines.append(_indent(f'Hiển thị thông báo lỗi "{{warning_minlength}}"'))

        lines.append(f"- Kiểm tra khi nhập {min_length} ký tự (đạt minLength)")
        lines.append(_indent("Hệ thống cho phép nhập"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_required}}"'))

    if conditional_disabled:
        lines.append("- Kiểm tra khi field bị disable theo điều kiện")
        lines.append(_indent(f"Textbox \"{name}\" ở trạng thái Disabled, không thể nhập"))

    return "\n".join(lines)


def combobox(name, placeholder=None, required=False, api_endpoint=None,
             is_single_select=True, max_search_len=None, **kwargs):
    """Generate Combobox (API-driven) validate skeleton."""
    lines = [f"### Kiểm tra combobox \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    if required:
        lines.append("- Kiểm tra bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    lines.append("- Kiểm tra hiển thị khi đã chọn giá trị")
    lines.append(_indent("Hiển thị icon X xóa nhanh"))

    lines.append("- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh")
    lines.append(_indent("Clear data đã chọn"))

    if api_endpoint:
        lines.append(f"- Kiểm tra danh sách khi mở combobox")
        lines.append(_indent(f"{{list_values}}"))
        lines.append(_indent(f"Endpoint: {api_endpoint}", level=2))

        lines.append("- Kiểm tra khi API không phản hồi (timeout)")
        lines.append(_indent('Hiển thị popup lỗi "Có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại."'))

        lines.append("- Kiểm tra khi API trả lỗi")
        lines.append(_indent("Hiển thị popup lỗi với nội dung errorDesc server trả về"))

        lines.append("- Kiểm tra khi API trả danh sách rỗng")
        lines.append(_indent('Hiển thị "Không tìm thấy" tại Combobox'))

        lines.append("- Kiểm tra trạng thái loading khi chờ API")
        lines.append(_indent("Hiển thị loading indicator"))
    else:
        lines.append("- Kiểm tra danh sách giá trị")
        lines.append(_indent("{{liệt kê giá trị cụ thể}}"))

    multi = "Hệ thống chỉ cho phép chọn 1" if is_single_select else "Cho phép chọn nhiều"
    lines.append(f"- Kiểm tra chọn 1 giá trị")
    lines.append(_indent("Hệ thống cho phép chọn"))

    lines.append(f"- Kiểm tra chọn nhiều giá trị")
    lines.append(_indent(multi))

    lines.append("- Kiểm tra hiển thị sau khi chọn giá trị")
    lines.append(_indent("Fill đúng text đã chọn, đóng combobox"))

    if api_endpoint:
        search_max = max_search_len or "N"
        lines.append(f"- Kiểm tra khi nhập số vào ô tìm kiếm")
        lines.append(_indent("Cho phép nhập"))

        lines.append("- Kiểm tra khi nhập chữ a-z A-Z vào ô tìm kiếm")
        lines.append(_indent("Cho phép nhập"))

        lines.append("- Kiểm tra khi nhập ký tự đặc biệt vào ô tìm kiếm")
        lines.append(_indent("{{allowSearchSpecialChars ? 'Cho phép nhập' : 'Hệ thống chặn'}}"))

        lines.append("- Kiểm tra khi nhập khoảng trắng vào ô tìm kiếm")
        lines.append(_indent("Cho phép nhập"))

        lines.append(f"- Kiểm tra khi nhập {search_max} ký tự vào ô tìm kiếm")
        lines.append(_indent(f"Hệ thống cho phép nhập {search_max} ký tự"))

        lines.append(f"- Kiểm tra khi nhập {int(search_max)+1} ký tự vào ô tìm kiếm (vượt maxSearchLen)")
        lines.append(_indent(f"Hệ thống chặn không cho nhập quá {search_max} ký tự"))

        lines.append("- Kiểm tra khi nhập từ khóa tồn tại")
        lines.append(_indent("Hiển thị kết quả tương ứng"))

        lines.append("- Kiểm tra khi nhập từ khóa không có trong danh sách")
        lines.append(_indent('Hiển thị "Không tìm thấy" tại Combobox'))

        lines.append("- Kiểm tra khi nhập 1 phần từ khóa")
        lines.append(_indent("Hiển thị kết quả chứa phần từ khóa"))

        lines.append("- Kiểm tra chọn bằng chuột (click)")
        lines.append(_indent("Cho phép chọn"))

        lines.append("- Kiểm tra chọn bằng bàn phím (Enter/Space)")
        lines.append(_indent("Cho phép chọn"))

    return "\n".join(lines)


def simple_dropdown(name, placeholder=None, required=False, values=None,
                    is_single_select=True, conditional_disabled=None, **kwargs):
    """Generate Simple Dropdown (hardcoded values) validate skeleton."""
    lines = [f"### Kiểm tra dropdown \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    if required:
        lines.append("- Kiểm tra bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    if values:
        lines.append(f"- Kiểm tra danh sách giá trị")
        lines.append(_indent(f"Hiển thị danh sách: {values}"))

    lines.append("- Kiểm tra chọn 1 giá trị")
    lines.append(_indent("Hệ thống cho phép chọn"))

    multi = "Hệ thống chỉ cho phép chọn 1" if is_single_select else "Cho phép chọn nhiều"
    lines.append("- Kiểm tra chọn nhiều giá trị")
    lines.append(_indent(multi))

    if values:
        first_val = values.split(",")[0].strip() if "," in values else values.strip()
        lines.append(f"- Kiểm tra chọn giá trị = \"{first_val}\"")
        lines.append(_indent(f'Hệ thống hiển thị text "{first_val}" tại dropdown'))

    lines.append("- Kiểm tra hiển thị icon X khi đã chọn giá trị")
    lines.append(_indent("Hiển thị icon X xóa nhanh"))

    lines.append("- Kiểm tra hoạt động khi thực hiện thao tác xóa nhanh")
    lines.append(_indent("Clear data đã chọn"))

    if conditional_disabled:
        lines.append(f"- Kiểm tra khi dropdown bị disable theo điều kiện: {conditional_disabled}")
        lines.append(_indent("Dropdown ở trạng thái Disabled"))

    return "\n".join(lines)


def toggle(name, default_value=None, conditional_disabled=None, has_permission=False, **kwargs):
    """Generate Toggle switch validate skeleton."""
    lines = [f"### Kiểm tra toggle \"{name}\"", ""]

    lines.append(f"- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    if default_value is not None:
        lines.append(f"- Kiểm tra giá trị mặc định")
        lines.append(_indent(f"Mặc định: {default_value}"))

    lines.append(f"- Kiểm tra khi click toggle chuyển trạng thái")
    lines.append(_indent("{{chuyển đổi trạng thái thành công}}"))

    lines.append(f"- Kiểm tra khi click toggle lại lần nữa")
    lines.append(_indent("{{quay về trạng thái ban đầu}}"))

    if conditional_disabled:
        lines.append(f"- Kiểm tra khi toggle bị disable theo điều kiện: {conditional_disabled}")
        lines.append(_indent("Toggle ở trạng thái Disabled, không thể click"))

    if has_permission:
        lines.append("- Kiểm tra khi user không có quyền thay đổi toggle")
        lines.append(_indent("Toggle ở trạng thái Disabled"))

    return "\n".join(lines)


def datepicker(name, placeholder=None, required=False, constraint=None,
               min_date=None, max_date=None, **kwargs):
    """Generate DatePicker validate skeleton."""
    lines = [f"### Kiểm tra datepicker \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra khi nhấn icon lịch")
    lines.append(_indent("Hiển thị bảng chọn ngày"))

    lines.append("- Kiểm tra khi nhập đúng định dạng ngày")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập sai định dạng ngày")
    lines.append(_indent('Hiển thị thông báo "{{warning_invalid_date}}"'))

    lines.append("- Kiểm tra khi nhập ngày không tồn tại (VD: 30/02/2025)")
    lines.append(_indent('Hiển thị thông báo "{{warning_invalid_date}}"'))

    if constraint:
        lines.append(f"- Kiểm tra khi nhập ngày vi phạm ràng buộc: {constraint}")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_constraint}}"'))

    lines.append("- Kiểm tra khi nhập ngày hợp lệ")
    lines.append(_indent("Hệ thống cho phép nhập"))

    if min_date:
        lines.append(f"- Kiểm tra khi nhập ngày trước minDate ({min_date})")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_mindate}}"'))

    if max_date:
        lines.append(f"- Kiểm tra khi nhập ngày sau maxDate ({max_date})")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_maxdate}}"'))

    lines.append("- Kiểm tra khi nhập ngày quá khứ")
    lines.append(_indent("{{theo ràng buộc nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập ngày tương lai")
    lines.append(_indent("{{theo ràng buộc nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập SQL injection")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra hiển thị icon X xóa nhanh khi đã chọn ngày")
    lines.append(_indent("Hiển thị icon X xóa nhanh"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def daterange(name, placeholder=None, required=False, **kwargs):
    """Generate DateRangePicker validate skeleton."""
    lines = [f"### Kiểm tra date range \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra chọn ngày bắt đầu")
    lines.append(_indent("Chọn được ngày hợp lệ"))

    lines.append("- Kiểm tra chọn ngày kết thúc")
    lines.append(_indent("Chọn được ngày hợp lệ"))

    lines.append("- Kiểm tra khi ngày kết thúc < ngày bắt đầu")
    lines.append(_indent('Hiển thị thông báo "{{warning_range_invalid}}"'))

    lines.append("- Kiểm tra khi nhập đúng định dạng")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập sai định dạng ngày")
    lines.append(_indent('Hiển thị thông báo "{{warning_invalid_date}}"'))

    lines.append("- Kiểm tra hiển thị icon X xóa nhanh khi đã chọn ngày")
    lines.append(_indent("Hiển thị icon X xóa nhanh"))

    lines.append("- Kiểm tra khi xóa ngày bắt đầu")
    lines.append(_indent("Ngày kết thúc vẫn giữ nguyên"))

    lines.append("- Kiểm tra khi xóa ngày kết thúc")
    lines.append(_indent("Ngày bắt đầu vẫn giữ nguyên"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    return "\n".join(lines)


def textarea(name, max_length=None, placeholder=None, required=False,
            allow_spaces=True, **kwargs):
    """Generate Textarea validate skeleton."""
    lines = [f"### Kiểm tra textarea \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra nhập ký tự thường")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhấn Enter xuống dòng")
    lines.append(_indent("Xuống dòng thành công, hiển thị đúng format"))

    lines.append("- Kiểm tra khi nhập ký tự đặc biệt")
    lines.append(_indent("{{allowSpecialChars ? 'Cho phép' : 'Chặn'}}"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập SQL injection")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    if max_length:
        max_minus = max_length - 1
        max_plus = max_length + 1
        lines.append(f"- Kiểm tra khi nhập {max_minus} ký tự")
        lines.append(_indent("Hệ thống cho phép nhập"))

        lines.append(f"- Kiểm tra khi nhập {max_length} ký tự (maxLength)")
        lines.append(_indent("Hệ thống cho phép nhập"))

        lines.append(f"- Kiểm tra khi nhập {max_plus} ký tự (vượt maxLength)")
        lines.append(_indent(f'Hiển thị cảnh báo "{{warning_maxlength}}"'))
    else:
        lines.append("- Kiểm tra khi nhập rất nhiều ký tự")
        lines.append(_indent("{{kiểm tra bộ đếm ký tự (nếu có)}}"))

    lines.append("- Kiểm tra hiển thị icon X xóa nhanh khi đã nhập")
    lines.append(_indent("Hiển thị icon X xóa nhanh"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def number_input(name, placeholder=None, required=False, min_value=None,
                 max_value=None, allow_decimal=None, **kwargs):
    """Generate NumberInput validate skeleton."""
    lines = [f"### Kiểm tra number input \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    lines.append("- Kiểm tra giá trị mặc định")
    lines.append(_indent("Mặc định rỗng"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra khi nhập số dương")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập số 0")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập số âm")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập số thập phân")
    exp = "Hệ thống cho phép nhập" if allow_decimal else "Hệ thống chặn không cho phép nhập"
    lines.append(_indent(exp))

    lines.append("- Kiểm tra khi nhập leading zero (VD: 00123)")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập chữ")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập ký tự đặc biệt (@#$%)")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập khoảng trắng")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập SQL injection")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    if min_value is not None:
        lines.append(f"- Kiểm tra khi nhập giá trị nhỏ hơn minValue ({min_value})")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_minvalue}}"'))

    if max_value is not None:
        lines.append(f"- Kiểm tra khi nhập giá trị lớn hơn maxValue ({max_value})")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_maxvalue}}"'))

    lines.append("- Kiểm tra khi sử dụng stepper tăng (+)")
    lines.append(_indent("Giá trị tăng đúng step"))

    lines.append("- Kiểm tra khi sử dụng stepper giảm (-)")
    lines.append(_indent("Giá trị giảm đúng step"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def checkbox(name, default_value=None, required=False, **kwargs):
    """Generate Checkbox validate skeleton."""
    lines = [f"### Kiểm tra checkbox \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị và enable"))

    if default_value is not None:
        lines.append("- Kiểm tra giá trị mặc định")
        lines.append(_indent(f"Mặc định: {'đã check' if default_value else 'chưa check'}"))

    lines.append("- Kiểm tra khi click chọn checkbox")
    lines.append(_indent("Checkbox được check, hiển thị trạng thái chọn"))

    lines.append("- Kiểm tra khi click lại để bỏ chọn")
    lines.append(_indent("Checkbox bỏ check, trở về trạng thái ban đầu"))

    if required:
        lines.append("- Kiểm tra khi không check và submit form")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def button(name, conditional_disabled=None, has_permission=True, **kwargs):
    """Generate Button validate skeleton."""
    lines = [f"### Kiểm tra button \"{name}\"", ""]

    lines.append(f"- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Luôn hiển thị"))

    lines.append(f"- Kiểm tra khi click button thành công")
    lines.append(_indent("{{mô tả action khi click thành công}}"))

    lines.append(f"- Kiểm tra khi click button khi form có lỗi validate")
    lines.append(_indent("Hệ thống hiển thị cảnh báo, không submit"))

    lines.append(f"- Kiểm tra khi click button khi hệ thống đang xử lý (loading)")
    lines.append(_indent("Button bị disable, hiển thị loading indicator"))

    if conditional_disabled:
        lines.append(f"- Kiểm tra khi button bị disable theo điều kiện: {conditional_disabled}")
        lines.append(_indent("Button ở trạng thái Disabled, không thể click"))

    if has_permission:
        lines.append("- Kiểm tra khi user không có quyền click button")
        lines.append(_indent("Button không hiển thị hoặc bị disable"))

    return "\n".join(lines)


def icon_x(name, **kwargs):
    """Generate Icon X validate skeleton."""
    lines = [f"### Kiểm tra icon x \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị icon X khi field có dữ liệu")
    lines.append(_indent("Icon X hiển thị rõ ràng"))

    lines.append("- Kiểm tra khi click icon X")
    lines.append(_indent("Xóa toàn bộ dữ liệu trong field liên quan"))

    lines.append("- Kiểm tra khi field rỗng")
    lines.append(_indent("Icon X không hiển thị"))

    return "\n".join(lines)


def radio_group(name, values=None, required=False, **kwargs):
    """Generate Radio Group validate skeleton."""
    lines = [f"### Kiểm tra radio group \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Tất cả radio buttons hiển thị, chưa chọn"))

    if values:
        lines.append(f"- Kiểm tra danh sách giá trị")
        lines.append(_indent(f"Hiển thị đủ: {values}"))

    lines.append("- Kiểm tra khi chọn 1 radio button")
    lines.append(_indent("Radio được chọn, các radio khác bỏ chọn"))

    lines.append("- Kiểm tra khi chọn radio khác")
    lines.append(_indent("Radio trước bỏ chọn, radio mới được chọn"))

    if required:
        lines.append("- Kiểm tra khi không chọn và submit form")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def file_upload(name, allowed_formats=None, max_size=None, required=False, **kwargs):
    """Generate File Upload validate skeleton."""
    lines = [f"### Kiểm tra file upload \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Vùng upload hiển thị, cho phép drag & drop"))

    if allowed_formats:
        lines.append(f"- Kiểm tra khi upload đúng định dạng ({allowed_formats})")
        lines.append(_indent("Upload thành công, hiển thị tên file"))

    lines.append("- Kiểm tra khi upload sai định dạng")
    lines.append(_indent('Hiển thị thông báo "{{warning_invalid_format}}"'))

    if max_size:
        lines.append(f"- Kiểm tra khi upload file đúng kích thước (≤{max_size})")
        lines.append(_indent("Upload thành công"))

        max_plus = f"{max_size}+MB"
        lines.append(f"- Kiểm tra khi upload file vượt kích thước ({max_plus})")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_maxsize}}"'))

    lines.append("- Kiểm tra khi upload file rỗng")
    lines.append(_indent('Hiển thị thông báo "{{warning_empty_file}}"'))

    lines.append("- Kiểm tra khi upload file trùng tên")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi upload file có tên chứa ký tự đặc biệt/unicode")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi upload trong khi đang loading")
    lines.append(_indent("Progress bar hiển thị"))

    lines.append("- Kiểm tra khi hủy upload")
    lines.append(_indent("Upload bị hủy, file không được lưu"))

    lines.append("- Kiểm tra khi xóa file đã upload")
    lines.append(_indent("File bị xóa khỏi danh sách"))

    if required:
        lines.append("- Kiểm tra khi không upload file và submit form")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def password_input(name, placeholder=None, required=False, min_length=None, **kwargs):
    """Generate Password Input validate skeleton."""
    lines = [f"### Kiểm tra password input \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Password được che bằng dấu • hoặc *"))

    lines.append("- Kiểm tra khi nhập password")
    lines.append(_indent("Password được che, không hiển thị rõ"))

    lines.append("- Kiểm tra khi nhấn icon hiển thị password")
    lines.append(_indent("Password được hiển thị rõ"))

    lines.append("- Kiểm tra khi nhấn lại icon ẩn password")
    lines.append(_indent("Password được che lại"))

    if placeholder:
        lines.append("- Kiểm tra placeholder")
        lines.append(_indent(f'Hiển thị placeholder "{placeholder}"'))

    lines.append("- Kiểm tra khi nhập ký tự thường")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập ký tự đặc biệt")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    if min_length:
        lines.append(f"- Kiểm tra khi nhập dưới minLength ({min_length} ký tự)")
        lines.append(_indent(f'Hiển thị thông báo "{{warning_minlength}}"'))

    lines.append("- Kiểm tra khi nhập maxLength")
    lines.append(_indent("Hệ thống cho phép nhập"))

    lines.append("- Kiểm tra khi nhập vượt maxLength")
    lines.append(_indent("Hệ thống chặn không cho nhập thêm"))

    lines.append("- Kiểm tra khi bỏ trống")
    lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    lines.append("- Kiểm tra hiển thị icon X xóa nhanh")
    lines.append(_indent("Icon X hiển thị khi có dữ liệu"))

    return "\n".join(lines)


def tag_input(name, placeholder=None, required=False, max_tags=None, **kwargs):
    """Generate Tag/Token Input validate skeleton."""
    lines = [f"### Kiểm tra tag input \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Vùng nhập tag hiển thị"))

    lines.append("- Kiểm tra khi nhập tag hợp lệ")
    lines.append(_indent("Tag được tạo dưới dạng chip/token"))

    lines.append("- Kiểm tra khi nhập tag trùng lặp")
    lines.append(_indent("Hệ thống báo trùng hoặc không cho thêm"))

    lines.append("- Kiểm tra khi xóa tag bằng icon X")
    lines.append(_indent("Tag bị xóa khỏi danh sách"))

    lines.append("- Kiểm tra khi nhấn Backspace khi input trống")
    lines.append(_indent("Xóa tag cuối cùng"))

    if max_tags:
        lines.append(f"- Kiểm tra khi thêm đủ {max_tags} tags")
        lines.append(_indent(f"Cho phép thêm đến {max_tags} tags"))

        lines.append(f"- Kiểm tra khi thêm quá {max_tags} tags")
        lines.append(_indent(f"Hệ thống chặn không cho thêm quá {max_tags} tags"))

    lines.append("- Kiểm tra khi nhập ký tự đặc biệt")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập emoji")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi nhập XSS script")
    lines.append(_indent("Hệ thống chặn không cho phép nhập"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống và submit")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


def rich_text_editor(name, required=False, **kwargs):
    """Generate Rich Text Editor validate skeleton."""
    lines = [f"### Kiểm tra rich text editor \"{name}\"", ""]

    lines.append("- Kiểm tra hiển thị mặc định")
    lines.append(_indent("Rich text editor hiển thị với thanh công cụ"))

    lines.append("- Kiểm tra nhập text thường")
    lines.append(_indent("Text được nhập và hiển thị đúng"))

    lines.append("- Kiểm tra khi nhấn Enter xuống dòng")
    lines.append(_indent("Xuống dòng trong editor"))

    lines.append("- Kiểm tra khi định dạng text (bold, italic)")
    lines.append(_indent("Định dạng được áp dụng"))

    lines.append("- Kiểm tra khi paste nội dung có định dạng")
    lines.append(_indent("Nội dung được paste, định dạng được giữ"))

    lines.append("- Kiểm tra khi paste nội dung có XSS")
    lines.append(_indent("Hệ thống chặn hoặc strip XSS"))

    lines.append("- Kiểm tra khi paste nội dung có SQL injection")
    lines.append(_indent("Hệ thống chặn hoặc strip SQL injection"))

    lines.append("- Kiểm tra khi paste nội dung quá dài")
    lines.append(_indent("{{theo nghiệp vụ}}"))

    lines.append("- Kiểm tra khi xóa toàn bộ nội dung")
    lines.append(_indent("Nội dung bị xóa, editor trở về trạng thái trống"))

    if required:
        lines.append("- Kiểm tra khi bỏ trống và submit")
        lines.append(_indent('Hiển thị thông báo "{{warning_required}}"'))

    return "\n".join(lines)


# ─── Template Map ────────────────────────────────────────────────────────────

TEMPLATES = {
    "textbox": textbox,
    "text": textbox,
    "input": textbox,
    "combobox": combobox,
    "dropdown_combobox": combobox,
    "simple_dropdown": simple_dropdown,
    "dropdown": simple_dropdown,
    "toggle": toggle,
    "switch": toggle,
    "datepicker": datepicker,
    "date": datepicker,
    "date_range": daterange,
    "daterange": daterange,
    "textarea": textarea,
    "multiline": textarea,
    "number": number_input,
    "number_input": number_input,
    "checkbox": checkbox,
    "button": button,
    "icon_x": icon_x,
    "icon_close": icon_x,
    "radio": radio_group,
    "radio_group": radio_group,
    "file": file_upload,
    "file_upload": file_upload,
    "upload": file_upload,
    "password": password_input,
    "password_input": password_input,
    "tag": tag_input,
    "tag_input": tag_input,
    "chip": tag_input,
    "richtext": rich_text_editor,
    "rich_text_editor": rich_text_editor,
}


def _parse_bool(val):
    """Parse string boolean values."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.strip().lower()
        if v in ("true", "1", "yes", "on"):
            return True
        if v in ("false", "0", "no", "off"):
            return False
    return None


def _parse_int(val):
    """Parse string int values."""
    if isinstance(val, int):
        return val
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Generate pre-filled field test case skeleton from metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_field_skeleton.py --field "Tên SLA" --type textbox --maxLength 100 --required true
  python generate_field_skeleton.py --field "Ngày hiệu lực" --type datepicker --constraint ">= ngày hiện tại"
  python generate_field_skeleton.py --field "Loại" --type combobox --apiEndpoint "/api/types" --isSingleSelect true
  python generate_field_skeleton.py --field "Trạng thái" --type simple_dropdown --values "A,B,C"
        """
    )
    parser.add_argument("--field", required=True, help="Field display name")
    parser.add_argument("--type", required=True,
                        choices=list(TEMPLATES.keys()),
                        help="Field type (determines which template to use)")
    parser.add_argument("--maxLength", type=int, default=None,
                        help="Maximum length (for textbox/textarea)")
    parser.add_argument("--minLength", type=int, default=None,
                        help="Minimum length (for textbox/textarea/password)")
    parser.add_argument("--maxValue", type=int, default=None,
                        help="Maximum numeric value (for number input)")
    parser.add_argument("--minValue", type=int, default=None,
                        help="Minimum numeric value (for number input)")
    parser.add_argument("--maxTags", type=int, default=None,
                        help="Maximum number of tags (for tag input)")
    parser.add_argument("--maxSize", type=str, default=None,
                        help="Maximum file size (e.g. '5MB', '2GB')")
    parser.add_argument("--allowedFormats", type=str, default=None,
                        help="Allowed file formats (e.g. 'pdf,docx,xlsx')")
    parser.add_argument("--values", type=str, default=None,
                        help="Comma-separated list of values (for simple_dropdown)")
    parser.add_argument("--placeholder", type=str, default=None,
                        help="Placeholder text")
    parser.add_argument("--apiEndpoint", type=str, default=None,
                        help="API endpoint URL (for combobox)")
    parser.add_argument("--constraint", type=str, default=None,
                        help="Business constraint (e.g. '>= ngày hiện tại')")
    parser.add_argument("--defaultValue", type=str, default=None,
                        help="Default value")
    parser.add_argument("--searchDescription", type=str, default=None,
                        help="Description for partial search (textbox)")
    parser.add_argument("--conditionalDisabled", type=str, default=None,
                        help="Condition for disabled state")
    parser.add_argument("--isSingleSelect", type=str, default="true",
                        help="Single select mode (true/false)")
    parser.add_argument("--isRequired", type=str, default="false",
                        help="Field is required (true/false)")
    parser.add_argument("--allowSpaces", type=str, default="true",
                        help="Allow spaces in text (true/false)")
    parser.add_argument("--allowSpecialChars", type=str, default="true",
                        help="Allow special characters (true/false)")
    parser.add_argument("--allowDecimal", type=str, default="false",
                        help="Allow decimal numbers (true/false)")
    parser.add_argument("--hasPermission", type=str, default="true",
                        help="User has permission to use this field (true/false)")

    args = parser.parse_args()

    # Normalize type
    ftype = args.type.lower()

    # Build kwargs dict
    kwargs = {
        "max_length": args.maxLength,
        "min_length": args.minLength,
        "max_value": args.maxValue,
        "min_value": args.minValue,
        "max_tags": args.maxTags,
        "max_size": args.maxSize,
        "allowed_formats": args.allowedFormats,
        "values": args.values,
        "placeholder": args.placeholder,
        "api_endpoint": args.apiEndpoint,
        "constraint": args.constraint,
        "default_value": args.defaultValue,
        "search_description": args.searchDescription,
        "conditional_disabled": args.conditionalDisabled,
        "is_single_select": _parse_bool(args.isSingleSelect),
        "required": _parse_bool(args.isRequired),
        "allow_spaces": _parse_bool(args.allowSpaces),
        "allow_special_chars": _parse_bool(args.allowSpecialChars),
        "allow_decimal": _parse_bool(args.allowDecimal),
        "has_permission": _parse_bool(args.hasPermission),
    }

    # Get template function
    template_fn = TEMPLATES.get(ftype, textbox)

    # Generate output
    try:
        output = template_fn(args.field, **kwargs)
        print(output)
    except Exception as e:
        print(f"# ERROR generating skeleton for field '{args.field}' ({ftype})", file=sys.stderr)
        print(f"# {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

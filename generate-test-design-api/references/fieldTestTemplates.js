/**
 * Field Test Templates - Hardcoded templates for comprehensive test coverage
 *
 * These templates ensure ALL test cases are included for each field type.
 * LLM only needs to adjust behavior based on RSD constraints.
 */

/**
 * Get example date string for a given format
 */
function getDateExample(format) {
  const examples = {
    'dd/MM/yyyy': '25/12/2024',
    'yyyy-MM-dd': '2024-12-25',
    'MM/dd/yyyy': '12/25/2024',
    'dd-MM-yyyy': '25-12-2024',
    'yyyy/MM/dd': '2024/12/25',
  }
  return examples[format] || '25/12/2024'
}

/**
 * Get a "wrong format" description for a given date format
 */
function getWrongDateFormatExample(format) {
  const examples = {
    'dd/MM/yyyy': 'yyyy/dd/MM thay vì dd/MM/yyyy',
    'yyyy-MM-dd': 'dd-MM-yyyy thay vì yyyy-MM-dd',
    'MM/dd/yyyy': 'yyyy/dd/MM thay vì MM/dd/yyyy',
    'dd-MM-yyyy': 'yyyy/dd/MM thay vì dd-MM-yyyy',
    'yyyy/MM/dd': 'dd/MM/yyyy thay vì yyyy/MM/dd',
  }
  return examples[format] || `sai định dạng ${format}`
}

/**
 * Generate comprehensive test cases for a STRING field
 */
export function generateStringFieldTests(fieldName, isRequired, maxLength = null) {
  const requiredCases = isRequired ? `
#### Để trống

#### Không truyền

#### Truyền null
` : `
#### Để trống

#### Không truyền

#### Truyền null
`

  const maxLengthCases = maxLength ? `
#### Truyền ${fieldName} = ${maxLength - 1} ký tự hợp lệ

#### Truyền ${fieldName} = ${maxLength} ký tự hợp lệ

#### Truyền ${fieldName} = ${maxLength + 1} ký tự hợp lệ
` : ''

  return `### ${fieldName} : String${isRequired ? ' (Required)' : ' (Optional)'}
${requiredCases}
${maxLengthCases}
#### Truyền ${fieldName} là ký tự số

#### Truyền ${fieldName} là chữ (thường/hoa) không dấu

#### Truyền ${fieldName} là chữ (thường/hoa) có dấu

#### Truyền ${fieldName} là ký tự đặc biệt

#### Truyền ${fieldName} là all space

#### Truyền ${fieldName} có space ở giữa

#### Truyền ${fieldName} có space đầu/cuối

#### Truyền ${fieldName} là XSS (VD: <script>alert(1)</script>)

#### Truyền ${fieldName} là SQL Injection (VD: ' OR 1=1 --)

#### Truyền ${fieldName} là object

#### Truyền ${fieldName} là mảng
`
}

/**
 * Generate comprehensive test cases for a NUMBER/INTEGER field
 */
export function generateNumberFieldTests(fieldName, isRequired, type = 'Integer') {
  const requiredCases = isRequired ? `
#### Để trống

#### Không truyền

#### Truyền null
` : `
#### Để trống

#### Không truyền

#### Truyền null
`

  return `### ${fieldName} : ${type}${isRequired ? ' (Required)' : ' (Optional)'}
${requiredCases}
#### Truyền ${fieldName} là số âm

#### Truyền ${fieldName} là số thập phân (VD: 1.5)

#### Truyền ${fieldName} là số có leading zero (VD: 00123)

#### Truyền ${fieldName} là số rất lớn vượt giới hạn ${type}

#### Truyền ${fieldName} là chuỗi ký tự (VD: "abc")

#### Truyền ${fieldName} là chuỗi chữ lẫn số (VD: "10abc000")

#### Truyền ${fieldName} là ký tự đặc biệt (VD: @#$%, *, -, +)

#### Truyền ${fieldName} là all space

#### Truyền ${fieldName} có space đầu/cuối (VD: " 123 ", "123 ")

#### Truyền ${fieldName} là boolean (true/false)

#### Truyền ${fieldName} là XSS (VD: <script>alert(1)</script>)

#### Truyền ${fieldName} là SQL Injection (VD: ' OR 1=1 --)

#### Truyền ${fieldName} là object

#### Truyền ${fieldName} là mảng
`
}

/**
 * Generate comprehensive test cases for a DATE field
 * @param {string} fieldName - Field name
 * @param {boolean} isRequired - Whether field is required
 * @param {Object} constraints - Optional constraints from RSD/PTTK
 *   - allowPastDate: boolean (default: true) - e.g. false for bookingDate
 *   - allowFutureDate: boolean (default: true) - e.g. false for birthDate
 *   - allowCurrentDate: boolean (default: true)
 */
export function generateDateFieldTests(fieldName, isRequired, constraints = {}, dateFormat = 'dd/MM/yyyy') {
  const { allowPastDate = true, allowFutureDate = true, allowCurrentDate = true } = constraints
  const dateExample = getDateExample(dateFormat)
  const wrongFormatExample = getWrongDateFormatExample(dateFormat)

  const requiredCases = isRequired ? `
#### Để trống

#### Không truyền

#### Truyền null
` : `
#### Để trống

#### Không truyền

#### Truyền null
`

  // Build date-related test cases based on constraints
  const dateCases = `#### Truyền ${fieldName} đúng định dạng ${dateFormat} (VD: ${dateExample})

#### Truyền ${fieldName} sai định dạng (VD: ${wrongFormatExample})

#### Truyền ${fieldName} là chuỗi không phải ngày tháng (VD: "abc123")

#### Truyền ${fieldName} là ngày không tồn tại (VD: 30/02/2025, 32/01/2025)
${allowPastDate ? `
#### Truyền ${fieldName} là ngày quá khứ (VD: 01/01/2020)
` : `
#### Truyền ${fieldName} là ngày quá khứ (VD: 01/01/2020) - KHÔNG được phép
`}${allowCurrentDate ? `
#### Truyền ${fieldName} là ngày hiện tại
` : `
#### Truyền ${fieldName} là ngày hiện tại - KHÔNG được phép
`}${allowFutureDate ? `
#### Truyền ${fieldName} là ngày tương lai (VD: 31/12/2099)
` : `
#### Truyền ${fieldName} là ngày tương lai (VD: 31/12/2099) - KHÔNG được phép
`}
#### Truyền ${fieldName} là số nguyên

#### Truyền ${fieldName} là XSS (VD: <script>alert(1)</script>)

#### Truyền ${fieldName} là SQL Injection (VD: ' OR 1=1 --)

#### Truyền ${fieldName} là object

#### Truyền ${fieldName} là mảng
`

  return `### ${fieldName} : Date${isRequired ? ' (Required)' : ' (Optional)'}
${requiredCases}
${dateCases}`
}

/**
 * Generate comprehensive test cases for a DATETIME field (Date + Time)
 * @param {string} fieldName - Field name
 * @param {boolean} isRequired - Whether field is required
 * @param {Object} constraints - Optional constraints from RSD/PTTK
 *   - allowPastDateTime: boolean (default: true) - e.g. false for booking time
 *   - allowFutureDateTime: boolean (default: true) - e.g. false for createdTime
 *   - allowCurrentDateTime: boolean (default: true)
 */
export function generateDateTimeFieldTests(fieldName, isRequired, constraints = {}, dateFormat = 'dd/MM/yyyy HH:mm:ss') {
  const { allowPastDateTime = true, allowFutureDateTime = true, allowCurrentDateTime = true } = constraints
  const dateExample = getDateExample(dateFormat.split(' ')[0]) + (dateFormat.includes('HH') ? ' 14:30:45' : '')
  const wrongFormatExample = getWrongDateFormatExample(dateFormat.split(' ')[0]) + (dateFormat.includes('HH') ? ' HH:mm:ss' : '')
  const requiredCases = isRequired ? `
#### Để trống

#### Không truyền

#### Truyền null
` : `
#### Để trống

#### Không truyền

#### Truyền null
`

  return `### ${fieldName} : DateTime${isRequired ? ' (Required)' : ' (Optional)'}
${requiredCases}
#### Truyền ${fieldName} đúng định dạng ${dateFormat} (VD: ${dateExample})

#### Truyền ${fieldName} sai định dạng ngày (VD: ${wrongFormatExample})

#### Truyền ${fieldName} sai định dạng giờ (VD: 25/12/2024 25:70:90)

#### Truyền ${fieldName} chỉ có ngày không có giờ (VD: 25/12/2024)

#### Truyền ${fieldName} là chuỗi không phải ngày giờ (VD: "abc123")

#### Truyền ${fieldName} là ngày không tồn tại (VD: 30/02/2025 14:30:45, 32/01/2025 00:00:00)

#### Truyền ${fieldName} là ngày giờ quá khứ (VD: 01/01/2020 10:00:00)${allowPastDateTime ? '' : ' - KHÔNG được phép'}

#### Truyền ${fieldName} là ngày giờ hiện tại${allowCurrentDateTime ? '' : ' - KHÔNG được phép'}

#### Truyền ${fieldName} là ngày giờ tương lai (VD: 31/12/2099 23:59:59)${allowFutureDateTime ? '' : ' - KHÔNG được phép'}

#### Truyền ${fieldName} là số nguyên

#### Truyền ${fieldName} là XSS (VD: <script>alert(1)</script>)

#### Truyền ${fieldName} là SQL Injection (VD: ' OR 1=1 --)

#### Truyền ${fieldName} là object

#### Truyền ${fieldName} là mảng
`
}

/**
 * Generate comprehensive test cases for an ARRAY field (with object items)
 * @param {string} fieldName - Field name
 * @param {boolean} isRequired - Whether field is required
 * @param {string[]} childFieldNames - Names of child fields inside the array items
 */
export function generateArrayFieldTests(fieldName, isRequired, childFieldNames = []) {
  const childNamesStr = childFieldNames.length > 0
    ? ` (gồm các trường: ${childFieldNames.join(', ')})`
    : ''

  const requiredCases = isRequired ? `
#### Không truyền

#### Truyền null
` : `
#### Không truyền

#### Truyền null
`

  return `### ${fieldName} : Array${isRequired ? ' (Required)' : ' (Optional)'}${childNamesStr}
${requiredCases}
#### Truyền ${fieldName} là mảng rỗng []

#### Truyền ${fieldName} chứa phần tử rỗng (VD: [{}])

#### Truyền ${fieldName} là string thay vì array

#### Truyền ${fieldName} là number thay vì array

#### Truyền ${fieldName} là object thay vì array

#### Truyền ${fieldName} là boolean thay vì array

#### Truyền ${fieldName} là XSS (VD: <script>alert(1)</script>)

#### Truyền ${fieldName} là SQL Injection (VD: ' OR 1=1 --)
`
}

/**
 * Generate comprehensive test cases for a MULTIPART FILE field (file upload API)
 * @param {string} fieldName - Field name (e.g., "file")
 * @param {boolean} isRequired - Whether field is required
 * @param {Object} constraints - Optional constraints from RSD/PTTK
 *   - allowedExtensions: string[] (e.g., [".xls", ".xlsx"])
 *   - maxFileSizeMB: number (e.g., 10 for 10MB)
 *   - maxRecords: number (max rows in file)
 *   - allowedChars: string[] (allowed filename characters)
 *   - allowDuplicate: boolean (whether duplicate filename is allowed)
 */
export function generateMultipartFileFieldTests(fieldName, isRequired, constraints = {}) {
  const {
    allowedExtensions = ['.xls', '.xlsx'],
    maxFileSizeMB = null,
    maxRecords = null,
    allowedChars = ['a-z', 'A-Z', '0-9', ' ', '_', '-', '.', '(', ')'],
    allowDuplicate = false,
  } = constraints

  // File format extension group (from allowedExtensions)
  const validExt = allowedExtensions[0] || '.xlsx'
  const validExt2 = allowedExtensions[1] || validExt
  // A non-allowed extension (for format test)
  const invalidExt = '.pdf'

  // Build extension cases
  const extensionCases = allowedExtensions.length >= 2
    ? `#### Truyền file có định dạng hợp lệ ${validExt} (VD: file_hop_le${validExt})

#### Truyền file có định dạng hợp lệ ${validExt2} (VD: file_hop_le${validExt2})

#### Truyền file có định dạng không hợp lệ ${invalidExt} → error`
    : `#### Truyền file có định dạng hợp lệ ${validExt} (VD: file_hop_le${validExt})

#### Truyền file có định dạng không hợp lệ ${invalidExt} → error`

  const requiredCases = isRequired ? `
#### Để trống field file (body: "${fieldName}": "")
#### Không truyền field file (body rỗng)
#### Truyền ${fieldName} = null` : `
#### Không truyền field file (body rỗng)
#### Truyền ${fieldName} = null`

  const sizeCases = maxFileSizeMB
    ? `#### Truyền file vượt dung lượng tối đa (> ${maxFileSizeMB}MB)`
    : ''

  const recordCases = maxRecords
    ? `#### Truyền file vượt số bản ghi tối đa (> ${maxRecords} bản ghi)`
    : ''

  const allowedCharsStr = allowedChars.length > 0
    ? `#### Truyền file có tên chứa ký tự đặc biệt không thuộc danh sách cho phép (VD: file!@#name${validExt})`
    : ''

  const duplicateCases = !allowDuplicate
    ? `#### Truyền file trùng tên với file ở trạng thái Đang kiểm tra của cùng CIF
#### Truyền file trùng tên với file ở trạng thái Đã kiểm tra của cùng CIF
#### Truyền file trùng tên với file ở trạng thái Đã đẩy duyệt của cùng CIF
#### Truyền file trùng tên với file có lỗi kiểm tra của cùng CIF`
    : ''

  return `### ${fieldName} : MultipartFile${isRequired ? ' (Required)' : ' (Optional)'}
${requiredCases}
#### Truyền file rỗng (0 byte)
${extensionCases}
${sizeCases}
${recordCases}
${allowedCharsStr}
#### Truyền file có tên chứa khoảng trắng (VD: file name${validExt})
#### Truyền file có tên chứa dấu tiếng Việt (VD: file_tên_${validExt})
${duplicateCases}
#### Truyền file không đúng template/mẫu (thiếu cột bắt buộc)`
}

export default {
  generateStringFieldTests,
  generateNumberFieldTests,
  generateDateFieldTests,
  generateDateTimeFieldTests,
  generateArrayFieldTests,
  generateMultipartFileFieldTests,
}

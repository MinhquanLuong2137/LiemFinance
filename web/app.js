"use strict";

const state = {
  transactions: [],
  visibleTransactions: [],
  dashboardReport: null,
  chartReport: null,
  expandedRows: new Set(),
  showAllTransactions: false,
  editingId: null,
  requestId: 0,
  language: getPreference("liemfinance-language", "vi") === "en" ? "en" : "vi",
  theme: getPreference("liemfinance-theme", "light") === "dark" ? "dark" : "light"
};
const byId = (id) => document.getElementById(id);
let currency = new Intl.NumberFormat(state.language === "en" ? "en-US" : "vi-VN", {
  style: "currency",
  currency: "VND",
  maximumFractionDigits: 0
});
let compactCurrency = new Intl.NumberFormat(state.language === "en" ? "en-US" : "vi-VN", {
  notation: "compact",
  maximumFractionDigits: 1
});

const messages = {
  vi: {
    brandHome: "LiemFinance trang chủ",
    localData: "Dữ liệu lưu trên thiết bị", dashboardEyebrow: "TỔNG QUAN TÀI CHÍNH",
    welcomeTitle: "Chào bạn", welcomeCopy: "Quản lý tài chính, quản lý tương lai.",
    refresh: "Làm mới", overview: "Tổng quan thu chi", totalIncome: "Tổng thu nhập",
    allIncome: "Tổng các khoản thu", totalExpense: "Tổng chi tiêu", allExpense: "Tổng các khoản chi",
    balance: "Số dư còn lại", balanceCaption: "Thu nhập trừ chi tiêu",
    reportEyebrow: "BÁO CÁO THU / CHI", reportTitle: "Tổng hợp theo thời gian",
    autoUpdated: "Cập nhật tự động", loadingReport: "Đang tải báo cáo...",
    visualStats: "Thống kê trực quan", dailyCashFlow: "DÒNG TIỀN HẰNG NGÀY",
    chartTitle: "Thu chi trong 30 ngày gần nhất", thirtyDays: "30 ngày",
    chartDailyTitle: "Thu chi theo ngày · 30 ngày gần nhất",
    chartWeeklyTitle: "Thu chi theo tuần · 12 tuần gần nhất",
    chartMonthlyTitle: "Thu chi theo tháng · 12 tháng gần nhất",
    chartYearlyTitle: "Thu chi theo năm", chartAllTitle: "Thu chi toàn bộ lịch sử",
    chartAria: "Biểu đồ cột ngang thu chi theo ngày trong 30 ngày gần nhất",
    allocation: "PHÂN BỔ", cashFlowComposition: "Cơ cấu dòng tiền",
    transactions: "Tổng giao dịch", record: "GHI NHẬN", addTransaction: "Thêm giao dịch",
    transactionType: "Loại giao dịch", expense: "Chi tiêu", income: "Thu nhập",
    amount: "Số tiền", transactionName: "Tên giao dịch",
    namePlaceholder: "Ví dụ: Ăn uống, Lương...", transactionDate: "Ngày giao dịch",
    note: "Ghi chú", optional: "(không bắt buộc)", notePlaceholder: "Thêm ghi chú...",
    cancelEdit: "Hủy sửa", saveTransaction: "Lưu giao dịch", updateTransaction: "Cập nhật giao dịch",
    editTransaction: "Sửa giao dịch",
    ledger: "SỔ GIAO DỊCH", history: "Lịch sử giao dịch",
    searchPlaceholder: "Tìm giao dịch...", filterType: "Lọc theo loại",
    allTypes: "Tất cả loại", time: "Thời gian", allTime: "Toàn bộ thời gian",
    specificDay: "Ngày cụ thể", currentWeek: "Tuần hiện tại", currentMonth: "Tháng hiện tại",
    customRange: "Khoảng tùy chọn", date: "Ngày", fromDate: "Từ ngày", toDate: "Đến",
    sort: "Sắp xếp", newestFirst: "Ngày mới nhất", amountAscending: "Số tiền tăng dần",
    amountDescending: "Số tiền giảm dần", topSpending: "Top chi tiêu",
    showItemDetails: "Hiển thị chi tiết món hàng", expandAll: "Mở rộng tất cả",
    collapseAll: "Thu gọn tất cả", transactionCategory: "Giao dịch / Hạng mục",
    type: "Loại", actions: "Thao tác", noTransactions: "Chưa có giao dịch phù hợp",
    adjustFilters: "Thử thay đổi bộ lọc hoặc thêm giao dịch mới.",
    localStorageNote: "Giao dịch được lưu cục bộ trong", incomeTotal: "Thu nhập",
    expenseTotal: "Chi tiêu", incomeShort: "Thu", expenseShort: "Chi",
    amountAxis: "Số tiền (VND)", noNote: "Không có ghi chú", transactionId: "Mã giao dịch",
    itemDetails: "Chi tiết món hàng", transactionCount: (count) => `${count} giao dịch trong dữ liệu hiện có`,
    countTransactions: (count) => `${count} giao dịch`, countCategories: (count) => `${count} hạng mục`,
    showingTransactions: (shown, total) => `Đang hiển thị ${shown} / ${total}`,
    countExpenseTransactions: (count) => `${count} giao dịch chi tiêu`,
    today: "Hôm nay", last7: "7 ngày gần nhất", last30: "1 tháng gần nhất",
    last365: "1 năm gần nhất", totalIncomeShort: "Tổng thu", totalExpenseShort: "Tổng chi",
    allTimeLabel: "Mọi thời điểm", expandDetails: "Mở rộng chi tiết",
    collapseDetails: "Thu gọn chi tiết", edit: "Sửa", delete: "Xóa",
    deleteConfirm: (name) => `Bạn có chắc muốn xóa giao dịch "${name}"?`,
    added: "Đã thêm giao dịch.", updated: "Đã cập nhật giao dịch.",
    deleted: "Đã xóa giao dịch.", serverInvalid: "Máy chủ trả về dữ liệu không hợp lệ.",
    requestFailed: "Không thể hoàn tất thao tác.", themeLight: "Sáng", themeDark: "Tối",
    switchToLight: "Chuyển sang giao diện sáng", switchToDark: "Chuyển sang giao diện tối",
    switchToEnglish: "Switch language to English", switchToVietnamese: "Chuyển sang Tiếng Việt",
    preferenceNotSaved: "Không thể lưu tùy chọn trên trình duyệt này.",
    loadTransactionsError: "Không thể đọc dữ liệu giao dịch.",
    reportError: "Không thể tạo báo cáo thu chi.",
    invalidTypeFilter: "Bộ lọc loại giao dịch không hợp lệ.",
    invalidPeriod: "Bộ lọc thời gian không hợp lệ.",
    invalidSort: "Thứ tự sắp xếp không hợp lệ.",
    invalidDay: "Ngày lọc phải theo định dạng YYYY-MM-DD.",
    invalidRange: "Khoảng thời gian cần có ngày bắt đầu và kết thúc hợp lệ.",
    reversedRange: "Ngày bắt đầu không thể sau ngày kết thúc.",
    itemLabel: "Món hàng", noMatchingSearch: "Không tìm thấy giao dịch phù hợp.",
    invalidData: "Dữ liệu giao dịch không hợp lệ.", invalidType: "Loại giao dịch không hợp lệ.",
    invalidAmount: "Số tiền phải là số hợp lệ lớn hơn 0.",
    emptyName: "Tên giao dịch không được để trống.",
    invalidDate: "Ngày giao dịch không hợp lệ.",
    expiredDate: "Không thể lưu giao dịch cũ hơn 365 ngày.",
    missingTransaction: "Không tìm thấy giao dịch.",
    saveError: "Không thể lưu giao dịch.", updateError: "Không thể cập nhật giao dịch.",
    deleteError: "Không thể xóa giao dịch.",
    chartPeriod: "Gom theo", chartDaily: "Theo ngày · 30 ngày",
    chartWeekly: "Theo tuần · 12 tuần", chartMonthly: "Theo tháng · 12 tháng",
    chartYearly: "Theo năm", chartAll: "Tất cả",
    topPeriod: "Thời gian Top", thisWeek: "Tuần này", thisMonth: "Tháng này",
    thisYear: "Năm nay", showAllTransactions: (count) => `Xem tất cả giao dịch (${count})`,
    collapseTransactions: "Thu gọn", shutdown: "Tắt ứng dụng",
    exit: "Thoát", shutdownConfirm: "Bạn có chắc chắn muốn thoát ứng dụng không?",
    shuttingDown: "Đang tắt ứng dụng...", shutdownFailed: "Không thể tắt máy chủ ứng dụng."
  },
  en: {
    brandHome: "LiemFinance home",
    localData: "Data stored on this device", dashboardEyebrow: "FINANCIAL OVERVIEW",
    welcomeTitle: "Welcome", welcomeCopy: "Manage your money, shape your future.",
    refresh: "Refresh", overview: "Income and expense overview", totalIncome: "Total income",
    allIncome: "All income", totalExpense: "Total expenses", allExpense: "All expenses",
    balance: "Current balance", balanceCaption: "Income minus expenses",
    reportEyebrow: "INCOME / EXPENSE REPORT", reportTitle: "Summary by period",
    autoUpdated: "Updated automatically", loadingReport: "Loading report...",
    visualStats: "Visual statistics", dailyCashFlow: "DAILY CASH FLOW",
    chartTitle: "Income and expenses over the last 30 days", thirtyDays: "30 days",
    chartDailyTitle: "Daily income and expenses · last 30 days",
    chartWeeklyTitle: "Weekly income and expenses · last 12 weeks",
    chartMonthlyTitle: "Monthly income and expenses · last 12 months",
    chartYearlyTitle: "Yearly income and expenses", chartAllTitle: "Income and expenses · all history",
    chartAria: "Horizontal bar chart of daily income and expenses for the last 30 days",
    allocation: "BREAKDOWN", cashFlowComposition: "Cash flow composition",
    transactions: "Transactions", record: "RECORD", addTransaction: "Add transaction",
    transactionType: "Transaction type", expense: "Expense", income: "Income",
    amount: "Amount", transactionName: "Transaction name",
    namePlaceholder: "E.g. Groceries, Salary...", transactionDate: "Transaction date",
    note: "Note", optional: "(optional)", notePlaceholder: "Add a note...",
    cancelEdit: "Cancel edit", saveTransaction: "Save transaction", updateTransaction: "Update transaction",
    editTransaction: "Edit transaction",
    ledger: "LEDGER", history: "Transaction history",
    searchPlaceholder: "Search transactions...", filterType: "Filter by type",
    allTypes: "All types", time: "Period", allTime: "All time",
    specificDay: "Specific day", currentWeek: "Current week", currentMonth: "Current month",
    customRange: "Custom range", date: "Date", fromDate: "From", toDate: "To",
    sort: "Sort", newestFirst: "Newest first", amountAscending: "Amount: low to high",
    amountDescending: "Amount: high to low", topSpending: "Top spending",
    showItemDetails: "Show item details", expandAll: "Expand all",
    collapseAll: "Collapse all", transactionCategory: "Transaction / Category",
    type: "Type", actions: "Actions", noTransactions: "No matching transactions",
    adjustFilters: "Try adjusting the filters or add a new transaction.",
    localStorageNote: "Transactions are stored locally in", incomeTotal: "Income",
    expenseTotal: "Expenses", incomeShort: "Income", expenseShort: "Expense",
    amountAxis: "Amount (VND)", noNote: "No note", transactionId: "Transaction ID",
    itemDetails: "Item details", transactionCount: (count) => `${count} transactions in current data`,
    countTransactions: (count) => `${count} transactions`, countCategories: (count) => `${count} categories`,
    showingTransactions: (shown, total) => `Showing ${shown} of ${total}`,
    countExpenseTransactions: (count) => `${count} expense transactions`,
    today: "Today", last7: "Last 7 days", last30: "Last 30 days",
    last365: "Last 365 days", totalIncomeShort: "Total income", totalExpenseShort: "Total expenses",
    allTimeLabel: "All time", expandDetails: "Expand details",
    collapseDetails: "Collapse details", edit: "Edit", delete: "Delete",
    deleteConfirm: (name) => `Are you sure you want to delete "${name}"?`,
    added: "Transaction added.", updated: "Transaction updated.",
    deleted: "Transaction deleted.", serverInvalid: "The server returned invalid data.",
    requestFailed: "Unable to complete the request.", themeLight: "Light", themeDark: "Dark",
    switchToLight: "Switch to light theme", switchToDark: "Switch to dark theme",
    switchToEnglish: "Switch language to English", switchToVietnamese: "Switch to Vietnamese",
    preferenceNotSaved: "This browser could not save your preference.",
    loadTransactionsError: "Unable to read transaction data.",
    reportError: "Unable to create the income and expense report.",
    invalidTypeFilter: "Invalid transaction type filter.",
    invalidPeriod: "Invalid time period filter.",
    invalidSort: "Invalid sort order.",
    invalidDay: "The date filter must use YYYY-MM-DD.",
    invalidRange: "Enter a valid start and end date for the range.",
    reversedRange: "The start date cannot be later than the end date.",
    itemLabel: "Item", noMatchingSearch: "No matching transactions found.",
    invalidData: "Invalid transaction data.", invalidType: "Invalid transaction type.",
    invalidAmount: "Amount must be a valid number greater than zero.",
    emptyName: "Transaction name cannot be empty.",
    invalidDate: "Invalid transaction date.",
    expiredDate: "Transactions older than 365 days cannot be saved.",
    missingTransaction: "Transaction not found.",
    saveError: "Unable to save the transaction.", updateError: "Unable to update the transaction.",
    deleteError: "Unable to delete the transaction.",
    chartPeriod: "Group by", chartDaily: "By day · 30 days",
    chartWeekly: "By week · 12 weeks", chartMonthly: "By month · 12 months",
    chartYearly: "By year", chartAll: "All",
    topPeriod: "Top period", thisWeek: "This week", thisMonth: "This month",
    thisYear: "This year", showAllTransactions: (count) => `Show all transactions (${count})`,
    collapseTransactions: "Show fewer", shutdown: "Exit application",
    exit: "Exit", shutdownConfirm: "Are you sure you want to exit the application?",
    shuttingDown: "Shutting down the application...", shutdownFailed: "Unable to stop the application server."
  }
};

function t(key, ...args) {
  const value = messages[state.language][key];
  return typeof value === "function" ? value(...args) : (value || key);
}

function translatedError(message) {
  const knownErrors = [
    ["Không thể đọc dữ liệu giao dịch:", "loadTransactionsError"],
    ["Không thể tạo báo cáo thu chi:", "reportError"],
    ["Bộ lọc loại giao dịch không hợp lệ.", "invalidTypeFilter"],
    ["Bộ lọc thời gian không hợp lệ.", "invalidPeriod"],
    ["Thứ tự sắp xếp không hợp lệ.", "invalidSort"],
    ["Ngày lọc phải theo định dạng YYYY-MM-DD.", "invalidDay"],
    ["Khoảng thời gian cần có ngày bắt đầu và kết thúc hợp lệ.", "invalidRange"],
    ["Ngày bắt đầu không thể sau ngày kết thúc.", "reversedRange"],
    ["Nội dung giao dịch phải là một đối tượng JSON.", "invalidData"],
    ["Loại giao dịch chỉ có thể là expense hoặc income.", "invalidType"],
    ["Tên giao dịch không được để trống.", "emptyName"],
    ["Số tiền không hợp lệ.", "invalidAmount"],
    ["Số tiền phải lớn hơn 0.", "invalidAmount"],
    ["Ngày giao dịch phải theo định dạng YYYY-MM-DD.", "invalidDate"],
    ["Ngày giao dịch không hợp lệ.", "invalidDate"],
    ["Không thể lưu giao dịch cũ hơn 365 ngày.", "expiredDate"],
    ["Không tìm thấy giao dịch.", "missingTransaction"],
    ["Không thể hoàn tất thao tác.", "requestFailed"]
  ];
  if (state.language === "en") {
    const match = knownErrors.find(([vietnamese]) => message.includes(vietnamese));
    if (match) return t(match[1]);
  }
  return message;
}

function applyTranslations() {
  document.documentElement.lang = state.language;
  document.title = state.language === "en"
    ? "LiemFinance — Personal Finance"
    : "LiemFinance — Quản lý tài chính";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAriaLabel));
  });
  byId("language-toggle-label").textContent = state.language === "vi" ? "EN" : "VI";
  byId("language-toggle").setAttribute("aria-label",
    state.language === "vi" ? t("switchToEnglish") : t("switchToVietnamese"));
  byId("theme-toggle-label").textContent = t(state.theme === "light" ? "themeDark" : "themeLight");
  byId("theme-toggle").setAttribute("aria-label",
    t(state.theme === "light" ? "switchToDark" : "switchToLight"));
  byId("theme-toggle").setAttribute("aria-pressed", String(state.theme === "dark"));
  byId("theme-toggle").querySelector(".theme-toggle-icon").textContent =
    state.theme === "light" ? "☾" : "☀";
  currency = new Intl.NumberFormat(state.language === "en" ? "en-US" : "vi-VN", {
    style: "currency", currency: "VND", maximumFractionDigits: 0
  });
  compactCurrency = new Intl.NumberFormat(state.language === "en" ? "en-US" : "vi-VN", {
    notation: "compact", maximumFractionDigits: 1
  });
  byId("today-label").textContent = new Intl.DateTimeFormat(
    state.language === "en" ? "en-US" : "vi-VN",
    { weekday: "long", day: "2-digit", month: "long", year: "numeric" }
  ).format(new Date());
  if (state.editingId) {
    byId("form-title").textContent = t("editTransaction");
    byId("submit-button").textContent = t("updateTransaction");
    byId("cancel-edit").textContent = t("cancelEdit");
  } else {
    byId("form-title").textContent = t("addTransaction");
    byId("submit-button").innerHTML = `<span>${t("saveTransaction")}</span> <span aria-hidden="true">→</span>`;
  }
  if (state.dashboardReport) {
    renderSummary();
    renderPeriodReports();
    renderHorizontalChart();
    renderHistory();
  }
  updateShowMoreButton();
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  document.documentElement.style.colorScheme = state.theme;
}

function getPreference(key, fallback) {
  try {
    return localStorage.getItem(key) || fallback;
  } catch (error) {
    return fallback;
  }
}

function savePreference(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    showToast(t("preferenceNotSaved"), true);
  }

}

function localDateString(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatDate(value) {
  const parts = value.split("-");
  if (parts.length !== 3) return value;
  const date = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]), 12);
  return new Intl.DateTimeFormat(state.language === "en" ? "en-US" : "vi-VN").format(date);
}

function normalizeSearch(value) {
  return String(value || "")
    .replace(/đ/g, "d")
    .replace(/Đ/g, "D")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("vi")
    .replace(/\s+/g, " ")
    .trim();
}

function showToast(message, isError) {
  const toast = byId("toast");
  toast.textContent = translatedError(message);
  toast.classList.toggle("is-error", Boolean(isError));
  toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("is-visible"), 3200);
}

async function request(path, options) {
  const response = await fetch(path, options);
  let payload;
  try {
    payload = await response.json();
  } catch (error) {
    throw new Error(t("serverInvalid"));
  }
  if (!response.ok) throw new Error(payload.error || t("requestFailed"));
  return payload;
}

async function loadTransactions() {
  const requestId = ++state.requestId;
  const filters = new URLSearchParams();
  const keyword = byId("search").value.trim();
  const type = byId("type-filter").value;
  const period = byId("period-filter").value;
  const topSpending = byId("sort-filter").value === "top_spending";
  if (topSpending) filters.set("period", byId("top-period-filter").value);
  if (keyword) filters.set("q", keyword);
  if (!topSpending && type !== "all") filters.set("type", type);
  if (!topSpending) {
    filters.set("period", period);
    if (period === "day") filters.set("date", byId("specific-date").value);
    if (period === "custom") {
      filters.set("from", byId("date-from").value);
      filters.set("to", byId("date-to").value);
    }
    const sort = byId("sort-filter").value;
    if (sort !== "top_spending") filters.set("sort", sort);
  }
  const query = filters.toString();
  const endpoint = topSpending ? "/api/transactions/top-spending" : "/api/transactions";
  const chartPeriod = byId("chart-period-filter").value;
  try {
    const [transactions, visibleTransactions, dashboardReport, chartReport] = await Promise.all([
      request("/api/transactions"),
      request(`${endpoint}${query ? `?${query}` : ""}`),
      request("/api/reports/dashboard"),
      request(`/api/reports/chart?period=${encodeURIComponent(chartPeriod)}`)
    ]);
    if (requestId !== state.requestId) return;
    state.transactions = transactions;
    state.visibleTransactions = visibleTransactions;
    state.dashboardReport = dashboardReport;
    state.chartReport = chartReport;
    renderSummary();
    renderPeriodReports();
    renderHorizontalChart();
    renderHistory();
  } catch (error) {
    if (requestId === state.requestId) showToast(error.message, true);
  }
}

function renderSummary() {
  const income = state.transactions
    .filter((item) => item.type === "income")
    .reduce((sum, item) => sum + Number(item.amount), 0);
  const expense = state.transactions
    .filter((item) => item.type !== "income")
    .reduce((sum, item) => sum + Number(item.amount), 0);
  const balance = income - expense;
  byId("total-income").textContent = currency.format(income);
  byId("total-expense").textContent = currency.format(expense);
  byId("total-balance").textContent = currency.format(balance);
  byId("total-balance").classList.toggle("negative", balance < 0);

  const sum = income + expense;
  const incomePercent = sum ? income / sum * 100 : 50;
  byId("money-donut").style.background =
    `conic-gradient(#91b69b 0 ${incomePercent}%, #a8424d ${incomePercent}% 100%)`;
  byId("donut-total").textContent = state.transactions.length;
  byId("transaction-count").textContent = t("transactionCount", state.transactions.length);
  byId("composition-legend").replaceChildren();
  [
    { label: t("incomeTotal"), amount: income, color: "#f2b236" },
    { label: t("expenseTotal"), amount: expense, color: "#80121d" }
  ].forEach((entry) => {
    const row = document.createElement("div");
    row.className = "legend-item";
    const dot = document.createElement("i");
    dot.style.background = entry.color;
    const copy = document.createElement("span");
    copy.append(document.createTextNode(entry.label));
    const amount = document.createElement("strong");
    amount.textContent = currency.format(entry.amount);
    copy.append(amount);
    row.append(dot, copy);
    byId("composition-legend").append(row);
  });
}

function renderPeriodReports() {
  const report = state.dashboardReport;
  const container = byId("period-reports");
  container.replaceChildren();
  const periods = [
    { key: "today", label: t("today") },
    { key: "last_7_days", label: t("last7") },
    { key: "last_30_days", label: t("last30") },
    { key: "last_365_days", label: t("last365") }
  ];
  periods.forEach(({ key, label }) => {
    const values = report.periods[key];
    const card = document.createElement("article");
    card.className = "period-report-card";
    const heading = document.createElement("div");
    heading.className = "period-report-heading";
    const title = document.createElement("h3");
    title.textContent = label;
    const range = document.createElement("span");
    range.textContent = key === "today"
      ? formatDate(values.start)
      : `${formatDate(values.start)} – ${formatDate(values.end)}`;
    heading.append(title, range);

    const income = document.createElement("div");
    income.className = "period-report-value income";
    const incomeLabel = document.createElement("span");
    incomeLabel.textContent = t("totalIncomeShort");
    const incomeAmount = document.createElement("strong");
    incomeAmount.textContent = currency.format(values.income);
    income.append(incomeLabel, incomeAmount);

    const expense = document.createElement("div");
    expense.className = "period-report-value expense";
    const expenseLabel = document.createElement("span");
    expenseLabel.textContent = t("totalExpenseShort");
    const expenseAmount = document.createElement("strong");
    expenseAmount.textContent = currency.format(values.expense);
    expense.append(expenseLabel, expenseAmount);
    card.append(heading, income, expense);
    container.append(card);
  });
}

function niceAxisMaximum(value) {
  if (value <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(value));
  const normalized = value / magnitude;
  const step = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10;
  return step * magnitude;
}

function renderHorizontalChart() {
  const days = state.chartReport.points;
  const chart = byId("horizontal-chart");
  const axis = byId("chart-axis");
  const chartTitles = {
    day: "chartDailyTitle",
    week: "chartWeeklyTitle",
    month: "chartMonthlyTitle",
    year: "chartYearlyTitle",
    all: "chartAllTitle"
  };
  document.querySelector(".trend-panel h2[data-i18n='chartTitle']").textContent =
    t(chartTitles[state.chartReport.period] || "chartTitle");
  chart.replaceChildren();
  axis.replaceChildren();
  const largestAmount = Math.max(
    0,
    ...days.flatMap((day) => [Number(day.income), Number(day.expense)])
  );
  const axisMaximum = niceAxisMaximum(largestAmount);
  const axisSteps = 4;

  days.forEach((day) => {
    const row = document.createElement("div");
    row.className = "horizontal-chart-day";
    const date = document.createElement("time");
    date.className = "horizontal-chart-date";
    date.dateTime = day.date;
    date.textContent = formatDate(day.date);
    const bars = document.createElement("div");
    bars.className = "horizontal-chart-bars";
    [
      { label: t("incomeShort"), amount: Number(day.income), className: "income" },
      { label: t("expenseShort"), amount: Number(day.expense), className: "expense" }
    ].forEach((entry) => {
      const line = document.createElement("div");
      line.className = `horizontal-bar-line ${entry.className}`;
      const track = document.createElement("div");
      track.className = "horizontal-bar-track";
      const bar = document.createElement("span");
      bar.className = "horizontal-bar";
      bar.style.width = `${entry.amount ? Math.max(entry.amount / axisMaximum * 100, 1) : 0}%`;
      bar.title = `${entry.label} ${date.textContent}: ${currency.format(entry.amount)}`;
      track.append(bar);
      const amount = document.createElement("span");
      amount.className = "horizontal-bar-value";
      amount.textContent = currency.format(entry.amount);
      line.append(track, amount);
      bars.append(line);
    });
    row.append(date, bars);
    chart.append(row);
  });

  const axisLabel = document.createElement("span");
  axisLabel.className = "chart-axis-title";
  axisLabel.textContent = t("amountAxis");
  const spacer = document.createElement("span");
  spacer.setAttribute("aria-hidden", "true");
  const ticks = document.createElement("div");
  ticks.className = "chart-axis-ticks";
  for (let step = 0; step <= axisSteps; step += 1) {
    const tick = document.createElement("span");
    const amount = axisMaximum * step / axisSteps;
    tick.textContent = `${compactCurrency.format(amount)} ₫`;
    tick.title = currency.format(amount);
    ticks.append(tick);
  }
  axis.append(spacer, ticks, axisLabel);
  chart.style.setProperty("--axis-maximum", String(axisMaximum));
}

function appendItemDetails(container, item) {
  const items = item.items || item.line_items || item.item_details;
  if (!byId("show-items").checked || !items || (!Array.isArray(items) && typeof items !== "string")) {
    return;
  }
  const section = document.createElement("div");
  section.className = "detail-field";
  const label = document.createElement("strong");
  label.textContent = t("itemDetails");
  const list = document.createElement("ul");
  const values = Array.isArray(items) ? items : [items];
  values.forEach((entry) => {
    const row = document.createElement("li");
    if (entry && typeof entry === "object") {
      const name = entry.name || entry.item || entry.title || t("itemLabel");
      const quantity = entry.quantity ? ` × ${entry.quantity}` : "";
      const amount = Number.isFinite(Number(entry.amount))
        ? ` — ${currency.format(Number(entry.amount))}`
        : "";
      row.textContent = `${name}${quantity}${amount}`;
    } else {
      row.textContent = String(entry);
    }
    list.append(row);
  });
  section.append(label, list);
  container.append(section);
}

function createTransactionDetails(item) {
  const details = document.createElement("div");
  details.className = "accordion-details";
  const note = document.createElement("div");
  note.className = "detail-field";
  const noteLabel = document.createElement("strong");
  noteLabel.textContent = t("note");
  const noteText = document.createElement("span");
  noteText.textContent = item.note || t("noNote");
  note.append(noteLabel, noteText);
  const id = document.createElement("div");
  id.className = "detail-field";
  const idLabel = document.createElement("strong");
  idLabel.textContent = t("transactionId");
  const idValue = document.createElement("code");
  idValue.textContent = item.id || "—";
  id.append(idLabel, idValue);
  details.append(note, id);
  appendItemDetails(details, item);
  return details;
}

function createTopSpendingDetails(category) {
  const details = document.createElement("div");
  details.className = "accordion-details top-details";
  category.transactions.forEach((item) => {
    const entry = document.createElement("div");
    entry.className = "top-detail-entry";
    const summary = document.createElement("div");
    summary.className = "top-detail-summary";
    const label = document.createElement("span");
    label.textContent = `${formatDate(item.date)} · ${item.note || t("noNote")}`;
    const amount = document.createElement("strong");
    amount.textContent = currency.format(Number(item.amount));
    summary.append(label, amount);
    entry.append(summary, createTransactionDetails(item));
    details.append(entry);
  });
  return details;
}

function hasItemDetails(item) {
  const items = item.items || item.line_items || item.item_details;
  return Boolean(items && (Array.isArray(items) || typeof items === "string"));
}

function renderHistory() {
  const rows = state.visibleTransactions;
  const displayedRows = state.showAllTransactions ? rows : rows.slice(0, 8);
  const isTopSpending = byId("sort-filter").value === "top_spending";
  const list = byId("transaction-list");
  list.replaceChildren();
  byId("history-count").textContent = isTopSpending
    ? t("countCategories", rows.length)
    : t("showingTransactions", displayedRows.length, rows.length);
  byId("empty-state").classList.toggle("hidden", rows.length > 0);
  displayedRows.forEach((item) => {
    const rowKey = isTopSpending ? `top:${item.name}` : String(item.id);
    const expanded = state.expandedRows.has(rowKey);
    const row = document.createElement("tr");
    const nameCell = document.createElement("td");
    const identity = document.createElement("div");
    identity.className = "transaction-name";
    const expandButton = document.createElement("button");
    expandButton.className = `expand-button${expanded ? " is-expanded" : ""}`;
    expandButton.type = "button";
    expandButton.dataset.action = "toggle";
    expandButton.dataset.key = rowKey;
    expandButton.setAttribute("aria-expanded", String(expanded));
    expandButton.setAttribute("aria-label", t(expanded ? "collapseDetails" : "expandDetails"));
    expandButton.textContent = "›";
    const mark = document.createElement("span");
    const income = item.type === "income";
    mark.className = `transaction-mark ${income ? "income" : "expense"}`;
    mark.textContent = income ? "↗" : "↘";
    const details = document.createElement("div");
    const title = document.createElement("div");
    title.className = "transaction-title";
    title.textContent = item.name;
    if (isTopSpending) {
      const count = document.createElement("div");
      count.className = "transaction-note";
      count.textContent = t("countExpenseTransactions", item.count);
      details.append(title, count);
    } else {
      details.append(title);
    }
    identity.append(expandButton, mark, details);
    nameCell.append(identity);

    const dateCell = document.createElement("td");
    dateCell.textContent = isTopSpending
      ? t({
        today: "today",
        this_week: "thisWeek",
        this_month: "thisMonth",
        this_year: "thisYear",
        all: "allTimeLabel"
      }[byId("top-period-filter").value] || "allTimeLabel")
      : formatDate(item.date);
    const typeCell = document.createElement("td");
    const pill = document.createElement("span");
    pill.className = `type-pill ${income ? "income" : "expense"}`;
    pill.textContent = income ? t("income") : t("expense");
    typeCell.append(pill);
    const amountCell = document.createElement("td");
    amountCell.className = `amount-cell ${income ? "income" : ""}${isTopSpending ? " top-amount" : ""}`;
    amountCell.textContent = isTopSpending
      ? currency.format(Number(item.amount))
      : `${income ? "+" : "−"}${currency.format(Number(item.amount))}`;
    const actionsCell = document.createElement("td");
    const actions = document.createElement("div");
    actions.className = "row-actions";
    if (!isTopSpending) {
      const editButton = document.createElement("button");
      editButton.className = "icon-button";
      editButton.type = "button";
      editButton.dataset.action = "edit";
      editButton.dataset.id = item.id;
      editButton.setAttribute("aria-label", `${t("edit")} ${item.name}`);
      editButton.title = t("edit");
      editButton.textContent = "✎";
      const deleteButton = document.createElement("button");
      deleteButton.className = "icon-button";
      deleteButton.type = "button";
      deleteButton.dataset.action = "delete";
      deleteButton.dataset.id = item.id;
      deleteButton.setAttribute("aria-label", `${t("delete")} ${item.name}`);
      deleteButton.title = t("delete");
      deleteButton.textContent = "×";
      actions.append(editButton, deleteButton);
    }
    actionsCell.append(actions);
    row.append(nameCell, dateCell, typeCell, amountCell, actionsCell);
    list.append(row);

    const detailRow = document.createElement("tr");
    detailRow.className = `accordion-row${expanded ? "" : " hidden"}`;
    const detailCell = document.createElement("td");
    detailCell.colSpan = 5;
    detailCell.append(isTopSpending
      ? createTopSpendingDetails(item)
      : createTransactionDetails(item));
    detailRow.append(detailCell);
    list.append(detailRow);
  });
  updateShowMoreButton();
}

function updateShowMoreButton() {
  const button = byId("show-more-button");
  const total = state.visibleTransactions.length;
  button.classList.toggle("hidden", total <= 8);
  button.textContent = state.showAllTransactions
    ? t("collapseTransactions")
    : t("showAllTransactions", total);
}

function selectType(type) {
  byId("transaction-type").value = type;
  document.querySelectorAll(".type-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.type === type);
  });
}

function resetForm() {
  state.editingId = null;
  byId("transaction-form").reset();
  byId("date").value = localDateString(new Date());
  selectType("expense");
  byId("form-title").textContent = t("addTransaction");
  byId("submit-button").innerHTML = `<span>${t("saveTransaction")}</span> <span aria-hidden="true">→</span>`;
  byId("cancel-edit").classList.add("hidden");
}

function startEditing(id) {
  const item = state.transactions.find((transaction) => transaction.id === id);
  if (!item) return;
  state.editingId = id;
  selectType(item.type || "expense");
  byId("amount").value = item.amount;
  byId("name").value = item.name;
  byId("date").value = item.date;
  byId("note").value = item.note || "";
  byId("form-title").textContent = t("editTransaction");
  byId("submit-button").textContent = t("updateTransaction");
  byId("cancel-edit").classList.remove("hidden");
  byId("transaction-form").scrollIntoView({ behavior: "smooth", block: "center" });
}

byId("transaction-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    type: byId("transaction-type").value,
    amount: byId("amount").value,
    name: byId("name").value,
    date: byId("date").value,
    note: byId("note").value
  };
  const editingId = state.editingId;
  try {
    await request(editingId
      ? `/api/transactions/${encodeURIComponent(editingId)}`
      : "/api/transactions", {
      method: editingId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    resetForm();
    await loadTransactions();
    showToast(editingId ? t("updated") : t("added"), false);
  } catch (error) {
    showToast(error.message, true);
  }
});

byId("transaction-list").addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  if (button.dataset.action === "toggle") {
    const rowKey = button.dataset.key;
    if (state.expandedRows.has(rowKey)) state.expandedRows.delete(rowKey);
    else state.expandedRows.add(rowKey);
    renderHistory();
    return;
  }
  if (button.dataset.action === "edit") {
    startEditing(button.dataset.id);
    return;
  }
  const item = state.transactions.find((transaction) => transaction.id === button.dataset.id);
  if (!item || !window.confirm(t("deleteConfirm", item.name))) return;
  try {
    await request(`/api/transactions/${encodeURIComponent(item.id)}`, { method: "DELETE" });
    if (state.editingId === item.id) resetForm();
    await loadTransactions();
    showToast(t("deleted"), false);
  } catch (error) {
    showToast(error.message, true);
  }
});

document.querySelectorAll(".type-button").forEach((button) => {
  button.addEventListener("click", () => selectType(button.dataset.type));
});
byId("cancel-edit").addEventListener("click", resetForm);
let searchTimer;
byId("search").addEventListener("input", () => {
  state.showAllTransactions = false;
  window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(loadTransactions, 220);
});
byId("type-filter").addEventListener("change", () => {
  state.showAllTransactions = false;
  loadTransactions();
});
byId("period-filter").addEventListener("change", () => {
  state.showAllTransactions = false;
  syncFilterControls();
  loadTransactions();
});
byId("specific-date").addEventListener("change", () => {
  state.showAllTransactions = false;
  loadTransactions();
});
byId("date-from").addEventListener("change", () => {
  state.showAllTransactions = false;
  loadTransactions();
});
byId("date-to").addEventListener("change", () => {
  state.showAllTransactions = false;
  loadTransactions();
});
byId("sort-filter").addEventListener("change", () => {
  state.showAllTransactions = false;
  syncFilterControls();
  loadTransactions();
});
byId("top-period-filter").addEventListener("change", () => {
  state.showAllTransactions = false;
  loadTransactions();
});
byId("chart-period-filter").addEventListener("change", loadTransactions);
byId("show-items").addEventListener("change", () => {
  if (byId("show-items").checked) {
    state.visibleTransactions.forEach((item) => {
      const records = byId("sort-filter").value === "top_spending"
        ? item.transactions || []
        : [item];
      if (records.some(hasItemDetails)) {
        state.expandedRows.add(byId("sort-filter").value === "top_spending"
          ? `top:${item.name}`
          : String(item.id));
      }
    });
  }
  renderHistory();
});
byId("expand-all").addEventListener("click", () => {
  state.visibleTransactions.forEach((item) => {
    state.expandedRows.add(byId("sort-filter").value === "top_spending"
      ? `top:${item.name}`
      : String(item.id));
  });
  renderHistory();
});
byId("collapse-all").addEventListener("click", () => {
  state.expandedRows.clear();
  renderHistory();
});
byId("show-more-button").addEventListener("click", () => {
  state.showAllTransactions = !state.showAllTransactions;
  renderHistory();
});
byId("refresh-button").addEventListener("click", loadTransactions);
byId("theme-toggle").addEventListener("click", () => {
  state.theme = state.theme === "light" ? "dark" : "light";
  savePreference("liemfinance-theme", state.theme);
  applyTheme();
  applyTranslations();
});
byId("language-toggle").addEventListener("click", () => {
  state.language = state.language === "vi" ? "en" : "vi";
  savePreference("liemfinance-language", state.language);
  applyTranslations();
});
byId("shutdown-button").addEventListener("click", async () => {
  if (!window.confirm(t("shutdownConfirm"))) return;
  try {
    await request("/api/shutdown", { method: "POST" });
    showToast(t("shuttingDown"), false);
  } catch (error) {
    showToast(error.message || t("shutdownFailed"), true);
  }
});
function syncFilterControls() {
  const period = byId("period-filter").value;
  const topSpending = byId("sort-filter").value === "top_spending";
  byId("top-period-control").classList.toggle("hidden", !topSpending);
  byId("day-filter-field").classList.toggle("hidden", period !== "day" || topSpending);
  byId("custom-range-fields").classList.toggle("hidden", period !== "custom" || topSpending);
  byId("period-filter").disabled = topSpending;
  byId("type-filter").disabled = topSpending;
  byId("specific-date").disabled = topSpending;
  byId("date-from").disabled = topSpending;
  byId("date-to").disabled = topSpending;
}
byId("specific-date").value = localDateString(new Date());
byId("date-from").value = localDateString(new Date(new Date().getFullYear(), new Date().getMonth(), 1));
byId("date-to").value = localDateString(new Date());
applyTheme();
applyTranslations();
syncFilterControls();
loadTransactions();

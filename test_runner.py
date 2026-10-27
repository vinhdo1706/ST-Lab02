"""Data-driven requirement tests for the original EduCommerce application (STLab02)."""

import argparse
import html
import json
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd

from ecommerce_app import Cart, Checkout, Customer, Shipping, fixture


REQUIRED_COLUMNS = [
    'test_case_id', 'requirement_id', 'condition_id', 'scenario_id',
    'title', 'priority', 'precondition', 'fixture_key', 'input_json',
    'expected_type', 'expected_json', 'execution_status', 'actual_result',
    'error_message', 'evidence_reference',
]
SUPPORTED = {
    'REQ-02': 'cart_state', 'REQ-07': 'promotion_state',
    'REQ-09': 'shipping_fee', 'REQ-10': 'payment_state',
    'REQ-15': 'inventory_state',
}


class CaseConfigurationError(Exception):
    """Invalid test data/setup: cannot fairly judge application behavior."""


def fresh_state(fixture_key):
    if fixture_key == 'empty':
        app = Checkout()
        return app, Customer('U_NEW'), Cart(app.catalog)
    if fixture_key in ('300k', '499999', '500k', '600k', '1000k', '1500k'):
        return fixture(fixture_key)
    raise CaseConfigurationError(f'Unknown fixture_key: {fixture_key}')


def exception_name(error):
    return f'{type(error).__name__}:{error}'


def cart_lines(cart):
    return [{'sku': line.sku, 'quantity': line.quantity} for line in cart.lines]


def stock_snapshot(app):
    return {sku: product.stock for sku, product in app.catalog.products.items()}


def run_business_case(req_id, app, customer, cart, data):
    """Invoke real EduCommerce functions and collect comparable return/state data."""
    if req_id == 'REQ-02':
        error = None
        for sku, quantity in data['actions']:
            try:
                cart.add(sku, quantity)
            except ValueError as exc:
                error = exception_name(exc)
                break
        return {'exception': error, 'lines': cart_lines(cart), 'subtotal': str(cart.subtotal())}

    if req_id == 'REQ-07':
        mode = data['mode']
        voucher = data.get('voucher')
        if data.get('setup_used'):
            customer.used_codes.add(voucher)
        if data.get('make_inactive'):
            app.promotions.codes[voucher].active = False
        error, status = None, None
        try:
            if mode == 'discount':
                app.promotions.discount(voucher, cart.subtotal(), customer)
            elif mode == 'checkout':
                order = app.place(customer, cart, voucher=voucher,
                                  method=data['method'], approved=data['approved'],
                                  key='PROMO-ORDER-1')
                status = order.status
            elif mode == 'reuse_after_success':
                app.place(customer, cart, voucher=voucher, key='PROMO-ORDER-1')
                app.place(customer, cart, voucher=voucher, key='PROMO-ORDER-2')
            else:
                raise CaseConfigurationError(f'Unsupported promotion mode: {mode}')
        except ValueError as exc:
            error = exception_name(exc)
        return {'exception': error, 'used_codes': sorted(customer.used_codes),
                'order_count': len(app.orders), 'payment_status': status}

    if req_id == 'REQ-09':
        error, fee = None, None
        try:
            fee = str(Shipping().calculate(Decimal(str(data['subtotal'])), data['area']))
        except ValueError as exc:
            error = exception_name(exc)
        return {'exception': error, 'fee': fee}

    if req_id == 'REQ-10':
        error, status = None, None
        try:
            order = app.place(customer, cart, method=data['method'],
                              approved=data['approved'], key='PAY-ORDER-1')
            status = order.status
        except ValueError as exc:
            error = exception_name(exc)
        return {'exception': error, 'status': status,
                'order_count': len(app.orders), 'charge_count': len(app.payments.charges)}

    if req_id == 'REQ-15':
        for sku, quantity in data['actions']:
            cart.add(sku, quantity)
        error = None
        try:
            app.place(customer, cart, method=data['method'],
                      approved=data['approved'], key='INV-ORDER-1')
        except ValueError as exc:
            error = exception_name(exc)
        return {'exception': error, 'stock_after': stock_snapshot(app),
                'order_count': len(app.orders), 'charge_count': len(app.payments.charges)}

    raise CaseConfigurationError(f'Unsupported requirement: {req_id}')


def check_expected(expected, actual, prefix=''):
    """Compare the expected keys only; actual may include additional diagnostic fields."""
    differences = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f'{prefix}: expected object, got {actual!r}']
        for key, value in expected.items():
            path = f'{prefix}.{key}' if prefix else key
            if key not in actual:
                differences.append(f'{path}: key missing')
            else:
                differences.extend(check_expected(value, actual[key], path))
    elif expected != actual:
        differences.append(f'{prefix}: expected={expected!r}; actual={actual!r}')
    return differences


def read_cases(path):
    # dtype=str prevents Excel-like interpretation of test IDs; keep_default_na=False
    # keeps blank execution fields blank. utf-8-sig accepts a Windows CSV BOM.
    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8-sig')
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise CaseConfigurationError('Missing CSV columns: ' + ', '.join(missing))
    return frame.to_dict(orient='records')


def validate_case_inputs(req, data):
    required = {
        'REQ-02': ('actions',),
        'REQ-07': ('mode', 'voucher'),
        'REQ-09': ('subtotal', 'area'),
        'REQ-10': ('method', 'approved'),
        'REQ-15': ('actions', 'method', 'approved'),
    }[req]
    missing = [key for key in required if key not in data]
    if missing:
        raise CaseConfigurationError('Missing test input: ' + ', '.join(missing))
    if req in ('REQ-02', 'REQ-15'):
        actions = data['actions']
        if not isinstance(actions, list) or any(
            not isinstance(item, list) or len(item) != 2 for item in actions
        ):
            raise CaseConfigurationError('actions must be a list of [sku, quantity]')
    if req == 'REQ-07':
        if data['mode'] not in ('discount', 'checkout', 'reuse_after_success'):
            raise CaseConfigurationError('Unknown promotion mode')
        if data['mode'] == 'checkout':
            missing = [key for key in ('method', 'approved') if key not in data]
            if missing:
                raise CaseConfigurationError('Missing checkout input: ' + ', '.join(missing))
    if req == 'REQ-09':
        try:
            Decimal(str(data['subtotal']))
        except (ValueError, TypeError, ArithmeticError) as exc:
            raise CaseConfigurationError('subtotal is not a valid decimal') from exc


def evaluate(row, repeated_ids):
    start = time.perf_counter()
    actual = {}
    error = ''
    status = 'BLOCKED'
    tc_id = row['test_case_id'].strip()
    try:
        if not tc_id:
            raise CaseConfigurationError('Empty test_case_id')
        if tc_id in repeated_ids:
            raise CaseConfigurationError(f'Duplicate test_case_id: {tc_id}')
        req = row['requirement_id'].strip()
        if SUPPORTED.get(req) != row['expected_type'].strip():
            raise CaseConfigurationError('Unsupported requirement / expected_type combination')
        if not row['condition_id'].strip() or not row['scenario_id'].strip():
            raise CaseConfigurationError('Missing condition/scenario trace')
        try:
            inputs = json.loads(row['input_json'])
            expected = json.loads(row['expected_json'])
        except json.JSONDecodeError as exc:
            raise CaseConfigurationError(f'Invalid input/expected JSON: {exc.msg}') from exc
        if not isinstance(inputs, dict) or not isinstance(expected, dict):
            raise CaseConfigurationError('input_json and expected_json must be JSON objects')
        validate_case_inputs(req, inputs)
        app, customer, cart = fresh_state(row['fixture_key'])
        try:
            actual = run_business_case(req, app, customer, cart, inputs)
        except CaseConfigurationError:
            raise
        except Exception as exc:
            status = 'FAIL'
            error = f'UNEXPECTED_APPLICATION_EXCEPTION: {type(exc).__name__}: {exc}'
        else:
            differences = check_expected(expected, actual)
            status = 'FAIL' if differences else 'PASS'
            error = '; '.join(differences)
    except (CaseConfigurationError, KeyError, TypeError, ValueError, IndexError) as exc:
        status = 'BLOCKED'
        error = f'TEST_SETUP: {type(exc).__name__}: {exc}'
    except Exception as exc:
        # An unexpected application error after valid data is FAIL, not a silent skip.
        status = 'FAIL'
        error = f'UNEXPECTED_EXCEPTION: {type(exc).__name__}: {exc}'
    duration_ms = round((time.perf_counter() - start) * 1000, 3)
    return {
        'run_id': 'RUN-' + (tc_id or 'MISSING-ID'),
        'test_case_id': tc_id,
        'requirement_id': row['requirement_id'],
        'condition_id': row['condition_id'],
        'scenario_id': row['scenario_id'],
        'title': row['title'],
        'priority': row['priority'],
        'execution_status': status,
        'expected_json': row['expected_json'],
        'actual_result': json.dumps(actual, ensure_ascii=False, sort_keys=True),
        'error_message': error,
        'evidence_reference': f'reports/test_execution.csv#{tc_id}',
        'execution_time_ms': duration_ms,
        'run_timestamp_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def export_csv(path, records, columns):
    import csv
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def make_dashboard(records, output, started_at):
    statuses = ('PASS', 'FAIL', 'BLOCKED')
    counts = Counter(row['execution_status'] for row in records)
    by_req = defaultdict(Counter)
    for row in records:
        by_req[row['requirement_id']][row['execution_status']] += 1
    total = len(records)
    executed = counts['PASS'] + counts['FAIL']
    rate = f'{counts["PASS"]/executed:.1%}' if executed else 'N/A'
    colors = {'PASS': '#278564', 'FAIL': '#c64747', 'BLOCKED': '#ad781b'}
    bars = []
    for i, req in enumerate(sorted(by_req)):
        y = 32 + i * 55
        bars.append(f'<text x="10" y="{y+17}" class="label">{html.escape(req)}</text>')
        offset = 125
        for status in statuses:
            n = by_req[req][status]
            if n:
                width = n * 42
                bars.append(f'<rect x="{offset}" y="{y}" width="{width}" height="25" rx="3" fill="{colors[status]}"><title>{status}: {n}</title></rect>')
                bars.append(f'<text x="{offset+width/2}" y="{y+17}" text-anchor="middle" fill="white" font-size="12">{n}</text>')
                offset += width + 3
    rows = []
    for item in records:
        cells = []
        for column in ('test_case_id', 'requirement_id', 'scenario_id', 'execution_status', 'execution_time_ms', 'error_message'):
            value = str(item.get(column, ''))
            cells.append('<td>' + html.escape(value) + '</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
    legend = ' '.join(f'<span class="legend"><i style="background:{colors[s]}"></i>{s}: {counts[s]}</span>' for s in statuses)
    svg = '\n'.join(bars)
    html_text = f'''<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>STLab02 · EduCommerce Test Dashboard</title>
<style>body{{font:15px/1.5 system-ui,Arial,sans-serif;color:#223044;background:#f6f8fb;margin:0}}main{{max-width:1120px;margin:auto;padding:36px 22px}}h1{{margin:0 0 6px}}.small{{color:#65758c}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:22px 0}}.card,section{{background:white;border:1px solid #dde5ed;border-radius:12px;padding:16px}}.num{{font-size:28px;font-weight:700}}section{{margin:16px 0;overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:9px;text-align:left;border-bottom:1px solid #e7edf3}}th{{background:#edf3f8}}.legend{{margin-right:18px}}i{{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px}}svg{{max-width:100%;height:auto}}.label{{font-size:13px;fill:#37465c;font-weight:600}}.note{{background:#fff7e8;border-left:4px solid #ad781b;padding:10px 14px}}</style></head>
<body><main><h1>EduCommerce · Test Execution</h1><div class="small">Thời điểm chạy (UTC): {html.escape(started_at)} · 5 yêu cầu được chọn: REQ-02, 07, 09, 10, 15</div>
<div class="cards"><div class="card"><div class="small">Số test case đã nạp</div><div class="num">{total}</div></div><div class="card"><div class="small">PASS</div><div class="num">{counts['PASS']}</div></div><div class="card"><div class="small">FAIL</div><div class="num">{counts['FAIL']}</div></div><div class="card"><div class="small">BLOCKED</div><div class="num">{counts['BLOCKED']}</div></div><div class="card"><div class="small">Tỷ lệ PASS trong số case đã chạy</div><div class="num">{rate}</div></div></div>
<section><h2>Trạng thái theo yêu cầu</h2><p>{legend}</p><svg viewBox="0 0 560 {len(by_req)*55+50}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Biểu đồ trạng thái theo yêu cầu">{svg}</svg></section>
<section><h2>Kết quả từng test case</h2><table><thead><tr><th>Test case</th><th>REQ</th><th>Tình huống</th><th>Trạng thái</th><th>Thời gian (ms)</th><th>Chi tiết</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>
<p class="note">Số case đã nạp = PASS + FAIL + BLOCKED ({total} = {counts['PASS']} + {counts['FAIL']} + {counts['BLOCKED']}). Tỷ lệ PASS = PASS/(PASS + FAIL); BLOCKED được thống kê riêng, không bị loại bỏ. Xem tệp CSV để đối chiếu đầy đủ expected và actual.</p>
</main></body></html>'''
    output.write_text(html_text, encoding='utf-8')
    return by_req, rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', default='test_cases.csv')
    parser.add_argument('--out', default='reports')
    args = parser.parse_args()
    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat(timespec='seconds')
    try:
        rows = read_cases(Path(args.cases))
        if not rows:
            raise CaseConfigurationError('CSV contains no test cases')
    except Exception as exc:
        print(f'BLOCKED: Không thể đọc dữ liệu kiểm thử: {type(exc).__name__}: {exc}')
        raise SystemExit(2) from exc
    ids = Counter(row['test_case_id'].strip() for row in rows)
    repeated_ids = {key for key, value in ids.items() if value > 1}
    records = [evaluate(row, repeated_ids) for row in rows]
    result_fields = list(records[0].keys()) if records else [
        'run_id', 'test_case_id', 'requirement_id', 'condition_id', 'scenario_id',
        'title', 'priority', 'execution_status', 'expected_json', 'actual_result',
        'error_message', 'evidence_reference', 'execution_time_ms', 'run_timestamp_utc',
    ]
    export_csv(output/'test_execution.csv', records, result_fields)
    matrix_cols = ['requirement_id', 'condition_id', 'scenario_id', 'test_case_id', 'run_id', 'execution_status']
    export_csv(output/'traceability_execution.csv', records, matrix_cols)
    summary_by_req, rate = make_dashboard(records, output/'test_dashboard.html', started_at)
    summary_rows = []
    for req in sorted(summary_by_req):
        count = summary_by_req[req]
        summary_rows.append({'requirement_id': req, 'loaded': sum(count.values()),
                             'PASS': count['PASS'], 'FAIL': count['FAIL'],
                             'BLOCKED': count['BLOCKED']})
    export_csv(output/'test_summary.csv', summary_rows,
               ['requirement_id', 'loaded', 'PASS', 'FAIL', 'BLOCKED'])
    counts = Counter(r['execution_status'] for r in records)
    metadata = {'run_timestamp_utc': started_at, 'cases_loaded': len(rows),
                'PASS': counts['PASS'], 'FAIL': counts['FAIL'],
                'BLOCKED': counts['BLOCKED'], 'pass_rate_executed': rate,
                'selected_requirements': sorted(SUPPORTED)}
    (output/'run_metadata.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')
    print('Thời điểm chạy (UTC):', started_at)
    for result in records:
        print(f"{result['test_case_id']:<20} {result['requirement_id']:<7} {result['execution_status']:<7} {result['error_message']}")
    print(f"TOTAL={len(rows)} PASS={counts['PASS']} FAIL={counts['FAIL']} BLOCKED={counts['BLOCKED']} PASS_RATE_EXECUTED={rate}")
    print('Các tệp kết quả:', ', '.join(str(p) for p in sorted(output.iterdir()) if p.is_file()))
    # Nonzero exit when any FAIL/BLOCKED; artifacts still written for diagnosis.
    return 0 if counts['FAIL'] == 0 and counts['BLOCKED'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())

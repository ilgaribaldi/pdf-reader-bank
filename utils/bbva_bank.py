from tabula import read_pdf
import re
import pandas as pd
import urllib.request
import os


# --------------------------------- Data handling --------------------------------- #


def convert_value(value):
    if pd.isnull(value):
        return ''

    if isinstance(value, (float, int)):
        return str(value)

    return value


def safe_get_cell(df, row, col):
    try:
        value = df.iloc[row, col]
        return convert_value(value)
    except IndexError:
        return ''


def safe_get_col(df, col):
    try:
        value = df.columns[col]
        return convert_value(value)
    except IndexError:
        return ''


# ------------------------------- Internal parsers ------------------------------- #


def parse_date_period(date_period):
    dates = re.findall(r'\d{2}/\d{2}/\d{4}', date_period)

    date_start = dates[0] if len(dates) > 0 else ''
    date_end = dates[1] if len(dates) > 1 else ''

    return date_start, date_end


def parse_state_country(state_country):
    parts = state_country.split()

    state = parts[0] if len(parts) > 0 else ''
    country = parts[1] if len(parts) > 1 else ''

    return state, country


# ------------------------------------- Data ------------------------------------- #


def load_dfs(path):
    top_right_box = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[40, 300, 150, 600],
        stream=True
    )[0]

    top_left_address = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[40, 0, 150, 250],
        stream=True
    )[0]

    top_left_fiscal_address = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[100, 0, 150, 250],
        stream=True
    )[0]

    middle_left_box = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[250, 0, 500, 300],
        stream=True
    )[0]

    middle_right_box = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[250, 300, 350, 600],
        stream=True
    )[0]

    movements_df_page_one = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='1',
        multiple_tables=True,
        area=[580, 0, 650, 1000],
        stream=True
    )[0]

    movements_df_all = read_pdf(
        path,
        encoding='ISO-8859-1',
        pages='all',
        multiple_tables=True,
        area=[130, 0, 750, 1000],
        stream=True
    )

    return (top_right_box,
            top_left_address,
            top_left_fiscal_address,
            middle_left_box,
            middle_right_box,
            movements_df_page_one,
            movements_df_all)


# ---------------------------------- Main parsers ---------------------------------- #

def parse_top_right_box(top_right_box):
    date_period = safe_get_col(top_right_box, -1)
    date_start, date_end = parse_date_period(date_period)
    date_cutoff = safe_get_cell(top_right_box, 0, -1)
    account_number = safe_get_cell(top_right_box, 1, -1)
    client_number = safe_get_cell(top_right_box, 2, -1)
    rfc = safe_get_cell(top_right_box, -2, -1)
    clabe = safe_get_cell(top_right_box, -1, -1)

    top_right_box_info = {
        'dateStart': date_start,
        'dateEnd': date_end,
        'dateCutoff': date_cutoff,
        'accountNumber': account_number,
        'clientNumber': client_number,
        'rfc': rfc,
        'clabe': clabe
    }

    return top_right_box_info


def parse_top_left_address(top_left_address):
    name = safe_get_col(top_left_address, 0)
    street = safe_get_cell(top_left_address, 0, 0)
    colony = safe_get_cell(top_left_address, 1, 0)
    city = safe_get_cell(top_left_address, 2, 0)
    state_country = safe_get_cell(top_left_address, -1, 0)
    state, country = parse_state_country(state_country)
    postcode = safe_get_cell(top_left_address, -1, -1)

    top_left_address_info = {
        'name': name,
        'street': street,
        'colony': colony,
        'city': city,
        'state': state,
        'country': country,
        'postcode': postcode,
    }

    return top_left_address_info


def parse_top_left_fiscal_address(top_left_fiscal_address):
    street = safe_get_col(top_left_fiscal_address, 0)
    colony = safe_get_cell(top_left_fiscal_address, 0, 0)
    city = safe_get_cell(top_left_fiscal_address, 1, 0)
    state_country = safe_get_cell(top_left_fiscal_address, -1, 0)
    state, country = parse_state_country(state_country)
    postcode = safe_get_cell(top_left_fiscal_address, -1, -1)

    top_left_fiscal_address_info = {
        'street' : street,
        'colony' : colony,
        'city' : city,
        'state': state,
        'country' : country,
        'postcode': postcode
    }

    return top_left_fiscal_address_info


def parse_middle_left_box(middle_left_box):
    average_balance = safe_get_cell(middle_left_box, 0, -1)
    days_of_period = safe_get_cell(middle_left_box, 1, -1)
    annual_gross_rate = safe_get_cell(middle_left_box, 2, -1)
    taxable_average_balance = safe_get_cell(middle_left_box, 3, -1)
    interest_favor = safe_get_cell(middle_left_box, 4, -1)
    withheld_isr = safe_get_cell(middle_left_box, 5, -1)
    account_commissions = safe_get_cell(middle_left_box, 6, -1)
    paid_checks = safe_get_cell(middle_left_box, 7, -1)
    account_handling = safe_get_cell(middle_left_box, 8, -1)
    annuity = safe_get_cell(middle_left_box, 9, -1)
    operations = safe_get_cell(middle_left_box, 10, -1)
    total_commissions = safe_get_cell(middle_left_box, 11, -1)

    middle_left_box_info = {
        'averageBalance': average_balance,
        'daysOfPeriod': days_of_period,
        'annualGrossRate': annual_gross_rate,
        'taxableAverageBalance': taxable_average_balance,
        'interestFavor': interest_favor,
        'withheldIsr': withheld_isr,
        'accountCommission': account_commissions,
        'paidChecks': paid_checks,
        'accountHandling': account_handling,
        'annuity': annuity,
        'operations': operations,
        'totalCommissions': total_commissions
    }

    return middle_left_box_info


def parse_middle_right_box(middle_right_box):
    initial_liquidation_balance = safe_get_cell(middle_right_box, 0, -1)
    initial_operation_balance = safe_get_cell(middle_right_box, 1, -1)
    deposits_credits = safe_get_cell(middle_right_box, 2, -1)
    withdrawals_debits = safe_get_cell(middle_right_box, 3, -1)
    final_balance = safe_get_cell(middle_right_box, 4, -1)
    final_operation_balance = safe_get_cell(middle_right_box, 5, -1)
    average_monthly_minimum_balance_to_date = safe_get_cell(middle_right_box, 6, -1)

    middle_right_box_info = {
        'initialLiquidationBalance': initial_liquidation_balance,
        'initialPperationBalance': initial_operation_balance,
        'depositsCredits': deposits_credits,
        'withdrawalsDebits': withdrawals_debits,
        'finalBalance': final_balance,
        'finalOperationBalance': final_operation_balance,
        'averageMonthlyMinimumBalanceToDate': average_monthly_minimum_balance_to_date
    }

    return middle_right_box_info


def movements_df_type(movements_df):
    if movements_df.columns[0] == 'OPER':
        return 1
    elif 'OPER LIQ' in movements_df.columns[0] and 'COD' in movements_df.columns[0]:
        return 2
    elif movements_df.columns[0] == 'OPER LIQ':
        return 3
    return 0


def parse_movements_type_1(movements_df_type_1):
    movements = []
    movement = {}

    for idx, row in enumerate(range(len(movements_df_type_1))):
        operation = safe_get_cell(movements_df_type_1, row, 0)

        operation_date_match = re.match(r'\d{2}/\w{3}', operation)

        if operation_date_match:

            if movement:
                movements.append(movement)

            operation_date = operation_date_match.group(0)

            liquidation_date_raw = safe_get_cell(movements_df_type_1, row, 1)
            liquidation_date_match = re.match(r'\d{2}/\w{3}', liquidation_date_raw)

            if liquidation_date_match:
                liquidation_date = liquidation_date_match.group(0)
                description_partial = re.sub(r'\d{2}/\w{3}\s*', '', liquidation_date_raw).strip()

            else:
                description_partial = liquidation_date_raw
                liquidation_date = ''

            charges = safe_get_cell(movements_df_type_1, idx, 4)
            credit = safe_get_cell(movements_df_type_1, idx, 5)
            operation = safe_get_cell(movements_df_type_1, idx, 6)
            liquidation = safe_get_cell(movements_df_type_1, idx, 7)

            movement = {
                'operationDate': operation_date,
                'liquidationDate': liquidation_date,
                'description': description_partial,
                'charges': charges,
                'credit': credit,
                'operation': operation,
                'liquidation': liquidation
            }
        else:
            if movement:
                description_partial = safe_get_cell(movements_df_type_1, idx, 1)
                movement['description'] += ' ' + description_partial

    if movement:
        movements.append(movement)

    return movements


def parse_movements_type_2(movements_df_type_2):
    movements = []
    movement = {}

    slice_index = movements_df_type_2[movements_df_type_2.iloc[:, 0] == 'Total de Movimientos'].index[0] - 1
    movements_df_type_2 = movements_df_type_2.loc[:slice_index - 1]

    for idx, row in enumerate(range(len(movements_df_type_2))):
        operation = safe_get_cell(movements_df_type_2, row, 0)

        dates_match = re.findall(r'\d{2}/[A-Z]{3}', operation)

        if dates_match:

            if movement:
                movements.append(movement)

            operation_date = dates_match[0]
            liquidation_date = dates_match[1] if len(dates_match) > 1 else ''

            description_partial = re.sub(r'(\d{2}/[A-Z]{3}\s*){1,2}', '', operation).strip()

            charges = safe_get_cell(movements_df_type_2, idx, 3)
            credit = safe_get_cell(movements_df_type_2, idx, 4)
            operation = safe_get_cell(movements_df_type_2, idx, -2)
            liquidation = safe_get_cell(movements_df_type_2, idx, -1)

            movement = {
                'operation_date': operation_date,
                'liquidation_date': liquidation_date,
                'description': description_partial,
                'charges': charges,
                'credit': credit,
                'operation': operation,
                'liquidation': liquidation
            }
        else:
            if movement:
                description_partial = safe_get_cell(movements_df_type_2, idx, 0)
                movement['description'] += ' ' + description_partial

    if movement:
        movements.append(movement)

    return movements


def parse_movements_type_3(movements_df_type_3):
    movements = []
    movement = {}

    slice_index = movements_df_type_3[movements_df_type_3.iloc[:, 0] == 'Total de Movimientos'].index[0] - 1
    movements_df_type_3 = movements_df_type_3.loc[:slice_index - 1]

    for idx, row in enumerate(range(len(movements_df_type_3))):
        operation = safe_get_cell(movements_df_type_3, row, 0)

        dates_match = re.findall(r'\d{2}/[A-Z]{3}', operation)

        if dates_match:

            if movement:
                movements.append(movement)

            operation_date = dates_match[0]
            liquidation_date = dates_match[1] if len(dates_match) > 1 else ''

            description_partial = safe_get_cell(movements_df_type_3, idx, 1)

            charges = safe_get_cell(movements_df_type_3, idx, 3)
            credit = safe_get_cell(movements_df_type_3, idx, 4)
            operation = safe_get_cell(movements_df_type_3, idx, -2)
            liquidation = safe_get_cell(movements_df_type_3, idx, -1)

            movement = {
                'operation_date': operation_date,
                'liquidation_date': liquidation_date,
                'description': description_partial,
                'charges': charges,
                'credit': credit,
                'operation': operation,
                'liquidation': liquidation
            }
        else:
            if movement:
                description_partial = safe_get_cell(movements_df_type_3, idx, 1)
                movement['description'] += ' ' + description_partial

    if movement:
        movements.append(movement)

    return movements


def get_movements(movements_df_all, movements_df_page_one):
    movements_info = []

    if movements_df_type(movements_df_page_one) == 1:
        movements = parse_movements_type_1(movements_df_page_one)
        movements_info.extend(movements)

    for movement_df in movements_df_all:
        if movements_df_type(movement_df) == 1:
            movements = parse_movements_type_1(movement_df)
            movements_info.extend(movements)
        elif movements_df_type(movement_df) == 2:
            movements = parse_movements_type_2(movement_df)
            movements_info.extend(movements)
        elif movements_df_type(movement_df) == 3:
            movements = parse_movements_type_3(movement_df)
            movements_info.extend(movements)

    return movements_info


# ---------------------------------- Extraction ---------------------------------- #


def get_data(path):
    (top_right_box,
     top_left_address,
     top_left_fiscal_address,
     middle_left_box,
     middle_right_box,
     movements_df_page_one,
     movements_df_all) = load_dfs(path)

    top_right_box_info = parse_top_right_box(top_right_box)
    top_left_address_info = parse_top_left_address(top_left_address)
    top_left_fiscal_address_info = parse_top_left_fiscal_address(top_left_fiscal_address)
    middle_left_box_info = parse_middle_left_box(middle_left_box)
    middle_right_box_info = parse_middle_right_box(middle_right_box)
    movements_info = get_movements(movements_df_all, movements_df_page_one)

    return (top_right_box_info,
            top_left_address_info,
            top_left_fiscal_address_info,
            middle_left_box_info,
            middle_right_box_info,
            movements_info)


def parse_data_for_response(
    top_right_box_info,
    top_left_address_info,
    top_left_fiscal_address_info,
    middle_left_box_info,
    middle_right_box_info,
    movements_info
):

    accountStatementSpecs = {**middle_left_box_info, **middle_right_box_info}

    response_data = {
        'info': top_right_box_info,
        'specs': accountStatementSpecs,
        'address': top_left_address_info,
        'fiscalAddress': top_left_fiscal_address_info,
        'movements': movements_info,
    }

    return response_data


def get_bbva_bank_statement_test(path):
    (top_right_box_info,
     top_left_address_info,
     top_left_fiscal_address_info,
     middle_left_box_info,
     middle_right_box_info,
     movements_info) = get_data(path)

    response_data = parse_data_for_response(
        top_right_box_info,
        top_left_address_info,
        top_left_fiscal_address_info,
        middle_left_box_info,
        middle_right_box_info,
        movements_info
    )

    return response_data


def get_bbva_bank_statement(url):
    pdf_path = "/tmp/temp4.pdf"
    urllib.request.urlretrieve(url, pdf_path)

    (top_right_box_info,
     top_left_address_info,
     top_left_fiscal_address_info,
     middle_left_box_info,
     middle_right_box_info,
     movements_info) = get_data(pdf_path)

    statement = parse_data_for_response(
        top_right_box_info,
        top_left_address_info,
        top_left_fiscal_address_info,
        middle_left_box_info,
        middle_right_box_info,
        movements_info
    )

    os.remove(pdf_path)

    return statement



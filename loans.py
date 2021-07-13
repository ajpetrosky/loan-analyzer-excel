"""
Schedule Classes
"""

from typing import NamedTuple, Optional
from math import log, floor, fabs
from datetime import date


class ScheduleDate:
    def __init__(self, month: int, year: int):
        self.month = month
        self.year = year

    def next_date(self):
        next_month = 1 if self.month == 12 else self.month + 1
        next_year = self.year + 1 if next_month == 1 else self.year
        return ScheduleDate(next_month, next_year)

    def previous_date(self):
        next_month = 12 if self.month == 1 else self.month - 1
        next_year = self.year - 1 if next_month == 12 else self.year
        return ScheduleDate(next_month, next_year)

    def __eq__(self, other):
        if isinstance(other, ScheduleDate):
            return self.month == other.month and self.year == other.year
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ScheduleDate):
            if self.year == other.year:
                return self.month < other.month
            else:
                return self.year < other.year
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, ScheduleDate):
            if self.year == other.year:
                return self.month <= other.month
            else:
                return self.year < other.year
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self):
        return str(self.month) + '/' + str(self.year)


class ScheduleRow:
    def __init__(self, payment_date: ScheduleDate, payment_amount: float, loan_balance: float):
        self.payment_date = payment_date
        self.payment_amount = payment_amount
        self.loan_balance = loan_balance

    def next_schedule_row(self, rate: float):
        next_date = self.payment_date.next_date()
        next_loan_balance = (self.loan_balance - self.payment_amount) * (1 + rate)
        next_payment = min(next_loan_balance, self.payment_amount)
        return ScheduleRow(next_date, next_payment, next_loan_balance)

    def to_dict(self):
        return {
            'payment_date': str(self.payment_date),
            'payment_amount': self.payment_amount,
            'loan_balance': self.loan_balance
        }

    def __str__(self):
        return 'Payment Dat: ' + str(self.payment_date) + ', Payment Amount: ' + str(self.payment_amount) + ', Loan Balance: ' + str(self.loan_balance)

    def __eq__(self, other):
        if isinstance(other, ScheduleRow):
            return self.payment_date == other.payment_date
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ScheduleRow):
            return self.payment_date < other.payment_date
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, ScheduleRow):
            return self.payment_date <= other.payment_date
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __add__(self, other):
        if isinstance(other, ScheduleRow):
            payment_amount = self.payment_amount + other.payment_amount
            loan_balance = self.loan_balance + other.loan_balance
            return ScheduleRow(ScheduleDate(self.payment_date.month, self.payment_date.year), payment_amount, loan_balance)
        return NotImplemented


class LoanDetails:
    def __init__(self, name: str, amortizing: bool, starting_balance: float, interest_rate: float, monthly_payment: float, payment_month: int, payment_year: int):
        self.name = name
        self.amortizing = amortizing
        self.starting_balance = starting_balance
        self.interest_rate = interest_rate
        self.monthly_payment = monthly_payment
        self.payments_start_date = ScheduleDate(payment_month, payment_year)


class Loan:
    def __init__(self, loan_details: Optional[LoanDetails], schedule: [ScheduleRow] = None):
        self.loan_details = loan_details
        self.schedule = schedule if schedule else create_schedule(loan_details)

    def __add__(self, other):
        if isinstance(other, Loan):
            longer, shorter = (other.schedule, self.schedule) if len(other.schedule) > len(self.schedule) else (self.schedule, other.schedule)
            schedule = [longer[i] + shorter[i] for i in range(len(shorter))]
            next_row = ScheduleRow(schedule[-1].payment_date.next_date(), longer[0].payment_amount, schedule[-1].loan_balance - longer[0].payment_amount)
            for i in range(len(longer)-len(shorter)):
                schedule.append(next_row)
                #next_row = next_row.next_schedule_row()
            return Loan(None, schedule)
        return NotImplemented


def create_schedule(loan: LoanDetails):
    monthly_rate = loan.interest_rate / 12
    number_of_periods = calculate_number_of_periods(loan, monthly_rate)
    today = date.today()
    today_schedule_date = ScheduleDate(today.month, today.year)
    first_row_date = loan.payments_start_date if loan.payments_start_date else today_schedule_date
    schedule = []
    if first_row_date != today_schedule_date:
        current_row = ScheduleRow(today_schedule_date, 0.0, 0.0)
        schedule.append(current_row)
        while current_row.payment_date < first_row_date.previous_date():
            current_row = current_row.next_schedule_row(0.0)
            schedule.append(current_row)
    first_row_with_payment = ScheduleRow(first_row_date, loan.monthly_payment, loan.starting_balance)
    previous_row = first_row_with_payment
    for _ in range(number_of_periods):
        schedule.append(previous_row)
        previous_row = previous_row.next_schedule_row(monthly_rate)

    return schedule


def calculate_number_of_periods(loan: LoanDetails, monthly_rate: float):
    return floor(-log(1 - ((monthly_rate * loan.starting_balance) / loan.monthly_payment))
                 / log(1 + monthly_rate))

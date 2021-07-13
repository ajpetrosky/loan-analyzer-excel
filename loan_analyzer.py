"""

"""

import sys
import pandas as pd
import numpy as np
from loans import *
from uuid import uuid1


def analyze_loans(file_loc: str):
    loans_df = pd.read_excel(file_loc)
    loans = []
    for index, row in loans_df.iterrows():
        loan_details = LoanDetails(row['Loan Name'], not row['Simple Interest?'], row['Balance'], row['Interest Rate'], row['Monthly Payment'], row['Start Month'], row['Start Year'])
        loan = Loan(loan_details)
        loans.append(loan)
    lens = [len(l.schedule) for l in loans]
    max_len = max(lens)
    extended_loan_schedules =[]
    for loan in loans:
        extended_loan_schedules.append(extend_schedule(loan.schedule, max_len))
    sum_schedule = np.sum(extended_loan_schedules, 0)
    df = pd.DataFrame.from_records([s.to_dict() for s in sum_schedule])
    df.to_excel('output-' + str(uuid1()) + '.xlsx')


def extend_schedule(schedule: [ScheduleRow], desired_len: int):
    while len(schedule) < desired_len:
        schedule.append(schedule[-1].next_schedule_row(0.0))
    return schedule


if __name__ == '__main__':
    #analyze_loans(sys.argv[1])
    analyze_loans("loans.xlsx")

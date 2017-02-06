import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    dMonthlyInvestment_R = 3500.00
    dREITDividendRate_frac      =    0.035 # Assuming a rather conservative rate of return.

    l_iOwnContributionMonths = [0, 1, 3, 4, 6, 7, 9, 10] # Missing every three months, saving for temple trip.
    l_dOwnContributionsPerMonth_R = []
    l_dDividendPayoutsPerMonth_R = [] # This will need to be thought about a bit.
    l_dFundValue_R = []
    l_iPaymentMonthNumber_n = []
    l_iDividendMonthNumber_n = []
    l_iOverallMonthNumber_n = []

    for month in range(12*30):
        l_iOverallMonthNumber_n.append(month)
        if len(l_dDividendPayoutsPerMonth_R) > 1:
            if l_dDividendPayoutsPerMonth_R[-1] >= dMonthlyInvestment_R * 2:
                dMonthlyInvestment_R = 0
        if month % 12 in l_iOwnContributionMonths:
            l_iPaymentMonthNumber_n.append(month)
            l_dOwnContributionsPerMonth_R.append(dMonthlyInvestment_R)
            if len(l_dFundValue_R):
                l_dFundValue_R.append(l_dFundValue_R[-1] + dMonthlyInvestment_R)
            else:
                l_dFundValue_R.append(dMonthlyInvestment_R) # Edge case for first month.
        else:
            l_iDividendMonthNumber_n.append(month)
            dDividendPayout_R = l_dFundValue_R[-1] * dREITDividendRate_frac

            l_dDividendPayoutsPerMonth_R.append(dDividendPayout_R)
            l_dFundValue_R.append(l_dFundValue_R[-1] + dDividendPayout_R)

    a_dROI_dimless = np.zeros(len(l_iOverallMonthNumber_n))
    for i in range(len(l_iOverallMonthNumber_n)):
        a_dROI_dimless[i] = l_dFundValue_R[i] / np.sum(l_dOwnContributionsPerMonth_R[0:i])

    plt.subplot(131)
    plt.plot(np.array(l_iPaymentMonthNumber_n) / 12, np.array(l_dOwnContributionsPerMonth_R) * 8, label="Own contributions per year")
    plt.plot(np.array(l_iDividendMonthNumber_n) / 12, np.array(l_dDividendPayoutsPerMonth_R) * 4, label="Dividend payout per year")
    plt.grid()
    #plt.legend()
    plt.subplot(132)
    plt.plot(np.array(l_iOverallMonthNumber_n[:-1]) / 12, np.diff(l_dFundValue_R), label="Fund rate of change per month")
    #plt.plot(np.array(l_iOverallMonthNumber_n) / 12, np.integrate.quad())
    plt.grid()
    #plt.legend()
    plt.subplot(133)
    plt.plot(np.array(l_iOverallMonthNumber_n) / 12, a_dROI_dimless)
    plt.show()


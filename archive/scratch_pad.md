# Initial data exploration


[All Employees: Leisure and Hospitality in the U.S. Virgin Islands - Seasonally Adjusted](https://fred.stlouisfed.org/series/SMS78000007000000001)

[All Employees: Leisure and Hospitality in the U.S. Virgin Islands - Not Seasonally Adjusted](https://fred.stlouisfed.org/series/SMU78000007000000001)

fred data exists, one number per month (seasonally adjusted or not). hurricane and covid declines visible

[USVIBER Tourism Indicator 2024](https://usviber.org/document/usvi-tourism-indicator-2024/)

[USVIBER Tourism Indicator 2022](https://usviber.org/wp-content/uploads/2023/12/Tourism-indicator-2022-12-28-23-1.pdf)

[USVIBER Tourism Indicator 2020](https://usviber.org/wp-content/uploads/2022/04/TOUR20-revised.pdf)

usviber is distinguishing between tourists and excursionists - excursionistis must be day trippers (broken into air and cruise)

broken down by air vs cruise arrival. and totals. yes hotel occupancy. no ADR, RevPAR. Only an aggregate visitor expenditure (tourist vs excursionist). same variables consistently available, although minor historical fluctuations year over year (i.e., +/- 3 million annual visitors) - must be data revision; _pretty sure they were drunk when they updated 2024's air excursionists number (216.7 vs 2022's 81.5 - the air visitors total is nonsensical as well in 2024 - 604.5 != 546.7 + 216.7)_


[Economic Census 2022](https://www.census.gov/data/tables/2022/econ/economic-census/virgin-islands.html)

[Economic Census 2017](https://www.census.gov/data/tables/2017/econ/economic-census/virgin-islands.html)

[Economic Census 2012](https://www.census.gov/data/tables/2012/econ/census/virgin-islands.html)

I can get number of establishments, sales, annual payroll, number of employees by sector, and number of guestrooms. .DAT files; | separated, instead of a comma - |SV file, instead of CSV

[BEA GDP for the U.S. Virgin Islands (USVI) 2022](https://www.bea.gov/data/gdp/gdp-us-virgin-islands-usvi)

[BEA GDP USVI](https://www.bea.gov/taxonomy/term/1161)

They stopped aggregating USVI data in 2022. ODI doesn't fund it anymore. The territories are orphaned step-children.

Data contains total GDP. Broken out is an accommodations and food service sector (total and percent of gdp, value added and value added by industry as percentage of gross domestic product). Plus an employment compensation.

[World Bank Tourism Receipts](api.worldbank.org/v2/country/VI/indicator/ST.INT.RCPT.CD?format=json)

[World Bank Toursim Arrivals](https://api.worldbank.org/v2/country/VI/indicator/ST.INT.ARVL?format=json)

Data starts in 1995. Ends in 2020. Huh. Visitor numbers and expenditures.

[NPS Visitor VIsitor Use Stats](irma.nps.gov/Stats/)

Annual and monthly recreation visitor stats for VIIS and BUIS (ST John and Buck Island)

## Plan EDA

I wanna see tourism numbers over time - VIBER and World bank, visitors and expenditures/receipts. Break VIBER down by tourist vs excursionist (cruise vs air). National park services visitors.

Tourism emploment - FRED emploment, VIBER employment, Census employment, payroll. BEA compensation of employees by industry.

Tourism infrastructure - Census guestrooms, revenue, number of establishments. BEA GDP for accomodations and food services (total and percent of gdp, value added and value added by industry as percentage of gross domestic product)

I'll need to account for inflation - convert to current dollars? nominal? let's account for inflation.

most of this data seems to be annual, although I have nps visitors and fred data monthly. 

I will want production-quality graphics from the start - the eda will be an appendix to the field note (simple html floating navbar header).
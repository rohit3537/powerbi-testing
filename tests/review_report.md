# DAX Measure Review Report

## PVQ PTQ
**Table:** Account Alignment
```dax
sum('Account Alignment'[Net Revenue])
/
sum('PTQ Revenue Quota'[Quota])
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Performance to Quota
**Table:** Account Alignment
```dax
IFERROR(sum('Account Alignment'[Net Revenue])/sum('Quota Revenue by Rep (LV)'[Quota]),0)
```

✅ No issues found

## Remaining Quota
**Table:** Account Alignment
```dax
sum('Quota Revenue by Rep (LV)'[Quota])
-sum('Account Alignment'[Net Revenue])
```

✅ No issues found

## Net Revenue Run Rate
**Table:** Account Alignment
```dax
sum('account alignment'[net Revenue])
/sum(DateTable[Elapsed Workdays])
*sum(DateTable[Workdays])
```

✅ No issues found

## Run Rate % to Quota
**Table:** Account Alignment
```dax
IFERROR([Net Revenue Run Rate]/sum('Quota Revenue by Rep (LV)'[Quota]),0)
```
**Depends on:** Net Revenue Run Rate

✅ No issues found

## Run Rate vs Quota
**Table:** Account Alignment
```dax
[Net Revenue Run Rate]
-sum('Quota Revenue by Rep (LV)'[Quota])
```
**Depends on:** Net Revenue Run Rate

✅ No issues found

## ADS
**Table:** Account Alignment
```dax
sum('Account Alignment'[net revenue])/sum('DateTable'[Elapsed Workdays])
```

✅ No issues found

## Daily Sales to Hit Goal
**Table:** Account Alignment
```dax
VAR _d = sum(DateTable[Elapsed Workdays])-sum(DateTable[Workdays])
VAR _value =
iferror(
if(
[Remaining quota]<0,
0,
[actual vs Quota]/(_d)
),
"")
RETURN
_value
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Progress to Quota
**Table:** Account Alignment
```dax
VAR color =
SWITCH(
TRUE(),
[Performance to Quota] < .5, "#EB895F",
"#9071CE"
)

VAR start_String = "data:image/svg+xml;utf8,"

VAR svg_full =
"<svg width='500' height='200' viewBox='0 10 750 100' fill='none' xmlns='http://www.w3.org/2000/svg'>
<rect x='30' y='32' width='" & 660 * [Performance to Quota] & "' height='80' rx='5' fill='" & color & "'/>
<rect x='5' y='10' width='710' height='130' rx='10' stroke='#777171' stroke-width='10'/>
</svg>"

RETURN
start_String & svg_full
```
**Depends on:** Performance to Quota

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Performance to Quota v2
**Table:** Account Alignment
```dax
IFERROR(sum('Account Alignment'[Net Revenue])/sum('Quota Revenue by Rep (LV)'[Quota]),0)
```

✅ No issues found

## Rep at or above Quota
**Table:** Account Alignment
```dax
COUNTROWS(
FILTER(
VALUES('GeneralAccountList (LV)'[Sales Rep]),
[Performance to Quota] > 1
)
)
```
**Depends on:** Performance to Quota

✅ No issues found

## Selected date
**Table:** Date(Filter)
```dax
EOMONTH(MAX('Date(Filter)'[Date]),0)
```

✅ No issues found

## Sum of Revenue total for Region
**Table:** DateTable
```dax
CALCULATE(SUM('EOD Data'[net Revenue]), ALLSELECTED('Region'[Region]))
```

✅ No issues found

## Rolling Qtr Start M
**Table:** DateTable
```dax
Var X = networkdays(min('EOD Data'[Current_Qtr Start]),min('EOD Data'[Current_Qtr End]),1,Holidays)
Var RefDate = [Reporting Through]
return

CALCULATE(
max('DateTable'[Date])-X,
Filter(
all('DateTable'),
'DateTable'[Date]<= RefDate &&
'DateTable'[Elapsed Workdays]=1
)
)
```
**Depends on:** Reporting Through

### Findings
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Rolling Qtr -1 Start M
**Table:** DateTable
```dax
Var X = networkdays(min('EOD Data'[Current_Qtr Start]),min('EOD Data'[Current_Qtr End]),1,Holidays)
Var RefDate = [Reporting Through]
return

CALCULATE(
max('DateTable'[Date])-(2*X),
Filter(
all('DateTable'),
'DateTable'[Date]<= RefDate &&
'DateTable'[Elapsed Workdays]=1
)
)
```
**Depends on:** Reporting Through

### Findings
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Reporting Through
**Table:** DateTable
```dax
max('EOD Data (LV)'[Reporting Through Column])
```

✅ No issues found

## List of Current_Qtr Start values 2
**Table:** DateTable
```dax
VAR __DISTINCT_VALUES_COUNT = DISTINCTCOUNT('EOD Data'[Current_Qtr Start])
VAR __MAX_VALUES_TO_SHOW = 3
RETURN
IF(
__DISTINCT_VALUES_COUNT > __MAX_VALUES_TO_SHOW,
CONCATENATE(
CONCATENATEX(
TOPN(
__MAX_VALUES_TO_SHOW,
VALUES('EOD Data'[Current_Qtr Start]),
'EOD Data'[Current_Qtr Start],
ASC
),
'EOD Data'[Current_Qtr Start],
", ",
'EOD Data'[Current_Qtr Start],
ASC
),
", etc."
),
CONCATENATEX(
VALUES('EOD Data'[Current_Qtr Start]),
'EOD Data'[Current_Qtr Start],
", ",
'EOD Data'[Current_Qtr Start],
ASC
)
)
```

✅ No issues found

## List of Current_Qtr Start values
**Table:** DateTable
```dax
VAR __DISTINCT_VALUES_COUNT = DISTINCTCOUNT('EOD Data'[Current_Qtr Start])
VAR __MAX_VALUES_TO_SHOW = 3
RETURN
IF(
__DISTINCT_VALUES_COUNT > __MAX_VALUES_TO_SHOW,
CONCATENATE(
CONCATENATEX(
TOPN(
__MAX_VALUES_TO_SHOW,
VALUES('EOD Data'[Current_Qtr Start]),
'EOD Data'[Current_Qtr Start],
ASC
),
'EOD Data'[Current_Qtr Start],
", ",
'EOD Data'[Current_Qtr Start],
ASC
),
", etc."
),
CONCATENATEX(
VALUES('EOD Data'[Current_Qtr Start]),
'EOD Data'[Current_Qtr Start],
", ",
'EOD Data'[Current_Qtr Start],
ASC
)
)
```

✅ No issues found

## CurrentQtrDisplay
**Table:** DateTable
```dax
"Q" & CEILING(MONTH(max('EOD Data'[Date]))/3,1) & " " & YEAR(max('EOD Data'[Date]))
```

✅ No issues found

## AvgRevPerAccountPerMonth
**Table:** DateTable
```dax
SUM('EOD Data'[net Revenue])
```

✅ No issues found

## % Elapsed
**Table:** DateTable
```dax
sum('DateTable'[Elapsed Workdays])/sum('DateTable'[Workdays])
```

✅ No issues found

## Recent Adopters
**Table:** Designation Site Count Table
```dax
sum('Designation Site Count Table'[Monthly Competitive])
```

✅ No issues found

## Fortress
**Table:** Designation Site Count Table
```dax
sum('Designation Site Count Table'[Monthly Fortress Accounts])
```

✅ No issues found

## Gap to RA Goal
**Table:** Designation Site Count Table
```dax
sum('Designation Site Count Table'[C Goal])-sum('Designation Site Count Table'[Monthly Competitive])
```

✅ No issues found

## Gap to F Goal
**Table:** Designation Site Count Table
```dax
sum('Designation Site Count Table'[F Goal])-sum('Designation Site Count Table'[Monthly Fortress Accounts])
```

✅ No issues found

## Gap to T Goal
**Table:** Designation Site Count Table
```dax
sum('Designation Site Count Table'[T Goal])-sum('Designation Site Count Table'[Monthly Tenzing Believers])
```

✅ No issues found

## Net Revenue (CM)
**Table:** EOD Data (LV)
```dax
VAR _date = [Selected date]
RETURN
CALCULATE(SUM('EOD Data (LV)'[Net Revenue]), 'EOD Data (LV)'[Date (Eomonth)] = _date)
```
**Depends on:** Selected date

✅ No issues found

## Net Revenue (YTD)
**Table:** EOD Data (LV)
```dax
VAR _date = [Selected date]
VAR _Y = YEAR([Selected date])
RETURN
CALCULATE(SUM('EOD Data (LV)'[Net Revenue]), 'EOD Data (LV)'[Date (Eomonth)] <= _date, YEAR('EOD Data (LV)'[Date (Eomonth)]) = _Y )
```
**Depends on:** Selected date

✅ No issues found

## Net Revenue (PYTD)
**Table:** EOD Data (LV)
```dax
VAR _date = EOMONTH([Selected date],-1)
VAR _Y = YEAR([Selected date])-1
RETURN
CALCULATE(SUM('EOD Data (LV)'[Net Revenue]), 'EOD Data (LV)'[Date (Eomonth)] <= _date, YEAR('EOD Data (LV)'[Date (Eomonth)]) = _Y )
```
**Depends on:** Selected date

✅ No issues found

## Net Revenue (PM)
**Table:** EOD Data (LV)
```dax
VAR _date = EOMONTH([Selected date],-1)
RETURN
CALCULATE(SUM('EOD Data (LV)'[Net Revenue]), 'EOD Data (LV)'[Date (Eomonth)] = _date)
```
**Depends on:** Selected date

✅ No issues found

## Net Revenue (CM diff %)
**Table:** EOD Data (LV)
```dax
( [Net Revenue (CM)] - [Net Revenue (PM)] ) / [Net Revenue (PM)]
```
**Depends on:** Net Revenue (CM), Net Revenue (PM)

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## Net Revenue (YTD diff %)
**Table:** EOD Data (LV)
```dax
( [Net Revenue (YTD)] - [Net Revenue (PYTD)] ) / [Net Revenue (PYTD)]
```
**Depends on:** Net Revenue (PYTD), Net Revenue (YTD)

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## Net Revenue (M Shape)
**Table:** EOD Data (LV)
```dax
IF([Net Revenue (CM diff %)] < 0," ▼ "," ▲ " )
```
**Depends on:** Net Revenue (CM diff %)

✅ No issues found

## Net Revenue (YTD Shape)
**Table:** EOD Data (LV)
```dax
IF([Net Revenue (YTD diff %)] < 0," ▼ "," ▲ " )
```
**Depends on:** Net Revenue (YTD diff %)

✅ No issues found

## Active Hospitals (CM)
**Table:** EOD Data (LV)
```dax
VAR _date = [Selected date]
RETURN
CALCULATE(DISTINCTCOUNT('EOD Data (LV)'[Hospital]), 'EOD Data (LV)'[Date (Eomonth)] = _date)
```
**Depends on:** Selected date

✅ No issues found

## Active Hospitals (PM)
**Table:** EOD Data (LV)
```dax
VAR _date = EOMONTH([Selected date],-1)
RETURN
CALCULATE(DISTINCTCOUNT('EOD Data (LV)'[Hospital]), 'EOD Data (LV)'[Date (Eomonth)] = _date)
```
**Depends on:** Selected date

✅ No issues found

## Active Hospital (Diff %)
**Table:** EOD Data (LV)
```dax
( [Active Hospitals (CM)] - [Active Hospitals (PM)] ) / [Active Hospitals (PM)]
```
**Depends on:** Active Hospitals (CM), Active Hospitals (PM)

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## Active Hospital (M Shape)
**Table:** EOD Data (LV)
```dax
IF([Active Hospital (Diff %)] < 0," ▼ "," ▲ " )
```
**Depends on:** Active Hospital (Diff %)

✅ No issues found

## Datefilter(YTD)
**Table:** EOD Data (LV)
```dax
VAR _date = [Selected date]
VAR _Y = YEAR([Selected date])
RETURN
IF(SELECTEDVALUE('EOD Data (LV)'[Date (Eomonth)]) <= _date && SELECTEDVALUE('EOD Data (LV)'[Date Year]) = _Y ,1,0)
```
**Depends on:** Selected date

### Findings
- ⚠️ **WARNING** [blank-handling]: SELECTEDVALUE() without fallback — returns BLANK when multiple values selected
  - *Suggestion:* Add a default: SELECTEDVALUE(Column, "default") or handle multi-select
- ⚠️ **WARNING** [blank-handling]: SELECTEDVALUE() without fallback — returns BLANK when multiple values selected
  - *Suggestion:* Add a default: SELECTEDVALUE(Column, "default") or handle multi-select

## PD1% - 1
**Table:** EOD Data (LV)
```dax
VAR _p = 1-[PD1 %]
RETURN
IF( [PD1 %] > 1, 1, _p)
```
**Depends on:** PD1 %

✅ No issues found

## PD2% - 1
**Table:** EOD Data (LV)
```dax
VAR _p = 1-[PD2 %]
RETURN
IF( [PD2 %] > 1, 1, _p)
```
**Depends on:** PD2 %

✅ No issues found

## PD3% - 1
**Table:** EOD Data (LV)
```dax
VAR _p = 1-[PD3 %]
RETURN
IF( [PD3 %] > 1, 1, _p)
```
**Depends on:** PD3 %

✅ No issues found

## PD4% - 1
**Table:** EOD Data (LV)
```dax
VAR _p = 1-[PD4 %]
RETURN
IF( [PD4 %] > 1, 1, _p)
```
**Depends on:** PD4 %

✅ No issues found

## PD5% - 1
**Table:** EOD Data (LV)
```dax
VAR _p = 1-[PD5 %]
RETURN
IF( [PD5 %] > 1, 1, _p)
```
**Depends on:** PD5 %

✅ No issues found

## Rolling Qtr Variance
**Table:** EOD Data (LV)
```dax
SUM('EOD Data (LV)'[Rolling Qtr Rev]) - SUM('EOD Data (LV)'[Rolling Qtr -1 Rev])
```

✅ No issues found

## Rolling Half Days between Orders
**Table:** EOD Data (LV)
```dax
if(
calculate(
distinctcount('EOD Data (LV)'[Sales Order #]),
Filter('EOD Data (LV)',
[date]>=max('EOD Data (LV)'[Rolling Qtr -1 Start Date])
)
)=0,
blank(),


NETWORKDAYS(
IF(max([Rolling Qtr -1 Start Date])<max('EOD Data (LV)'[Date of First Transaction]),max('EOD Data (LV)'[Date of First Transaction]),MAX('EOD Data (LV)'[Rolling Qtr -1 Start Date])),
[Reporting Through],
1,
Holidays)

/
calculate(
distinctcount('EOD Data (LV)'[SALES ORDER #]),
Filter('EOD Data (LV)',
[date]>=max('EOD Data (LV)'[Rolling Qtr -1 Start Date])
)))
```
**Depends on:** Reporting Through

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'EOD Data (LV)' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'EOD Data (LV)' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (2 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly

## Rolling Qtr Days between Orders
**Table:** EOD Data (LV)
```dax
NETWORKDAYS(
IF(max([Rolling Qtr Start Date])<max('EOD Data (LV)'[Date of First Transaction]),
max('EOD Data (LV)'[Date of First Transaction]),
MAX('EOD Data (LV)'[Rolling Qtr Start Date])),
[Reporting Through],
1,
Holidays)

/
calculate(
distinctcount('EOD Data (LV)'[SALES ORDER #]),
Filter('EOD Data (LV)',
[date]>=max('EOD Data (LV)'[Rolling Qtr Start Date])
))
```
**Depends on:** Reporting Through

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'EOD Data (LV)' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

## Qtr - Qtr Ordering Behavior
**Table:** EOD Data (LV)
```dax
if([Rolling Qtr Days between Orders]=(1/0),"No Orders for 3+ Months",

SWITCH(
true(),
[rolling qtr days between orders]<[Rolling Half Days between Orders],"Ordering More Frequently",
[rolling qtr days between orders]>[Rolling Half Days between Orders],"Ordering Less Frequently",

blank()
)
)
```
**Depends on:** Rolling Half Days between Orders, Rolling Qtr Days between Orders

✅ No issues found

## Days Since Last Order
**Table:** EOD Data (LV)
```dax
networkdays(max('EOD Data (LV)'[date]),
[Reporting Through],
1,
Holidays)
```
**Depends on:** Reporting Through

✅ No issues found

## Current Ordering Status
**Table:** EOD Data (LV)
```dax
if([Rolling Qtr Days between Orders]=(1/0),"No Orders in 3+ Months",

if(
'EOD Data (LV)'[Rolling Qtr Day Variance]<=5 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]>0,
"Due for SO",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]<=10 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]>5,
"1 Wk Overdue for SO",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]<=15 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]>10,
"2 Wks Overdue for SO",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]<=20 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]>15,
"3 Wks Overdue for SO",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]>20,
"4 Wks+ Overdue for SO",

if(
'EOD Data (LV)'[Rolling Qtr Day Variance]>=-5 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]<0,
"Due for SO within 1 Wk",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]>=-10 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]<-5,
"Due for SO within 2 Wks",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]>=-15 &&
'EOD Data (LV)'[Rolling Qtr Day Variance]<-10,
"Due for SO within 3 Wks",
if(
'EOD Data (LV)'[Rolling Qtr Day Variance]<-15,
"Due for SO within 4 Wks",
"Error"
)))))))))
)
```
**Depends on:** Rolling Qtr Days between Orders

✅ No issues found

## Rolling Qtr Day Variance
**Table:** EOD Data (LV)
```dax
if([Rolling Qtr Days between Orders]=blank(),
blank(),
[Days Since Last Order]- [Rolling Qtr Days between Orders]
)
```
**Depends on:** Days Since Last Order, Rolling Qtr Days between Orders

✅ No issues found

## Avg Sales/Hospital
**Table:** EOD Data (LV)
```dax
sum('Account Alignment'[Net Revenue])/DISTINCTCOUNT('EOD Data (LV)'[Hospital])
```

✅ No issues found

## Measure
**Table:** EOD Data (LV)
```dax
MAX('EOD Data'[Rolling Qtr Start Date])
```

✅ No issues found

## Rolling Qtr Rev Measure
**Table:** EOD Data (LV)
```dax
VAR X =
NETWORKDAYS(
MIN('EOD Data (LV)'[Current_Qtr Start]),
MIN('EOD Data (LV)'[Current_Qtr End]),
1,
Holidays
)
VAR WorkdaysTable =
FILTER(
ALL(DateTable),
DateTable[Elapsed Workdays] = 1
&& DateTable[Date] <= TODAY()
)
VAR StartDate =
MINX(
TOPN(X, WorkdaysTable, DateTable[Date], DESC),
DateTable[Date]
)
RETURN
CALCULATE(
SUM('EOD Data (LV)'[net revenue]),
FILTER(
ALL(DateTable[Date]),
DateTable[Date] >= StartDate
&& DateTable[Date] <= TODAY()
)
)
```

✅ No issues found

## Rolling Qtr -1 Rev Measure
**Table:** EOD Data (LV)
```dax
VAR X =
NETWORKDAYS(
MIN('EOD Data (LV)'[Current_Qtr Start]),
MIN('EOD Data (LV)'[Current_Qtr End]),
1,
Holidays
)
VAR WorkdaysTable =
FILTER(
ALL(DateTable),
DateTable[Elapsed Workdays] = 1
&& DateTable[Date] <= TODAY()
)
VAR RollingQtrStartDate =
MINX(
TOPN(X, WorkdaysTable, DateTable[Date], DESC),
DateTable[Date]
)
VAR RollingQtrMinus1StartDate =
MINX(
TOPN(X * 2, WorkdaysTable, DateTable[Date], DESC),
DateTable[Date]
)
RETURN
CALCULATE(
SUM('EOD Data (LV)'[net revenue]),
FILTER(
ALL(DateTable[Date]),
DateTable[Date] >= RollingQtrMinus1StartDate
&& DateTable[Date] < RollingQtrStartDate
)
)
```

✅ No issues found

## Measure 2
**Table:** EOD Data (LV)
```dax
VAR X =
NETWORKDAYS(
MIN('EOD Data (LV)'[Current_Qtr Start]),
MIN('EOD Data (LV)'[Current_Qtr End]),
1,
Holidays
)
VAR WorkdaysTable =
FILTER(
ALL(DateTable),
DateTable[Elapsed Workdays] = 1
&& DateTable[Date] <= TODAY()
)
VAR StartDate =
MINX(
TOPN(X, WorkdaysTable, DateTable[Date], DESC),
DateTable[Date]
)
RETURN
StartDate
```

✅ No issues found

## RS_Reporting Through
**Table:** EOD Data (LV)
```dax
// The max date in data, respecting filter context
// This is the anchor — "today" for this dataset
CALCULATE(
MAX('EOD Data (LV)'[Date]),
ALL('EOD Data (LV)')
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [filter-context]: ALL('EOD Data (LV)') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

**Requirement:** The maximum (latest) date in the EOD Data table, ignoring all filter context. This is the anchor date for all rolling window calculations.

**Alignment:** POSSIBLE MISMATCH — requirement mentions filtering but no FILTER/CALCULATE in DAX

## RS_Current Qtr Start
**Table:** EOD Data (LV)
```dax
// First day of the quarter containing the reporting-through date
VAR RT = [RS_Reporting Through]
RETURN
DATE(YEAR(RT), (ROUNDUP(DIVIDE(MONTH(RT), 3), 0) * 3) - 2, 1)
```
**Depends on:** RS_Reporting Through

### Findings
- ℹ️ **INFO** [divide-by-zero]: DIVIDE() has only 2 arguments — returns BLANK on zero denominator
  - *Suggestion:* Add a 3rd argument: DIVIDE(x, y, 0) to return 0 instead of BLANK

**Requirement:** First day of the calendar quarter containing the reporting-through date. For example, if reporting through is Feb 15, this returns Jan 1.

**Alignment:** NEEDS REVIEW — 

## RS_Current Qtr End
**Table:** EOD Data (LV)
```dax
EDATE([RS_Current Qtr Start], 3) - 1
```
**Depends on:** RS_Current Qtr Start

✅ No issues found

**Requirement:** Last day of the calendar quarter containing the reporting-through date. For example, if reporting through is Feb 15, this returns Mar 31.

**Alignment:** NEEDS REVIEW — 

## RS_Qtr Workdays
**Table:** EOD Data (LV)
```dax
// Number of workdays in the current calendar quarter
// This is the "X" that defines the rolling window size
NETWORKDAYS(
[RS_Current Qtr Start],
[RS_Current Qtr End],
1,
Holidays
)
```
**Depends on:** RS_Current Qtr End, RS_Current Qtr Start

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

**Requirement:** Count of working days (Monday-Friday, excluding holidays) in the current calendar quarter. Uses the Holidays table for holiday exclusions.

**Alignment:** NEEDS REVIEW — 

## RS_Elapsed Workdays
**Table:** EOD Data (LV)
```dax
// Count of elapsed workdays up to and including reporting-through date
VAR RT = [RS_Reporting Through]
RETURN
CALCULATE(
COUNTROWS(DateTable),
ALL(DateTable),
DateTable[Date] <= RT,
DateTable[Elapsed Workdays] = 1
)
```
**Depends on:** RS_Reporting Through

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

**Requirement:** Count of working days from the current quarter start through the reporting-through date. Represents how far into the quarter we are.

**Alignment:** NEEDS REVIEW — column 'date' mentioned in requirement

## RS_Rolling Qtr Start
**Table:** EOD Data (LV)
```dax
// Walk backward X elapsed workdays from Reporting Through
// X = number of workdays in the current calendar quarter
VAR X = [RS_Qtr Workdays]
VAR RT = [RS_Reporting Through]
VAR WorkdaysUpToRT =
FILTER(
ALL(DateTable),
DateTable[Elapsed Workdays] = 1
&& DateTable[Date] <= RT
)
RETURN
MINX(
TOPN(X, WorkdaysUpToRT, DateTable[Date], DESC),
DateTable[Date]
)
```
**Depends on:** RS_Qtr Workdays, RS_Reporting Through

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

**Requirement:** The start date of the rolling quarter window. Calculated by walking backward X workdays from the reporting-through date, where X equals the number of elapsed workdays in the current calendar quarter.

**Alignment:** LIKELY MATCH — column 'date' mentioned in requirement, column 'elapsed workdays' mentioned in requirement, requirement mentions filtering but no FILTER/CALCULATE in DAX

## RS_Rolling Qtr -1 Start
**Table:** EOD Data (LV)
```dax
// Walk backward X*2 elapsed workdays from Reporting Through
// This gives us the start of the prior rolling quarter
VAR X = [RS_Qtr Workdays]
VAR RT = [RS_Reporting Through]
VAR WorkdaysUpToRT =
FILTER(
ALL(DateTable),
DateTable[Elapsed Workdays] = 1
&& DateTable[Date] <= RT
)
RETURN
MINX(
TOPN(X * 2, WorkdaysUpToRT, DateTable[Date], DESC),
DateTable[Date]
)
```
**Depends on:** RS_Qtr Workdays, RS_Reporting Through

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## RS_Rolling Qtr Rev
**Table:** EOD Data (LV)
```dax
// Revenue from Rolling Qtr Start through Reporting Through
VAR RQStart = [RS_Rolling Qtr Start]
VAR RT = [RS_Reporting Through]
RETURN
CALCULATE(
SUM('EOD Data (LV)'[net revenue]),
FILTER(
ALL(DateTable[Date]),
DateTable[Date] >= RQStart
&& DateTable[Date] <= RT
)
)
```
**Depends on:** RS_Reporting Through, RS_Rolling Qtr Start

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

**Requirement:** Sum of net revenue for all dates from the rolling quarter start through the reporting-through date. This provides a rolling window of revenue that dynamically adjusts with the calendar.

**Alignment:** LIKELY MATCH — column 'date' mentioned in requirement

## RS_Rolling Qtr -1 Rev
**Table:** EOD Data (LV)
```dax
// Revenue from Rolling Qtr -1 Start up to (but not including) Rolling Qtr Start
VAR RQM1Start = [RS_Rolling Qtr -1 Start]
VAR RQStart = [RS_Rolling Qtr Start]
RETURN
CALCULATE(
SUM('EOD Data (LV)'[net revenue]),
FILTER(
ALL(DateTable[Date]),
DateTable[Date] >= RQM1Start
&& DateTable[Date] < RQStart
)
)
```
**Depends on:** RS_Rolling Qtr -1 Start, RS_Rolling Qtr Start

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

**Requirement:** Sum of net revenue for the prior rolling quarter window. The window is from 2X workdays back to X workdays back (exclusive of rolling quarter start). Used for quarter-over-quarter comparison.

**Alignment:** NEEDS REVIEW — 

## RS_Rolling Qtr Days between Orders
**Table:** EOD Data (LV)
```dax
// Average days between orders in the current rolling quarter
// = workdays in window / distinct order count in window
VAR RQStart = [RS_Rolling Qtr Start]
VAR RT = [RS_Reporting Through]
VAR FirstTxn = MAX('EOD Data (LV)'[Date of First Transaction])
VAR EffectiveStart = IF(RQStart < FirstTxn, FirstTxn, RQStart)
VAR OrderCount =
CALCULATE(
DISTINCTCOUNT('EOD Data (LV)'[Sales Order #]),
FILTER(
'EOD Data (LV)',
'EOD Data (LV)'[Date] >= RQStart
&& 'EOD Data (LV)'[Date] <= RT
)
)
RETURN
IF(
OrderCount = 0,
BLANK(),
NETWORKDAYS(EffectiveStart, RT, 1, Holidays)
/ OrderCount
)
```
**Depends on:** RS_Reporting Through, RS_Rolling Qtr Start

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'EOD Data (LV)' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

**Requirement:** Average number of working days between distinct order dates within the rolling quarter window. Calculated as NETWORKDAYS(start, end) divided by the count of distinct order dates in that period. Returns BLANK if there are no orders.

**Alignment:** LIKELY MATCH — 

## RS_Rolling Half Days between Orders
**Table:** EOD Data (LV)
```dax
// Average days between orders from the -1 quarter start through reporting-through
// Matches original logic: full timespan / all orders from -1 start onward
VAR RQM1Start = [RS_Rolling Qtr -1 Start]
VAR RT = [RS_Reporting Through]
VAR FirstTxn = MAX('EOD Data (LV)'[Date of First Transaction])
VAR EffectiveStart = IF(RQM1Start < FirstTxn, FirstTxn, RQM1Start)
VAR OrderCount =
CALCULATE(
DISTINCTCOUNT('EOD Data (LV)'[Sales Order #]),
FILTER(
'EOD Data (LV)',
'EOD Data (LV)'[Date] >= RQM1Start
)
)
RETURN
IF(
OrderCount = 0,
BLANK(),
NETWORKDAYS(EffectiveStart, RT, 1, Holidays)
/ OrderCount
)
```
**Depends on:** RS_Reporting Through, RS_Rolling Qtr -1 Start

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'EOD Data (LV)' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

**Requirement:** Same as RS_Rolling Qtr Days between Orders but over a rolling half-year (2 quarters) window. Used to compare recent ordering frequency against longer-term patterns.

**Alignment:** NEEDS REVIEW — 

## RS_Qtr - Qtr Ordering Behavior
**Table:** EOD Data (LV)
```dax
VAR CurrentDays = [RS_Rolling Qtr Days between Orders]
VAR PriorDays = [RS_Rolling Half Days between Orders]
RETURN
IF(
ISBLANK(CurrentDays) && ISBLANK(PriorDays),
"No Orders for 3+ Months",
IF(
ISBLANK(CurrentDays) || CurrentDays = (1/0),
"No Orders for 3+ Months",
SWITCH(
TRUE(),
ISBLANK(PriorDays), "Ordering More Frequently",
CurrentDays < PriorDays, "Ordering More Frequently",
CurrentDays > PriorDays, "Ordering Less Frequently",
"Ordering More Frequently"
)
)
)
```
**Depends on:** RS_Rolling Half Days between Orders, RS_Rolling Qtr Days between Orders

✅ No issues found

**Requirement:** Classifies each hospital's ordering behavior by comparing rolling quarter days between orders vs rolling half days between orders. Categories: "Ordering More Frequently" if qtr < half (shorter gap = more frequent), "Ordering Less Frequently" if qtr > half, "No Orders for 3+ Months" if no orders in the rolling quarter.

**Alignment:** NEEDS REVIEW — 

## RS_Days Since Last Order
**Table:** EOD Data (LV)
```dax
VAR RT = [RS_Reporting Through]
VAR LastOrderDate = MAX('EOD Data (LV)'[Date])
RETURN
NETWORKDAYS(LastOrderDate, RT, 1, Holidays)
```
**Depends on:** RS_Reporting Through

✅ No issues found

## RS_Rolling Qtr Day Variance
**Table:** EOD Data (LV)
```dax
IF(
[RS_Rolling Qtr Days between Orders] = BLANK(),
BLANK(),
[RS_Days Since Last Order] - [RS_Rolling Qtr Days between Orders]
)
```
**Depends on:** RS_Days Since Last Order, RS_Rolling Qtr Days between Orders

✅ No issues found

## RS_Rolling Qtr Variance
**Table:** EOD Data (LV)
```dax
[RS_Rolling Qtr Rev] - [RS_Rolling Qtr -1 Rev]
```
**Depends on:** RS_Rolling Qtr -1 Rev, RS_Rolling Qtr Rev

### Findings
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## RS_Current Ordering Status
**Table:** EOD Data (LV)
```dax
VAR DayVar = [RS_Rolling Qtr Day Variance]
VAR DaysBO = [RS_Rolling Qtr Days between Orders]
RETURN
IF(
DaysBO = (1/0),
"No Orders in 3+ Months",
IF(DayVar <= 5 && DayVar > 0, "Due for SO",
IF(DayVar <= 10 && DayVar > 5, "1 Wk Overdue for SO",
IF(DayVar <= 15 && DayVar > 10, "2 Wks Overdue for SO",
IF(DayVar <= 20 && DayVar > 15, "3 Wks Overdue for SO",
IF(DayVar > 20, "4 Wks+ Overdue for SO",
IF(DayVar >= -5 && DayVar < 0, "Due for SO within 1 Wk",
IF(DayVar >= -10 && DayVar < -5, "Due for SO within 2 Wks",
IF(DayVar >= -15 && DayVar < -10, "Due for SO within 3 Wks",
IF(DayVar < -15, "Due for SO within 4 Wks",
"Error"
)))))))))
)
```
**Depends on:** RS_Rolling Qtr Day Variance, RS_Rolling Qtr Days between Orders

✅ No issues found

## Prior Qtr ASP
**Table:** EOD Data NO RLS
```dax
sum('EOD Data no rls'[Revenue])/sum('EOD Data no rls'[Sum of Quantity])
```

✅ No issues found

## Revenue Trend per Account per Quarter
**Table:** EOD Data
```dax
(SUM('EOD Data'[net Revenue])/(calculate(DISTINCTCOUNTNOBLANK('EOD Data'[Internal ID]),GeneralAccountList[Active Hospital Count]>=1)))/(NETWORKDAYS(min('EOD Data'[Date]),max('EOD Data'[Date]),1,'Holidays'))*21.5*3
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Average of Revenue divided by Count of Internal ID
**Table:** EOD Data
```dax
DIVIDE(
AVERAGE('EOD Data'[net Revenue]),
DISTINCTCOUNT('EOD Data'[Internal ID])
)
```

### Findings
- ℹ️ **INFO** [divide-by-zero]: DIVIDE() has only 2 arguments — returns BLANK on zero denominator
  - *Suggestion:* Add a 3rd argument: DIVIDE(x, y, 0) to return 0 instead of BLANK

## CohortMonth
**Table:** EOD Data
```dax
CALCULATE(
MIN('EOD Data'[Date]),
ALLEXCEPT('EOD Data', 'EOD Data'[Internal ID])
)
```

✅ No issues found

## Sum of Revenue rolling average
**Table:** EOD Data
```dax
IF(
ISFILTERED('DateTable'[Date]),
ERROR("Time intelligence quick measures can only be grouped or filtered by the Power BI-provided date hierarchy or primary date column."),
VAR __LAST_DATE = ENDOFMONTH('DateTable'[Date].[Date])
VAR __DATE_PERIOD =
DATESBETWEEN(
'DateTable'[Date].[Date],
STARTOFMONTH(DATEADD(__LAST_DATE, -1, MONTH)),
ENDOFMONTH(DATEADD(__LAST_DATE, 1, MONTH))
)
RETURN
AVERAGEX(
CALCULATETABLE(
SUMMARIZE(
VALUES('DateTable'),
'DateTable'[Date].[Year],
'DateTable'[Date].[QuarterNo],
'DateTable'[Date].[Quarter],
'DateTable'[Date].[MonthNo],
'DateTable'[Date].[Month]
),
__DATE_PERIOD
),
CALCULATE(SUM('EOD Data'[net Revenue]), ALL('DateTable'[Date].[Day]))
)
)
```

✅ No issues found

## TotalMonthRevenue_CohortAvg
**Table:** EOD Data
```dax
VAR IsInMonth = ISINSCOPE('EOD Data'[PurchaseMonthSequence])
VAR IsInAccount = ISINSCOPE('EOD Data'[Hospital])
VAR VisibleAccounts = VALUES('EOD Data'[Hospital])
VAR VisibleMonths = VALUES('EOD Data'[PurchaseMonthSequence])
VAR Result =
SWITCH(
TRUE(),

// Cell Level (Account + Month)
IsInAccount && IsInMonth,
SUM('EOD Data'[net Revenue]),

// Row Total (per Account)
IsInAccount && NOT IsInMonth,
AVERAGEX(
VisibleMonths,
CALCULATE(SUM('EOD Data'[net Revenue]))
),

// Column Total (per Month)
NOT IsInAccount && IsInMonth,
AVERAGEX(
VisibleAccounts,
CALCULATE(SUM('EOD Data'[net Revenue]))
),

// Bottom-right grand total (Overall Avg)
NOT IsInAccount && NOT IsInMonth,
AVERAGEX(
VisibleAccounts,
AVERAGEX(
VisibleMonths,
CALCULATE(SUM('EOD Data'[net Revenue]))
)
)
)
RETURN Result
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (3 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly

## RevenueWithPctFooter
**Table:** EOD Data
```dax
VAR VisibleAccounts = VALUES('EOD Data'[Hospital])
VAR VisibleMonths = VALUES('EOD Data'[PurchaseMonthSequence])

// Total revenue per column (month) across accounts
VAR ColumnAvg =
AVERAGEX(
VisibleAccounts,
CALCULATE(SUM('EOD Data'[net Revenue]))
)

// Overall grand average across all accounts & months
VAR OverallAvg =
AVERAGEX(
VisibleAccounts,
AVERAGEX(
VisibleMonths,
CALCULATE(SUM('EOD Data'[net Revenue]))
)
)

// Revenue per cell (account + month)
VAR CellRevenue = SUM('EOD Data'[net Revenue])

// Row average (account total avg across months)
VAR RowAvg =
AVERAGEX(
VisibleMonths,
CALCULATE(SUM('EOD Data'[net Revenue]))
)

RETURN
SWITCH(
TRUE(),

// Normal matrix cells (account & month)
ISINSCOPE('EOD Data'[Hospital]) && ISINSCOPE('EOD Data'[PurchaseMonthSequence]),
CellRevenue,

// Row grand total (account average across months)
ISINSCOPE('EOD Data'[Hospital]) && NOT ISINSCOPE('EOD Data'[PurchaseMonthSequence]),
RowAvg,

// Footer row (column grand total): % of curve
NOT ISINSCOPE('EOD Data'[Hospital]) && ISINSCOPE('EOD Data'[PurchaseMonthSequence]),
DIVIDE(ColumnAvg, OverallAvg),

// Bottom-right corner
BLANK()
)
```

### Findings
- ℹ️ **INFO** [divide-by-zero]: DIVIDE() has only 2 arguments — returns BLANK on zero denominator
  - *Suggestion:* Add a 3rd argument: DIVIDE(x, y, 0) to return 0 instead of BLANK
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (3 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly

## Sales_GrandAvg
**Table:** EOD Data
```dax
IF(
HASONEVALUE('EOD Data'[PurchaseMonthSequence]),
SUM('EOD Data'[Revenue]),
AVERAGEX(
VALUES('EOD Data'[PurchaseMonthSequence]),
CALCULATE(SUM('EOD Data'[Revenue]))
)
)
```

✅ No issues found

## Avg ASP Line
**Table:** EOD Data
```dax
DIVIDE(
SUM('EOD Data'[net Revenue]),
SUM('EOD Data'[Sum of Quantity])
)
```

### Findings
- ℹ️ **INFO** [divide-by-zero]: DIVIDE() has only 2 arguments — returns BLANK on zero denominator
  - *Suggestion:* Add a 3rd argument: DIVIDE(x, y, 0) to return 0 instead of BLANK

## Count of Internal ID running total in Qutr Year
**Table:** EOD Data
```dax
CALCULATE(
DISTINCTCOUNT('EOD Data'[Internal ID]),
FILTER(
CALCULATETABLE(
SUMMARIZE('DateTable', 'DateTable'[Sort Quarter], 'DateTable'[Wk Qutr Year]),
ALLSELECTED('DateTable')
),
ISONORAFTER(
'DateTable'[Sort Quarter], MAX('DateTable'[Sort Quarter]), DESC,
'DateTable'[Wk Qutr Year], MAX('DateTable'[Wk Qutr Year]), DESC
)
)
)
```

✅ No issues found

## Months Post Launch
**Table:** EOD Data
```dax
datediff(
edate(date(Year(min('EOD Data'[Date])),month(min('EOD Data'[Date])),day(min('EOD Data'[Date]))),-1)
,
date(year(today()-1),month(today()-1),day(today()-1))
,
MONTH)
```

✅ No issues found

## Revenue Generating Months
**Table:** EOD Data
```dax
distinctcount('EOD Data'[Start of Month])
```

✅ No issues found

## Monthly Reorder Rate
**Table:** EOD Data
```dax
[Revenue Generating Months]/[Months Post Launch]
```
**Depends on:** Months Post Launch, Revenue Generating Months

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Rollup Months Post Launch
**Table:** EOD Data
```dax
SUMX(
VALUES('generalaccountlist'[internal ID]),
VAR LaunchDate =
CALCULATE(
MINX(
VALUES('eod data'[date]),
min('eod data'[date]
)
))
VAR EndDate =
MIN(
MAX('datetable'[Date]),
[Reporting Through]  -- Assume this is a measure or constant defined elsewhere
)
VAR MonthsActive =
DATEDIFF(LaunchDate, EndDate, MONTH) + 1
RETURN
IF(MonthsActive >= 1, MonthsActive, 0)
)
```
**Depends on:** Reporting Through

✅ No issues found

## Rollup Revenue Generating Months
**Table:** EOD Data
```dax
SUMX(
VALUES('EOD Data'[Internal ID]),
CALCULATE(
DISTINCTCOUNT('EOD Data'[Start of Month])
)
)
```

✅ No issues found

## Rollup Monthly Reorder Rate
**Table:** EOD Data
```dax
[Rollup Revenue Generating Months]/[Rollup Months Post Launch]
```
**Depends on:** Rollup Months Post Launch, Rollup Revenue Generating Months

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## QoQ Declining Accounts
**Table:** EOD Data
```dax
VAR HasSlicerSelection = ISFILTERED('DateTable'[Year Quarter])

VAR SelectedQuarterStart =
IF(
HasSlicerSelection,
MAX('DateTable'[StartofQuarter]),
CALCULATE(
MAX('DateTable'[StartofQuarter]),
FILTER(
ALL('DateTable'),
'DateTable'[Date] <= TODAY() &&
'DateTable'[EndofQuarter] >= TODAY()
)
)
)

VAR PrevQuarterStart = EDATE(SelectedQuarterStart, -3)

VAR SelectedQuarterEnd =
CALCULATE(
MAX('DateTable'[EndofQuarter]),
FILTER(ALL('DateTable'), 'DateTable'[StartofQuarter] = SelectedQuarterStart)
)

VAR PrevQuarterEnd =
CALCULATE(
MAX('DateTable'[EndofQuarter]),
FILTER(ALL('DateTable'), 'DateTable'[StartofQuarter] = PrevQuarterStart)
)

VAR DecliningIDs =
FILTER (
ALL('EOD Data'[Internal ID]),
VAR CurrRev =
CALCULATE(
SUM('EOD Data'[Revenue Qtr Pace]),
REMOVEFILTERS('DateTable'),

'EOD Data'[Date] >= SelectedQuarterStart &&
'EOD Data'[Date] <= SelectedQuarterEnd
)
VAR PrevRev =
CALCULATE(
SUM('EOD Data'[net Revenue]),
REMOVEFILTERS('DateTable'),

'EOD Data'[Date] >= PrevQuarterStart &&
'EOD Data'[Date] <= PrevQuarterEnd
)
RETURN
NOT ISBLANK(PrevRev) && CurrRev < PrevRev
)

RETURN
COUNTROWS(DecliningIDs)
```

### Findings
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (5 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Quarters Post Launch
**Table:** EOD Data
```dax
IF(
DATEDIFF(
IF(
MIN(DateTable[Date]) > MIN(GeneralAccountList[adjusted Date of First Sale]),
MIN(DateTable[Date]),
MIN(GeneralAccountList[adjusted Date of First Sale])
),
IF(
MAX(DateTable[Date]) > [Reporting Through],
[Reporting Through],
MAX(DateTable[Date])
),
QUARTER
) >= 1,

DATEDIFF(
IF(
MIN(GeneralAccountList[adjusted Date of First Sale]) < MIN(DateTable[Date]),
MIN(DateTable[Date]),
MIN(GeneralAccountList[adjusted Date of First Sale])
),
IF(
MAX(DateTable[Date]) > [Reporting Through],
[Reporting Through],
MAX(DateTable[Date])
),
QUARTER
) + 1,

0
)
```
**Depends on:** Reporting Through

✅ No issues found

## Revenue Generating Quarters
**Table:** EOD Data
```dax
distinctcount('EOD Data'[Start of Quarter])
```

✅ No issues found

## Quarterly Reorder Rate
**Table:** EOD Data
```dax
[Revenue Generating Quarters]/[Quarters Post Launch]
```
**Depends on:** Quarters Post Launch, Revenue Generating Quarters

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Rollup Revenue Generating Quarters
**Table:** EOD Data
```dax
SUMX(
VALUES('EOD Data'[Internal ID]),
CALCULATE(
DISTINCTCOUNT('EOD Data'[Start of Quarter])
)
)
```

✅ No issues found

## Rollup Quarters Post Launch
**Table:** EOD Data
```dax
SUMX(
VALUES(GeneralAccountList[internal ID]),
VAR LaunchDate =
CALCULATE(
MINX(
VALUES(GeneralAccountList[Adjusted Date of First Sale]),
IF(
GeneralAccountList[Adjusted Date of First Sale] < MIN(DateTable[Date]),
MIN('DateTable'[Date]),
GeneralAccountList[Adjusted Date of First Sale]
)
)
)
VAR EndDate =
MIN(
MAX('DateTable'[Date]),
[Reporting Through]
)
VAR QuartersActive = DATEDIFF(LaunchDate, EndDate, QUARTER) + 1
RETURN
IF(QuartersActive >= 1, QuartersActive, 0)
)
```
**Depends on:** Reporting Through

✅ No issues found

## Rollup Quarterly Reorder Rate
**Table:** EOD Data
```dax
[Rollup Revenue Generating quarters]/[Rollup quarters Post Launch]
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## TotalQuarterRevenue_CohortAvg
**Table:** EOD Data
```dax
VAR IsInQuarter = ISINSCOPE('EOD Data'[PurchaseQuarterSequence])
VAR IsInAccount = ISINSCOPE('EOD Data'[Hospital])
VAR VisibleAccounts = VALUES('EOD Data'[Hospital])
VAR VisibleQuarters = VALUES('EOD Data'[PurchaseQuarterSequence])
VAR Result =
SWITCH(
TRUE(),

// Cell Level (Account + Month)
IsInAccount && IsInQuarter,
SUM('EOD Data'[net Revenue]),

// Row Total (per Account)
IsInAccount && NOT IsInQuarter,
AVERAGEX(
VisibleQuarters,
CALCULATE(SUM('EOD Data'[net Revenue]))
),

// Column Total (per Month)
NOT IsInAccount && IsInQuarter,
AVERAGEX(
VisibleAccounts,
CALCULATE(SUM('EOD Data'[net Revenue]))
),

// Bottom-right grand total (Overall Avg)
NOT IsInAccount && NOT IsInQuarter,
AVERAGEX(
VisibleAccounts,
AVERAGEX(
VisibleQuarters,
CALCULATE(SUM('EOD Data'[net Revenue]))
)
)
)
RETURN Result
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (3 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly

## Daily Sales - Daily Quota
**Table:** EOD Data
```dax
sum('EOD Data'[Qtr Daily Sales])-sum('Quota Revenue'[Month Daily Quota])
```

✅ No issues found

## Qtr Daily Sales - Qtr Daily Goal
**Table:** EOD Data
```dax
sum('EOD Data'[Qtr Daily Sales])-sum('Quota Revenue'[Qtr Daily Quota])
```

✅ No issues found

## % Ordering Accounts
**Table:** EOD Data
```dax
DISTINCTCOUNT('EOD Data'[Internal ID])/sum('TM Region Sites'[Monthly Total Accounts])
```

✅ No issues found

## EOD Total Hospitals
**Table:** EOD Data
```dax
calculate(DISTINCTCOUNT([internal id]),all('eod data'),filter('eod data','EOD Data'[Date]>=date(2023,1,1)),filter('eod data','EOD Data'[Date]<=max('eod data'[date])))
```

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'eod data' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'eod data' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ℹ️ **INFO** [filter-context]: ALL('eod data') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## EOD Total Hospitals 2
**Table:** EOD Data
```dax
calculate(distinctcount('eod data'[internal id]),all('eod data'),filter('eod data','eod data'[date]<=max('eod data'[date])))
```

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'eod data' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ℹ️ **INFO** [filter-context]: ALL('eod data') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## % Ordering Accounts Qtr
**Table:** EOD Data
```dax
DISTINCTCOUNT('EOD Data'[Internal ID])/sum('TM Region Sites qtr'[qtr Total Accounts])
```

✅ No issues found

## Annualized Sales
**Table:** EOD Data
```dax
sum('eod data'[net revenue])/sum('DateTable'[Elapsed Workdays])*250
```

✅ No issues found

## 4 Qtr Growth
**Table:** EOD Data
```dax
sum([Current Qtr Revenue Trend]) + sum('EOD Data'[Quarter -1 Revenue])+sum('EOD Data'[Quarter -2 Revenue])+sum('EOD Data'[Quarter -3 Revenue])
```

✅ No issues found

## Annual Goal
**Table:** EOD Data
```dax
10000000
```

✅ No issues found

## H2 HP ASP Goal
**Table:** EOD Data
```dax
5338
```

✅ No issues found

## Revenue 0
**Table:** EOD Data
```dax
sum('eod data'[revenue])+0
```

✅ No issues found

## HP Access Rev
**Table:** EOD Data
```dax
calculate(
sum('EOD Data'[net Revenue]),
filter('Product Family','Product Family'[System]="HiPoint"),
filter('Product Family','Product Family'[Clearance]="Access")
)
```

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'Product Family' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'Product Family' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

## HP Reperfusion Rev
**Table:** EOD Data
```dax
calculate(
sum('EOD Data'[net Revenue]),
filter('Product Family','Product Family'[System]="HiPoint"),
filter('Product Family','Product Family'[Clearance]="Reperfusion")
)
```

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'Product Family' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'Product Family' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

## HP System Rev
**Table:** EOD Data
```dax
[HP Access Rev]+[HP Reperfusion Rev]
```
**Depends on:** HP Access Rev, HP Reperfusion Rev

### Findings
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## National Months Post Launch
**Table:** EOD Data
```dax
datediff(
date(Year(min('EOD Data'[Date])),month(min('EOD Data'[Date])),day(min('EOD Data'[Date])))
,
date(year(today()-1),month(today()-1),day(today()-1))
,
MONTH)+1
```

✅ No issues found

## National Revenue Generating Months
**Table:** EOD Data
```dax
distinctcount('EOD Data'[Start of Month])+0
```

✅ No issues found

## National Monthly Reorder Rate
**Table:** EOD Data
```dax
[National Revenue Generating Months]/[national Months Post Launch]
```
**Depends on:** National Revenue Generating Months

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Revenue Qtr Pace Measure
**Table:** EOD Data
```dax
sum('EOD Data'[net Revenue])
/sum(DateTable[Elapsed Workdays])
*sum(DateTable[Workdays])
```

✅ No issues found

## Revenue Qtr Pace Measure Acuity
**Table:** EOD Data
```dax
calculate(
sum('EOD Data'[net Revenue]),
filter(DateTable,'DateTable'[Current Qtr]=1
)
)
+
(

calculate(
sum(
'eod data'[net revenue]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91)
)
)
/
calculate(
sum(
'DateTable'[Workdays]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91) &&
'datetable'[elapsed workdays]=1
)
)

*
calculate(
sum (
'DateTable'[Current Qtr]),
filter(
(DateTable),
'DateTable'[Elapsed Workdays]=0 &&
DateTable[Workdays]=1)
)
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (4 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Revenue Qtr Pace Measrue Acuity 2
**Table:** EOD Data
```dax
calculate(
sum('EOD Data'[net Revenue]),
filter(DateTable,'DateTable'[Current Qtr]=1
)
)

+

(
(
calculate(
sum(
'eod data'[net revenue]),
Filter(
all('DateTable'),
'datetable'[date]>=minx(
TOPN( 91,
FILTER(
ALL ( DateTable ),
DateTable[Elapsed Workdays] = 1
),
DateTable[Date],
DESC ),
DateTable[Date]
)
)
)

/

calculate(
sum(
'DateTable'[Workdays]),
Filter(
all('DateTable'),
'datetable'[date]>=minx(
TOPN( 91,
FILTER(
ALL ( DateTable ),
DateTable[Elapsed Workdays] = 1
),
DateTable[Date],
DESC ),
DateTable[Date]
) &&
'datetable'[date]<=today()-1
)
)
)
*
calculate(
sum (
'DateTable'[Current Qtr]),
filter(
(DateTable),
'DateTable'[Elapsed Workdays]=0 &&
DateTable[Workdays]=1)
)
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (4 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Acuity 90 Day Rev
**Table:** EOD Data
```dax
calculate(
sum(
'eod data'[net revenue]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91)
)
)
```

### Findings
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Acuity Workdays last 90 days
**Table:** EOD Data
```dax
calculate(
sum(
'DateTable'[Workdays]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91) &&
'datetable'[date]<=today()-1
)
)
```

### Findings
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Acuity Remaining Workdays
**Table:** EOD Data
```dax
calculate(
sum (
'DateTable'[Current Qtr]),
filter(
(DateTable),
'DateTable'[Elapsed Workdays]=0 &&
DateTable[Workdays]=1)
)
```

✅ No issues found

## Acuity Pace
**Table:** EOD Data
```dax
(
(
calculate(
sum(
'eod data'[net revenue]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91)
)
)
/
calculate(
sum(
'DateTable'[Workdays]),
Filter(
all('DateTable'),
'datetable'[date]>=(today()-91) &&
'datetable'[elapsed workdays]=1
)
)
)
*
calculate(
sum (
'DateTable'[Current Qtr]),
filter(
(DateTable),
'DateTable'[Elapsed Workdays]=0 &&
DateTable[Workdays]=1)
)
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (3 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored
- ℹ️ **INFO** [filter-context]: ALL('DateTable') removes all filters on this table
  - *Suggestion:* Verify this is intentional — slicers on this table will be ignored

## Rolling Qtr -1 Days between Orders
**Table:** EOD Data
```dax
if(
calculate(
distinctcount('EOD Data'[SALES ORDER #]),
Filter('eod data',
[date]>=max('EOD Data'[Rolling Qtr -1 Start Date]) &&
[date]<max('EOD Data'[Rolling Qtr Start Date])
))=0,blank(),

NETWORKDAYS(
IF(max([Rolling Qtr -1 Start Date])<max('EOD Data'[Date of First Transaction]),max('EOD Data'[Date of First Transaction]),MAX('EOD Data'[Rolling Qtr -1 Start Date])),
max('EOD Data'[Rolling Qtr Start Date]),
1,
Holidays)

/
calculate(
distinctcount('EOD Data'[SALES ORDER #]),
Filter('eod data',
[date]>=max('EOD Data'[Rolling Qtr -1 Start Date]) &&
[date]<max('EOD Data'[Rolling Qtr Start Date])
))
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'eod data' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'eod data' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance
- ℹ️ **INFO** [complexity]: Nested CALCULATE detected (2 levels)
  - *Suggestion:* Review filter context transitions — nested CALCULATE can behave unexpectedly

## % to Quota ATM
**Table:** EOD Data
```dax
sum('EOD Data'[Net Revenue])
/
'Quota ATM'[Quota ATM]
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Remaining Quota ATM
**Table:** EOD Data
```dax
sum('EOD Data'[Net Revenue])
-
'Quota ATM'[Quota ATM]
```

✅ No issues found

## ATM Run Rate % to Quota
**Table:** EOD Data
```dax
[Revenue Qtr Pace Measure]
/
'Quota ATM'[Quota ATM]
```
**Depends on:** Revenue Qtr Pace Measure

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## ATM Run Rate v Quota
**Table:** EOD Data
```dax
[Revenue Qtr Pace Measure]-'Quota ATM'[Quota ATM]
```
**Depends on:** Revenue Qtr Pace Measure

✅ No issues found

## ATM Daily Sales to Hit Goal
**Table:** EOD Data
```dax
if([Remaining Quota ATM]>0,0,
[Remaining Quota ATM]/
(sum(DateTable[Elapsed Workdays])-sum(DateTable[Workdays]))
)
```
**Depends on:** Remaining Quota ATM

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Hospital Count by PD
**Table:** GeneralAccountList (LV)
```dax
COUNT('GeneralAccountList (LV)'[Current Qtr Product Depth])
```

✅ No issues found

## Prior Qtr Hospital Count by PD
**Table:** GeneralAccountList (LV)
```dax
COUNT('GeneralAccountList (LV)'[Prior Qtr Product Depth]
)
```

✅ No issues found

## Inactive Hospitals
**Table:** GeneralAccountList (LV)
```dax
count('GeneralAccountList (LV)'[internal id])-sum('GeneralAccountList (LV)'[Active Hospital Count])
```

✅ No issues found

## Launched Sites
**Table:** GeneralAccountList
```dax
count('GeneralAccountList'[Internal ID])
```

✅ No issues found

## Account Designation Less Converted
**Table:** GeneralAccountList
```dax
count(GeneralAccountList[Account Designation])-sum(GeneralAccountList[Converted Reperfusion Accounts])
```

✅ No issues found

## New Hospitals 2
**Table:** GeneralAccountList
```dax
calculate(count('GeneralAccountList'[Internal ID]),'GeneralAccountList'[Active Hospital Count]=1)
```

✅ No issues found

## Eligibility
**Table:** PClub
```dax
if(and(sum(PClub[Hire Date])<=date(2025,1,31),sum(PClub[YTD PTQ])>=1),"Eligible","Ineligible")
```

✅ No issues found

## BC2.0 ASP Variance to Quota
**Table:** Product Family
```dax
1250-'EOD Data'[ASP]
```

✅ No issues found

## HP88 Repurfusion ASP Variance to Quota
**Table:** Product Family
```dax
6295-'EOD Data'[ASP]
```

✅ No issues found

## HP70 Repurfusion ASP Variance to Quota
**Table:** Product Family
```dax
5795 -'EOD Data'[ASP]
```

✅ No issues found

## PTQ
**Table:** PTQ EOD Data
```dax
sum('account alignment'[Net Revenue])/sum('PTQ Revenue Quota'[Quota])
```

✅ No issues found

## PTQ Annualized Sales
**Table:** PTQ EOD Data
```dax
sum('PTQ EOD Data'[Revenue])/sum('ptq DateTable'[elapsed workdays])*250
```

✅ No issues found

## PTQ PTQ
**Table:** PTQ Revenue Quota
```dax
sum('PTQ Revenue Quota'[Net Revenue])/sum('PTQ Revenue Quota'[Quota])
```

✅ No issues found

## Quota ATM
**Table:** Quota ATM
```dax
calculate(
sum('Quota ATM'[Quota]),
USERELATIONSHIP('Quota ATM'[Quota Month End],'DateTable'[Date])
)
```

✅ No issues found

## New Site Count
**Table:** Quota New Site
```dax
calculate(distinctcount('GeneralAccountList'[Internal ID]),
'GeneralAccountList'[Date of First Sale]>=min('Launch Date Table'[Date])
,'GeneralAccountList'[Date of First Sale]<=max('Launch Date Table'[Date]))
```

✅ No issues found

## New Site Goals
**Table:** Quota New Site
```dax
sum('Quota New Site'[New Site Goal])
```

✅ No issues found

## New Site Delta
**Table:** Quota New Site
```dax
[New Site Count]-[New Site Goals]
```
**Depends on:** New Site Count, New Site Goals

### Findings
- ℹ️ **INFO** [blank-handling]: Arithmetic on measures without BLANK guard — BLANK propagates through +, -, *
  - *Suggestion:* Wrap with IF(ISBLANK([Measure]), 0, [Measure]) or use COALESCE()

## Product % to Quota
**Table:** Quota Product Revenue
```dax
sum('EOD Data'[Revenue])/sum('Quota Product Revenue'[Quota])
```

✅ No issues found

## Region % of Quota
**Table:** Quota Rev by Region
```dax
sum('EOD Data'[net Revenue])/sum('Quota Rev by Region'[Quota])
```

✅ No issues found

## Region Actual v Quota
**Table:** Quota Rev by Region
```dax
sum('EOD Data'[net Revenue])-sum('Quota Rev by Region'[Quota])
```

✅ No issues found

## Region Pace vs Quota
**Table:** Quota Rev by Region
```dax
[Revenue Qtr Pace Measure] - sum('Quota Rev by region'[Quota])
```
**Depends on:** Revenue Qtr Pace Measure

✅ No issues found

## Region Pace % to Quota
**Table:** Quota Rev by Region
```dax
[Revenue Qtr Pace Measure]/sum('Quota Rev by region'[Quota])
```
**Depends on:** Revenue Qtr Pace Measure

✅ No issues found

## Actual vs Quota
**Table:** Quota Revenue by Rep (LV)
```dax
sum('EOD Data (LV)'[net Revenue]) - sum('Quota Revenue by Rep (LV)'[Quota])
```

✅ No issues found

## Pace vs Quota
**Table:** Quota Revenue
```dax
[Revenue Qtr Pace Measure] - sum('Quota Revenue'[Quota])
```
**Depends on:** Revenue Qtr Pace Measure

✅ No issues found

## Qtr Daily Sales to Achieve Goal
**Table:** Quota Revenue
```dax
iferror(if('Quota Revenue'[Actual vs Quota]>0,0,'Quota Revenue'[Actual vs Quota]/(sum(DateTable[Elapsed Workdays])-sum(DateTable[Workdays]))),"")
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Daily Quota
**Table:** Quota Revenue
```dax
sum('Quota Revenue'[Quota])/
networkdays(min(DateTable[Date]),max(DateTable[Date]),1,Holidays)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## Qtr Daily Quota Measure
**Table:** Quota Revenue
```dax
sum('Quota Revenue'[Quota])/
networkdays(
min('Quota Revenue'[Quota Month Start]),
max('Quota Revenue'[Quota Month End]),
1,
Holidays
)
```

### Findings
- ⚠️ **WARNING** [divide-by-zero]: Raw division (/) without DIVIDE() or IF zero-guard
  - *Suggestion:* Use DIVIDE(numerator, denominator, 0) to handle divide-by-zero safely

## RS_Behavior Hospital Count
**Table:** RS_Ordering Summary
```dax
VAR SelectedCategory = SELECTEDVALUE('RS_Ordering Summary'[Ordering Behavior])
VAR HospitalBehaviors =
ADDCOLUMNS(
VALUES('EOD Data (LV)'[Hospital]),
"Behavior", [RS_Qtr - Qtr Ordering Behavior]
)
RETURN
COUNTROWS(
FILTER(
HospitalBehaviors,
[Behavior] = SelectedCategory
)
)
```
**Depends on:** RS_Qtr - Qtr Ordering Behavior

### Findings
- ⚠️ **WARNING** [blank-handling]: SELECTEDVALUE() without fallback — returns BLANK when multiple values selected
  - *Suggestion:* Add a default: SELECTEDVALUE(Column, "default") or handle multi-select

**Requirement:** Count of distinct hospitals matching each ordering behavior category. Used to populate the ordering behavior summary donut chart.

**Alignment:** NEEDS REVIEW — column 'behavior' mentioned in requirement

## New Sites
**Table:** TM Region Sites
```dax
calculate(
DISTINCTCOUNT('GeneralAccountList'[Internal ID]),
filter('generalaccountlist',
GeneralAccountList[Date of First Transaction].[Date]))
```

### Findings
- ⚠️ **WARNING** [performance]: FILTER iterates entire 'generalaccountlist' table
  - *Suggestion:* Consider FILTER(VALUES(...)) or KEEPFILTERS() for better performance

## New Hospitals
**Table:** Total and New Accounts
```dax
calculate(count('Total and New Accounts'[Hospital Name]),'GeneralAccountList'[Active Hospital Count]=1)
```

✅ No issues found

## Total Hospitals
**Table:** Total and New Accounts
```dax
calculate(count('Total and New Accounts'[Date of First Sale]),'Total and New Accounts'[Hospital Rev]>0
,
all(DateTable),filter(DateTable,'DateTable'[Date]<max('EOD Data'[Reporting Through Column]))
)
```

✅ No issues found

# Exploratory Data Analysis Report

## Overall Dataset Statistics
- **Total Records**: 1158808
- **Date Range**: 2012-01-01 to 2017-06-22

## Remaining Missing Values
```text
Reported Date                0
State Name                   0
District Name                0
Market Name                  0
Crop                         0
Variety                      0
Arrivals (Tonnes)            0
Min Price (Rs./Quintal)      0
Max Price (Rs./Quintal)      0
Modal Price (Rs./Quintal)    0
Mandi                        0
Year                         0
Month                        0
```

## Crop Distribution (Wheat vs Rice)
```text
Crop
Wheat    696445
Rice     462363
```

## Geographic Coverage
- **Total States**: 26
- **Total Districts**: 437
- **Total Mandis**: 1928

### Top 10 States by Records
```text
State Name
Uttar Pradesh     257000
Madhya Pradesh    197270
West Bengal       142690
Gujarat           102540
Rajasthan         102055
Maharashtra        97119
Karnataka          48891
Jharkhand          44063
Assam              34770
Kerala             31432
```

### Top 10 Mandis by Records
```text
Mandi
Gujarat - Vadodara(Baroda) - Vadodara         8537
Kerala - Alappuzha - Alappuzha                6621
West Bengal - Bankura - Bishnupur(Bankura)    5513
Gujarat - Dahod - Dahod                       5193
Jharkhand - Koderma - Koderma                 4761
West Bengal - Malda - Samsi                   4665
Karnataka - Shimoga - Shimoga                 4504
Assam - Kamrup - P.O. Uparhali Guwahati       4395
Gujarat - Junagarh - Mangrol                  4261
Karnataka - Kolar - Chintamani                4181
```

## Variety Distribution

### Wheat Varieties (Top 5)
```text
Variety
Other          392493
Dara           100071
Lokwan          43122
Local           17048
147 Average     16869
```

### Rice Varieties (Top 5)
```text
Variety
Other     145544
Iii        72832
Fine       59091
Coarse     29192
Common     21720
```

## Mandi Suitability for Time Series Forecasting
To train a robust forecasting model, we need mandis with long, continuous historical records.
Total months in dataset: 66

### Top 10 Mandis by Continuity and Volume
```text
      Crop                                              Mandi  Months_With_Data         mean          std  count  Volatility (CV)
215   Rice                     Kerala - Alappuzha - Alappuzha                66  3517.453449  1575.701229   5639         0.447966
83    Rice              Gujarat - Vadodara(Baroda) - Vadodara                64  2582.483553   564.760908   4864         0.218689
53    Rice            Assam - Kamrup - P.O. Uparhali Guwahati                66  3972.212514  2391.704914   4395         0.602109
944  Wheat                       Gujarat - Junagarh - Mangrol                66  1648.233748   217.137730   4261         0.131740
168   Rice                     Karnataka - Kolar - Chintamani                63  2770.147094  1057.498802   4181         0.381748
203   Rice                      Karnataka - Shimoga - Shimoga                63  2875.994601   806.597524   4075         0.280459
43    Rice                            Assam - Cachar - Cachar                66  2599.025413   645.725686   4053         0.248449
186   Rice  Karnataka - Mangalore(Dakshin Kannad) - Mangalore                63  2639.352415   376.131829   3913         0.142509
103   Rice                      Jharkhand - Koderma - Koderma                66  2380.332303   614.096385   3882         0.257988
692   Rice         West Bengal - Bankura - Bishnupur(Bankura)                66  2224.403897   283.826828   3746         0.127597
```

## Suspicious / Outlier Values
- **High Price Outliers (> 3162.50)**: 66671 records (5.75%)
- Note: Extreme high prices might be due to rare premium varieties or data entry errors.

## Modeling Recommendations
Based on the EDA:
1. **Crops**: Both Wheat and Rice have sufficient data. We can train separate models or one model with Crop as a feature.
2. **Mandis**: We should filter for mandis that have at least 80-90% data continuity (e.g., > 120 months of data). Training a single model for all mandis without sufficient data would lead to poor forecasting.
3. **Target Variable**: `Modal Price (Rs./Quintal)` is well-distributed and is the standard indicator of market price.
4. **Features**: Include Month (for seasonality), Year, and lag features (e.g., previous month's price). Arrivals can be included if available at inference time, but lag prices are more crucial.
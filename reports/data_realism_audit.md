# Data realism and reconciliation audit

Read-only checks of the existing synthetic dataset; no regeneration or forced distribution adjustment.

## Financial and cycle distributions

| index | opportunity_amount | net_deal_value | discount_percentage | engagement_score | sales_cycle_days |
| --- | --- | --- | --- | --- | --- |
| count | 198000.0 | 198000.0 | 198000.0 | 198000.0 | 186289.0 |
| mean | 904282.57 | 831719.41 | 7.99 | 54.5 | 65.57 |
| std | 1080743.99 | 995092.04 | 4.56 | 19.54 | 48.06 |
| min | 31008.34 | 28291.6 | 0.01 | 1.1 | 2.0 |
| 1% | 88594.18 | 81212.05 | 0.79 | 12.1 | 4.0 |
| 25% | 271117.63 | 248723.14 | 4.55 | 40.0 | 21.0 |
| 50% | 520731.21 | 478632.21 | 7.25 | 55.1 | 60.0 |
| 75% | 1086834.1 | 998781.89 | 10.69 | 69.5 | 101.0 |
| 99% | 5279602.74 | 4867517.51 | 21.14 | 92.7 | 187.0 |
| max | 22091285.47 | 20058887.21 | 32.2 | 99.9 | 359.0 |

Amounts are INR; discount/engagement are percentage-point scales; cycles are days. Long tails are expected for enterprise contracts and remain visible rather than being removed merely for looking unusual.

## Observed stages and outcomes

| sales_stage | deal_status | count |
| --- | --- | --- |
| Closed Lost | Closed Lost | 141102 |
| Closed Won | Closed Won | 45187 |
| Demo | Open | 1257 |
| Demo | Stalled | 177 |
| Discovery | Open | 2189 |
| Discovery | Stalled | 164 |
| Lead | Open | 2187 |
| Negotiation | Open | 919 |
| Negotiation | Stalled | 408 |
| Proposal | Open | 1766 |
| Proposal | Stalled | 483 |
| Qualified | Open | 2131 |
| Qualified | Stalled | 30 |

## Variation by region

| region | opportunities | win_rate | average_deal_size | average_sales_cycle | open_pipeline |
| --- | --- | --- | --- | --- | --- |
| East | 48646 | 0.2473 | 777584.5874 | 112.8235 | 2322451737.77 |
| North | 49662 | 0.2442 | 768221.1064 | 113.2149 | 2478629001.65 |
| South | 49976 | 0.2378 | 770741.3314 | 112.8497 | 2312867304.48 |
| West | 49716 | 0.2411 | 792867.8864 | 113.2761 | 2509999267.55 |

## Variation by industry

| industry | opportunities | win_rate | average_deal_size | average_sales_cycle | open_pipeline |
| --- | --- | --- | --- | --- | --- |
| BFSI | 39263 | 0.2403 | 884780.2314 | 113.3052 | 2167930369.77 |
| Healthcare | 38898 | 0.2428 | 732761.0112 | 112.5989 | 1885159057.23 |
| IT Services | 39275 | 0.2434 | 741772.3601 | 113.1326 | 1779742717.47 |
| Manufacturing | 39636 | 0.2418 | 747012.9064 | 112.851 | 1842749594.11 |
| Retail | 40928 | 0.2445 | 781106.8425 | 113.3051 | 1948365572.87 |

## Variation by product

| product | opportunities | win_rate | average_deal_size | average_sales_cycle | open_pipeline |
| --- | --- | --- | --- | --- | --- |
| Cloud Enablement | 49566 | 0.2412 | 814312.512 | 113.012 | 2554214154.67 |
| Data Advisory | 49573 | 0.2407 | 1048924.3499 | 113.4386 | 3188029235.26 |
| Security Services | 49160 | 0.2438 | 724314.7196 | 112.7461 | 2220672796.68 |
| Workflow Suite | 49701 | 0.2446 | 526650.9693 | 112.9724 | 1661031124.84 |

## Variation by customer_segment

| customer_segment | opportunities | win_rate | average_deal_size | average_sales_cycle | open_pipeline |
| --- | --- | --- | --- | --- | --- |
| Enterprise | 31735 | 0.2119 | 2332852.9545 | 121.1153 | 4369590325.53 |
| Mid-market | 72948 | 0.2422 | 838744.6636 | 111.7379 | 3641764285.13 |
| SMB | 93317 | 0.2533 | 288823.3161 | 111.7196 | 1612592700.79 |

## Variation by sales_rep_id

| sales_rep_id | opportunities | win_rate | average_deal_size | average_sales_cycle | open_pipeline | ytd_attainment |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 4188 | 0.2469 | 729854.9046 | 111.3938 | 191188373.33 | 0.8407207629197896 |
| 2 | 4099 | 0.1192 | 820019.5263 | 110.8116 | 152698968.72 | 0.40952673719409133 |
| 3 | 3937 | 0.196 | 737326.1424 | 111.4472 | 168581211.28 | 0.708314148068094 |
| 4 | 4351 | 0.3958 | 806855.3576 | 115.1288 | 214046581.42 | 1.6572480106518428 |
| 5 | 3939 | 0.2236 | 765907.2803 | 110.8185 | 154372656.97 | 0.7935284318091211 |
| 6 | 4310 | 0.2619 | 749241.9883 | 113.3639 | 208071607.27 | 0.9673036944837688 |
| 7 | 4420 | 0.1844 | 757231.4767 | 112.0246 | 198557056.88 | 0.5312595165362557 |
| 8 | 4191 | 0.2575 | 752216.1405 | 113.5182 | 178463559.27 | 0.8545495839122436 |
| 9 | 4202 | 0.2359 | 688927.5198 | 113.3961 | 230759715.06 | 0.6948125698897227 |
| 10 | 4282 | 0.2454 | 813442.6407 | 114.1271 | 208150131.02 | 1.005333794246807 |
| 11 | 4098 | 0.2388 | 843083.1999 | 111.5877 | 198766393.69 | 0.8795063387262567 |
| 12 | 3959 | 0.243 | 777357.9443 | 113.1009 | 209211049.57 | 0.727471592410999 |
| 13 | 3797 | 0.3061 | 746304.1045 | 112.3373 | 201184946.42 | 0.9785916232672379 |
| 14 | 4279 | 0.2809 | 770115.5891 | 112.7162 | 215476521.91 | 0.9212887048166585 |
| 15 | 4215 | 0.2261 | 856569.8765 | 112.0929 | 206237044.88 | 0.9275965301618257 |
| 16 | 3957 | 0.1669 | 903316.3706 | 113.2839 | 171997569.99 | 1.0251147493385173 |
| 17 | 4462 | 0.1867 | 751599.4335 | 111.6717 | 211224822.82 | 0.6156670461712331 |
| 18 | 4037 | 0.2629 | 831304.1691 | 114.0859 | 226005683.89 | 0.9031916022014431 |
| 19 | 4588 | 0.2456 | 769108.7372 | 113.0667 | 257630554.35 | 0.8570599177344449 |
| 20 | 4046 | 0.213 | 827332.967 | 112.9412 | 189005036.88 | 0.8666263913593064 |
| 21 | 4396 | 0.2175 | 684851.8287 | 113.0874 | 186336947.7 | 0.6257579799348859 |
| 22 | 4358 | 0.2328 | 849623.8339 | 113.5529 | 238964065.11 | 0.9661217899784847 |
| 23 | 3876 | 0.2662 | 789553.796 | 113.9689 | 204512966.26 | 0.9630710066512936 |
| 24 | 3705 | 0.3064 | 781588.84 | 116.0294 | 201423107.34 | 1.0048049371638492 |
| 25 | 4144 | 0.35 | 841262.5343 | 114.8884 | 259661027.53 | 1.2420237713597184 |
| 26 | 3748 | 0.1702 | 707780.6588 | 111.9983 | 163079829.11 | 0.5209730209809668 |
| 27 | 4122 | 0.3241 | 702561.2567 | 113.2995 | 202137989.78 | 1.4707341198621238 |
| 28 | 4392 | 0.141 | 728212.4048 | 110.8112 | 180831173.36 | 0.48889919584826136 |
| 29 | 4041 | 0.2835 | 762096.2632 | 113.1735 | 236448689.24 | 1.0018689268226018 |
| 30 | 4242 | 0.2355 | 784155.4366 | 112.0447 | 227586596.95 | 1.1140127419317094 |
| 31 | 4556 | 0.1802 | 777057.8365 | 111.9613 | 220826806.72 | 0.588564811190099 |
| 32 | 3891 | 0.2505 | 765557.3459 | 112.1329 | 182635414.94 | 1.0109825260286955 |
| 33 | 4423 | 0.2424 | 795101.0374 | 113.5793 | 236367750.42 | 0.9218324632588484 |
| 34 | 3973 | 0.2035 | 787126.4172 | 113.358 | 131006418.42 | 0.8868445093046607 |
| 35 | 3874 | 0.2706 | 735729.3334 | 114.6291 | 198192866.11 | 1.1202927095382518 |
| 36 | 4256 | 0.291 | 786442.4414 | 114.1105 | 239854439.07 | 1.304158010107888 |
| 37 | 3976 | 0.2072 | 731831.0101 | 111.1392 | 178519495.37 | 0.7227703799694694 |
| 38 | 3691 | 0.3225 | 872312.4939 | 114.1952 | 212427496.63 | 0.981147591653035 |
| 39 | 4362 | 0.2262 | 848346.5479 | 114.9001 | 199893896.0 | 1.029207741096899 |
| 40 | 4413 | 0.2776 | 770962.121 | 113.168 | 209906196.36 | 1.0193017539222216 |
| 41 | 3733 | 0.1885 | 764581.6755 | 112.3283 | 142975031.09 | 0.6046561080144739 |
| 42 | 4270 | 0.2494 | 760883.5191 | 112.3064 | 211945944.34 | 1.1174416241613243 |
| 43 | 4130 | 0.2109 | 718413.2347 | 112.3634 | 161979730.46 | 0.8202887209142655 |
| 44 | 4111 | 0.1966 | 729604.3778 | 111.2343 | 174340370.89 | 0.5929773233341494 |
| 45 | 3732 | 0.2831 | 738193.7379 | 111.4715 | 189381709.37 | 0.7985766040853088 |
| 46 | 3940 | 0.3011 | 804000.3312 | 114.7808 | 200980276.97 | 1.0817036917948557 |
| 47 | 4119 | 0.2607 | 760269.3347 | 111.2565 | 207961166.1 | 0.8584663595876056 |
| 48 | 4169 | 0.2501 | 786125.9448 | 113.4417 | 232140424.19 | 0.9120945483567553 |

## Integrity and temporal checks

- 198,000 unique clean opportunities, 827,893 activities and 705,379 stage visits inspected.
- Every activity falls within its opportunity lifetime. Advanced activities occur only after the relevant stage entry.
- All stored cohort KPIs independently reconcile to the underlying records.
- Validation precedes held-out test; all backtest cutoffs precede forecast periods.
- Independently recomputed selected-model held-out WAPE: 14.115409%.
- Future-outcome mutation regression tests verify that later statuses/stages do not affect earlier snapshot predictions.

## Interpretation and limitations

The observed deal values, discount range, imperfect win rates, cycle dispersion and differences between representatives are plausible for this simulated commercial scale. This is a structural sanity audit, not calibration against a real Indian company. Quotas are planning assumptions. Forward-only stage visits, one account per customer, immutable initial expected dates and full-contract bookings simplify the process. No distribution was modified during this audit.

# Deversifi Data Challenge

1. [Goal](#Goal)
2. [Disclaimer](#Disclaimer)
3. [Preliminary Work](#Preliminary_Work)
4. [Important note](#Important_note)
5. [Data cleaning](#Data_cleaning)
6. [Data aggregation](#Data_aggregation)
7. [Data exploration](#Data_exploration)
8. [What sources have the best conversion](#What_sources_have_the_best_conversion)
9. [What sources have brought the most value over this period](What_sources_have_brought_the_most_value_over_this_period)
10. [Conclusion](Conclusion)


## Goal

You are the Data Analyst at DeversiFi. This afternoon the Marketing and Product teams have a meeting to review the different sources of users to our app over the last week.
You have the data attached (explanation of it below) and will be asked 2 questions:

- What sources have the best conversion?
- What sources have brought the most value over this period?

## Disclaimer
For this analysis I have decided to use SQL.

In my opinion SQL is the best tool because of its beautiful and friendly syntax, as well as, the possibility to manage data directly from the database, without any intermediate steps.

Moreover, SQL ensures fast and reproducible results.

In order to present the results, I have decided to use simple tables instead of graphical representations.

## Preliminary_Work
First of all, it is important to create [a proper database structure](https://github.com/robimalco/deversifi/blob/main/structure.sql) able to host our data.

As a first initial task, I have uploaded all the data using [this python script](https://github.com/robimalco/deversifi/blob/main/load_data.py).

## Important_note

> :x: While developing this work, I noticed how the trade_id *TR_3320* presents an extremely high value of 9705308440 SUSHI.

In order to produce more meaningful results, this value has been changed into 9.705308440:
``` sql
UPDATE trades SET amount= 9.705308440 WHERE trade_ID = 'TR_3320';
```

## Data_cleaning

Clean the column *source* of the table *connected_wallets*:

``` sql
UPDATE connected_wallets SET source = 'twitter' WHERE source LIKE '%twitter%';
UPDATE connected_wallets SET source = 'reddit' WHERE source LIKE '%reddit%';
UPDATE connected_wallets SET source = 'deversifi' WHERE source LIKE '%deversifi%';
```

## Data_aggregation
Add the column *source* to the tables *registrations* and *trades*:
``` sql
UPDATE registrations r SET source = c.source FROM connected_wallets c WHERE r.address = c.address;
UPDATE trades t SET source = c.source FROM connected_wallets c WHERE t.address = c.address;
```

## Data_exploration

Our customer funnel has three steps:

Wallet Connected --> User Registered --> Trade Done

Let's measure how many users we have at each step:

``` sql
WITH
	funnel_connected_wallets AS (
		SELECT
			source,
			COUNT(DISTINCT address) AS count_users
		FROM connected_wallets
		GROUP BY 1),
	funnel_registrations AS (
		SELECT
			source,
			COUNT(DISTINCT address) AS count_users
		FROM registrations
		GROUP BY 1),
	funnel_trades AS (
		SELECT
			source,
			COUNT(DISTINCT address) AS count_users
		FROM trades
		GROUP BY 1)
SELECT
	fc.source,
	fc.count_users AS connected_users,
	fr.count_users AS registered_users,
	ft.count_users AS traded_users
FROM funnel_connected_wallets fc
LEFT JOIN funnel_registrations fr ON(fc.source = fr.source)
LEFT JOIN funnel_trades ft ON(fr.source = ft.source)
ORDER BY 2 DESC;
```

As results we have:

|  source  | connected_users  | registered_users  | traded_users |
|----------|-----------------:|------------------:|-------------:|
| twitter  |             371  |              230  |          230 |
| _email   |             163  |              163  |          163 |
| reddit   |             133  |              133  |          133 |
| deversifi|             132  |              131  |          131 |
| _blog    |             110  |               94  |           94 |
| _discord |              90  |               90  |           90 |
| nan      |               1  |                   |              |


It seems that for the purpose of this simulation, the step *registered_users* can be avoided, because every user which completes the registration makes a trade.

## What_sources_have_the_best_conversion

First of all, let's give a proper definition of conversion:

> "A user can be considered converted as soon as completes the first trade"

This query allows us to answer this question:

``` sql
WITH
	funnel_connected_wallets AS (
		SELECT
			source,
			COUNT(DISTINCT address) AS count_users
		FROM connected_wallets
		GROUP BY 1),
	funnel_trades AS (
		SELECT
			source,
			COUNT(DISTINCT address) AS count_users
		FROM trades
		GROUP BY 1)
SELECT
	fc.source,
	ROUND(100.0 * ft.count_users / fc.count_users, 0) AS conversion_rate
FROM funnel_connected_wallets fc
LEFT JOIN funnel_trades ft ON(fc.source = ft.source)
WHERE fc.source != 'nan'
ORDER BY 2 DESC;
```

As results we have:

|  source  | conversion_rate %|
|----------|----------------:|
| _discord |             100 |
| _email   |             100 |
| reddit   |             100 |
| deversifi|              99 |
| _blog    |              85 |
| twitter  |              62 |

Based on this basic overview, *Discord*, *Email* and *Reddit* are the sources with the best conversion.

## What_sources_have_brought_the_most_value_over_this_period

In order to answer this question we need to add the token price into the *trades* table:
``` sql
UPDATE trades t SET price = tp.price FROM token_prices tp WHERE t.pair LIKE '%'|| tp.token || '%';
``` 


Moreover, we can add the volume of the trade:

``` sql
UPDATE trades t SET volume = price * amount;
``` 

Our *trades* table now looks like this:

| id| trade_id |  address   |   pair    |    amount      |  source   |  price   |      volume|
|---|----------|------------|-----------|---------------:|-----------|---------:|-----------:|
| 11| TR_11    | 0x00119619 | ETH:USD   | -0.6448572118  | _blog     |  2800.0  | -1805      |
| 12| TR_12    | 0x00184486 | ETH:USD   |   1.086133144  | twitter   |  2800.0  |   3041     |
| 13| TR_13    | 0x001B23E0 | SUSHI:USD |  -356.5727694  | twitter   |    9.43  |   -3362    |
| 14| TR_14    | 0x00118CEB | DOGE:USD  |   3305.849609  | deversifi |     1.2  |      3967  |
| 15| TR_15    | 0x00103AA0 | BTC:USD   |  0.1345378536  | twitter   | 43000.0  |  5785      |


Now we can finally discover the most profitable source in terms of volume:

``` sql
SELECT
    source,
    ROUND(SUM(ABS(volume))) AS volume
FROM trades
GROUP BY 1
ORDER BY 2 DESC;
``` 

> :warning: Please note how the absolute value has been used. This because for Deversifi both sell and buy transactions are "positive" generator of revenues!

Here the results:

|  source |     total_volume |
|-----------|---------------:|
| deversifi| 14140957        |
| twitter  | 8501289         |
| _email   | 4450184         |
| reddit   | 3345410         |
| _blog    | 2509714         |
| _discord |  957219         |

## Conclusion

Here the full comparison of the sources:

|  source  | conversion_rate %| total_volume  |
|----------|----------------:|---------------:|
| _discord |             100 |     0.9M       |
| _email   |             100 |     4.4M       |
| reddit   |             100 |     3.3M       |
| deversifi|              99 |     14M        |
| _blog    |              85 |     2.5M       |
| twitter  |              62 |     8.5M       |

The most profitable source is *Deversifi*, which is probably when a user comes directly to the platform using SEO/SEM/organic results. Not only the conversion is almost 100%, but the total volume eclipses many other sources.

*Twitter* is also a great source of revenue, but a deeper work has to be made in order to increase the conversion rate.

All other sources are presenting similar results.

I am personally surprised at the low result of *Discord*. In this case a better work has to be made to engage more relevant users.
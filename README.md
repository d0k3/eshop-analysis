# 3DS eShop analysis tool
_A python script to help you get deeper insights into the Nintendo 3DS eshops_

# Requirements
To run this script, you need the following:
* an up-to-date installation of Python 3 (at least 3.6.x)
* the requests module installed (`py -3 -mpip install requests` from the command line)

# What it does
This script will scrape the Nintendo 3DS eShops for all available regions (> 200 regions), merge the data, and compare with the [3dsdb](http://www.3dsdb.com/) and the data from _that titlekey site_. It gives insights (among others) into what titles are available globally, and what titles have already been archived.

# How to run
Just run the script via `py -3 eat.py` (or `python3 eat.py` on unix). To include information about titlekeys into the results __(highly recommended)__, add `-t [TITLEKEYURL]` or `--titlekeyurl [TITLEKEYURL]`, whereas `[TITLEKEYURL]` is the URL (with 'http//') of _that titlekeys site_. If you don't want to do this every time, you may also edit `titlekeyurl` in the source code, it's right at the top. To add proper title ids and title sizes to the results __(also highly recommended)__, you need to provide `ctr-common-1.crt` and `ctr-common-1.key`.

You may also limit the scope of analysed regions via `-r [REGION]` or `--region=[REGION]`, whereas `[REGION]` is `english`, `main` or the two letter country code of a specific region. Resulting CSV files will be written to the `results` subdirectory, intermediate dumps will be written to the `dumped` subdirectory.

# Credits
I actually learnt Python writing this script, and doing so wouldn't have been possible with @ihaveamac's help. @ihaveamac also started this by providing the eShop parser function. Thanks a gigaton!

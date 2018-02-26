#!/usr/bin/env python3

import os
import sys

import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import copy
import csv
from xml.etree import ElementTree
from typing import List

titlekeyurl = None 
urlbase = 'https://samurai.ctr.shop.nintendo.net/samurai/ws/{lang}/titles?offset={offs}'

dumpdest = 'dumped'
resultdest = 'results'

csv_eshop_analysis = resultdest + '/' + 'eshop_analysis_all_in_one.csv'
csv_3dsdb_releases = resultdest + '/' + '3dsdb_releases.csv'
csv_missing_3dsdb_from_eshop = resultdest + '/' + 'missing_3dsdb_from_eshop.csv'
csv_missing_retail_dumps_no_download = resultdest + '/' + 'missing_retail_dumps_no_download.csv'
csv_missing_downloads_only_retail = resultdest + '/' + 'missing_downloads_only_retail.csv'
csv_missing_titlekeys = resultdest + '/' + 'missing_titlekeys.csv'
csv_missing_archive_eshop = resultdest + '/' + 'missing_archive_eshop.csv'
csv_missing_archive_all = resultdest + '/' + 'missing_archive_all.csv'

csv_fieldnames_eshop = ['product_code', 'region_id', 'name', 'publisher', 'publisher_id', 'genre', 'release_eshop', 'release_retail', 'eshop_regions', 'score', 'votes', 'titlekey_known', '3dsdb_id', 'alternative_download', 'alternative_with_titlekey']
csv_fieldnames_3dsdb = ['title_id', 'product_code', 'region_id', 'name', 'publisher', 'region', 'languages', '3dsdb_id', 'alternative_download', 'alternative_with_titlekey']

langs_english = ('US', 'GB', 'AU')
langs_main = ('US', 'GB', 'AU', 'JP', 'ES', 'DE', 'IT', 'FR', 'NL', 'KR', 'TW', 'HK')
langs_all = ('US', 'GB', 'AU', 'JP', 'ES', 'DE', 'IT', 'FR', 'NL', 'AX', 'AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AQ', 'AG', 'AR', 'AM', 'AW', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BV', 'BR', 'IO', 'BN', 'BG', 'BF', 'BI', 'KH', 'CM', 'CA', 'CV', 'KY', 'CF', 'TD', 'CL', 'CN', 'CX', 'CC', 'CO', 'KM', 'CD', 'CG', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'ER', 'EE', 'ET', 'FK', 'FO', 'FJ', 'FI', 'GF', 'PF', 'TF', 'GA', 'GM', 'GE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GN', 'GW', 'GY', 'HT', 'HM', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IL', 'JM', 'JO', 'KZ', 'KE', 'KI', 'KP', 'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'AN', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NF', 'MP', 'NO', 'OM', 'PK', 'PW', 'PS', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'RE', 'RO', 'RU', 'RW', 'SH', 'KN', 'LC', 'PM', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'CS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'GS', 'LK', 'SD', 'SR', 'SJ', 'SZ', 'SE', 'CH', 'SY', 'TW', 'TJ', 'TZ', 'TH', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'UM', 'UY', 'UZ', 'VU', 'VA', 'VE', 'VN', 'VG', 'VI', 'WF', 'EH', 'YE', 'ZM', 'ZW')

merged_eshop_elements: List[ElementTree.Element] = []
db_release_elements: List[ElementTree.Element] = []
enctitlekeydb_data = []


def write_eshop_content(el, out):
    # sort data
    for ee in el:
        if ee.tag != 'content':
            print(ee.tag)
            print(ee.get('id'))
    el.sort(key=lambda x: int(x.get('index')))

    # generate merged XML
    merged_root: ElementTree.Element = ElementTree.Element('contents')
    merged_root.set('contents', str(len(el)))
    merged_root.extend(el)

    # save to file
    merged = ElementTree.ElementTree(merged_root)
    merged.write(out)


def merge_eshop_content(cn, pc, l):
    dup = False
    tt = cn.find('title')

    for cn0 in merged_eshop_elements:
        tt0 = cn0.find('title')
        pc0 = tt0.find('product_code').text

        if pc == pc0:
            # duplicate found, merge data
            dup = True

            sel = cn0.find('eshop_regions').find(l)
            sel.text = 'true'

            if tt.find('retail_sales').text == 'true':
                tt0.find('retail_sales').text = 'true'
            if tt.find('eshop_sales').text == 'true':
                tt0.find('eshop_sales').text = 'true'
            if tt.find('demo_available').text == 'true':
                tt0.find('demo_available').text = 'true'
            if tt.find('aoc_available').text == 'true':
                tt0.find('aoc_available').text = 'true'

            rd = tt.find('release_date_on_eshop')
            rd0 = tt0.find('release_date_on_eshop')
            if rd is not None and rd0 is not None and rd0.text > rd.text:
                rd0.text = rd.text
            
            rd = tt.find('release_date_on_retail')
            rd0 = tt0.find('release_date_on_retail')
            if rd is not None and rd0 is not None and rd0.text > rd.text:
                rd0.text = rd.text

            sr = tt.find('star_rating_info')
            sr0 = tt0.find('star_rating_info')
            if sr is not None and sr0 is not None:
                vt = int(sr.find('votes').text) + int(sr0.find('votes').text)
                s1 = int(sr.find('star1').text) + int(sr0.find('star1').text)
                s2 = int(sr.find('star2').text) + int(sr0.find('star2').text)
                s3 = int(sr.find('star3').text) + int(sr0.find('star3').text)
                s4 = int(sr.find('star4').text) + int(sr0.find('star4').text)
                s5 = int(sr.find('star5').text) + int(sr0.find('star5').text)
                sc = round(((s1 * 1) + (s2 * 2) + (s3 * 3) + (s4 * 4) + (s5 * 5)) / vt, 2)

                sr0.find('votes').text = str(vt)
                sr0.find('star1').text = str(s1)
                sr0.find('star2').text = str(s2)
                sr0.find('star3').text = str(s3)
                sr0.find('star4').text = str(s4)
                sr0.find('star5').text = str(s5)
                sr0.find('score').text = str(sc)

            break

    # not duplicate - copy, create eshop_region info and add element
    if not dup:
        cncp = copy.deepcopy(cn)
        ttcp = cncp.find('title')

        # add eshop_regions
        sel = ElementTree.SubElement(cncp, 'eshop_regions')
        for lng in langs:
            cur = ElementTree.SubElement(sel, lng)
            cur.text = 'false'
            if lng == l:
                cur.text = 'true'

        # add titlekey (if available)
        sel = ElementTree.SubElement(cncp, 'enctitlekey')
        if ttcp.find('eshop_sales').text == 'true':
            for ttk in enctitlekeydb_data:
                if ttk['serial'] == pc:
                    sel.text = ttk['encTitleKey']
                    break

        # remove unneeded stuff
        sel = ttcp.find('rating_info')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('price_on_retail')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('price_on_retail_detail')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('tentative_price_on_eshop')
        if sel is not None:
            ttcp.remove(sel)
        sel = ttcp.find('banner_url')
        if sel is not None:
            ttcp.remove(sel)

        merged_eshop_elements.append(cncp)

    # true if mnew addition
    return not dup


def get_eshop_content():
    # handle eshop content
    with requests.session() as s:
        for l in langs:
            count_ok = 0
            count_new = 0
            offset = 0
            title_elements: List[ElementTree.Element] = []
            while True:
                url = urlbase.format(lang=l, offs=offset)
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
                with s.get(url, verify=False) as r:
                # with s.get(url, verify='nintendo-ca-g3.pem') as r:
                    el = ElementTree.fromstring(r.content)
                    # check this eshop
                    if el.find('contents') is None:
                        break
                    # the only element inside an eshop element should be a contents one.
                    contents_root: ElementTree.Element = list(el)[0]

                    # check length
                    length = int(contents_root.get('length'))
                    if length <= 0:
                        break
                    offset += length

                    # on screen output
                    print('Scraping ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\r')

                    # clean up and add elements from the contents root to the title_elements lists
                    for cn in contents_root:
                        pc = cn.find('title').find('product_code').text
                        if not pc.startswith(('CTR-', 'KTR-')):
                            continue
                        title_elements.append(cn)

                        # merge eshope content
                        if merge_eshop_content(cn, pc, l):
                            count_new += 1
                        count_ok += 1

            if offset > 0:
                print('Scraping ' + l + ' eshop content: ' + str(count_ok) + ' / ' + str(offset) + ' entries (' + str(count_new) + ' new)', end = '\n')
                # save to file
                out = dumpdest + '/contents-eshop-' + l + '.xml'
                write_eshop_content(title_elements, out)

    # save merged data to file
    out = dumpdest + '/contents-eshop-MERGED.xml'
    write_eshop_content(merged_eshop_elements, out)


def get_3dsdb_content():
    print('Loading 3DSDB cart data: ...', end = '\r')

    url = 'http://3dsdb.com/xml.php'
    with requests.get(url) as r:
        out = dumpdest + '/3dsdb.xml'
        with open(out, 'wb') as f:
            f.write(r.content)

        el = ElementTree.fromstring(r.content)

        # count and get rid of crap (eshop, demo, update, movie, selfmade) entries
        count_all = 0
        count_ok = 0
        for rl in el:
            count_all += 1
            type = rl.find('type').text
            serial = rl.find('serial').text
            code = serial[4:8]
            if not serial.startswith(('CTR-', 'KTR-')):
                continue
            if not code.startswith(('A', 'B', 'C', 'E')):
                continue
            if type != '1':
                continue
            db_release_elements.append(rl)
            count_ok += 1

        print('Loading 3DSDB cart data: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')


def get_enctitlekeydb_data():
    global enctitlekeydb_data
    print('Loading titlekeydb data: ...', end = '\r')

    url = titlekeyurl + '/json_enc'
    with requests.get(url) as r:
        out = dumpdest + '/titlkeydb.json'
        with open(out, 'wb') as f:
            f.write(r.content)
        enctitlekeydb_data = r.json()

        print('Loading titlekeydb data: ' + str(len(enctitlekeydb_data)) + ' entries', end = '\n')


def analyse_3dsdb(english_only):
    # analyse the data and build CSV files
    with open(csv_missing_3dsdb_from_eshop, 'w', encoding='utf-8') as md_csv, open(csv_3dsdb_releases, 'w', encoding='utf-8') as db_csv:

        # find cart dumps missing in eshop
        mdw = csv.DictWriter(md_csv, fieldnames = csv_fieldnames_3dsdb, lineterminator='\n')
        dbw = csv.DictWriter(db_csv, fieldnames = csv_fieldnames_3dsdb, lineterminator='\n')
        mdw.writeheader()
        dbw.writeheader()
        count_all = len(db_release_elements)
        count_missing = 0

        for rl in db_release_elements:
            print('Adding missing entries from 3dsdb.com: ' + str(count_missing) + ' / ' + str(count_all) + ' entries', end = '\r')
            serial = rl.find('serial').text
            type = serial[0:3]
            code = serial[4:8]
            gid = serial[4:7]
            rid = serial[7:8]
            pc_p = type + '-P-' + code
            pc_n = type + '-N-' + code
            eshop_alt = []
            eshop_alt_ttk = []

            if english_only and not rid in ('A', 'E', 'P'):
                continue

            found = False
            for cn in merged_eshop_elements:
                pc = cn.find('title').find('product_code').text
                es = cn.find('title').find('eshop_sales').text
                ttk = cn.find('enctitlekey').text
                if pc == pc_n or pc == pc_p:
                    found = True
                elif pc[6:9] == gid and es == 'true':
                    eshop_alt.append(pc)
                    if ttk is not None:
                        eshop_alt_ttk.append(pc)

            title_id = rl.find('titleid').text
            region = rl.find('region').text
            lang = rl.find('languages').text
            name = rl.find('name').text
            pub = rl.find('publisher').text
            dbid = rl.find('id').text

            if not found:
                mdw.writerow({'title_id': title_id, 'product_code': pc_p, 'region_id': rid, 'name': name, 'publisher': pub, 'region': region, 'languages': lang, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk)})
                count_missing += 1
            dbw.writerow({'title_id': title_id, 'product_code': pc_p, 'region_id': rid, 'name': name, 'publisher': pub, 'region': region, 'languages': lang, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk)})

        print('Adding missing entries from 3dsdb.com: ' + str(count_missing) + ' / ' + str(count_all) + ' entries', end = '\n')


def build_eshop_analysis():
    with open(csv_eshop_analysis, 'w', encoding='utf-8') as ea_csv:
        eaw = csv.DictWriter(ea_csv, fieldnames = csv_fieldnames_eshop, lineterminator='\n')
        eaw.writeheader()
        count_all = len(merged_eshop_elements)
        count_ok = 0

        # process merged eshop elements
        for cn in merged_eshop_elements:
            print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')

            tt = cn.find('title')
            pl = tt.find('platform')
            pub = tt.find('publisher')
            sr = tt.find('star_rating_info')
            es = cn.find('eshop_regions')

            pc = tt.find('product_code').text
            rid = pc[9:10]
            name = tt.find('name').text
            genre = tt.find('display_genre').text
            pub_name = pub.find('name').text
            pub_id = pub.get('id')

            rel_e = ''
            if tt.find('release_date_on_eshop') is not None:
                rel_e = tt.find('release_date_on_eshop').text

            rel_r = ''
            if tt.find('release_date_on_retail') is not None:
                rel_r = tt.find('release_date_on_retail').text

            eshop_regs = []
            for l in langs:
                if es.find(l).text == 'true':
                    eshop_regs.append(l)

            score = ''
            votes = ''
            if sr is not None and sr.find('score') is not None:
                score = sr.find('score').text
                votes = sr.find('votes').text

            titlekey = cn.find('enctitlekey').text
            titlekey_known = 'false'
            if titlekey is not None and titlekey != '':
                titlekey_known = 'true'

            dbid = ''
            serial = pc[0:3] + '-' + pc[6:10]
            for rl in db_release_elements:
                if rl.find('serial').text == serial:
                    dbid = rl.find('id').text
                    break

            code = pc[6:10]
            gid = pc[6:9]
            eshop_alt = []
            eshop_alt_ttk = []
            for cn0 in merged_eshop_elements:
                ttk0 = cn0.find('enctitlekey').text
                es0 = cn0.find('title').find('eshop_sales').text
                pc0 = cn0.find('title').find('product_code').text
                code0 = pc0[6:10]
                gid0 = pc0[6:9]
                if code0 != code and gid0 == gid and es0 == 'true':
                    eshop_alt.append(pc0)
                    if ttk0 is not None:
                        eshop_alt_ttk.append(pc0)

            eaw.writerow({'product_code': pc, 'region_id': rid, 'name': name, 'publisher': pub_name, 'publisher_id': pub_id, 'genre': genre, 'release_eshop': rel_e, 'release_retail': rel_r, 'eshop_regions': '/'.join(eshop_regs), 'score': score, 'votes': votes, 'titlekey_known': titlekey_known, '3dsdb_id': dbid, 'alternative_download': ' / '.join(eshop_alt), 'alternative_with_titlekey': ' / '.join(eshop_alt_ttk)})
            count_ok += 1

        # append data from 3DSDB
        with open(csv_missing_3dsdb_from_eshop, encoding='utf-8') as md_csv:
            mdr = csv.DictReader(md_csv)
            for r in mdr:
                print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\r')
                eaw.writerow({'product_code': r['product_code'], 'region_id': r['region_id'], 'name': r['name'], 'publisher': r['publisher'], 'release_retail': '3DSDB', '3dsdb_id': r['3dsdb_id'], 'alternative_download': r['alternative_download'], 'alternative_with_titlekey': r['alternative_with_titlekey']})
                count_ok += 1
                count_all += 1

        print('Merging all entries: ' + str(count_ok) + ' / ' + str(count_all) + ' entries', end = '\n')


def analyse_missing():
    with open(csv_eshop_analysis, 'r', encoding='utf-8') as ea_csv, open(csv_missing_retail_dumps_no_download, 'w', encoding='utf-8') as mrd_csv, open(csv_missing_downloads_only_retail, 'w', encoding='utf-8') as mdr_csv, open(csv_missing_titlekeys, 'w', encoding='utf-8') as mtk_csv, open(csv_missing_archive_eshop, 'w', encoding='utf-8') as mfe_csv, open(csv_missing_archive_all, 'w', encoding='utf-8') as mfa_csv:
        ear = csv.DictReader(ea_csv)
        mrdw = csv.DictWriter(mrd_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mdrw = csv.DictWriter(mdr_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mtkw = csv.DictWriter(mtk_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mfew = csv.DictWriter(mfe_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mfaw = csv.DictWriter(mfa_csv, fieldnames=csv_fieldnames_eshop, lineterminator='\n')
        mrdw.writeheader()
        mdrw.writeheader()
        mtkw.writeheader()
        mfew.writeheader()
        mfaw.writeheader()

        m_retail_dumps = 0
        m_downloads = 0
        m_downloads_alt = 0
        m_titlekey = 0
        m_archive_eshop = 0
        m_archive_all = 0
        count_all = 0

        for r in ear:
            has_download = r['release_eshop'] is not None and r['release_eshop'] != ''
            has_titlekey = r['titlekey_known'] is not None and r['titlekey_known'] != ''
            has_cartdump = r['3dsdb_id'] is not None and r['3dsdb_id'] != ''
            has_alt = r['alternative_download'] is not None and r['alternative_download'] != ''
            has_alt_ttk = r['alternative_with_titlekey'] is not None and r['alternative_with_titlekey'] != ''

            print('Deeper analysis: ' + str(count_all) + ' entries', end = '\r')

            if not has_download and not has_cartdump:
                m_retail_dumps += 1
                mrdw.writerow(r)

            if has_download and not has_titlekey:
                m_titlekey += 1
                mtkw.writerow(r)

            if not has_download:
                m_downloads += 1

            if not has_download and not has_alt:
                m_downloads_alt += 1
                mdrw.writerow(r)

            if (not has_download or not has_titlekey) and not has_alt_ttk:
                m_archive_eshop += 1
                mfew.writerow(r)
                if not has_cartdump:
                    m_archive_all += 1
                    mfaw.writerow(r)

            count_all += 1

        print('Deeper analysis: ' + str(count_all) + ' entries', end = '\n')

        # print summary
        print('\n')
        print('Analysis summary:')
        print('--------------------------------')

        print('Total titles processed         :', str(count_all))
        if titlekeyurl:
            print('Titles with missing titlekeys  :', str(m_titlekey))
        print('Titles with no downloads       :', str(m_downloads))
        print('... and no alt downloads       :', str(m_downloads_alt))
        print('Missing cartdumps, no download :', str(m_retail_dumps))
        if titlekeyurl:
            print('No archival from eshop         :', str(m_archive_eshop))
        print('No archival from eshop or 3dsdb:', str(m_archive_all))


if __name__ == '__main__':
    langs = langs_all
    english_only = False

    # say hello
    print('\n')
    print('3DS eshop analysis tool (c) 2018')
    print('--------------------------------')

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--region", type=str, help="specify eshop region (english/main/all/XX)")
    if not titlekeyurl:
        parser.add_argument("-t", "--titlekeyurl", type=str, help="specify titlekey page url (with http://)")
    args = parser.parse_args()

    if args.region == 'english':
        langs = langs_english
        english_only = True
    elif args.region == 'main':
        langs = langs_main
    elif args.region == 'all':
        langs = langs_all
    elif args.region:
        langs = []
        langs.append(args.region)
        english_only = True

    if args.titlekeyurl:
        titlekeyurl = args.titlekeyurl

    # make dirs for data
    os.makedirs(dumpdest, exist_ok=True)
    os.makedirs(resultdest, exist_ok=True)

    # get all required contents
    if titlekeyurl:
        get_enctitlekeydb_data()
    get_3dsdb_content()
    get_eshop_content()
    analyse_3dsdb(english_only)
    build_eshop_analysis()
    analyse_missing()

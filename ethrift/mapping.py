"""Maps values from ebay urls to FindItemsAdvanced accepted values."""

EBAY_DOMAIN_TO_GLOBAL_ID = {'ebay.com': 'EBAY-US', 'ebay.ca': 'EBAY-ENCA',
                            'cafr.ebay.ca': 'EBAY-FRCA', 'ebay.co.uk': 'EBAY-GB',
                            'ebay.com.au': 'EBAY-AU', 'ebay.at': 'EBAY-AT',
                            'benl.ebay.be': 'EBAY-NLBE', 'befr.ebay.be': 'EBAY-FRBE',
                            'ebay.fr': 'EBAY-FR', 'ebay.de': 'EBAY-DE',
                            'ebay.it': 'EBAY-IT', 'ebay.nl': 'EBAY-NL',
                            'ebay.es': 'EBAY-ES', 'ebay.ch': 'EBAY-CH',
                            'ebay.com.hk': 'EBAY-HK', 'ebay.com.sg': 'EBAY-SG',
                            'ebay.ie': 'EBAY-IE', 'ebay.com.my': 'EBAY-MY',
                            'ebay.ph': 'EBAY-PH', 'ebay.pl': 'EBAY-PL'}

EBAY_COUNTRY_GROUPS = {'EUROPE': ['PT', 'ES', 'DE', 'CH', 'AT', 'BE', 'BG',
                                  'CZ', 'CY', 'HR', 'DK', 'SI', 'EE', 'FI',
                                  'FR', 'GR', 'HU', 'IE', 'IT', 'LT', 'LU',
                                  'NL', 'PL', 'SE', 'GB', 'LV', 'MT', 'RO',
                                  'SK', 'ME', 'MK', 'AL', 'RS', 'TR', 'BA',
                                  'AM', 'AZ', 'BY', 'MD', 'GE', 'UA', 'LI',
                                  'NO', 'IS', 'CH'],
                       'EUROPEAN UNION': ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ',
                                          'DK', 'EE', 'FI', 'FR', 'DE', 'GR',
                                          'HU', 'IE', 'IT', 'LV', 'LT', 'LU',
                                          'MT', 'NL', 'PL', 'PT', 'RO', 'SK',
                                          'SI', 'ES', 'SE'],
                       'ASIA': ['AF', 'BH', 'BD', 'BN', 'BT', 'BR', 'KH',
                                'CN', 'YE', 'HK', 'IN', 'ID', 'IR', 'IL',
                                'JP', 'JO', 'KR', 'KW', 'LA', 'LB', 'MO',
                                'MY', 'MN', 'NP', 'OM', 'PK', 'PG', 'PH',
                                'QA', 'SA', 'SG', 'LK', 'SY', 'TH', 'TR',
                                'AE', 'VN'],
                       'NORTH AMERICA': ['US', 'CA', 'MX', 'AG', 'BS', 'BB',
                                         'BZ', 'CR', 'CU', 'DM', 'DO', 'SV',
                                         'GD', 'GT', 'HT', 'HN', 'JM', 'NI',
                                         'PA', 'KN', 'LC', 'VC', 'TT'],
                       'FRANCE BORDERS': ['ES', 'IT', 'CH', 'LU', 'DE', 'BE'],
                       # I wish I didn't have to make this
                       'WORLDWIDE': ['US', 'CA', 'GB', 'AF', 'AL', 'DZ', 'AS',
                                     'AD', 'AO', 'AI', 'AG', 'AR', 'AM', 'AW',
                                     'AU', 'AU', 'AZ', 'BS', 'BH', 'BD', 'BB',
                                     'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO',
                                     'BA', 'BW', 'BR', 'VG', 'BN', 'BG', 'BF',
                                     'MM', 'BI', 'KH', 'CM', 'CV', 'KY', 'CF',
                                     'TD', 'CL', 'CN', 'CO', 'KM', 'CD', 'CG',
                                     'CK', 'CR', 'CI', 'HR', 'CY', 'CZ', 'DK',
                                     'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ',
                                     'ER', 'EE', 'ET', 'FK', 'FJ', 'FI', 'FR',
                                     'GF', 'PF', 'GA', 'GM', 'GE', 'DE', 'GH',
                                     'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT',
                                     'GN', 'GW', 'GY', 'HT', 'HN', 'HK', 'HU',
                                     'IS', 'IN', 'ID', 'IR', 'IE', 'IL', 'IT',
                                     'JM', 'SJ', 'JP', 'JO', 'KZ', 'KE', 'KI',
                                     'KR', 'KW', 'KG', 'LA', 'LV', 'LB', 'LI',
                                     'LT', 'LU', 'MO', 'MK', 'MG', 'MW', 'MY',
                                     'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU',
                                     'YT', 'MX', 'FM', 'MD', 'MC', 'MN', 'MS',
                                     'MA', 'MZ', 'NA', 'NR', 'NP', 'NL', 'AN',
                                     'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'NO',
                                     'OM', 'PK', 'PW', 'PA', 'PG', 'PY', 'PE',
                                     'PH', 'PL', 'PT', 'PR', 'QA', 'RO', 'RU',
                                     'RW', 'SH', 'KN', 'LC', 'PM', 'VC', 'SM',
                                     'SA', 'SN', 'SC', 'SL', 'SG', 'SK', 'SI',
                                     'SB', 'SO', 'ZA', 'ES', 'LK', 'SR', 'SZ',
                                     'SE', 'CH', 'SY', 'PF', 'TW', 'TJ', 'TZ',
                                     'TH', 'TG', 'TO', 'TT', 'TN', 'TR', 'TM',
                                     'TC', 'TV', 'UG', 'UA', 'AE', 'UY', 'UZ',
                                     'VU', 'VA', 'VE', 'VN', 'VI', 'WF', 'EH',
                                     'WS', 'YE', 'YU', 'ZM', 'ZW', 'RE', 'ME',
                                     'RS']
                       }

EBAY_GLOBAL_ID_LOCATED_IN = {'EBAY-FRCA': {1: ['CA'],
                                           2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                           3: ['CA']},
                             'EBAY-NLBE': {1: ['BE'],
                                           2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                           3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-FRBE': {1: ['BE'],
                                           2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                           3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-US': {3: ['US'],
                                         4: EBAY_COUNTRY_GROUPS['NORTH AMERICA'],
                                         5: EBAY_COUNTRY_GROUPS['EUROPE'],
                                         6: EBAY_COUNTRY_GROUPS['ASIA']},
                             'EBAY-CA': {1: ['CA'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['NORTH AMERICA']},
                             'EBAY-GB': {1: ['GB'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-AU': {1: ['AU'],
                                         2:  EBAY_COUNTRY_GROUPS['WORLDWIDE']},
                             'EBAY-AT': {1: ['AT'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-FR': {1: ['FR'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION'],
                                         4: EBAY_COUNTRY_GROUPS['FRANCE BORDERS']},
                             'EBAY-DE': {1: ['DE'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPE']},
                             'EBAY-IT': {1: ['IT'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-NL': {1: ['NL'],
                                         2:  EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-ES': {1: ['ES'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION']},
                             'EBAY-CH': {1: ['CH'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPE']},
                             'EBAY-HK': {2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['ASIA'],
                                         4: ['HK', 'CN', 'TW']},
                             'EBAY-IE': {1: ['IE'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['EUROPEAN UNION'],
                                         5: ['IE', 'GB']},
                             'EBAY-MY': {1: ['MY'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['ASIA']},
                             'EBAY-PH': {1: ['PH'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['ASIA']},
                             'EBAY-PL': {1: ['PL'],
                                         2:  EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3:  EBAY_COUNTRY_GROUPS['EUROPE']},
                             'EBAY-SG': {1: ['SG'],
                                         2: EBAY_COUNTRY_GROUPS['WORLDWIDE'],
                                         3: EBAY_COUNTRY_GROUPS['ASIA']}
                             }

EBAY_LISTING_TYPE = {'LH_Auction': ['Auction', 'AuctionWithBIN'],
                     'LH_BO': ['FixedPrice'],
                     'LH_BIN': ['FixedPrice', 'AuctionWithBIN'],
                     'LH_CAds': ['Classified']}

EBAY_SINGLE_DIGIT_CONDITION_IDS = {'3': ['1000', '1500', '1750'],
                                   '4': ['2750', '3000', '4000', '5000', '6000'],
                                   '10': [],
                                   '11': ['1000', '1500', '1750'],
                                   '12': ['2750', '3000', '4000', '5000', '6000'],
                                   }  # EBAY HAS NOT CONFIRMED THIS


def map_ebay_site_to_id(hostname):
    """Maps hostname from ebay url to the website's Global ID

    Each ebay website has a specific Global ID that can be
    used in requests. Uses the values in EBAY_DOMAIN_TO_GLOBAL_ID sourced from:
    https://developer.ebay.com/DevZone/finding/CallRef/Enums/GlobalIdList.html

    Keyword Arguments:
        hostname               -- Example: www.ebay.com

    Return Value:
    Global ID. Example: EBAY-US
    """
    aux = EBAY_DOMAIN_TO_GLOBAL_ID.get(hostname)

    if not aux and 'ebay.com' in hostname:
        aux = 'EBAY-US'
    elif not aux:
        return None

    return aux


def map_global_id_located_in(global_id, prefloc):
    """Maps values for the item location filter from the url
    to the it's list of countries depending on the ebay' website
    being use

    Keyword Arguments:
        global_id               -- Ebay website Global ID
        prefloc                 -- Value for the filter in query string

    Return Value:
    List of countries as ISO codes. Example: ['US', 'CA', 'MX]
    """
    aux = EBAY_GLOBAL_ID_LOCATED_IN.get(global_id)
    return aux.get(int(prefloc[0]))


def map_ebay_query_to_listing_type(query):
    """Maps possible query parameters to listing type 

    Keyword Arguments:
        query               -- query string

    Return Value:
    List of accepted listing types. Example: ['FixedPrice', 'AuctionWithBIN']
    """
    for p, value in EBAY_LISTING_TYPE.items():
        if query.get(p):
            return value


def map_condition_ids(query):
    """Gets condition IDs from query string and maps them if needed

    Normally condition IDs simply come concatenated with | (e.g: 3000|4000)
    but for some searches, single digit condition IDs (not accepted by the API)
    are given. This function get the condition IDs from the query string and maps
    the single digit ones to a list of equivalent condition IDs.

    Keyword Arguments:
        query               -- query string

    Return Value:
    List of condition IDs. Example: ['2750', '3000', '4000', '5000', '6000']
    """
    condition = query.get('LH_ItemCondition')[0]
    condition = condition.split('|')
    for condition_id in condition:
        if len(condition_id) < 4:
            condition.extend(
                EBAY_SINGLE_DIGIT_CONDITION_IDS.get(condition_id))

    # Convert to set to remove duplicates and then back to list
    condition = list(set(condition))
    return condition

import asyncio
import logging
import re
import discord
import requests

import util

REDIRECT_LAYERS = 3
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
URL_REGEX2 = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,‌​3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s‌​()<>]+|(([^\s()<‌​>]+|(([^\s()<>]+‌​)))*))+(?:&#‌​40;([^\s()<>]+|((‌​;[^\s()<>]+)))*&‌​#41;|[^\s`!()[&#‌​93;{};:'".,<>?«»“”‘’‌​]))""", re.DOTALL)
ANY_URL_REGEX = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
WEB_URL_REGEX = re.compile(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|top|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")
IP_REGEX = re.compile(r"""[0-9]+(?:\.[0-9]+){3}:[0-9]+""")
STACKOVERFLOW_REGEX = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''')

EXTENSTIONS = ['aaa', 'aarp', 'abarth', 'abb', 'abbott', 'abbvie', 'abc', 'able', 'abogado', 'abudhabi', 'ac', 'academy', 'accenture', 'accountant', 'accountants', 'aco', 'active', 'actor', 'ad', 'adac', 'ads', 'adult', 'ae', 'aeg', 'aero', 'aetna', 'af', 'afamilycompany', 'afl', 'africa', 'ag', 'agakhan', 'agency', 'ai', 'aig', 'aigo', 'airbus', 'airforce', 'airtel', 'akdn', 'al', 'alfaromeo', 'alibaba', 'alipay', 'allfinanz', 'allstate', 'ally', 'alsace', 'alstom', 'am', 'americanexpress', 'americanfamily', 'amex', 'amfam', 'amica', 'amsterdam', 'analytics', 'android', 'anquan', 'anz', 'ao', 'aol', 'apartments', 'app', 'apple', 'aq', 'aquarelle', 'ar', 'arab', 'aramco', 'archi', 'army', 'arpa', 'art', 'arte', 'as', 'asda', 'asia', 'associates', 'at', 'athleta', 'attorney', 'au', 'auction', 'audi', 'audible', 'audio', 'auspost', 'author', 'auto', 'autos', 'avianca', 'aw', 'aws', 'ax', 'axa', 'az', 'azure', 'ba', 'baby', 'baidu', 'banamex', 'bananarepublic', 'band', 'bank', 'bar', 'barcelona', 'barclaycard', 'barclays', 'barefoot', 'bargains', 'baseball', 'basketball', 'bauhaus', 'bayern', 'bb', 'bbc', 'bbt', 'bbva', 'bcg', 'bcn', 'bd', 'be', 'beats', 'beauty', 'beer', 'bentley', 'berlin', 'best', 'bestbuy', 'bet', 'bf', 'bg', 'bh', 'bharti', 'bi', 'bible', 'bid', 'bike', 'bing', 'bingo', 'bio', 'biz', 'bj', 'black', 'blackfriday', 'blanco', 'blockbuster', 'blog', 'bloomberg', 'blue', 'bm', 'bms', 'bmw', 'bn', 'bnl', 'bnpparibas', 'bo', 'boats', 'boehringer', 'bofa', 'bom', 'bond', 'boo', 'book', 'booking', 'boots', 'bosch', 'bostik', 'boston', 'bot', 'boutique', 'box', 'br', 'bradesco', 'bridgestone', 'broadway', 'broker', 'brother', 'brussels', 'bs', 'bt', 'budapest', 'bugatti', 'build', 'builders', 'business', 'buy', 'buzz', 'bv', 'bw', 'by', 'bz', 'bzh', 'ca', 'cab', 'cafe', 'cal', 'call', 'calvinklein', 'cam', 'camera', 'camp', 'cancerresearch', 'canon', 'capetown', 'capital', 'capitalone', 'car', 'caravan', 'cards', 'care', 'career', 'careers', 'cars', 'cartier', 'casa', 'case', 'caseih', 'cash', 'casino', 'cat', 'catering', 'catholic', 'cba', 'cbn', 'cbre', 'cbs', 'cc', 'cd', 'ceb', 'center', 'ceo', 'cern', 'cf', 'cfa', 'cfd', 'cg', 'ch', 'chanel', 'channel', 'chase', 'chat', 'cheap', 'chintai', 'chloe', 'christmas', 'chrome', 'chrysler', 'church', 'ci', 'cipriani', 'circle', 'cisco', 'citadel', 'citi', 'citic', 'city', 'cityeats', 'ck', 'cl', 'claims', 'cleaning', 'click', 'clinic', 'clinique', 'clothing', 'cloud', 'club', 'clubmed', 'cm', 'cn', 'co', 'coach', 'codes', 'coffee', 'college', 'cologne', 'com', 'comcast', 'commbank', 'community', 'company', 'compare', 'computer', 'comsec', 'condos', 'construction', 'consulting', 'contact', 'contractors', 'cooking', 'cookingchannel', 'cool', 'coop', 'corsica', 'country', 'coupon', 'coupons', 'courses', 'cr', 'credit', 'creditcard', 'creditunion', 'cricket', 'crown', 'crs', 'cruise', 'cruises', 'csc', 'cu', 'cuisinella', 'cv', 'cw', 'cx', 'cy', 'cymru', 'cyou', 'cz', 'dabur', 'dad', 'dance', 'data', 'date', 'dating', 'datsun', 'day', 'dclk', 'dds', 'de', 'deal', 'dealer', 'deals', 'degree', 'delivery', 'dell', 'deloitte', 'delta', 'democrat', 'dental', 'dentist', 'desi', 'design', 'dev', 'dhl', 'diamonds', 'diet', 'digital', 'direct', 'directory', 'discount', 'discover', 'dish', 'diy', 'dj', 'dk', 'dm', 'dnp', 'do', 'docs', 'doctor', 'dodge', 'dog', 'doha', 'domains', 'dot', 'download', 'drive', 'dtv', 'dubai', 'duck', 'dunlop', 'duns', 'dupont', 'durban', 'dvag', 'dvr', 'dz', 'earth', 'eat', 'ec', 'eco', 'edeka', 'edu', 'education', 'ee', 'eg', 'email', 'emerck', 'energy', 'engineer', 'engineering', 'enterprises', 'epost', 'epson', 'equipment', 'er', 'ericsson', 'erni', 'es', 'esq', 'estate', 'esurance', 'et', 'etisalat', 'eu', 'eurovision', 'eus', 'events', 'everbank', 'exchange', 'expert', 'exposed', 'express', 'extraspace', 'fage', 'fail', 'fairwinds', 'faith', 'family', 'fan', 'fans', 'farm', 'farmers', 'fashion', 'fast', 'fedex', 'feedback', 'ferrari', 'ferrero', 'fi', 'fiat', 'fidelity', 'fido', 'film', 'final', 'finance', 'financial', 'fire', 'firestone', 'firmdale', 'fish', 'fishing', 'fit', 'fitness', 'fj', 'fk', 'flickr', 'flights', 'flir', 'florist', 'flowers', 'fly', 'fm', 'fo', 'foo', 'food', 'foodnetwork', 'football', 'ford', 'forex', 'forsale', 'forum', 'foundation', 'fox', 'fr', 'free', 'fresenius', 'frl', 'frogans', 'frontdoor', 'frontier', 'ftr', 'fujitsu', 'fujixerox', 'fun', 'fund', 'furniture', 'futbol', 'fyi', 'ga', 'gal', 'gallery', 'gallo', 'gallup', 'game', 'games', 'gap', 'garden', 'gb', 'gbiz', 'gd', 'gdn', 'ge', 'gea', 'gent', 'genting', 'george', 'gf', 'gg', 'ggee', 'gh', 'gi', 'gift', 'gifts', 'gives', 'giving', 'gl', 'glade', 'glass', 'gle', 'global', 'globo', 'gm', 'gmail', 'gmbh', 'gmo', 'gmx', 'gn', 'godaddy', 'gold', 'goldpoint', 'golf', 'goo', 'goodhands', 'goodyear', 'goog', 'google', 'gop', 'got', 'gov', 'gp', 'gq', 'gr', 'grainger', 'graphics', 'gratis', 'green', 'gripe', 'grocery', 'group', 'gs', 'gt', 'gu', 'guardian', 'gucci', 'guge', 'guide', 'guitars', 'guru', 'gw', 'gy', 'hair', 'hamburg', 'hangout', 'haus', 'hbo', 'hdfc', 'hdfcbank', 'health', 'healthcare', 'help', 'helsinki', 'here', 'hermes', 'hgtv', 'hiphop', 'hisamitsu', 'hitachi', 'hiv', 'hk', 'hkt', 'hm', 'hn', 'hockey', 'holdings', 'holiday', 'homedepot', 'homegoods', 'homes', 'homesense', 'honda', 'honeywell', 'horse', 'hospital', 'host', 'hosting', 'hot', 'hoteles', 'hotels', 'hotmail', 'house', 'how', 'hr', 'hsbc', 'ht', 'htc', 'hu', 'hughes', 'hyatt', 'hyundai', 'ibm', 'icbc', 'ice', 'icu', 'id', 'ie', 'ieee', 'ifm', 'ikano', 'il', 'im', 'imamat', 'imdb', 'immo', 'immobilien', 'in', 'industries', 'infiniti', 'info', 'ing', 'ink', 'institute', 'insurance', 'insure', 'int', 'intel', 'international', 'intuit', 'investments', 'io', 'ipiranga', 'iq', 'ir', 'irish', 'is', 'iselect', 'ismaili', 'ist', 'istanbul', 'it', 'itau', 'itv', 'iveco', 'iwc', 'jaguar', 'java', 'jcb', 'jcp', 'je', 'jeep', 'jetzt', 'jewelry', 'jio', 'jlc', 'jll', 'jm', 'jmp', 'jnj', 'jo', 'jobs', 'joburg', 'jot', 'joy', 'jp', 'jpmorgan', 'jprs', 'juegos', 'juniper', 'kaufen', 'kddi', 'ke', 'kerryhotels', 'kerrylogistics', 'kerryproperties', 'kfh', 'kg', 'kh', 'ki', 'kia', 'kim', 'kinder', 'kindle', 'kitchen', 'kiwi', 'km', 'kn', 'koeln', 'komatsu', 'kosher', 'kp', 'kpmg', 'kpn', 'kr', 'krd', 'kred', 'kuokgroup', 'kw', 'ky', 'kyoto', 'kz', 'la', 'lacaixa', 'ladbrokes', 'lamborghini', 'lamer', 'lancaster', 'lancia', 'lancome', 'land', 'landrover', 'lanxess', 'lasalle', 'lat', 'latino', 'latrobe', 'law', 'lawyer', 'lb', 'lc', 'lds', 'lease', 'leclerc', 'lefrak', 'legal', 'lego', 'lexus', 'lgbt', 'li', 'liaison', 'lidl', 'life', 'lifeinsurance', 'lifestyle', 'lighting', 'like', 'lilly', 'limited', 'limo', 'lincoln', 'linde', 'link', 'lipsy', 'live', 'living', 'lixil', 'lk', 'loan', 'loans', 'locker', 'locus', 'loft', 'lol', 'london', 'lotte', 'lotto', 'love', 'lpl', 'lplfinancial', 'lr', 'ls', 'lt', 'ltd', 'ltda', 'lu', 'lundbeck', 'lupin', 'luxe', 'luxury', 'lv', 'ly', 'ma', 'macys', 'madrid', 'maif', 'maison', 'makeup', 'man', 'management', 'mango', 'map', 'market', 'marketing', 'markets', 'marriott', 'marshalls', 'maserati', 'mattel', 'mba', 'mc', 'mcd', 'mcdonalds', 'mckinsey', 'md', 'me', 'med', 'media', 'meet', 'melbourne', 'meme', 'memorial', 'men', 'menu', 'meo', 'merckmsd', 'metlife', 'mg', 'mh', 'miami', 'microsoft', 'mil', 'mini', 'mint', 'mit', 'mitsubishi', 'mk', 'ml', 'mlb', 'mls', 'mm', 'mma', 'mn', 'mo', 'mobi', 'mobile', 'mobily', 'moda', 'moe', 'moi', 'mom', 'monash', 'money', 'monster', 'montblanc', 'mopar', 'mormon', 'mortgage', 'moscow', 'moto', 'motorcycles', 'mov', 'movie', 'movistar', 'mp', 'mq', 'mr', 'ms', 'msd', 'mt', 'mtn', 'mtr', 'mu', 'museum', 'mutual', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'nab', 'nadex', 'nagoya', 'name', 'nationwide', 'natura', 'navy', 'nba', 'nc', 'ne', 'nec', 'net', 'netbank', 'netflix', 'network', 'neustar', 'new', 'newholland', 'news', 'next', 'nextdirect', 'nexus', 'nf', 'nfl', 'ng', 'ngo', 'nhk', 'ni', 'nico', 'nike', 'nikon', 'ninja', 'nissan', 'nissay', 'nl', 'no', 'nokia', 'northwesternmutual', 'norton', 'now', 'nowruz', 'nowtv', 'np', 'nr', 'nra', 'nrw', 'ntt', 'nu', 'nyc', 'nz', 'obi', 'observer', 'off', 'office', 'okinawa', 'olayan', 'olayangroup', 'oldnavy', 'ollo', 'om', 'omega', 'one', 'ong', 'onl', 'online', 'onyourside', 'ooo', 'open', 'oracle', 'orange', 'org', 'organic', 'origins', 'osaka', 'otsuka', 'ott', 'ovh', 'pa', 'page', 'pamperedchef', 'panasonic', 'panerai', 'paris', 'pars', 'partners', 'parts', 'party', 'passagens', 'pay', 'pccw', 'pe', 'pet', 'pf', 'pfizer', 'pg', 'ph', 'pharmacy', 'phd', 'philips', 'phone', 'photo', 'photography', 'photos', 'physio', 'piaget', 'pics', 'pictet', 'pictures', 'pid', 'pin', 'ping', 'pink', 'pioneer', 'pizza', 'pk', 'pl', 'place', 'play', 'playstation', 'plumbing', 'plus', 'pm', 'pn', 'pnc', 'pohl', 'poker', 'politie', 'porn', 'post', 'pr', 'pramerica', 'praxi', 'press', 'prime', 'pro', 'prod', 'productions', 'prof', 'progressive', 'promo', 'properties', 'property', 'protection', 'pru', 'prudential', 'ps', 'pt', 'pub', 'pw', 'pwc', 'py', 'qa', 'qpon', 'quebec', 'quest', 'qvc', 'racing', 'radio', 'raid', 're', 'read', 'realestate', 'realtor', 'realty', 'recipes', 'red', 'redstone', 'redumbrella', 'rehab', 'reise', 'reisen', 'reit', 'reliance', 'ren', 'rent', 'rentals', 'repair', 'report', 'republican', 'rest', 'restaurant', 'review', 'reviews', 'rexroth', 'rich', 'richardli', 'ricoh', 'rightathome', 'ril', 'rio', 'rip', 'rmit', 'ro', 'rocher', 'rocks', 'rodeo', 'rogers', 'room', 'rs', 'rsvp', 'ru', 'rugby', 'ruhr', 'run', 'rw', 'rwe', 'ryukyu', 'sa', 'saarland', 'safe', 'safety', 'sakura', 'sale', 'salon', 'samsclub', 'samsung', 'sandvik', 'sandvikcoromant', 'sanofi', 'sap', 'sapo', 'sarl', 'sas', 'save', 'saxo', 'sb', 'sbi', 'sbs', 'sc', 'sca', 'scb', 'schaeffler', 'schmidt', 'scholarships', 'school', 'schule', 'schwarz', 'science', 'scjohnson', 'scor', 'scot', 'sd', 'se', 'search', 'seat', 'secure', 'security', 'seek', 'select', 'sener', 'services', 'ses', 'seven', 'sew', 'sex', 'sexy', 'sfr', 'sg', 'sh', 'shangrila', 'sharp', 'shaw', 'shell', 'shia', 'shiksha', 'shoes', 'shop', 'shopping', 'shouji', 'show', 'showtime', 'shriram', 'si', 'silk', 'sina', 'singles', 'site', 'sj', 'sk', 'ski', 'skin', 'sky', 'skype', 'sl', 'sling', 'sm', 'smart', 'smile', 'sn', 'sncf', 'so', 'soccer', 'social', 'softbank', 'software', 'sohu', 'solar', 'solutions', 'song', 'sony', 'soy', 'space', 'spiegel', 'spot', 'spreadbetting', 'sr', 'srl', 'srt', 'st', 'stada', 'staples', 'star', 'starhub', 'statebank', 'statefarm', 'statoil', 'stc', 'stcgroup', 'stockholm', 'storage', 'store', 'stream', 'studio', 'study', 'style', 'su', 'sucks', 'supplies', 'supply', 'support', 'surf', 'surgery', 'suzuki', 'sv', 'swatch', 'swiftcover', 'swiss', 'sx', 'sy', 'sydney', 'symantec', 'systems', 'sz', 'tab', 'taipei', 'talk', 'taobao', 'target', 'tatamotors', 'tatar', 'tattoo', 'tax', 'taxi', 'tc', 'tci', 'td', 'tdk', 'team', 'tech', 'technology', 'tel', 'telecity', 'telefonica', 'temasek', 'tennis', 'teva', 'tf', 'tg', 'th', 'thd', 'theater', 'theatre', 'tiaa', 'tickets', 'tienda', 'tiffany', 'tips', 'tires', 'tirol', 'tj', 'tjmaxx', 'tjx', 'tk', 'tkmaxx', 'tl', 'tm', 'tmall', 'tn', 'to', 'today', 'tokyo', 'tools', 'top', 'toray', 'toshiba', 'total', 'tours', 'town', 'toyota', 'toys', 'tr', 'trade', 'trading', 'training', 'travel', 'travelchannel', 'travelers', 'travelersinsurance', 'trust', 'trv', 'tt', 'tube', 'tui', 'tunes', 'tushu', 'tv', 'tvs', 'tw', 'tz', 'ua', 'ubank', 'ubs', 'uconnect', 'ug', 'uk', 'unicom', 'university', 'uno', 'uol', 'ups', 'us', 'uy', 'uz', 'va', 'vacations', 'vana', 'vanguard', 'vc', 've', 'vegas', 'ventures', 'verisign', 'versicherung', 'vet', 'vg', 'vi', 'viajes', 'video', 'vig', 'viking', 'villas', 'vin', 'vip', 'virgin', 'visa', 'vision', 'vista', 'vistaprint', 'viva', 'vivo', 'vlaanderen', 'vn', 'vodka', 'volkswagen', 'volvo', 'vote', 'voting', 'voto', 'voyage', 'vu', 'vuelos', 'wales', 'walmart', 'walter', 'wang', 'wanggou', 'warman', 'watch', 'watches', 'weather', 'weatherchannel', 'webcam', 'weber', 'website', 'wed', 'wedding', 'weibo', 'weir', 'wf', 'whoswho', 'wien', 'wiki', 'williamhill', 'win', 'windows', 'wine', 'winners', 'wme', 'wolterskluwer', 'woodside', 'work', 'works', 'world', 'wow', 'ws', 'wtc', 'wtf', 'xbox', 'xerox', 'xfinity', 'xihuan', 'xin', 'xn--11b4c3d', 'xn--1ck2e1b', 'xn--1qqw23a', 'xn--2scrj9c', 'xn--30rr7y', 'xn--3bst00m', 'xn--3ds443g', 'xn--3e0b707e', 'xn--3hcrj9c', 'xn--3oq18vl8pn36a', 'xn--3pxu8k', 'xn--42c2d9a', 'xn--45br5cyl', 'xn--45brj9c', 'xn--45q11c', 'xn--4gbrim', 'xn--54b7fta0cc', 'xn--55qw42g', 'xn--55qx5d', 'xn--5su34j936bgsg', 'xn--5tzm5g', 'xn--6frz82g', 'xn--6qq986b3xl', 'xn--80adxhks', 'xn--80ao21a', 'xn--80aqecdr1a', 'xn--80asehdb', 'xn--80aswg', 'xn--8y0a063a', 'xn--90a3ac', 'xn--90ae', 'xn--90ais', 'xn--9dbq2a', 'xn--9et52u', 'xn--9krt00a', 'xn--b4w605ferd', 'xn--bck1b9a5dre4c', 'xn--c1avg', 'xn--c2br7g', 'xn--cck2b3b', 'xn--cg4bki', 'xn--clchc0ea0b2g2a9gcd', 'xn--czr694b', 'xn--czrs0t', 'xn--czru2d', 'xn--d1acj3b', 'xn--d1alf', 'xn--e1a4c', 'xn--eckvdtc9d', 'xn--efvy88h', 'xn--estv75g', 'xn--fct429k', 'xn--fhbei', 'xn--fiq228c5hs', 'xn--fiq64b', 'xn--fiqs8s', 'xn--fiqz9s', 'xn--fjq720a', 'xn--flw351e', 'xn--fpcrj9c3d', 'xn--fzc2c9e2c', 'xn--fzys8d69uvgm', 'xn--g2xx48c', 'xn--gckr3f0f', 'xn--gecrj9c', 'xn--gk3at1e', 'xn--h2breg3eve', 'xn--h2brj9c', 'xn--h2brj9c8c', 'xn--hxt814e', 'xn--i1b6b1a6a2e', 'xn--imr513n', 'xn--io0a7i', 'xn--j1aef', 'xn--j1amh', 'xn--j6w193g', 'xn--jlq61u9w7b', 'xn--jvr189m', 'xn--kcrx77d1x4a', 'xn--kprw13d', 'xn--kpry57d', 'xn--kpu716f', 'xn--kput3i', 'xn--l1acc', 'xn--lgbbat1ad8j', 'xn--mgb9awbf', 'xn--mgba3a3ejt', 'xn--mgba3a4f16a', 'xn--mgba7c0bbn0a', 'xn--mgbaakc7dvf', 'xn--mgbaam7a8h', 'xn--mgbab2bd', 'xn--mgbai9azgqp6j', 'xn--mgbayh7gpa', 'xn--mgbb9fbpob', 'xn--mgbbh1a', 'xn--mgbbh1a71e', 'xn--mgbc0a9azcg', 'xn--mgbca7dzdo', 'xn--mgberp4a5d4ar', 'xn--mgbgu82a', 'xn--mgbi4ecexp', 'xn--mgbpl2fh', 'xn--mgbt3dhd', 'xn--mgbtx2b', 'xn--mgbx4cd0ab', 'xn--mix891f', 'xn--mk1bu44c', 'xn--mxtq1m', 'xn--ngbc5azd', 'xn--ngbe9e0a', 'xn--ngbrx', 'xn--node', 'xn--nqv7f', 'xn--nqv7fs00ema', 'xn--nyqy26a', 'xn--o3cw4h', 'xn--ogbpf8fl', 'xn--p1acf', 'xn--p1ai', 'xn--pbt977c', 'xn--pgbs0dh', 'xn--pssy2u', 'xn--q9jyb4c', 'xn--qcka1pmc', 'xn--qxam', 'xn--rhqv96g', 'xn--rovu88b', 'xn--rvc1e0am3e', 'xn--s9brj9c', 'xn--ses554g', 'xn--t60b56a', 'xn--tckwe', 'xn--tiq49xqyj', 'xn--unup4y', 'xn--vermgensberater-ctb', 'xn--vermgensberatung-pwb', 'xn--vhquv', 'xn--vuq861b', 'xn--w4r85el8fhu5dnra', 'xn--w4rs40l', 'xn--wgbh1c', 'xn--wgbl6a', 'xn--xhq521b', 'xn--xkc2al3hye2a', 'xn--xkc2dl3a5ee0h', 'xn--y9a3aq', 'xn--yfro4i67o', 'xn--ygbi2ammx', 'xn--zfr164b', 'xperia', 'xxx', 'xyz', 'yachts', 'yahoo', 'yamaxun', 'yandex', 'ye', 'yodobashi', 'yoga', 'yokohama', 'you', 'youtube', 'yt', 'yun', 'za', 'zappos', 'zara', 'zero', 'zip', 'zippo', 'zm', 'zone', 'zuerich', 'zw']

REGS = [URL_REGEX, URL_REGEX2, ANY_URL_REGEX, WEB_URL_REGEX, IP_REGEX, STACKOVERFLOW_REGEX]

log = logging.getLogger(__name__)
moderator_roles = ['moderator', 'unikrn staff', 'unikrn admin']
DELETE_TIME = 5


URL_SOURCE = 'https://raw.githubusercontent.com/MyEtherWallet/ethereum-lists/master/urls-darklist.json'
UPDATE_PERIOD = 3600  # Every hour


@util.listenerfinder.register
class GetUrlsTask(util.ScheduledTask):

    blacklist = []

    async def task(self):
        while True:
            log.info('updating url blacklist...')
            response = requests.get(URL_SOURCE)
            content = response.content.decode()
            GetUrlsTask.blacklist = re.findall(r'"id": ?"(.+)"', content)  # because it errors with proper json.loads...
            log.debug('updated blacklist: ', GetUrlsTask.blacklist)
            await asyncio.sleep(UPDATE_PERIOD)


@util.listenerfinder.register
class URLModerator(util.Listener):
    def __init__(self):
        super().__init__()

    def is_triggered_message(self, msg: discord.Message):
        should_delete = False

        for blacklist_url in GetUrlsTask.blacklist:
            if re.search(r'\b{}\b'.format(blacklist_url), msg.content, flags=re.IGNORECASE):
                should_delete = True

        for reg in REGS:
            should_delete = should_delete or re.match(reg, msg.content)

        split = msg.content.split(' ')
        for word in split:
            lower_word = word.lower()
            if lower_word.startswith("http:") or lower_word.startswith("https:"):
                should_delete = True
            for extension in EXTENSTIONS:
                if lower_word.endswith("." + extension):
                    should_delete = True

        for role in msg.author.roles:
            if role.name.lower() in moderator_roles:
                should_delete = False

        return should_delete

    async def on_message(self, msg: discord.Message):
        if not msg:
            return
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained a URL was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                message = '_{} removed message: {}, from channel {} because it contained a link._'.format(msg.author.mention, msg.content, msg.channel.mention)
                await self.client.send_message(channel, message)
        await asyncio.sleep(DELETE_TIME)
        if notice:
            await self.client.delete_message(notice)


@util.listenerfinder.register
class AddressDeletor(util.Listener):
    def is_triggered_message(self, msg: discord.Message):
        if any((r.name.lower() in moderator_roles) for r in msg.author.roles):
            return False
        if re.search(r'[0-9a-f]{38,45}', msg.content, flags=re.IGNORECASE):
            return True

    async def on_message(self, msg: discord.Message):
        if not msg:
            return
        await self.client.delete_message(msg)
        notice = await self.client.send_message(msg.channel, '_A message from {} that contained an ethereum address was deleted._'.format(msg.author.mention))
        channels = self.client.get_all_channels()
        for channel in channels:
            if channel.name.lower() == 'godwatch':
                '_{} removed message: {}, from channel {}._'.format(msg.author.mention, msg.content,
                                                                    msg.channel.mention)
                await self.client.send_message(channel, '_{} removed message: {}, from channel {} because it contained an Ethereum address._'.format(msg.author.mention, msg.content, msg.channel.mention))
        await asyncio.sleep(DELETE_TIME)
        if notice:
            await self.client.delete_message(notice)
        return

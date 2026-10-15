import os
import platform
from cudatext import *
from pathlib import Path
import sys
import urllib.request, urllib.parse, json
import random
from .libs import pyperclip
from cudax_lib import get_translation
_ = get_translation(__file__)

class Command:
    def __init__(self):
        self.conf_file = Path(app_path(APP_DIR_SETTINGS)) / 'cuda_language_translator.json'
        if self.conf_file.exists() == False:
            with self.conf_file.open(mode='w', encoding='utf-8') as f:
                json.dump({
                    'automatic copy to clipboard': 0
                }, f, indent=2)
        #
        self.languages = {'abk':'abkhaz','ace':'acehnese','ach':'acholi','aar':'afar','af':'afrikaans','sq':'albanian','alz':'alur','am':'amharic','ar':'arabic','hy':'armenian','as':'assamese','ava':'avar','awa':'awadhi','ay':'aymara','az':'azerbaijani','ban':'balinese','bal':'baluchi','bm':'bambara','bci':'baoulé','bak':'bashkir','eu':'basque','btx':'batak karo','bts':'batak simalungun','bbc':'batak toba','be':'belarusian','bem':'bemba','bn':'bengali','bew':'betawi','bho':'bhojpuri','bik':'bikol','bs':'bosnian','bre':'breton','bg':'bulgarian','bua':'buryat','yue':'cantonese','ca':'catalan','ceb':'cebuano','cha':'chamorro','che':'chechen','zh':'chinese','zh-cn':'chinese (simplified)','zh-tw':'chinese (traditional)','chk':'chuukese','chv':'chuvash','co':'corsican','crh':'crimean tatar','hr':'croatian','cs':'czech','da':'danish','fa-af':'dari','dv':'dhivehi','din':'dinka','doi':'dogri','dom':'dombe','nl':'dutch','dyu':'dyula','dzo':'dzongkha','en':'english','eo':'esperanto','et':'estonian','fao':'faroese','fij':'fijian','fil':'filipino (tagalog)','fi':'finnish','fon':'fon','fr':'french','fy':'frisian','fur':'friulian','ful':'fulani','gaa':'ga','gl':'galician','ka':'georgian','de':'german','el':'greek','gn':'guarani','gu':'gujarati','ht':'haitian creole','cnh':'hakha chin','ha':'hausa','haw':'hawaiian','he':'hebrew','iw':'hebrew','hil':'hiligaynon','hi':'hindi','hmn':'hmong','hu':'hungarian','hrx':'hunsrik','iba':'iban','is':'icelandic','ig':'igbo','ilo':'ilocano','id':'indonesian','ga':'irish','it':'italian','jam':'jamaican patois','ja':'japanese','jv':'javanese','jw':'javanese','kac':'jingpo','kal':'kalaallisut','kn':'kannada','kau':'kanuri','pam':'kapampangan','kk':'kazakh','kha':'khasi','km':'khmer','cgg':'kiga','kik':'kikongo','rw':'kinyarwanda','ktu':'kituba','trp':'kokborok','kom':'komi','gom':'konkani','ko':'korean','kri':'krio','ku':'kurdish','ckb':'kurdish (sorani)','ky':'kyrgyz','lo':'lao','ltg':'latgalian','la':'latin','lv':'latvian','lij':'ligurian','lim':'limburgish','ln':'lingala','lt':'lithuanian','lmo':'lombard','lg':'luganda','luo':'luo','lb':'luxembourgish','mk':'macedonian','mad':'madurese','mai':'maithili','mak':'makassar','mg':'malagasy','ms':'malay','ms-arab':'malay (jawi)','ml':'malayalam','mt':'maltese','mam':'mam','glv':'manx','mi':'maori','mr':'marathi','mah':'marshallese','mwr':'marwadi','mfe':'mauritian creole','mhr':'meadow mari','mni-mtei':'meiteilon (manipuri)','min':'minang','lus':'mizo','mn':'mongolian','my':'myanmar (burmese)','nhe':'nahuatl (eastern huasteca)','ndc-zw':'ndau','nde':'ndebele (south)','new':'nepalbhasa (newari)','ne':'nepali','no':'norwegian','nus':'nuer','ny':'nyanja (chichewa)','oci':'occitan','or':'odia (oriya)','om':'oromo','oss':'ossetian','pag':'pangasinan','pap':'papiamento','ps':'pashto','fa':'persian','pl':'polish','por':'portuguese (portugal)','pt':'portuguese (portugal,brazil)','pa':'punjabi','pa-arab':'punjabi (shahmukhi)','kek':"q'eqchi'",'qu':'quechua','rom':'romani','ro':'romanian','run':'rundi','ru':'russian','sme':'sami (north)','sm':'samoan','sag':'sango','sa':'sanskrit','sat':'santali','gd':'scots gaelic','nso':'sepedi','sr':'serbian','st':'sesotho','crs':'seychellois creole','shn':'shan','sn':'shona','scn':'sicilian','szl':'silesian','sd':'sindhi','si':'sinhala (sinhalese)','sk':'slovak','sl':'slovenian','so':'somali','es':'spanish','su':'sundanese','sus':'susu','sw':'swahili','ssw':'swati','sv':'swedish','tl':'tagalog (filipino)','tah':'tahitian','tg':'tajik','ber-atn':'tamazight','ber':'tamazight (tifinagh)','ta':'tamil','tt':'tatar','te':'telugu','tet':'tetum','th':'thai','bod':'tibetan','ti':'tigrinya','tiv':'tiv','tpi':'tok pisin','ton':'tongan','ts':'tsonga','tsn':'tswana','tcy':'tulu','tum':'tumbuka','tr':'turkish','tk':'turkmen','tuk':'tuvan','ak':'twi (akan)','udm':'udmurt','uk':'ukrainian','ur':'urdu','ug':'uyghur','uz':'uzbek','ven':'venda','vec':'venetian','vi':'vietnamese','war':'waray','cy':'welsh','wol':'wolof','xh':'xhosa','sah':'yakut','yi':'yiddish','yo':'yoruba','yua':'yucatec maya','zap':'zapotec','zu':'zulu'}

    def translate(self, text, target_lang):
        """Translate text using Google Translate free endpoints with fallbacks.

        Endpoints (in order):
        1. translate.googleapis.com/translate_a/single (client=gtx)
        2. translate-pa.googleapis.com/v1/translateHtml
        3. dictionaryextension-pa.googleapis.com/v1/dictionaryExtensionData
        """
        if not text:
            return None

        # 30 recent Chrome / Edge / Firefox User-Agents; pick one at random per request
        user_agents = [
            # Chrome Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            # Chrome macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            # Chrome Linux
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            # Edge Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
            # Edge macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            # Firefox Windows
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
            # Firefox macOS
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.7; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.6; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13.6; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0",
            # Firefox Linux
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
            # Extra recent Chrome
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.85 Safari/537.36",
        ]
        assert len(user_agents) == 30

        def _ua():
            return random.choice(user_agents)

        def _try_gtx():
            url = (
                "https://translate.googleapis.com/translate_a/single"
                "?client=gtx&sl=auto&tl=" + target_lang +
                "&dt=t&q=" + urllib.parse.quote(text)
            )
            req = urllib.request.Request(url, headers={"User-Agent": _ua()})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            return "".join(part[0] for part in data[0] if part and part[0])

        def _try_translate_pa():
            # POST application/json+protobuf
            # Body: [[["text"],"auto","target"],"wt_lib"]
            url = "https://translate-pa.googleapis.com/v1/translateHtml"
            body = json.dumps(
                [[[text], "auto", target_lang], "wt_lib"]
            ).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                method="POST",
                headers={
                    "User-Agent": _ua(),
                    "Accept": "*/*",
                    "Content-Type": "application/json+protobuf",
                    "X-Goog-API-Key": "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            # Response shape: [["translated"], ["src_lang"]]
            if isinstance(data, list) and data and isinstance(data[0], list) and data[0]:
                return data[0][0]
            raise ValueError("unexpected translate-pa response")

        def _try_dictionary_extension():
            # GET dictionaryExtensionData – better quality in some reports
            # Note: this endpoint is oriented around a source term; we still
            # pass target via strategy / language params as used publicly.
            q = urllib.parse.quote(text)
            url = (
                "https://dictionaryextension-pa.googleapis.com/v1/dictionaryExtensionData"
                "?language=" + target_lang +
                "&key=AIzaSyA6EEtrDCfBkHV8uU2lgGY-N383ZgAOo7Y"
                "&term=" + q +
                "&strategy=2"
            )
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": _ua(),
                    "x-referer": "chrome-extension://mgijmajocgfcbeboacabfgobmjgjcoja",
                },
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            # Observed shape:
            # {"status": 200, "translateResponse": {"translateText": "...", ...}}
            if isinstance(data, dict):
                tr = data.get("translateResponse") or {}
                if isinstance(tr, dict):
                    t = tr.get("translateText")
                    if isinstance(t, str) and t.strip():
                        return t
                for key in ("translateText", "translatedText", "text", "translation"):
                    if key in data and isinstance(data[key], str) and data[key].strip():
                        return data[key]
            raise ValueError("unexpected dictionaryextension response")

        errors = []
        for name, fn in (
            ("gtx", _try_gtx),
            ("translate-pa", _try_translate_pa),
            ("dictionaryextension", _try_dictionary_extension),
        ):
            try:
                result = fn()
                if result:
                    return result
            except Exception as e:
                errors.append(f"{name}: {e}")

        # All endpoints failed
        msg_status(
            "Language Translator: all endpoints failed – "
            + "; ".join(errors[:2])
        )
        return None

    def show_language_menu(self):
        lang1 = self.load_option('languages')
        if lang1:
            lang1__ = {}
            for lang1_ in lang1:
                key = lang1_.strip()
                if key in self.languages:
                    lang1__[key] = self.languages[key]
            # sort recent languages by name
            lang1_items = sorted(lang1__.items(), key=lambda x: x[1].lower())
            lang1__ = dict(lang1_items)
            #
            lang2__ = {}
            for code, name in self.languages.items():
                if code not in lang1__:
                    lang2__[code] = name
            # sort remaining languages by name
            lang2_items = sorted(lang2__.items(), key=lambda x: x[1].lower())
            lang2__ = dict(lang2_items)
            #
            langs = '\n'.join([f"{code}: {name}" for code, name in lang1__.items()]) + '\n--\n'
            langs += '\n'.join([f"{code}: {name}" for code, name in lang2__.items()])
            #
            langs_ = {**lang1__, '--': '--', **lang2__}
        else:
            # sort all languages by name
            sorted_items = sorted(self.languages.items(), key=lambda x: x[1].lower())
            langs_ = dict(sorted_items)
            langs = '\n'.join([f"{code}: {name}" for code, name in langs_.items()])
        res = dlg_menu(DMENU_LIST, langs, 0, _('Select target language'))
        if res is not None:
            self.save_option('languages', list(langs_.keys())[res])
            return list(langs_.keys())[res]

        return False

    def translate_with_selection(self):
        selected_lang = self.show_language_menu()
        if selected_lang:
            txt = ed.get_text_sel()
            if len(txt) > 0:
                return self.translate(txt, selected_lang)

        return None

    def res2tab(self):
        translated = self.translate_with_selection()
        if translated:
            file_open('')
            ed.set_text_all(translated)
            self.actc(translated)

    def res2msgbox(self):
        translated = self.translate_with_selection()
        if translated:
            msg_box(translated, MB_OK + MB_ICONINFO)
            self.actc(translated)

    def res2clipboard(self):
        translated = self.translate_with_selection()
        if translated:
            pyperclip.copy(translated)
            msg_status('Language Translator: ' + _('translated text copied to clipboard.'))

    def res2statusbar(self):
        translated = self.translate_with_selection()
        if translated:
            msg_status('Language Translator: ' + translated)
            self.actc(translated)

    def config(self):
        file_open(str(self.conf_file))

    def load_option(self, option):
        data = {}
        if self.conf_file.exists():
            with self.conf_file.open(encoding='utf-8') as f:
                data = json.load(f)
            for param, val in data.items():
                if (param == option):
                    return val

        return False

    def save_option(self, key_, val_):
        data = {}
        if self.conf_file.exists():
            with self.conf_file.open(encoding='utf-8') as f:
                data = json.load(f)
                if key_ in data:
                    vals = []
                    if isinstance(data[key_], list):
                        for i in data[key_]:
                            vals.append(i)
                    else:
                        vals.append(data[key_])
                    vals.append(val_)
                    vals = list(set(vals))
                    data.update({key_:vals})
                else:
                    data.update({key_:[val_]})
            with self.conf_file.open(mode='w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        return False

    def actc(self, translated):
        if self.load_option('automatic copy to clipboard') == 1:
            pyperclip.copy(translated)
            msg_status('Language Translator: ' + _('translated text copied to clipboard (option: automatic copy to clipboard).'))
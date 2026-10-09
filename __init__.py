import os
import platform
from cudatext import *
from pathlib import Path
import json
import asyncio
from cudax_lib import get_translation
_ = get_translation(__file__)

install_first = ''

try:
    from googletrans import Translator, constants
    googletrans_imported = True
except:
    googletrans_imported = False
    install_first += '\npip install -U googletrans'

try:
    import httpx
    httpx_imported = True
except:
    httpx_imported = False
    install_first += '\npip install httpx'

try:
    from httpx_curl_cffi import AsyncCurlTransport
    httpx_curl_cffi_imported = True
except:
    httpx_curl_cffi_imported = False
    install_first += '\npip install httpx_curl_cffi'

try:
    import pyperclip
    pyperclip_imported = True
except:
    pyperclip_imported = False
    install_first += '\npip install pyperclip'
    if platform.system() == 'Linux':
        install_first += '\nsudo apt-get install xsel'

if install_first:
    msg_box(_('Install first') + ': ' + install_first, MB_OK + MB_ICONERROR)

class Command:
    def __init__(self):
        self.conf_file = Path(app_path(APP_DIR_SETTINGS)) / 'cuda_deep_translator.json'
        self.translator = Translator(
            service_urls=["translate.googleapis.com"],
            raise_exception=True,
        )
        self.original_client = self.translator.client
        self.languages = constants.LANGUAGES
        self.target_lang = 'en'

    async def translate(self, text, target_lang):
        if text:
            try:
                transport = AsyncCurlTransport(
                    impersonate="chrome",
                    default_headers=True,
                )
                self.translator.client = httpx.AsyncClient(
                    transport=transport,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/140.0.0.0 Safari/537.36"
                        ),
                    },
                )
                self.translator.token_acquirer.client = self.translator.client
                translated = await self.translator.translate(
                    text,
                    dest=target_lang,
                )
            except Exception as e:
                print("error:")
                print(type(e), e)
            finally:
                await self.translator.client.aclose()
                await self.original_client.aclose()

            return translated.text

        return None

    def show_language_menu(self):
        langs = '\n' . join([f"{code}: {name}" for code, name in self.languages.items()])
        res = dlg_menu(DMENU_LIST, langs, 0, _('Select target language'))
        if res is not None:
            selected_code = list(self.languages.keys())[res]
            self.target_lang = selected_code
            return selected_code

        return None

    async def translate_with_selection(self):
        if googletrans_imported and httpx_imported and httpx_curl_cffi_imported:
            selected_lang = self.show_language_menu()
            if selected_lang:
                txt = ed.get_text_sel()
                if len(txt) > 0:
                    translated = await self.translate(txt, selected_lang)
                    return translated

        return None

    def res2tab(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translated = loop.run_until_complete(self.translate_with_selection())
        if translated:
            file_open('')
            ed.set_text_all(translated)
            self.actc(translated)

    def res2msgbox(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translated = loop.run_until_complete(self.translate_with_selection())
        if translated:
            msg_box(translated, MB_OK + MB_ICONINFO)
            self.actc(translated)

    def res2clipboard(self):
        if pyperclip_imported:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            translated = loop.run_until_complete(self.translate_with_selection())
            if translated:
                pyperclip.copy(translated)
                msg_status('Googletrans Language Translator: ' + _('translated text copied to clipboard.'))

    def res2statusbar(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        translated = loop.run_until_complete(self.translate_with_selection())
        if translated:
            msg_status('Googletrans Language Translator: ' + translated)
            self.actc(translated)

    def config(self):
        if self.conf_file.exists() == False:
            with self.conf_file.open(mode='w', encoding='utf-8') as f:
                json.dump({'automatic copy to clipboard': 0, 'target_language': 'en'}, f, indent=2)
        file_open(str(self.conf_file))

    def check_option(self, option):
        data = {}
        if self.conf_file.exists():
            with self.conf_file.open(encoding='utf-8') as f:
                data = json.load(f)
        for param, val in data.items():
            if (param == option and val == 1):
                return True

        return False

    def actc(self, translated):
        if self.check_option('automatic copy to clipboard'):
            pyperclip.copy(translated)
            msg_status('Googletrans Language Translator: ' + _('translated text copied to clipboard (option: automatic copy to clipboard).'))
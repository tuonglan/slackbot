import os, requests

PAPAGO_API_URL = 'https://openapi.naver.com/v1/papago/n2mt'
DEFAULT_CONTENT_TYPE = 'application/x-www-form-urlencoded; charset=UTF-8'


class PapagoTranslator:
    def __init__(self, client_id, client_secret, source_lang='ko', target_lang='en'):
        self._headers = {
                'X-Naver-Client-Id': client_id,
                'X-Naver-Client-Secret': client_secret,
                'Content-Type': DEFAULT_CONTENT_TYPE
            }
        self._source_lang = source_lang
        self._target_lang = target_lang

    def translate(self, text, source_lang=None, target_lang=None):
        s_lang = (source_lang or self._source_lang)
        t_lang = (target_lang or self._target_lang)
        payload = {'text': text, 'source': s_lang, 'target': t_lang}

        res = requests.post(PAPAGO_API_URL, headers=self._headers, data=payload)
        if res.status_code != 200:
            raise Exception("Translation error: %s" % res)

        js = res.json()
        if not 'message' in js:
            raise Exception("Translation error code: %s, message: %s" % (js['errorCode'], js['errorMessage']))
        return {'text': js['message']['result']['translatedText'],
                'lang': js['message']['result']['srcLangType']}




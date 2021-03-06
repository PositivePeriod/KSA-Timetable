from django import forms
from django.core.exceptions import ValidationError
from .excel import RAW_LEN, TIME_R, CLASS_NUM_R, LECTURE_LEN, TIME_S, CLASS_NUM_S, days

raw_data_example = '''예시
1 	수리정보과학부 	자연계열교과핵심 	수학2 	4 	1 	정명주 	월3|월4|화2|수1|목5 	3 	18 	15
2 	화학생물학부 	자연계열교과핵심 	생물학및실험2 	3 	1 	권창섭 	월5|수2|목1 	6 	18 	16
3 	인문예술학부 	인문계열교과핵심 	한국사의이해 	3 	1 	강재순 	월6|목2|금1 	3 	18 	15'''
raw_data_short_example = raw_data_example.splitlines()[1]

lecture_data_example = '''예시
수학2, 정명주, 월3/월4/화2/수1/목5, 3반
생물학및실험2, 권창섭, 월5/수2/목1, 6반
한국사의이해, 강재순, 월6/목2/금1, 3반'''


raw_error_message = [
    '{row}번째 줄이 형식에 맞지 않습니다. 예시와 형식이 같은지 확인해주세요.',
    f'예시: {raw_data_short_example}',
    '주의: 각 항목은 2개 이상의 공백이나 탭으로 구분되어 있어야 합니다.',
    '해결이 되지 않는다면 key 값을 가지고 20-017 김병권에게 연락해주세요.',
]


def raw_error(row):
    errors = raw_error_message.copy()
    errors[0] = errors[0].format(row=row)
    return ValidationError([ValidationError(message) for message in errors])


lecture_error_message = [
    '{row}번째 줄이 형식에 맞지 않습니다.',
    '"교과명, 교원, 수업 시간, 분반" 형식인지 확인해 주세요.',
    '해결이 되지 않는다면 key 값을 가지고 20-017 김병권에게 연락해주세요.',
]


def lecture_error(row):
    errors = lecture_error_message.copy()
    errors[0] = errors[0].format(row=row)
    return ValidationError([ValidationError(message) for message in errors])


class RawForm(forms.Form):
    raw_data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': raw_data_example, 'rows': 15, 'cols': 150}),
                               label='',
                               help_text='''<br>
                                <a href="https://students.ksa.hs.kr/" target="_blank">https://students.ksa.hs.kr/</a>
                                > 수강정보 > 수강신청현황<br>
                                본인의 수강신청과목 표를 붙여넣으면 됩니다.(머리글 행 제외)<br>''')

    def clean_raw_data(self):
        cleaned_data = self.cleaned_data
        data = cleaned_data.get('raw_data')
        data = data.strip()
        data = data.splitlines()
        for i in range(len(data)):
            data[i] = data[i].replace('\t', '  ')  # two spaces
            data[i] = data[i].split('  ')
            data[i] = list(filter(None, data[i]))
            if len(data[i]) != RAW_LEN:
                raise raw_error(i+1)
            for j in range(len(data[i])):
                data[i][j] = data[i][j].strip()
            data[i][TIME_R] = data[i][TIME_R].split('|')
            for j in range(len(data[i][TIME_R])):
                if data[i][TIME_R][j][0] not in days or (not data[i][TIME_R][j][1:].isdigit()):
                    raise raw_error(i+1)
            if not data[i][CLASS_NUM_R].isdigit():
                raise raw_error(i+1)
        return cleaned_data.get('raw_data')


class DataForm(forms.Form):
    lecture_data = forms.CharField(widget=forms.Textarea(attrs={'placeholder': lecture_data_example,
                                                                'rows': 15, 'cols': 50}),
                                   label='수업 정보')
    use_link = forms.BooleanField(label='온라인 수업', required=False)
    include_aa = forms.BooleanField(label='AA 모임', required=False)
    links = forms.CharField(widget=forms.TextInput(attrs={'size': 50}), label='온라인 수업 링크')

    def clean_lecture_data(self):
        clean_data = self.cleaned_data
        data = clean_data.get('lecture_data')
        data = data.splitlines()
        for i in range(len(data)):
            data[i] = data[i].split(',')
            if len(data[i]) != LECTURE_LEN:
                raise lecture_error(i+1)
            for j in range(len(data[i])):
                data[i][j] = data[i][j].strip()
            data[i][TIME_S] = data[i][TIME_S].split('/')
            for j in range(len(data[i][TIME_S])):
                if not (data[i][TIME_S][j][0] in days and data[i][TIME_S][j][1:].isdigit()):
                    raise lecture_error(i+1)
            if not (data[i][CLASS_NUM_S].isdigit() or data[i][CLASS_NUM_S][:-1].isdigit()):
                raise lecture_error(i+1)
        return clean_data.get('lecture_data')

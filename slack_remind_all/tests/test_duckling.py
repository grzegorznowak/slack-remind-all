from utils.duckling_mod import DucklingWrapperMod


def test_duckling():
    d = DucklingWrapperMod()
    result = d.parse_time(u'Let\'s meet at 11:45am')

    assert result[-1]['dim'] == 'time'
    assert result[-1]['text'] == 'at 11:45am'

    result2 = d.parse_time(u'to scratch after midnight')
    assert result2[-1]['value']['value']['to'] is None

    result3 = d.parse_time(u'to scratch after midday')
    assert result3[-1]['text'] == 'after noon'




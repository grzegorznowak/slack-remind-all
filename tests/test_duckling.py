from duckling import DucklingWrapper


def test_duckling():
    d = DucklingWrapper()
    result = d.parse_time(u'Let\'s meet at 11:45am')

    assert result[-1]['dim'] == 'time'
    assert result[-1]['text'] == 'at 11:45am'